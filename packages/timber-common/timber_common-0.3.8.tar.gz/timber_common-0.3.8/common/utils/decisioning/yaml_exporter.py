# common/utils/decisioning/yaml_exporter.py
"""
YAML Exporter for Decision Definitions

Exports decision structures to the native YAML format.
Useful for:
- Converting DMN/CSV to YAML
- Debugging/inspecting decisions
- Version control friendly format
"""

import logging
from typing import Dict, Any, Union

from common.services.decisioning.models import (
    HitPolicy, DecisionType, ComparisonOperator,
    InputDefinition, OutputDefinition, RuleCondition, Rule,
    DecisionTable, Expression, DecisionNode, DecisionGraph,
)

logger = logging.getLogger(__name__)


def export_decision(
    decision: Union[DecisionTable, Expression, DecisionGraph],
) -> str:
    """
    Export a decision to YAML string.
    
    Args:
        decision: Decision to export
        
    Returns:
        YAML string
    """
    import yaml
    
    data = _decision_to_dict(decision)
    return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)


def export_decisions(
    decisions: list,
) -> str:
    """
    Export multiple decisions to YAML string.
    
    Args:
        decisions: List of decisions to export
        
    Returns:
        YAML string
    """
    import yaml
    
    data = {
        'decisions': [_decision_to_dict(d) for d in decisions]
    }
    return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)


def export_to_file(
    decision: Union[DecisionTable, Expression, DecisionGraph],
    path: str,
) -> None:
    """
    Export a decision to a YAML file.
    
    Args:
        decision: Decision to export
        path: Output file path
    """
    yaml_str = export_decision(decision)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(yaml_str)


def _decision_to_dict(
    decision: Union[DecisionTable, Expression, DecisionGraph],
) -> Dict[str, Any]:
    """Convert a decision to dictionary."""
    if isinstance(decision, DecisionTable):
        return _table_to_dict(decision)
    elif isinstance(decision, Expression):
        return _expression_to_dict(decision)
    elif isinstance(decision, DecisionGraph):
        return _graph_to_dict(decision)
    else:
        raise ValueError(f"Unknown decision type: {type(decision)}")


def _table_to_dict(table: DecisionTable) -> Dict[str, Any]:
    """Convert a decision table to dictionary."""
    data = {
        'id': table.id,
        'name': table.name,
        'type': 'decision_table',
        'hit_policy': table.hit_policy.name,
    }
    
    if table.description:
        data['description'] = table.description
    
    if table.version != '1.0.0':
        data['version'] = table.version
    
    if table.tags:
        data['tags'] = table.tags
    
    # Inputs
    data['inputs'] = [_input_to_dict(inp) for inp in table.inputs]
    
    # Outputs
    data['outputs'] = [_output_to_dict(out) for out in table.outputs]
    
    # Rules
    data['rules'] = [_rule_to_dict(rule) for rule in table.rules]
    
    return data


def _expression_to_dict(expr: Expression) -> Dict[str, Any]:
    """Convert an expression decision to dictionary."""
    data = {
        'id': expr.id,
        'name': expr.name,
        'type': 'expression',
        'expression': expr.expression,
    }
    
    if expr.description:
        data['description'] = expr.description
    
    if expr.version != '1.0.0':
        data['version'] = expr.version
    
    if expr.inputs:
        data['inputs'] = [_input_to_dict(inp) for inp in expr.inputs]
    
    if expr.output:
        data['output'] = _output_to_dict(expr.output)
    
    return data


def _graph_to_dict(graph: DecisionGraph) -> Dict[str, Any]:
    """Convert a decision graph to dictionary."""
    data = {
        'id': graph.id,
        'name': graph.name,
        'type': 'decision_graph',
    }
    
    if graph.description:
        data['description'] = graph.description
    
    if graph.version != '1.0.0':
        data['version'] = graph.version
    
    if graph.input_data:
        data['inputs'] = [_input_to_dict(inp) for inp in graph.input_data.values()]
    
    # Nodes
    data['nodes'] = [_node_to_dict(node) for node in graph.decisions.values()]
    
    return data


def _node_to_dict(node: DecisionNode) -> Dict[str, Any]:
    """Convert a decision node to dictionary."""
    data = {
        'id': node.id,
        'name': node.name,
        'type': node.decision_type.value,
    }
    
    if node.description:
        data['description'] = node.description
    
    if node.dependencies:
        data['dependencies'] = node.dependencies
    
    # Include definition based on type
    if node.decision_type == DecisionType.DECISION_TABLE:
        if isinstance(node.definition, DecisionTable):
            data['definition'] = _table_to_dict(node.definition)
    elif node.decision_type == DecisionType.EXPRESSION:
        if isinstance(node.definition, Expression):
            data['definition'] = _expression_to_dict(node.definition)
        elif isinstance(node.definition, str):
            data['definition'] = node.definition
    else:
        data['definition'] = node.definition
    
    return data


def _input_to_dict(inp: InputDefinition) -> Dict[str, Any]:
    """Convert an input definition to dictionary."""
    data = {'name': inp.name}
    
    if inp.type != 'any':
        data['type'] = inp.type
    
    if inp.label and inp.label != inp.name:
        data['label'] = inp.label
    
    if inp.description:
        data['description'] = inp.description
    
    if inp.allowed_values:
        data['allowed_values'] = inp.allowed_values
    
    if inp.default is not None:
        data['default'] = inp.default
    
    if not inp.required:
        data['required'] = False
    
    return data


def _output_to_dict(out: OutputDefinition) -> Dict[str, Any]:
    """Convert an output definition to dictionary."""
    data = {'name': out.name}
    
    if out.type != 'any':
        data['type'] = out.type
    
    if out.label and out.label != out.name:
        data['label'] = out.label
    
    if out.description:
        data['description'] = out.description
    
    if out.allowed_values:
        data['allowed_values'] = out.allowed_values
    
    if out.default is not None:
        data['default'] = out.default
    
    if out.priority_order:
        data['priority_order'] = out.priority_order
    
    return data


def _rule_to_dict(rule: Rule) -> Dict[str, Any]:
    """Convert a rule to dictionary."""
    data = {}
    
    # Only include ID if not auto-generated
    if rule.id and not rule.id.startswith('rule_'):
        data['id'] = rule.id
    
    # Conditions
    conditions = {}
    for cond in rule.conditions:
        conditions[cond.input_name] = _condition_to_dict(cond)
    
    if conditions:
        data['conditions'] = conditions
    
    # Outputs
    data['outputs'] = rule.outputs
    
    if rule.annotation:
        data['annotation'] = rule.annotation
    
    if rule.description:
        data['description'] = rule.description
    
    if rule.priority != 0:
        data['priority'] = rule.priority
    
    if not rule.enabled:
        data['enabled'] = False
    
    return data


def _condition_to_dict(cond: RuleCondition) -> Any:
    """Convert a condition to dictionary or simple value."""
    # ANY operator
    if cond.operator == ComparisonOperator.ANY:
        return '-'
    
    # Simple equality
    if cond.operator == ComparisonOperator.EQUAL:
        return cond.value
    
    # Complex condition
    data = {
        'operator': cond.operator.value,
        'value': cond.value,
    }
    
    if cond.value_end is not None:
        data['value_end'] = cond.value_end
    
    return data
