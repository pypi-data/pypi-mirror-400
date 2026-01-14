# common/utils/decisioning/yaml_parser.py
"""
YAML Parser for Decision Definitions

Parses the native YAML format into decision engine structures.
This is the canonical format - all other formats convert to this.

YAML Format Example:
```yaml
decisions:
  - id: loan_approval
    name: Loan Approval Decision
    type: decision_table
    hit_policy: FIRST
    inputs:
      - name: credit_score
        type: number
        required: true
      - name: annual_income
        type: number
    outputs:
      - name: approved
        type: boolean
      - name: rate
        type: number
    rules:
      - conditions:
          credit_score: {operator: ">=", value: 700}
          annual_income: {operator: ">=", value: 50000}
        outputs:
          approved: true
          rate: 5.5
```
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Union

from common.services.decisioning.models import (
    HitPolicy, DecisionType, ComparisonOperator,
    InputDefinition, OutputDefinition, RuleCondition, Rule,
    DecisionTable, Expression, DecisionNode, DecisionGraph,
)

logger = logging.getLogger(__name__)


def parse_file(path: str) -> List[Union[DecisionTable, Expression, DecisionGraph]]:
    """
    Parse a YAML file into decision structures.
    
    Args:
        path: Path to YAML file
        
    Returns:
        List of parsed decisions
    """
    import yaml
    
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    return parse_dict(data)


def parse_dict(data: Dict[str, Any]) -> List[Union[DecisionTable, Expression, DecisionGraph]]:
    """
    Parse a dictionary into decision structures.
    
    Args:
        data: Parsed YAML dictionary
        
    Returns:
        List of parsed decisions
    """
    decisions = []
    
    # Handle both single decision and list of decisions
    decision_list = data.get('decisions', [data] if 'id' in data else [])
    
    for decision_data in decision_list:
        decision = _parse_decision(decision_data)
        if decision:
            decisions.append(decision)
    
    return decisions


def _parse_decision(data: Dict[str, Any]) -> Union[DecisionTable, Expression, DecisionGraph, None]:
    """Parse a single decision definition."""
    decision_type = data.get('type', 'decision_table')
    
    if decision_type == 'decision_table':
        return _parse_decision_table(data)
    elif decision_type == 'expression':
        return _parse_expression(data)
    elif decision_type == 'decision_graph' or decision_type == 'graph':
        return _parse_decision_graph(data)
    else:
        logger.warning(f"Unknown decision type: {decision_type}")
        return None


def _parse_decision_table(data: Dict[str, Any]) -> DecisionTable:
    """Parse a decision table."""
    # Parse inputs
    inputs = []
    for input_data in data.get('inputs', []):
        inputs.append(_parse_input_definition(input_data))
    
    # Parse outputs
    outputs = []
    for output_data in data.get('outputs', []):
        outputs.append(_parse_output_definition(output_data))
    
    # Parse rules
    rules = []
    for i, rule_data in enumerate(data.get('rules', [])):
        rule = _parse_rule(rule_data, i, inputs)
        rules.append(rule)
    
    # Parse hit policy
    hit_policy = HitPolicy.FIRST
    if 'hit_policy' in data:
        hit_policy = HitPolicy.from_string(data['hit_policy'])
    
    return DecisionTable(
        id=data['id'],
        name=data.get('name', data['id']),
        hit_policy=hit_policy,
        inputs=inputs,
        outputs=outputs,
        rules=rules,
        description=data.get('description'),
        version=data.get('version', '1.0.0'),
        tags=data.get('tags', []),
    )


def _parse_input_definition(data: Union[Dict, str]) -> InputDefinition:
    """Parse an input definition."""
    if isinstance(data, str):
        return InputDefinition(name=data)
    
    return InputDefinition(
        name=data['name'],
        type=data.get('type', 'any'),
        label=data.get('label'),
        description=data.get('description'),
        allowed_values=data.get('allowed_values'),
        default=data.get('default'),
        required=data.get('required', True),
    )


def _parse_output_definition(data: Union[Dict, str]) -> OutputDefinition:
    """Parse an output definition."""
    if isinstance(data, str):
        return OutputDefinition(name=data)
    
    return OutputDefinition(
        name=data['name'],
        type=data.get('type', 'any'),
        label=data.get('label'),
        description=data.get('description'),
        allowed_values=data.get('allowed_values'),
        default=data.get('default'),
        priority_order=data.get('priority_order'),
    )


def _parse_rule(
    data: Dict[str, Any],
    index: int,
    inputs: List[InputDefinition],
) -> Rule:
    """Parse a rule."""
    rule_id = data.get('id', f'rule_{index + 1}')
    
    # Parse conditions
    conditions = []
    conditions_data = data.get('conditions', {})
    
    # Handle list format (explicit conditions)
    if isinstance(conditions_data, list):
        for cond in conditions_data:
            conditions.append(_parse_condition(cond))
    # Handle dict format (input_name -> condition)
    elif isinstance(conditions_data, dict):
        for input_name, cond_value in conditions_data.items():
            condition = _parse_condition_value(input_name, cond_value)
            conditions.append(condition)
    
    # Parse outputs
    outputs = data.get('outputs', {})
    
    return Rule(
        id=rule_id,
        conditions=conditions,
        outputs=outputs,
        annotation=data.get('annotation'),
        description=data.get('description'),
        priority=data.get('priority', 0),
        enabled=data.get('enabled', True),
    )


def _parse_condition(data: Dict[str, Any]) -> RuleCondition:
    """Parse an explicit condition definition."""
    operator = ComparisonOperator.from_string(data.get('operator', '=='))
    
    return RuleCondition(
        input_name=data['input'],
        operator=operator,
        value=data.get('value'),
        value_end=data.get('value_end'),
    )


def _parse_condition_value(input_name: str, value: Any) -> RuleCondition:
    """Parse a condition value (can be simple value or operator dict)."""
    # Wildcard / any
    if value == '-' or value == '*' or value is None:
        return RuleCondition(
            input_name=input_name,
            operator=ComparisonOperator.ANY,
            value=None,
        )
    
    # Simple equality
    if not isinstance(value, dict):
        return RuleCondition(
            input_name=input_name,
            operator=ComparisonOperator.EQUAL,
            value=value,
        )
    
    # Operator dict: {operator: ">=", value: 100}
    operator = ComparisonOperator.from_string(value.get('operator', '=='))
    
    return RuleCondition(
        input_name=input_name,
        operator=operator,
        value=value.get('value'),
        value_end=value.get('value_end'),
    )


def _parse_expression(data: Dict[str, Any]) -> Expression:
    """Parse an expression decision."""
    inputs = []
    for input_data in data.get('inputs', []):
        inputs.append(_parse_input_definition(input_data))
    
    output = None
    if 'output' in data:
        output = _parse_output_definition(data['output'])
    
    return Expression(
        id=data['id'],
        name=data.get('name', data['id']),
        expression=data['expression'],
        inputs=inputs,
        output=output,
        description=data.get('description'),
        version=data.get('version', '1.0.0'),
    )


def _parse_decision_graph(data: Dict[str, Any]) -> DecisionGraph:
    """Parse a decision graph."""
    decisions = {}
    
    for node_data in data.get('nodes', data.get('decisions', [])):
        node = _parse_decision_node(node_data)
        decisions[node.id] = node
    
    input_data = {}
    for input_def in data.get('inputs', []):
        inp = _parse_input_definition(input_def)
        input_data[inp.name] = inp
    
    return DecisionGraph(
        id=data['id'],
        name=data.get('name', data['id']),
        decisions=decisions,
        input_data=input_data,
        description=data.get('description'),
        version=data.get('version', '1.0.0'),
    )


def _parse_decision_node(data: Dict[str, Any]) -> DecisionNode:
    """Parse a decision node in a graph."""
    node_type = data.get('type', 'decision_table')
    decision_type = _map_to_decision_type(node_type)
    
    # Parse the definition based on type
    if decision_type == DecisionType.DECISION_TABLE:
        definition = _parse_decision_table(data.get('definition', data))
    elif decision_type == DecisionType.EXPRESSION:
        if isinstance(data.get('definition'), str):
            # Simple expression string
            definition = data['definition']
        else:
            definition = _parse_expression(data.get('definition', data))
    else:
        definition = data.get('definition')
    
    return DecisionNode(
        id=data['id'],
        name=data.get('name', data['id']),
        decision_type=decision_type,
        definition=definition,
        dependencies=data.get('dependencies', data.get('requires', [])),
        description=data.get('description'),
    )


def _map_to_decision_type(type_str: str) -> DecisionType:
    """Map string to DecisionType enum."""
    mapping = {
        'decision_table': DecisionType.DECISION_TABLE,
        'table': DecisionType.DECISION_TABLE,
        'expression': DecisionType.EXPRESSION,
        'expr': DecisionType.EXPRESSION,
        'literal': DecisionType.LITERAL,
        'context': DecisionType.CONTEXT,
        'function': DecisionType.FUNCTION,
        'invocation': DecisionType.INVOCATION,
        'relation': DecisionType.RELATION,
    }
    return mapping.get(type_str.lower(), DecisionType.DECISION_TABLE)
