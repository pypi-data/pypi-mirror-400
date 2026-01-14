# common/utils/decisioning/csv_parser.py
"""
CSV Parser for Decision Tables

Parses CSV files into decision table structures.
CSV format is simpler than YAML/DMN but useful for spreadsheet-based rules.

CSV Format:
- First row: Headers with input/output markers
- Subsequent rows: Rules

Header Format:
- Input columns: Start with "input:" or end with "(input)"
- Output columns: Start with "output:" or end with "(output)"
- Without markers: First columns assumed inputs, last columns assumed outputs

Example CSV:
```csv
input:credit_score,input:income,output:approved,output:rate
>=700,>=50000,true,5.5
>=650,>=75000,true,6.5
<650,-,false,0
```

Condition Syntax in Cells:
- Simple value: exact match (e.g., "approved", 100)
- Comparison: >=700, <50, !=0
- Range: 100..200 (between)
- List: [a,b,c] (in)
- Wildcard: - or * (any)
"""

import csv
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from common.services.decisioning.models import (
    HitPolicy, ComparisonOperator,
    InputDefinition, OutputDefinition, RuleCondition, Rule,
    DecisionTable,
)

logger = logging.getLogger(__name__)


def parse_file(
    path: str,
    decision_id: str,
    decision_name: Optional[str] = None,
    hit_policy: HitPolicy = HitPolicy.FIRST,
) -> DecisionTable:
    """
    Parse a CSV file into a decision table.
    
    Args:
        path: Path to CSV file
        decision_id: ID to assign to the decision
        decision_name: Name for the decision (defaults to ID)
        hit_policy: Hit policy to use (defaults to FIRST)
        
    Returns:
        Parsed DecisionTable
    """
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    return parse_rows(rows, decision_id, decision_name, hit_policy)


def parse_string(
    csv_string: str,
    decision_id: str,
    decision_name: Optional[str] = None,
    hit_policy: HitPolicy = HitPolicy.FIRST,
) -> DecisionTable:
    """
    Parse a CSV string into a decision table.
    
    Args:
        csv_string: CSV content
        decision_id: ID to assign to the decision
        decision_name: Name for the decision
        hit_policy: Hit policy to use
        
    Returns:
        Parsed DecisionTable
    """
    import io
    reader = csv.reader(io.StringIO(csv_string))
    rows = list(reader)
    
    return parse_rows(rows, decision_id, decision_name, hit_policy)


def parse_rows(
    rows: List[List[str]],
    decision_id: str,
    decision_name: Optional[str] = None,
    hit_policy: HitPolicy = HitPolicy.FIRST,
) -> DecisionTable:
    """
    Parse CSV rows into a decision table.
    
    Args:
        rows: List of CSV rows
        decision_id: ID to assign to the decision
        decision_name: Name for the decision
        hit_policy: Hit policy to use
        
    Returns:
        Parsed DecisionTable
    """
    if not rows:
        raise ValueError("CSV has no data")
    
    # Parse headers
    headers = rows[0]
    inputs, outputs, input_indices, output_indices = _parse_headers(headers)
    
    # Parse rules
    rules = []
    for i, row in enumerate(rows[1:]):
        if not any(cell.strip() for cell in row):
            continue  # Skip empty rows
        
        rule = _parse_rule_row(row, i, inputs, outputs, input_indices, output_indices)
        if rule:
            rules.append(rule)
    
    return DecisionTable(
        id=decision_id,
        name=decision_name or decision_id,
        hit_policy=hit_policy,
        inputs=inputs,
        outputs=outputs,
        rules=rules,
    )


