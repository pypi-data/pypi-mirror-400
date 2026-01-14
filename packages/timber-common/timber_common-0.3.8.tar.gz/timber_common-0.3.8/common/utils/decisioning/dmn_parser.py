# common/utils/decisioning/dmn_parser.py
"""
DMN XML Parser

Parses standard OMG DMN (Decision Model and Notation) XML files
and converts them to the internal YAML format.

Supports DMN 1.1, 1.2, and 1.3 schemas.

DMN Structure:
- definitions: Root element
  - decision: A decision (can contain decisionTable, literalExpression, etc.)
  - inputData: Input data element
  - knowledgeSource: Business knowledge
  - businessKnowledgeModel: Reusable decision logic
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Union, Optional
from xml.etree import ElementTree as ET

from common.services.decisioning.models import (
    HitPolicy, DecisionType, ComparisonOperator,
    InputDefinition, OutputDefinition, RuleCondition, Rule,
    DecisionTable, Expression, DecisionNode, DecisionGraph,
)

logger = logging.getLogger(__name__)

# DMN Namespaces
DMN_NAMESPACES = {
    'dmn': 'https://www.omg.org/spec/DMN/20191111/MODEL/',
    'dmn13': 'https://www.omg.org/spec/DMN/20191111/MODEL/',
    'dmn12': 'http://www.omg.org/spec/DMN/20180521/MODEL/',
    'dmn11': 'http://www.omg.org/spec/DMN/20151101/dmn.xsd',
    'feel': 'https://www.omg.org/spec/DMN/20191111/FEEL/',
    'dmndi': 'https://www.omg.org/spec/DMN/20191111/DMNDI/',
}


def parse_file(path: str) -> List[Union[DecisionTable, Expression, DecisionGraph]]:
    """
    Parse a DMN XML file into decision structures.
    
    Args:
        path: Path to DMN file
        
    Returns:
        List of parsed decisions
    """
    tree = ET.parse(path)
    root = tree.getroot()
    
    return parse_element(root)


def parse_string(xml_string: str) -> List[Union[DecisionTable, Expression, DecisionGraph]]:
    """
    Parse a DMN XML string into decision structures.
    
    Args:
        xml_string: DMN XML content
        
    Returns:
        List of parsed decisions
    """
    root = ET.fromstring(xml_string)
    return parse_element(root)


def parse_element(root: ET.Element) -> List[Union[DecisionTable, Expression, DecisionGraph]]:
    """
    Parse a DMN XML element tree.
    
    Args:
        root: Root XML element
        
    Returns:
        List of parsed decisions
    """
    # Detect namespace
    ns = _detect_namespace(root)
    
    decisions = []
    
    # Parse all decision elements
    for decision_elem in root.findall(f'.//{ns}decision', DMN_NAMESPACES) + \
                         root.findall('.//decision'):
        try:
            decision = _parse_decision_element(decision_elem, ns)
            if decision:
                decisions.append(decision)
        except Exception as e:
            logger.warning(f"Failed to parse decision element: {e}")
    
    # If there are information requirements, build a graph
    if _has_dependencies(root, ns):
        graph = _build_decision_graph(root, ns, decisions)
        if graph:
            return [graph]
    
    return decisions


def _detect_namespace(root: ET.Element) -> str:
    """Detect the DMN namespace from the root element."""
    tag = root.tag
    
    # Extract namespace from tag like {namespace}localname
    if tag.startswith('{'):
        ns_uri = tag[1:tag.index('}')]
        
        # Map to prefix
        for prefix, uri in DMN_NAMESPACES.items():
            if uri == ns_uri:
                return f'{prefix}:'
    
    # Try common prefixes
    for prefix in ['dmn', 'dmn13', 'dmn12', 'dmn11']:
        if root.find(f'.//{prefix}:decision', DMN_NAMESPACES) is not None:
            return f'{prefix}:'
    
    # No namespace
    return ''


def _parse_decision_element(
    elem: ET.Element,
    ns: str,
) -> Optional[Union[DecisionTable, Expression]]:
    """Parse a DMN decision element."""
    decision_id = elem.get('id', '')
    decision_name = elem.get('name', decision_id)
    
    # Check for decision table
    dt_elem = elem.find(f'{ns}decisionTable', DMN_NAMESPACES) or \
              elem.find('decisionTable')
    
    if dt_elem is not None:
        return _parse_decision_table_element(dt_elem, decision_id, decision_name, ns)
    
    # Check for literal expression
    expr_elem = elem.find(f'{ns}literalExpression', DMN_NAMESPACES) or \
                elem.find('literalExpression')
    
    if expr_elem is not None:
        return _parse_expression_element(expr_elem, decision_id, decision_name, ns)
    
    # Check for invocation
    inv_elem = elem.find(f'{ns}invocation', DMN_NAMESPACES) or \
               elem.find('invocation')
    
    if inv_elem is not None:
        # Convert invocation to expression for simplicity
        return _parse_invocation_element(inv_elem, decision_id, decision_name, ns)
    
    logger.warning(f"Decision '{decision_id}' has no recognized expression type")
    return None


def _parse_decision_table_element(
    elem: ET.Element,
    decision_id: str,
    decision_name: str,
    ns: str,
) -> DecisionTable:
    """Parse a DMN decisionTable element."""
    # Parse hit policy
    hit_policy_str = elem.get('hitPolicy', 'UNIQUE')
    aggregation = elem.get('aggregation', '')
    hit_policy = _map_hit_policy(hit_policy_str, aggregation)
    
    # Parse inputs
    inputs = []
    for input_elem in elem.findall(f'{ns}input', DMN_NAMESPACES) + elem.findall('input'):
        inp = _parse_input_element(input_elem, ns)
        inputs.append(inp)
    
    # Parse outputs
    outputs = []
    for output_elem in elem.findall(f'{ns}output', DMN_NAMESPACES) + elem.findall('output'):
        out = _parse_output_element(output_elem, ns)
        outputs.append(out)
    
    # Parse rules
    rules = []
    for i, rule_elem in enumerate(elem.findall(f'{ns}rule', DMN_NAMESPACES) + elem.findall('rule')):
        rule = _parse_rule_element(rule_elem, i, inputs, outputs, ns)
        rules.append(rule)
    
    return DecisionTable(
        id=decision_id,
        name=decision_name,
        hit_policy=hit_policy,
        inputs=inputs,
        outputs=outputs,
        rules=rules,
    )


def _parse_input_element(elem: ET.Element, ns: str) -> InputDefinition:
    """Parse a DMN input element."""
    input_id = elem.get('id', '')
    label = elem.get('label', input_id)
    
    # Get input expression
    input_expr = elem.find(f'{ns}inputExpression', DMN_NAMESPACES) or \
                 elem.find('inputExpression')
    
    name = input_id
    input_type = 'any'
    
    if input_expr is not None:
        type_ref = input_expr.get('typeRef', 'any')
        input_type = _map_dmn_type(type_ref)
        
        # Get the text expression
        text_elem = input_expr.find(f'{ns}text', DMN_NAMESPACES) or \
                    input_expr.find('text')
        if text_elem is not None and text_elem.text:
            name = text_elem.text.strip()
    
    # Get allowed values
    allowed_values = None
    values_elem = elem.find(f'{ns}inputValues', DMN_NAMESPACES) or \
                  elem.find('inputValues')
    if values_elem is not None:
        text_elem = values_elem.find(f'{ns}text', DMN_NAMESPACES) or \
                    values_elem.find('text')
        if text_elem is not None and text_elem.text:
            allowed_values = _parse_feel_list(text_elem.text)
    
    return InputDefinition(
        name=name,
        type=input_type,
        label=label,
        allowed_values=allowed_values,
    )


def _parse_output_element(elem: ET.Element, ns: str) -> OutputDefinition:
    """Parse a DMN output element."""
    output_id = elem.get('id', '')
    name = elem.get('name', output_id)
    label = elem.get('label', name)
    type_ref = elem.get('typeRef', 'any')
    
    # Get allowed values
    allowed_values = None
    values_elem = elem.find(f'{ns}outputValues', DMN_NAMESPACES) or \
                  elem.find('outputValues')
    if values_elem is not None:
        text_elem = values_elem.find(f'{ns}text', DMN_NAMESPACES) or \
                    values_elem.find('text')
        if text_elem is not None and text_elem.text:
            allowed_values = _parse_feel_list(text_elem.text)
    
    return OutputDefinition(
        name=name,
        type=_map_dmn_type(type_ref),
        label=label,
        allowed_values=allowed_values,
    )


def _parse_rule_element(
    elem: ET.Element,
    index: int,
    inputs: List[InputDefinition],
    outputs: List[OutputDefinition],
    ns: str,
) -> Rule:
    """Parse a DMN rule element."""
    rule_id = elem.get('id', f'rule_{index + 1}')
    
    # Get annotation
    annotation = None
    desc_elem = elem.find(f'{ns}description', DMN_NAMESPACES) or \
                elem.find('description')
    if desc_elem is not None and desc_elem.text:
        annotation = desc_elem.text.strip()
    
    # Parse input entries
    conditions = []
    input_entries = elem.findall(f'{ns}inputEntry', DMN_NAMESPACES) + elem.findall('inputEntry')
    
    for i, entry_elem in enumerate(input_entries):
        if i < len(inputs):
            input_name = inputs[i].name
            text_elem = entry_elem.find(f'{ns}text', DMN_NAMESPACES) or \
                        entry_elem.find('text')
            
            if text_elem is not None and text_elem.text:
                condition = _parse_feel_condition(input_name, text_elem.text.strip())
                conditions.append(condition)
    
    # Parse output entries
    output_values = {}
    output_entries = elem.findall(f'{ns}outputEntry', DMN_NAMESPACES) + elem.findall('outputEntry')
    
    for i, entry_elem in enumerate(output_entries):
        if i < len(outputs):
            output_name = outputs[i].name
            text_elem = entry_elem.find(f'{ns}text', DMN_NAMESPACES) or \
                        entry_elem.find('text')
            
            if text_elem is not None and text_elem.text:
                output_values[output_name] = _parse_feel_value(text_elem.text.strip())
    
    return Rule(
        id=rule_id,
        conditions=conditions,
        outputs=output_values,
        annotation=annotation,
    )


def _parse_expression_element(
    elem: ET.Element,
    decision_id: str,
    decision_name: str,
    ns: str,
) -> Expression:
    """Parse a DMN literalExpression element."""
    text_elem = elem.find(f'{ns}text', DMN_NAMESPACES) or elem.find('text')
    expression = text_elem.text.strip() if text_elem is not None and text_elem.text else ''
    
    type_ref = elem.get('typeRef', 'any')
    
    return Expression(
        id=decision_id,
        name=decision_name,
        expression=expression,
        output=OutputDefinition(name='result', type=_map_dmn_type(type_ref)),
    )


def _parse_invocation_element(
    elem: ET.Element,
    decision_id: str,
    decision_name: str,
    ns: str,
) -> Expression:
    """Parse a DMN invocation element (converted to expression)."""
    # Get the called decision
    expr_elem = elem.find(f'{ns}literalExpression', DMN_NAMESPACES) or \
                elem.find('literalExpression')
    
    expression = ''
    if expr_elem is not None:
        text_elem = expr_elem.find(f'{ns}text', DMN_NAMESPACES) or expr_elem.find('text')
        if text_elem is not None and text_elem.text:
            expression = text_elem.text.strip()
    
    return Expression(
        id=decision_id,
        name=decision_name,
        expression=expression,
    )


def _has_dependencies(root: ET.Element, ns: str) -> bool:
    """Check if the DMN has decision dependencies."""
    for decision in root.findall(f'.//{ns}decision', DMN_NAMESPACES) + root.findall('.//decision'):
        req_elems = decision.findall(f'{ns}informationRequirement', DMN_NAMESPACES) + \
                    decision.findall('informationRequirement')
        if req_elems:
            return True
    return False


def _build_decision_graph(
    root: ET.Element,
    ns: str,
    decisions: List[Union[DecisionTable, Expression]],
) -> Optional[DecisionGraph]:
    """Build a decision graph from DMN with dependencies."""
    # Map decision IDs to definitions
    decision_map = {d.id: d for d in decisions}
    
    # Parse decision requirements
    nodes = {}
    
    for decision_elem in root.findall(f'.//{ns}decision', DMN_NAMESPACES) + root.findall('.//decision'):
        decision_id = decision_elem.get('id', '')
        
        if decision_id not in decision_map:
            continue
        
        # Get dependencies
        dependencies = []
        req_elems = decision_elem.findall(f'{ns}informationRequirement', DMN_NAMESPACES) + \
                    decision_elem.findall('informationRequirement')
        
        for req_elem in req_elems:
            # Required decision
            req_decision = req_elem.find(f'{ns}requiredDecision', DMN_NAMESPACES) or \
                          req_elem.find('requiredDecision')
            if req_decision is not None:
                href = req_decision.get('href', '')
                dep_id = href.lstrip('#')
                if dep_id:
                    dependencies.append(dep_id)
            
            # Required input
            req_input = req_elem.find(f'{ns}requiredInput', DMN_NAMESPACES) or \
                       req_elem.find('requiredInput')
            if req_input is not None:
                href = req_input.get('href', '')
                dep_id = href.lstrip('#')
                if dep_id:
                    dependencies.append(dep_id)
        
        # Create node
        definition = decision_map[decision_id]
        decision_type = DecisionType.DECISION_TABLE if isinstance(definition, DecisionTable) else DecisionType.EXPRESSION
        
        nodes[decision_id] = DecisionNode(
            id=decision_id,
            name=definition.name,
            decision_type=decision_type,
            definition=definition,
            dependencies=dependencies,
        )
    
    if not nodes:
        return None
    
    # Get graph ID from definitions
    graph_id = root.get('id', 'decision_graph')
    graph_name = root.get('name', graph_id)
    
    return DecisionGraph(
        id=graph_id,
        name=graph_name,
        decisions=nodes,
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _map_hit_policy(policy: str, aggregation: str = '') -> HitPolicy:
    """Map DMN hit policy string to HitPolicy enum."""
    policy = policy.upper()
    
    if policy == 'COLLECT' and aggregation:
        agg_map = {
            'SUM': HitPolicy.COLLECT_SUM,
            'MIN': HitPolicy.COLLECT_MIN,
            'MAX': HitPolicy.COLLECT_MAX,
            'COUNT': HitPolicy.COLLECT_COUNT,
        }
        return agg_map.get(aggregation.upper(), HitPolicy.COLLECT)
    
    mapping = {
        'UNIQUE': HitPolicy.UNIQUE,
        'FIRST': HitPolicy.FIRST,
        'PRIORITY': HitPolicy.PRIORITY,
        'ANY': HitPolicy.ANY,
        'COLLECT': HitPolicy.COLLECT,
        'RULE ORDER': HitPolicy.RULE_ORDER,
        'OUTPUT ORDER': HitPolicy.OUTPUT_ORDER,
    }
    return mapping.get(policy, HitPolicy.UNIQUE)


def _map_dmn_type(type_ref: str) -> str:
    """Map DMN type reference to internal type."""
    type_map = {
        'string': 'string',
        'number': 'number',
        'boolean': 'boolean',
        'date': 'date',
        'time': 'time',
        'dateTime': 'datetime',
        'dayTimeDuration': 'duration',
        'yearMonthDuration': 'duration',
        'Any': 'any',
    }
    return type_map.get(type_ref, 'any')


def _parse_feel_condition(input_name: str, feel_expr: str) -> RuleCondition:
    """Parse a FEEL expression into a condition."""
    feel_expr = feel_expr.strip()
    
    # Empty or dash means ANY
    if not feel_expr or feel_expr == '-':
        return RuleCondition(
            input_name=input_name,
            operator=ComparisonOperator.ANY,
            value=None,
        )
    
    # Check for comparison operators
    patterns = [
        (r'^>=\s*(.+)$', ComparisonOperator.GREATER_THAN_OR_EQUAL),
        (r'^<=\s*(.+)$', ComparisonOperator.LESS_THAN_OR_EQUAL),
        (r'^>\s*(.+)$', ComparisonOperator.GREATER_THAN),
        (r'^<\s*(.+)$', ComparisonOperator.LESS_THAN),
        (r'^!=\s*(.+)$', ComparisonOperator.NOT_EQUAL),
        (r'^=\s*(.+)$', ComparisonOperator.EQUAL),
        (r'^not\s*\((.+)\)$', ComparisonOperator.NOT_IN),
    ]
    
    for pattern, operator in patterns:
        match = re.match(pattern, feel_expr, re.IGNORECASE)
        if match:
            value = _parse_feel_value(match.group(1).strip())
            return RuleCondition(
                input_name=input_name,
                operator=operator,
                value=value,
            )
    
    # Check for range (between)
    range_match = re.match(r'^\[(\d+)\.\.(\d+)\]$', feel_expr)
    if range_match:
        return RuleCondition(
            input_name=input_name,
            operator=ComparisonOperator.BETWEEN,
            value=_parse_feel_value(range_match.group(1)),
            value_end=_parse_feel_value(range_match.group(2)),
        )
    
    # Check for list (in)
    if feel_expr.startswith('"') or feel_expr.startswith("'") or \
       feel_expr[0].isdigit() or feel_expr.lower() in ('true', 'false'):
        # Simple value - equality
        return RuleCondition(
            input_name=input_name,
            operator=ComparisonOperator.EQUAL,
            value=_parse_feel_value(feel_expr),
        )
    
    # Expression - store as-is for expression evaluation
    return RuleCondition(
        input_name=input_name,
        operator=ComparisonOperator.EQUAL,
        value=f'${feel_expr}',  # Mark as expression
    )


def _parse_feel_value(value_str: str) -> Any:
    """Parse a FEEL value string into Python value."""
    value_str = value_str.strip()
    
    # Null
    if value_str.lower() == 'null':
        return None
    
    # Boolean
    if value_str.lower() == 'true':
        return True
    if value_str.lower() == 'false':
        return False
    
    # String (quoted)
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # Number
    try:
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass
    
    # Return as-is (could be expression reference)
    return value_str


def _parse_feel_list(feel_expr: str) -> List[Any]:
    """Parse a FEEL list expression."""
    # Handle comma-separated values
    values = []
    
    # Simple split on comma (doesn't handle nested structures)
    for item in feel_expr.split(','):
        item = item.strip()
        if item:
            values.append(_parse_feel_value(item))
    
    return values if values else None
