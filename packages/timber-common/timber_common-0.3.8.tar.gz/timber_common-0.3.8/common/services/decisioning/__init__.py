# common/services/decisioning/__init__.py
"""
DMN-Inspired Decision Engine

A comprehensive decisioning service supporting:
- Decision Tables with 11 hit policies
- FEEL-like expression evaluation with 80+ functions
- Decision Requirement Graphs (DRG)
- Multiple input formats (YAML, DMN XML, CSV)

Configuration (via environment or Timber config):
    DECISION_CONFIG_DIRS: Comma-separated directories for decision files
                          Default: config/decisioning,data/decisions
    DECISION_AUTO_LOAD: Auto-load on initialization (default: True)
    DECISION_CACHE_ENABLED: Enable evaluation caching (default: True)
    DECISION_CACHE_TTL_SECONDS: Cache TTL (default: 300)
    DECISION_TRACE_ENABLED: Enable execution tracing (default: False)
    DECISION_LOG_EVALUATIONS: Log evaluations to database (default: False)

Usage:
    from common.services.decisioning import decision_engine, initialize_decision_engine
    
    # Option 1: Initialize with auto-loading from configured directories
    await initialize_decision_engine()
    
    # Option 2: Manual loading
    await decision_engine.load_from_file("config/decisioning/loan_approval.yaml")
    
    # Evaluate
    result = await decision_engine.evaluate(
        decision_id="loan_approval",
        inputs={
            'credit_score': 720,
            'annual_income': 85000,
            'loan_amount': 250000,
        }
    )
    
    if result.success:
        print(f"Decision: {result.outputs}")
    else:
        print(f"Errors: {result.errors}")
"""

from .models import (
    # Enums
    HitPolicy,
    DecisionType,
    ComparisonOperator,
    DataType,
    
    # Data classes
    InputDefinition,
    OutputDefinition,
    RuleCondition,
    Rule,
    DecisionTable,
    Expression,
    DecisionNode,
    DecisionGraph,
    EvaluationResult,
)

from .expression_engine import ExpressionEngine
from .table_evaluator import DecisionTableEvaluator
from .graph_evaluator import DecisionGraphEvaluator

from .decision_engine import (
    DecisionEngine,
    get_decision_engine,
    initialize_decision_engine,
    decision_engine,
)

__all__ = [
    # Main service
    'DecisionEngine',
    'get_decision_engine',
    'initialize_decision_engine',
    'decision_engine',
    
    # Component engines
    'ExpressionEngine',
    'DecisionTableEvaluator',
    'DecisionGraphEvaluator',
    
    # Enums
    'HitPolicy',
    'DecisionType',
    'ComparisonOperator',
    'DataType',
    
    # Data classes
    'InputDefinition',
    'OutputDefinition',
    'RuleCondition',
    'Rule',
    'DecisionTable',
    'Expression',
    'DecisionNode',
    'DecisionGraph',
    'EvaluationResult',
]
