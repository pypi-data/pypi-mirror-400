# common/services/decisioning/graph_evaluator.py
"""
Decision Graph Evaluator

Evaluates Decision Requirement Graphs (DRG) from DMN.
Handles decision dependencies and execution ordering.
"""

import logging
import time
from typing import Dict, Any, List, Set

from .models import (
    DecisionType,
    DecisionTable, Expression, DecisionNode, DecisionGraph,
    EvaluationResult,
)
from .expression_engine import ExpressionEngine
from .table_evaluator import DecisionTableEvaluator

logger = logging.getLogger(__name__)


class DecisionGraphEvaluator:
    """Evaluates Decision Requirement Graphs (DRG)."""
    
    def __init__(
        self,
        table_evaluator: DecisionTableEvaluator,
        expression_engine: ExpressionEngine,
    ):
        self.table_evaluator = table_evaluator
        self.expression_engine = expression_engine
    
    def evaluate(
        self,
        graph: DecisionGraph,
        target_decision: str,
        inputs: Dict[str, Any],
        trace: bool = False,
    ) -> EvaluationResult:
        """
        Evaluate a decision graph to compute target decision.
        
        Args:
            graph: Decision graph definition
            target_decision: ID of the decision to evaluate
            inputs: Input values
            trace: Whether to include execution trace
            
        Returns:
            EvaluationResult
        """
        start_time = time.time()
        
        result = EvaluationResult(
            decision_id=target_decision,
            success=True,
        )
        
        if target_decision not in graph.decisions:
            result.success = False
            result.errors.append(f"Unknown decision: {target_decision}")
            return result
        
        # Build execution order (topological sort)
        try:
            execution_order = self._topological_sort(graph, target_decision)
        except ValueError as e:
            result.success = False
            result.errors.append(str(e))
            return result
        
        if trace:
            result.trace.append({
                'phase': 'planning',
                'execution_order': execution_order,
                'target': target_decision,
            })
        
        # Execute decisions in order
        context = dict(inputs)
        decision_results: Dict[str, EvaluationResult] = {}
        
        for decision_id in execution_order:
            node = graph.decisions[decision_id]
            
            if trace:
                result.trace.append({
                    'phase': 'executing',
                    'decision': decision_id,
                    'context_keys': list(context.keys()),
                })
            
            try:
                node_result = self._evaluate_node(node, context, trace)
                decision_results[decision_id] = node_result
                
                # Add outputs to context for downstream decisions
                for output_name, output_value in node_result.outputs.items():
                    # Store with both the output name and the decision_id.output_name
                    context[output_name] = output_value
                    context[f"{decision_id}.{output_name}"] = output_value
                
                # Also store the whole result under the decision ID
                if len(node_result.outputs) == 1:
                    # Single output - store directly
                    context[decision_id] = next(iter(node_result.outputs.values()))
                else:
                    # Multiple outputs - store as dict
                    context[decision_id] = node_result.outputs
                
                if not node_result.success:
                    result.errors.extend(node_result.errors)
                    if decision_id == target_decision:
                        result.success = False
                
                result.warnings.extend(node_result.warnings)
                
                if trace:
                    result.trace.append({
                        'phase': 'completed',
                        'decision': decision_id,
                        'success': node_result.success,
                        'outputs': node_result.outputs,
                        'matched_rules': node_result.matched_rules,
                    })
                
            except Exception as e:
                logger.error(f"Error evaluating {decision_id}: {e}", exc_info=True)
                result.errors.append(f"Error evaluating {decision_id}: {e}")
                if decision_id == target_decision:
                    result.success = False
                    break
        
        # Get final outputs from target decision
        if target_decision in decision_results:
            target_result = decision_results[target_decision]
            result.outputs = target_result.outputs
            result.matched_rules = target_result.matched_rules
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    def evaluate_all(
        self,
        graph: DecisionGraph,
        inputs: Dict[str, Any],
        trace: bool = False,
    ) -> Dict[str, EvaluationResult]:
        """
        Evaluate all decisions in a graph.
        
        Args:
            graph: Decision graph definition
            inputs: Input values
            trace: Whether to include execution trace
            
        Returns:
            Dict mapping decision ID to EvaluationResult
        """
        results = {}
        
        # Find all root decisions (not dependencies of any other)
        roots = self._find_roots(graph)
        
        for root_id in roots:
            result = self.evaluate(graph, root_id, inputs, trace)
            results[root_id] = result
        
        return results
    
    def _find_roots(self, graph: DecisionGraph) -> List[str]:
        """Find root decisions (not depended on by others)."""
        all_deps: Set[str] = set()
        for node in graph.decisions.values():
            all_deps.update(node.dependencies)
        
        roots = [
            node_id for node_id in graph.decisions
            if node_id not in all_deps
        ]
        
        return roots
    
    def _topological_sort(
        self,
        graph: DecisionGraph,
        target: str,
    ) -> List[str]:
        """
        Get execution order via topological sort.
        
        Only includes decisions required for the target.
        """
        visited: Set[str] = set()
        order: List[str] = []
        temp_visited: Set[str] = set()
        
        def visit(node_id: str):
            if node_id in temp_visited:
                raise ValueError(f"Circular dependency detected at: {node_id}")
            if node_id in visited:
                return
            
            temp_visited.add(node_id)
            
            node = graph.decisions.get(node_id)
            if node:
                for dep in node.dependencies:
                    if dep in graph.decisions:
                        visit(dep)
                    # else: it's an input, not a decision
            
            temp_visited.remove(node_id)
            visited.add(node_id)
            order.append(node_id)
        
        visit(target)
        return order
    
    def _evaluate_node(
        self,
        node: DecisionNode,
        context: Dict[str, Any],
        trace: bool,
    ) -> EvaluationResult:
        """Evaluate a single decision node."""
        
        # Decision Table
        if node.decision_type == DecisionType.DECISION_TABLE:
            if isinstance(node.definition, DecisionTable):
                return self.table_evaluator.evaluate(node.definition, context, trace)
            else:
                return EvaluationResult(
                    decision_id=node.id,
                    success=False,
                    errors=[f"Invalid decision table definition for {node.id}"],
                )
        
        # Expression
        elif node.decision_type == DecisionType.EXPRESSION:
            if isinstance(node.definition, Expression):
                try:
                    value = self.expression_engine.evaluate(
                        node.definition.expression, context
                    )
                    output_name = node.definition.output.name if node.definition.output else 'result'
                    return EvaluationResult(
                        decision_id=node.id,
                        success=True,
                        outputs={output_name: value},
                    )
                except Exception as e:
                    return EvaluationResult(
                        decision_id=node.id,
                        success=False,
                        errors=[str(e)],
                    )
            elif isinstance(node.definition, str):
                # Direct expression string
                try:
                    value = self.expression_engine.evaluate(node.definition, context)
                    return EvaluationResult(
                        decision_id=node.id,
                        success=True,
                        outputs={'result': value},
                    )
                except Exception as e:
                    return EvaluationResult(
                        decision_id=node.id,
                        success=False,
                        errors=[str(e)],
                    )
        
        # Literal value
        elif node.decision_type == DecisionType.LITERAL:
            return EvaluationResult(
                decision_id=node.id,
                success=True,
                outputs={node.id: node.definition},
            )
        
        # Context (multiple name-value pairs)
        elif node.decision_type == DecisionType.CONTEXT:
            if isinstance(node.definition, dict):
                outputs = {}
                for name, expr in node.definition.items():
                    if isinstance(expr, str):
                        outputs[name] = self.expression_engine.evaluate(expr, context)
                    else:
                        outputs[name] = expr
                return EvaluationResult(
                    decision_id=node.id,
                    success=True,
                    outputs=outputs,
                )
        
        # Function definition (store for later invocation)
        elif node.decision_type == DecisionType.FUNCTION:
            return EvaluationResult(
                decision_id=node.id,
                success=True,
                outputs={node.id: node.definition},
            )
        
        # Invocation (call another decision with arguments)
        elif node.decision_type == DecisionType.INVOCATION:
            # node.definition should be {'decision': 'target_id', 'bindings': {...}}
            if isinstance(node.definition, dict):
                target_id = node.definition.get('decision')
                bindings = node.definition.get('bindings', {})
                
                # Resolve bindings
                resolved_bindings = {}
                for param, expr in bindings.items():
                    if isinstance(expr, str):
                        resolved_bindings[param] = self.expression_engine.evaluate(expr, context)
                    else:
                        resolved_bindings[param] = expr
                
                # Note: actual invocation would require access to the graph
                # This is a simplified version
                return EvaluationResult(
                    decision_id=node.id,
                    success=True,
                    outputs={'invocation': {'target': target_id, 'bindings': resolved_bindings}},
                )
        
        # Relation (table of values)
        elif node.decision_type == DecisionType.RELATION:
            if isinstance(node.definition, list):
                return EvaluationResult(
                    decision_id=node.id,
                    success=True,
                    outputs={node.id: node.definition},
                )
        
        return EvaluationResult(
            decision_id=node.id,
            success=False,
            errors=[f"Unsupported decision type: {node.decision_type}"],
        )
    
    def get_dependencies(self, graph: DecisionGraph, decision_id: str) -> List[str]:
        """Get all dependencies for a decision (transitive)."""
        deps: Set[str] = set()
        
        def collect_deps(node_id: str):
            node = graph.decisions.get(node_id)
            if node:
                for dep in node.dependencies:
                    if dep not in deps and dep in graph.decisions:
                        deps.add(dep)
                        collect_deps(dep)
        
        collect_deps(decision_id)
        return list(deps)
    
    def validate_graph(self, graph: DecisionGraph) -> Dict[str, Any]:
        """Validate a decision graph."""
        errors = []
        warnings = []
        
        # Check for missing dependencies
        for node_id, node in graph.decisions.items():
            for dep in node.dependencies:
                if dep not in graph.decisions and dep not in graph.input_data:
                    errors.append(
                        f"Decision '{node_id}' has unknown dependency: '{dep}'"
                    )
        
        # Check for circular dependencies
        for node_id in graph.decisions:
            try:
                self._topological_sort(graph, node_id)
            except ValueError as e:
                errors.append(str(e))
        
        # Check for orphan decisions
        roots = self._find_roots(graph)
        if not roots:
            warnings.append("No root decisions found - all decisions are dependencies")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'decision_count': len(graph.decisions),
            'root_decisions': roots,
        }
