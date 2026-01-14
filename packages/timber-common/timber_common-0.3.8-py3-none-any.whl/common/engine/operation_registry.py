"""
Operation Registry System

This module provides a decorator-based system for registering operations
that can be called from configuration files.
"""

from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import inspect


class OperationType(Enum):
    """Types of operations supported"""
    FETCH = "fetch"           # Fetch data from external sources
    TRANSFORM = "transform"   # Transform/process data
    AGGREGATE = "aggregate"   # Aggregate/summarize data
    VALIDATE = "validate"     # Validate data
    CUSTOM = "custom"         # Custom operations


@dataclass
class OperationMetadata:
    """Metadata for a registered operation"""
    name: str
    operation_type: OperationType
    function: Callable
    description: Optional[str] = None
    inputs: Optional[List[Dict[str, Any]]] = None
    outputs: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


class OperationRegistry:
    """
    Registry for business logic operations.
    
    Allows operations to be registered and called dynamically from configuration.
    """
    
    def __init__(self):
        self._operations: Dict[str, OperationMetadata] = {}
    
    def register(
        self,
        name: str,
        operation_type: OperationType = OperationType.CUSTOM,
        description: Optional[str] = None,
        inputs: Optional[List[Dict[str, Any]]] = None,
        outputs: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Decorator to register an operation.
        
        Usage:
            @registry.register(
                name="fetch_stock_data",
                operation_type=OperationType.FETCH,
                description="Fetches historical stock data"
            )
            def my_fetch_function(symbol: str, period: str):
                ...
        """
        def decorator(func: Callable) -> Callable:
            # Auto-extract inputs from function signature if not provided
            if inputs is None:
                sig = inspect.signature(func)
                extracted_inputs = []
                for param_name, param in sig.parameters.items():
                    input_def = {
                        "name": param_name,
                        "type": param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "any",
                        "required": param.default == inspect.Parameter.empty
                    }
                    if param.default != inspect.Parameter.empty:
                        input_def["default"] = param.default
                    extracted_inputs.append(input_def)
                final_inputs = extracted_inputs
            else:
                final_inputs = inputs
            
            metadata = OperationMetadata(
                name=name,
                operation_type=operation_type,
                function=func,
                description=description or func.__doc__,
                inputs=final_inputs,
                outputs=outputs,
                tags=tags or []
            )
            
            self._operations[name] = metadata
            return func
        
        return decorator
    
    def get_operation(self, name: str) -> Optional[OperationMetadata]:
        """Get operation metadata by name"""
        return self._operations.get(name)
    
    def execute(self, name: str, **kwargs) -> Any:
        """Execute an operation by name with given arguments"""
        operation = self.get_operation(name)
        if not operation:
            raise ValueError(f"Operation '{name}' not found in registry")
        
        return operation.function(**kwargs)
    
    def list_operations(
        self,
        operation_type: Optional[OperationType] = None,
        tags: Optional[List[str]] = None
    ) -> List[OperationMetadata]:
        """List all registered operations, optionally filtered"""
        operations = list(self._operations.values())
        
        if operation_type:
            operations = [op for op in operations if op.operation_type == operation_type]
        
        if tags:
            operations = [
                op for op in operations
                if op.tags and any(tag in op.tags for tag in tags)
            ]
        
        return operations
    
    def get_operation_schema(self, name: str) -> Dict[str, Any]:
        """Get JSON schema for an operation"""
        operation = self.get_operation(name)
        if not operation:
            raise ValueError(f"Operation '{name}' not found")
        
        return {
            "name": operation.name,
            "type": operation.operation_type.value,
            "description": operation.description,
            "inputs": operation.inputs or [],
            "outputs": operation.outputs or [],
            "tags": operation.tags or []
        }
    
    def export_schema(self) -> Dict[str, Any]:
        """Export full registry schema for documentation/validation"""
        return {
            "version": "1.0",
            "operations": {
                name: self.get_operation_schema(name)
                for name in self._operations.keys()
            }
        }


# Global registry instance
registry = OperationRegistry()


# Convenience decorators
def fetch_operation(name: str, **kwargs):
    """Decorator for fetch operations"""
    return registry.register(name, operation_type=OperationType.FETCH, **kwargs)


def transform_operation(name: str, **kwargs):
    """Decorator for transform operations"""
    return registry.register(name, operation_type=OperationType.TRANSFORM, **kwargs)


def aggregate_operation(name: str, **kwargs):
    """Decorator for aggregate operations"""
    return registry.register(name, operation_type=OperationType.AGGREGATE, **kwargs)