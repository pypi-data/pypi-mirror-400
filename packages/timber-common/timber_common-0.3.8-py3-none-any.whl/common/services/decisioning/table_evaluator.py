# common/services/decisioning/table_evaluator.py
"""
Decision Table Evaluator

Evaluates DMN decision tables with support for all hit policies.
"""

import logging
import re
import time
from typing import Dict, Any, List, Optional

from .models import (
    HitPolicy, ComparisonOperator,
    DecisionTable, Rule, RuleCondition,
    EvaluationResult,
)
from .expression_engine import ExpressionEngine

logger = logging.getLogger(__name__)


class DecisionTableEvaluator:
    """Evaluates decision tables with various hit policies."""
    
    def __init__(self, expression_engine: ExpressionEngine):
        self.expression_engine = expression_engine
    
    def evaluate(
        self,
        table: DecisionTable,
        inputs: Dict[str, Any],
        trace: bool = False,
    ) -> EvaluationResult:
        """
        Evaluate a decision table.
        
        Args:
            table: Decision table definition
            inputs: Input values
            trace: Whether to include execution trace
            
        Returns:
            EvaluationResult with outputs and matched rules
        """
        start_time = time.time()
        
        result = EvaluationResult(
            decision_id=table.id,
            success=True,
        )
        
        # Validate inputs
        validation_errors = self._validate_inputs(table, inputs)
        if validation_errors:
            result.errors.extend(validation_errors)
            result.success = False
            return result
        
        # Apply defaults
        context = self._apply_defaults(table, inputs)
        
        # Find matching rules
        matching_rules: List[Rule] = []
        
        for rule in table.rules:
            if not rule.enabled:
                continue
            
            if trace:
                result.trace.append({
                    'rule_id': rule.id,
                    'evaluating': True,
                })
            
            match_result = self._rule_matches(rule, context)
            
            if match_result['matched']:
                matching_rules.append(rule)
                result.matched_rules.append(rule.id)
                
                if trace:
                    result.trace.append({
                        'rule_id': rule.id,
                        'matched': True,
                        'outputs': rule.outputs,
                    })
            elif trace:
                result.trace.append({
                    'rule_id': rule.id,
                    'matched': False,
                    'failed_condition': match_result.get('failed_condition'),
                })
        
        # Apply hit policy
        try:
            outputs = self._apply_hit_policy(table, matching_rules, context)
            result.outputs = outputs
        except Exception as e:
            result.errors.append(str(e))
            result.success = False
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    def _validate_inputs(
        self,
        table: DecisionTable,
        inputs: Dict[str, Any],
    ) -> List[str]:
        """Validate inputs against definitions."""
        errors = []
        
        for input_def in table.inputs:
            value = inputs.get(input_def.name)
            
            # Check required
            if input_def.required and value is None and input_def.default is None:
                errors.append(f"Missing required input: {input_def.name}")
                continue
            
            if value is None:
                continue
            
            # Check type
            if input_def.type != "any":
                type_valid = self._check_type(value, input_def.type)
                if not type_valid:
                    errors.append(
                        f"Input '{input_def.name}' has invalid type: "
                        f"expected {input_def.type}, got {type(value).__name__}"
                    )
            
            # Check allowed values
            if input_def.allowed_values and value not in input_def.allowed_values:
                errors.append(
                    f"Input '{input_def.name}' has invalid value: {value}. "
                    f"Allowed: {input_def.allowed_values}"
                )
        
        return errors
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_checks = {
            'string': lambda v: isinstance(v, str),
            'number': lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            'integer': lambda v: isinstance(v, int) and not isinstance(v, bool),
            'boolean': lambda v: isinstance(v, bool),
            'date': lambda v: hasattr(v, 'year') and hasattr(v, 'month') and hasattr(v, 'day'),
            'datetime': lambda v: hasattr(v, 'year') and hasattr(v, 'hour'),
            'list': lambda v: isinstance(v, (list, tuple)),
            'any': lambda v: True,
        }
        
        check = type_checks.get(expected_type, lambda v: True)
        return check(value)
    
    def _apply_defaults(
        self,
        table: DecisionTable,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply default values for missing inputs."""
        context = dict(inputs)
        
        for input_def in table.inputs:
            if input_def.name not in context or context[input_def.name] is None:
                if input_def.default is not None:
                    context[input_def.name] = input_def.default
        
        return context
    
    def _rule_matches(
        self,
        rule: Rule,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Check if a rule matches the given context."""
        for condition in rule.conditions:
            # ANY operator matches everything
            if condition.operator == ComparisonOperator.ANY:
                continue
            
            input_value = context.get(condition.input_name)
            
            # Evaluate condition value if it's an expression
            condition_value = condition.value
            if isinstance(condition_value, str) and condition_value.startswith('$'):
                condition_value = self.expression_engine.evaluate(
                    condition_value[1:], context
                )
            
            if not self._evaluate_condition(
                input_value, condition.operator, condition_value, condition.value_end
            ):
                return {
                    'matched': False,
                    'failed_condition': {
                        'input': condition.input_name,
                        'operator': condition.operator.value,
                        'expected': condition_value,
                        'actual': input_value,
                    },
                }
        
        return {'matched': True}
    
    def _evaluate_condition(
        self,
        input_value: Any,
        operator: ComparisonOperator,
        condition_value: Any,
        value_end: Optional[Any] = None,
    ) -> bool:
        """Evaluate a single condition."""
        
        if operator == ComparisonOperator.EQUAL:
            return input_value == condition_value
        
        elif operator == ComparisonOperator.NOT_EQUAL:
            return input_value != condition_value
        
        elif operator == ComparisonOperator.LESS_THAN:
            return input_value < condition_value
        
        elif operator == ComparisonOperator.LESS_THAN_OR_EQUAL:
            return input_value <= condition_value
        
        elif operator == ComparisonOperator.GREATER_THAN:
            return input_value > condition_value
        
        elif operator == ComparisonOperator.GREATER_THAN_OR_EQUAL:
            return input_value >= condition_value
        
        elif operator == ComparisonOperator.IN:
            if isinstance(condition_value, (list, tuple, set)):
                return input_value in condition_value
            return input_value == condition_value
        
        elif operator == ComparisonOperator.NOT_IN:
            if isinstance(condition_value, (list, tuple, set)):
                return input_value not in condition_value
            return input_value != condition_value
        
        elif operator == ComparisonOperator.BETWEEN:
            if input_value is None:
                return False
            return condition_value <= input_value <= value_end
        
        elif operator == ComparisonOperator.MATCHES:
            if input_value is None:
                return False
            return bool(re.match(str(condition_value), str(input_value)))
        
        elif operator == ComparisonOperator.STARTS_WITH:
            if input_value is None:
                return False
            return str(input_value).startswith(str(condition_value))
        
        elif operator == ComparisonOperator.ENDS_WITH:
            if input_value is None:
                return False
            return str(input_value).endswith(str(condition_value))
        
        elif operator == ComparisonOperator.CONTAINS:
            if input_value is None:
                return False
            return str(condition_value) in str(input_value)
        
        elif operator == ComparisonOperator.IS_NULL:
            return input_value is None
        
        elif operator == ComparisonOperator.IS_NOT_NULL:
            return input_value is not None
        
        elif operator == ComparisonOperator.ANY:
            return True
        
        return False
    
    def _apply_hit_policy(
        self,
        table: DecisionTable,
        matching_rules: List[Rule],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply hit policy to matching rules."""
        if not matching_rules:
            # Return default outputs if no rules match
            return {out.name: out.default for out in table.outputs}
        
        policy = table.hit_policy
        
        # =====================================================================
        # SINGLE-HIT POLICIES
        # =====================================================================
        
        if policy == HitPolicy.UNIQUE:
            if len(matching_rules) > 1:
                raise ValueError(
                    f"UNIQUE hit policy violated: {len(matching_rules)} rules matched "
                    f"({', '.join(r.id for r in matching_rules)})"
                )
            return self._evaluate_outputs(matching_rules[0], context)
        
        elif policy == HitPolicy.FIRST:
            return self._evaluate_outputs(matching_rules[0], context)
        
        elif policy == HitPolicy.PRIORITY:
            # Get priority order from first output definition
            priority_order = None
            if table.outputs and table.outputs[0].priority_order:
                priority_order = table.outputs[0].priority_order
            
            if priority_order:
                # Sort by priority of output value
                def get_priority(rule):
                    outputs = self._evaluate_outputs(rule, context)
                    first_output = next(iter(outputs.values()), None)
                    if first_output in priority_order:
                        return priority_order.index(first_output)
                    return len(priority_order)
                
                matching_rules.sort(key=get_priority)
            else:
                # Sort by rule priority
                matching_rules.sort(key=lambda r: r.priority, reverse=True)
            
            return self._evaluate_outputs(matching_rules[0], context)
        
        elif policy == HitPolicy.ANY:
            # All matching rules must have same output
            first_outputs = self._evaluate_outputs(matching_rules[0], context)
            for rule in matching_rules[1:]:
                outputs = self._evaluate_outputs(rule, context)
                if outputs != first_outputs:
                    raise ValueError(
                        f"ANY hit policy violated: conflicting outputs from rules "
                        f"{matching_rules[0].id} and {rule.id}"
                    )
            return first_outputs
        
        # =====================================================================
        # MULTI-HIT POLICIES
        # =====================================================================
        
        elif policy == HitPolicy.COLLECT:
            return {
                out.name: [
                    self._evaluate_outputs(rule, context).get(out.name)
                    for rule in matching_rules
                ]
                for out in table.outputs
            }
        
        elif policy == HitPolicy.COLLECT_SUM:
            return {
                out.name: sum(
                    self._evaluate_outputs(rule, context).get(out.name, 0) or 0
                    for rule in matching_rules
                )
                for out in table.outputs
            }
        
        elif policy == HitPolicy.COLLECT_MIN:
            return {
                out.name: min(
                    self._evaluate_outputs(rule, context).get(out.name)
                    for rule in matching_rules
                )
                for out in table.outputs
            }
        
        elif policy == HitPolicy.COLLECT_MAX:
            return {
                out.name: max(
                    self._evaluate_outputs(rule, context).get(out.name)
                    for rule in matching_rules
                )
                for out in table.outputs
            }
        
        elif policy == HitPolicy.COLLECT_COUNT:
            return {'count': len(matching_rules)}
        
        elif policy == HitPolicy.RULE_ORDER:
            return {
                out.name: [
                    self._evaluate_outputs(rule, context).get(out.name)
                    for rule in matching_rules
                ]
                for out in table.outputs
            }
        
        elif policy == HitPolicy.OUTPUT_ORDER:
            # Sort by output priority, then collect
            if table.outputs and table.outputs[0].priority_order:
                priority_order = table.outputs[0].priority_order
                
                def get_priority(rule):
                    outputs = self._evaluate_outputs(rule, context)
                    first_output = next(iter(outputs.values()), None)
                    if first_output in priority_order:
                        return priority_order.index(first_output)
                    return len(priority_order)
                
                matching_rules.sort(key=get_priority)
            
            return {
                out.name: [
                    self._evaluate_outputs(rule, context).get(out.name)
                    for rule in matching_rules
                ]
                for out in table.outputs
            }
        
        return {}
    
    def _evaluate_outputs(
        self,
        rule: Rule,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Evaluate rule outputs, handling expressions."""
        outputs = {}
        
        for name, value in rule.outputs.items():
            if isinstance(value, str) and value.startswith('$'):
                # Evaluate expression
                outputs[name] = self.expression_engine.evaluate(value[1:], context)
            else:
                outputs[name] = value
        
        return outputs
