# common/services/decisioning/models.py
"""
Decision Engine Data Models

Core data structures for DMN-inspired decisioning:
- Enums for hit policies, operators, decision types
- Dataclasses for inputs, outputs, rules, conditions
- Decision structures: tables, expressions, graphs
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Union


# =============================================================================
# ENUMS
# =============================================================================

class HitPolicy(Enum):
    """
    Decision table hit policies (DMN standard).
    
    Single-hit policies (return single result):
    - UNIQUE (U): Only one rule can match
    - FIRST (F): First matching rule wins
    - PRIORITY (P): Rule with highest priority output wins
    - ANY (A): Any matching rule (all must have same output)
    
    Multi-hit policies (return collection):
    - COLLECT (C): Collect all matching outputs
    - COLLECT_SUM (C+): Sum numeric outputs
    - COLLECT_MIN (C<): Minimum of outputs
    - COLLECT_MAX (C>): Maximum of outputs
    - COLLECT_COUNT (C#): Count of matches
    - RULE_ORDER (R): All matches in rule order
    - OUTPUT_ORDER (O): All matches in output priority order
    """
    UNIQUE = "U"
    FIRST = "F"
    PRIORITY = "P"
    ANY = "A"
    COLLECT = "C"
    COLLECT_SUM = "C+"
    COLLECT_MIN = "C<"
    COLLECT_MAX = "C>"
    COLLECT_COUNT = "C#"
    RULE_ORDER = "R"
    OUTPUT_ORDER = "O"
    
    @classmethod
    def from_string(cls, value: str) -> 'HitPolicy':
        """Parse hit policy from string."""
        # Direct match
        for policy in cls:
            if policy.value == value or policy.name == value.upper():
                return policy
        
        # Common aliases
        aliases = {
            'unique': cls.UNIQUE,
            'first': cls.FIRST,
            'priority': cls.PRIORITY,
            'any': cls.ANY,
            'collect': cls.COLLECT,
            'sum': cls.COLLECT_SUM,
            'min': cls.COLLECT_MIN,
            'max': cls.COLLECT_MAX,
            'count': cls.COLLECT_COUNT,
            'rule_order': cls.RULE_ORDER,
            'output_order': cls.OUTPUT_ORDER,
        }
        
        return aliases.get(value.lower(), cls.FIRST)


class DecisionType(Enum):
    """Types of decisions."""
    DECISION_TABLE = "decision_table"
    EXPRESSION = "expression"
    INVOCATION = "invocation"
    CONTEXT = "context"
    RELATION = "relation"
    FUNCTION = "function"
    LITERAL = "literal"


class ComparisonOperator(Enum):
    """Comparison operators for rule conditions."""
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    IN = "in"
    NOT_IN = "not in"
    BETWEEN = "between"
    MATCHES = "matches"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    CONTAINS = "contains"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    ANY = "-"  # Matches anything (wildcard)
    
    @classmethod
    def from_string(cls, value: str) -> 'ComparisonOperator':
        """Parse operator from string."""
        # Direct match
        for op in cls:
            if op.value == value or op.name == value.upper():
                return op
        
        # Common aliases
        aliases = {
            '=': cls.EQUAL,
            'eq': cls.EQUAL,
            'equals': cls.EQUAL,
            'ne': cls.NOT_EQUAL,
            'neq': cls.NOT_EQUAL,
            'lt': cls.LESS_THAN,
            'lte': cls.LESS_THAN_OR_EQUAL,
            'le': cls.LESS_THAN_OR_EQUAL,
            'gt': cls.GREATER_THAN,
            'gte': cls.GREATER_THAN_OR_EQUAL,
            'ge': cls.GREATER_THAN_OR_EQUAL,
            'regex': cls.MATCHES,
            'like': cls.CONTAINS,
            '*': cls.ANY,
            '-': cls.ANY,
            'any': cls.ANY,
            'null': cls.IS_NULL,
            'not_null': cls.IS_NOT_NULL,
        }
        
        return aliases.get(value.lower(), cls.EQUAL)


class DataType(Enum):
    """Data types for inputs/outputs."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    DURATION = "duration"
    LIST = "list"
    ANY = "any"


# =============================================================================
# INPUT/OUTPUT DEFINITIONS
# =============================================================================

@dataclass
class InputDefinition:
    """Definition of a decision input."""
    name: str
    type: str = "any"  # string, number, boolean, date, any
    label: Optional[str] = None
    description: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    default: Optional[Any] = None
    required: bool = True
    
    def __post_init__(self):
        if self.label is None:
            self.label = self.name


@dataclass
class OutputDefinition:
    """Definition of a decision output."""
    name: str
    type: str = "any"
    label: Optional[str] = None
    description: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    default: Optional[Any] = None
    priority_order: Optional[List[Any]] = None  # For PRIORITY hit policy
    
    def __post_init__(self):
        if self.label is None:
            self.label = self.name


# =============================================================================
# RULES AND CONDITIONS
# =============================================================================

@dataclass
class RuleCondition:
    """A single condition in a rule."""
    input_name: str
    operator: ComparisonOperator
    value: Any
    value_end: Optional[Any] = None  # For BETWEEN operator
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], input_name: str) -> 'RuleCondition':
        """Create condition from dictionary."""
        if isinstance(data, dict):
            operator = ComparisonOperator.from_string(data.get('operator', '=='))
            value = data.get('value')
            value_end = data.get('value_end')
        else:
            # Simple value - assume equality
            operator = ComparisonOperator.EQUAL
            value = data
            value_end = None
        
        return cls(
            input_name=input_name,
            operator=operator,
            value=value,
            value_end=value_end,
        )