def _parse_headers(headers: List[str]) -> Tuple[
    List[InputDefinition],
    List[OutputDefinition],
    List[int],
    List[int],
]:
    """
    Parse CSV headers to identify inputs and outputs.
    
    Returns:
        Tuple of (inputs, outputs, input_indices, output_indices)
    """
    inputs = []
    outputs = []
    input_indices = []
    output_indices = []
    
    # First pass: identify explicitly marked columns
    for i, header in enumerate(headers):
        header = header.strip()
        
        # Check for explicit markers
        if header.lower().startswith('input:'):
            name = header[6:].strip()
            inputs.append(_create_input_def(name, header))
            input_indices.append(i)
        elif header.lower().startswith('output:'):
            name = header[7:].strip()
            outputs.append(_create_output_def(name, header))
            output_indices.append(i)
        elif header.lower().endswith('(input)'):
            name = header[:-7].strip()
            inputs.append(_create_input_def(name, header))
            input_indices.append(i)
        elif header.lower().endswith('(output)'):
            name = header[:-8].strip()
            outputs.append(_create_output_def(name, header))
            output_indices.append(i)
    
    # If no explicit markers, infer from position
    if not inputs and not outputs:
        # Assume last column(s) are outputs
        # Use common output names to detect
        output_names = {'result', 'output', 'decision', 'approved', 'action', 'score', 'rate', 'risk'}
        
        for i, header in enumerate(headers):
            name = header.strip().lower()
            
            # Check if it looks like an output
            if name in output_names or any(name.endswith(f'_{on}') for on in output_names):
                outputs.append(_create_output_def(header.strip(), header))
                output_indices.append(i)
            else:
                inputs.append(_create_input_def(header.strip(), header))
                input_indices.append(i)
        
        # If still no outputs, assume last column is output
        if not outputs and inputs:
            last_input = inputs.pop()
            input_indices.pop()
            outputs.append(_create_output_def(last_input.name, last_input.name))
            output_indices.append(len(headers) - 1)
    
    return inputs, outputs, input_indices, output_indices


def _create_input_def(name: str, header: str) -> InputDefinition:
    """Create an input definition from header."""
    # Extract type hint if present: name:type
    if ':' in name and not name.startswith('input:'):
        parts = name.split(':')
        name = parts[0].strip()
        input_type = parts[1].strip() if len(parts) > 1 else 'any'
    else:
        input_type = 'any'
    
    return InputDefinition(
        name=name,
        type=input_type,
        label=name,
    )


def _create_output_def(name: str, header: str) -> OutputDefinition:
    """Create an output definition from header."""
    # Extract type hint if present
    if ':' in name and not name.startswith('output:'):
        parts = name.split(':')
        name = parts[0].strip()
        output_type = parts[1].strip() if len(parts) > 1 else 'any'
    else:
        output_type = 'any'
    
    return OutputDefinition(
        name=name,
        type=output_type,
        label=name,
    )


def _parse_rule_row(
    row: List[str],
    index: int,
    inputs: List[InputDefinition],
    outputs: List[OutputDefinition],
    input_indices: List[int],
    output_indices: List[int],
) -> Optional[Rule]:
    """Parse a single rule row."""
    # Parse conditions
    conditions = []
    for i, input_idx in enumerate(input_indices):
        if input_idx >= len(row):
            continue
        
        cell = row[input_idx].strip()
        input_name = inputs[i].name
        
        condition = _parse_cell_condition(input_name, cell)
        conditions.append(condition)
    
    # Parse outputs
    output_values = {}
    for i, output_idx in enumerate(output_indices):
        if output_idx >= len(row):
            continue
        
        cell = row[output_idx].strip()
        output_name = outputs[i].name
        
        output_values[output_name] = _parse_cell_value(cell)
    
    if not conditions and not output_values:
        return None
    
    return Rule(
        id=f'rule_{index + 1}',
        conditions=conditions,
        outputs=output_values,
    )


