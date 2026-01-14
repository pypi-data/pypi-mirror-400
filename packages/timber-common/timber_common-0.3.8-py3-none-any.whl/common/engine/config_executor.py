"""
Configuration Executor

Executes business logic operations defined in YAML/JSON configuration files.

FIXED: Properly handles DataFrame and complex object references without converting to strings.
"""

import yaml
import json
from typing import Any, Dict, Optional, List
from pathlib import Path
from jinja2 import Environment, BaseLoader, TemplateSyntaxError
import re

from common.engine.operation_registry import registry, OperationType


class ConfigExecutor:
    """
    Executes operations defined in configuration files.
    
    Supports:
    - Simple operation calls
    - Pipeline composition
    - Variable substitution with Jinja2
    - Conditional execution
    - Error handling
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize executor.
        
        Args:
            config_path: Path to configuration file or directory
        """
        self.config_path = config_path
        self.jinja_env = Environment(loader=BaseLoader())
        self.context: Dict[str, Any] = {}
    
    def load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file"""
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        with open(path_obj, 'r') as f:
            if path_obj.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif path_obj.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {path_obj.suffix}")
    
    def render_template(self, template_str: str, context: Dict[str, Any]) -> Any:
        """
        Render a Jinja2 template string with given context.
        
        IMPORTANT: For direct variable references (like {{ var }} or {{ var[0] }}),
        returns the actual Python object from context instead of string representation.
        This preserves DataFrames and other complex objects.
        
        Args:
            template_str: Template string (e.g., "{{ symbol }}" or "{{ df[0] }}")
            context: Variables available to template
            
        Returns:
            Rendered value (can be string, number, DataFrame, etc.)
        """
        if not isinstance(template_str, str):
            return template_str
        
        # If it looks like a template
        if '{{' in template_str or '{%' in template_str:
            try:
                # Check if this is a simple variable reference (not a complex expression)
                # Matches patterns like:
                #   {{ variable_name }}
                #   {{ variable_name[0] }}
                #   {{ variable_name[0][1] }}
                #   {{ variable_name['key'] }}
                simple_var_pattern = r'^\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*(?:\[[^\]]+\])*)\s*\}\}$'
                match = re.match(simple_var_pattern, template_str.strip())
                
                if match:
                    # This is a simple variable reference - evaluate directly in context
                    var_expr = match.group(1)
                    try:
                        # Use eval with the context as locals (safe for variable lookups)
                        # We restrict __builtins__ to prevent code execution
                        result = eval(var_expr, {"__builtins__": {}}, context)
                        return result
                    except Exception as e:
                        # If eval fails, fall back to template rendering
                        print(f"Warning: Failed to eval '{var_expr}': {e}")
                        pass
                
                # For complex expressions or filters (like {{ var | default(10) }}), use Jinja2
                template = self.jinja_env.from_string(template_str)
                result = template.render(**context)
                
                # Try to evaluate as Python literal if it looks like one
                try:
                    import ast
                    return ast.literal_eval(result)
                except (ValueError, SyntaxError):
                    return result
            except TemplateSyntaxError as e:
                raise ValueError(f"Template syntax error: {e}")
        
        return template_str
    
    def resolve_inputs(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve input values using context and templates"""
        resolved = {}
        for key, value in inputs.items():
            if isinstance(value, dict):
                resolved[key] = self.resolve_inputs(value, context)
            elif isinstance(value, list):
                resolved[key] = [
                    self.resolve_inputs(item, context) if isinstance(item, dict) else self.render_template(item, context)
                    for item in value
                ]
            else:
                resolved[key] = self.render_template(value, context)
        return resolved
    
    def execute_operation(self, operation_config: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Execute a single operation.
        
        Args:
            operation_config: Operation configuration
            context: Current execution context
            
        Returns:
            Operation result
        """
        operation_name = operation_config.get('operation')
        if not operation_name:
            raise ValueError("Operation configuration must include 'operation' key")
        
        # Get inputs and resolve templates
        inputs = operation_config.get('inputs', {})
        resolved_inputs = self.resolve_inputs(inputs, context)
        
        # Debug: print input types
        # print(f"Executing {operation_name} with inputs:")
        # for k, v in resolved_inputs.items():
        #     print(f"  {k}: {type(v).__name__}")
        
        # Execute operation
        try:
            result = registry.execute(operation_name, **resolved_inputs)
            return result
        except Exception as e:
            # Handle error based on config
            on_error = operation_config.get('on_error', 'raise')
            if on_error == 'raise':
                raise
            elif on_error == 'continue':
                return None
            elif on_error == 'return_error':
                return {"error": str(e)}
            else:
                raise ValueError(f"Unknown error handling mode: {on_error}")
    
    def execute_pipeline(self, pipeline_config: Dict[str, Any], initial_context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a pipeline of operations.
        
        Args:
            pipeline_config: Pipeline configuration with steps
            initial_context: Initial variables for the pipeline
            
        Returns:
            Final result based on pipeline's return configuration
        """
        context = initial_context.copy() if initial_context else {}
        steps = pipeline_config.get('steps', [])
        
        for i, step in enumerate(steps):
            # Check condition if present
            condition = step.get('condition')
            if condition:
                should_execute = self.render_template(condition, context)
                if not should_execute:
                    continue
            
            # Execute operation
            result = self.execute_operation(step, context)
            
            # Store result in context if output_var specified
            output_var = step.get('output_var')
            if output_var:
                context[output_var] = result
                # Debug
                # print(f"Step {i+1}: Stored {output_var} as {type(result).__name__}")
        
        # Return final result
        return_expr = pipeline_config.get('return')
        if return_expr:
            return self.render_template(f"{{{{ {return_expr} }}}}", context)
        
        return context
    
    def execute_config(self, config: Dict[str, Any], operation_name: str, **kwargs) -> Any:
        """
        Execute a named operation from a configuration.
        
        Args:
            config: Full configuration dictionary
            operation_name: Name of the operation to execute
            **kwargs: Arguments to pass to the operation
            
        Returns:
            Operation result
        """
        operations = config.get('operations', {})
        operation_config = operations.get(operation_name)
        
        if not operation_config:
            raise ValueError(f"Operation '{operation_name}' not found in config")
        
        op_type = operation_config.get('type', 'simple')
        
        if op_type == 'pipeline':
            return self.execute_pipeline(operation_config, initial_context=kwargs)
        elif op_type == 'simple' or op_type == 'fetch':
            # For simple operations, merge config with kwargs
            inputs = operation_config.get('inputs', {})
            # Override config inputs with provided kwargs
            inputs.update(kwargs)
            
            exec_config = {
                'operation': operation_config.get('operation', operation_name),
                'inputs': inputs
            }
            return self.execute_operation(exec_config, context=kwargs)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
    
    def execute_from_file(self, config_file: str, operation_name: str, **kwargs) -> Any:
        """
        Load config from file and execute operation.
        
        Args:
            config_file: Path to configuration file
            operation_name: Name of operation to execute
            **kwargs: Arguments to pass
            
        Returns:
            Operation result
        """
        config = self.load_config(config_file)
        return self.execute_config(config, operation_name, **kwargs)


class ConfigBuilder:
    """Helper class to build configuration programmatically"""
    
    def __init__(self):
        self.config = {
            'version': '1.0',
            'operations': {}
        }
    
    def add_simple_operation(
        self,
        name: str,
        operation: str,
        inputs: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ):
        """Add a simple operation"""
        self.config['operations'][name] = {
            'type': 'simple',
            'operation': operation,
            'inputs': inputs or {},
        }
        if description:
            self.config['operations'][name]['description'] = description
        return self
    
    def add_pipeline(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        return_expr: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Add a pipeline operation"""
        self.config['operations'][name] = {
            'type': 'pipeline',
            'steps': steps,
        }
        if return_expr:
            self.config['operations'][name]['return'] = return_expr
        if description:
            self.config['operations'][name]['description'] = description
        return self
    
    def to_yaml(self, file_path: str):
        """Export configuration to YAML file"""
        with open(file_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
    
    def to_json(self, file_path: str):
        """Export configuration to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration dictionary"""
        return self.config