@dataclass
class Rule:
    """A decision table rule."""
    id: str
    conditions: List[RuleCondition]
    outputs: Dict[str, Any]
    annotation: Optional[str] = None
    description: Optional[str] = None
    priority: int = 0
    enabled: bool = True


# =============================================================================
# DECISION STRUCTURES
# =============================================================================

@dataclass
class DecisionTable:
    """A complete decision table."""
    id: str
    name: str
    hit_policy: HitPolicy = HitPolicy.UNIQUE
    inputs: List[InputDefinition] = field(default_factory=list)
    outputs: List[OutputDefinition] = field(default_factory=list)
    rules: List[Rule] = field(default_factory=list)
    description: Optional[str] = None
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)


@dataclass
class Expression:
    """An expression-based decision."""
    id: str
    name: str
    expression: str
    inputs: List[InputDefinition] = field(default_factory=list)
    output: Optional[OutputDefinition] = None
    description: Optional[str] = None
    version: str = "1.0.0"


@dataclass
class DecisionNode:
    """A node in a Decision Requirement Graph."""
    id: str
    name: str
    decision_type: DecisionType
    definition: Union['DecisionTable', 'Expression', str, Any]  # str for references
    dependencies: List[str] = field(default_factory=list)  # IDs of required decisions
    description: Optional[str] = None


@dataclass
class DecisionGraph:
    """A Decision Requirement Graph (DRG)."""
    id: str
    name: str
    decisions: Dict[str, DecisionNode] = field(default_factory=dict)
    input_data: Dict[str, InputDefinition] = field(default_factory=dict)
    description: Optional[str] = None
    version: str = "1.0.0"


# =============================================================================
# EVALUATION RESULT
# =============================================================================

@dataclass
class EvaluationResult:
    """Result of evaluating a decision."""
    decision_id: str
    success: bool
    outputs: Dict[str, Any] = field(default_factory=dict)
    matched_rules: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    trace: List[Dict[str, Any]] = field(default_factory=list)
    
    def get(self, output_name: str, default: Any = None) -> Any:
        """Get an output value."""
        return self.outputs.get(output_name, default)
    
    def __bool__(self) -> bool:
        """Returns True if evaluation succeeded."""
        return self.success