def _parse_cell_condition(input_name: str, cell: str) -> RuleCondition:
    """Parse a condition cell value."""
    cell = cell.strip()
    
    # Empty or wildcard
    if not cell or cell == '-' or cell == '*':
        return RuleCondition(
            input_name=input_name,
            operator=ComparisonOperator.ANY,
            value=None,
        )
    
    # Comparison operators
    patterns = [
        (r'^>=\s*(.+)$', ComparisonOperator.GREATER_THAN_OR_EQUAL),
        (r'^<=\s*(.+)$', ComparisonOperator.LESS_THAN_OR_EQUAL),
        (r'^>\s*(.+)$', ComparisonOperator.GREATER_THAN),
        (r'^<\s*(.+)$', ComparisonOperator.LESS_THAN),
        (r'^!=\s*(.+)$', ComparisonOperator.NOT_EQUAL),
        (r'^=\s*(.+)$', ComparisonOperator.EQUAL),
        (r'^not\s+in\s*\[(.+)\]$', ComparisonOperator.NOT_IN),
        (r'^in\s*\[(.+)\]$', ComparisonOperator.IN),
    ]
    
    for pattern, operator in patterns:
        match = re.match(pattern, cell, re.IGNORECASE)
        if match:
            value_str = match.group(1).strip()
            
            # Handle list for IN/NOT_IN
            if operator in (ComparisonOperator.IN, ComparisonOperator.NOT_IN):
                value = [_parse_cell_value(v.strip()) for v in value_str.split(',')]
            else:
                value = _parse_cell_value(value_str)
            
            return RuleCondition(
                input_name=input_name,
                operator=operator,
                value=value,
            )
    
    # Range: 100..200 or 100-200
    range_match = re.match(r'^(\d+(?:\.\d+)?)\s*(?:\.\.|-)\s*(\d+(?:\.\d+)?)$', cell)
    if range_match:
        return RuleCondition(
            input_name=input_name,
            operator=ComparisonOperator.BETWEEN,
            value=_parse_cell_value(range_match.group(1)),
            value_end=_parse_cell_value(range_match.group(2)),
        )
    
    # List: [a,b,c]
    list_match = re.match(r'^\[(.+)\]$', cell)
    if list_match:
        values = [_parse_cell_value(v.strip()) for v in list_match.group(1).split(',')]
        return RuleCondition(
            input_name=input_name,
            operator=ComparisonOperator.IN,
            value=values,
        )
    
    # Simple value - equality
    return RuleCondition(
        input_name=input_name,
        operator=ComparisonOperator.EQUAL,
        value=_parse_cell_value(cell),
    )


def _parse_cell_value(value_str: str) -> Any:
    """Parse a cell value into Python type."""
    value_str = value_str.strip()
    
    # Boolean
    if value_str.lower() == 'true':
        return True
    if value_str.lower() == 'false':
        return False
    
    # Null
    if value_str.lower() in ('null', 'none', ''):
        return None
    
    # Quoted string
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
    
    # Expression marker
    if value_str.startswith('$'):
        return value_str
    
    # Return as string
    return value_str


def to_csv_string(table: DecisionTable) -> str:
    """
    Convert a decision table to CSV string.
    
    Args:
        table: Decision table to convert
        
    Returns:
        CSV string representation
    """
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    headers = []
    for inp in table.inputs:
        headers.append(f'input:{inp.name}')
    for out in table.outputs:
        headers.append(f'output:{out.name}')
    
    writer.writerow(headers)
    
    # Rules
    for rule in table.rules:
        row = []
        
        # Input conditions
        for inp in table.inputs:
            condition = next(
                (c for c in rule.conditions if c.input_name == inp.name),
                None
            )
            if condition:
                row.append(_condition_to_csv(condition))
            else:
                row.append('-')
        
        # Output values
        for out in table.outputs:
            value = rule.outputs.get(out.name)
            row.append(_value_to_csv(value))
        
        writer.writerow(row)
    
    return output.getvalue()


def _condition_to_csv(condition: RuleCondition) -> str:
    """Convert a condition to CSV cell value."""
    if condition.operator == ComparisonOperator.ANY:
        return '-'
    
    if condition.operator == ComparisonOperator.EQUAL:
        return _value_to_csv(condition.value)
    
    if condition.operator == ComparisonOperator.BETWEEN:
        return f'{condition.value}..{condition.value_end}'
    
    if condition.operator == ComparisonOperator.IN:
        values = ','.join(_value_to_csv(v) for v in condition.value)
        return f'[{values}]'
    
    if condition.operator == ComparisonOperator.NOT_IN:
        values = ','.join(_value_to_csv(v) for v in condition.value)
        return f'not in [{values}]'
    
    # Comparison operator
    op_map = {
        ComparisonOperator.GREATER_THAN: '>',
        ComparisonOperator.GREATER_THAN_OR_EQUAL: '>=',
        ComparisonOperator.LESS_THAN: '<',
        ComparisonOperator.LESS_THAN_OR_EQUAL: '<=',
        ComparisonOperator.NOT_EQUAL: '!=',
    }
    
    op = op_map.get(condition.operator, '=')
    return f'{op}{_value_to_csv(condition.value)}'


def _value_to_csv(value: Any) -> str:
    """Convert a value to CSV cell string."""
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        # Quote if contains special characters
        if ',' in value or '"' in value:
            return f'"{value}"'
        return value
    return str(value)
