# common/services/decisioning/expression_engine.py
"""
FEEL-like Expression Evaluator

Supports:
- Arithmetic: +, -, *, /, %, **
- Comparison: ==, !=, <, <=, >, >=
- Logical: and, or, not
- String: contains(), starts_with(), ends_with(), upper(), lower()
- List: in, count(), sum(), min(), max(), avg()
- Date: today(), now(), date(), duration()
- Conditional: if-then-else
- Null handling: null, is_null()
"""

import logging
import math
import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, Any, Callable, Optional, List

logger = logging.getLogger(__name__)


class ExpressionEngine:
    """
    FEEL-like expression evaluator.
    
    Evaluates expressions with a context of variables, supporting
    a rich set of built-in functions and operators.
    """
    
    def __init__(self):
        self._functions: Dict[str, Callable] = {}
        self._register_builtin_functions()
    
    def _register_builtin_functions(self) -> None:
        """Register built-in functions."""
        
        # =====================================================================
        # MATH FUNCTIONS
        # =====================================================================
        self._functions['abs'] = abs
        self._functions['round'] = round
        self._functions['floor'] = math.floor
        self._functions['ceil'] = math.ceil
        self._functions['ceiling'] = math.ceil
        self._functions['sqrt'] = math.sqrt
        self._functions['pow'] = pow
        self._functions['log'] = math.log
        self._functions['log10'] = math.log10
        self._functions['exp'] = math.exp
        self._functions['sin'] = math.sin
        self._functions['cos'] = math.cos
        self._functions['tan'] = math.tan
        self._functions['modulo'] = lambda a, b: a % b
        
        # =====================================================================
        # AGGREGATION FUNCTIONS
        # =====================================================================
        self._functions['min'] = lambda *args: min(args[0] if len(args) == 1 and isinstance(args[0], (list, tuple)) else args)
        self._functions['max'] = lambda *args: max(args[0] if len(args) == 1 and isinstance(args[0], (list, tuple)) else args)
        self._functions['sum'] = lambda x: sum(x) if isinstance(x, (list, tuple)) else x
        self._functions['avg'] = lambda x: sum(x) / len(x) if x else 0
        self._functions['mean'] = lambda x: sum(x) / len(x) if x else 0
        self._functions['median'] = self._median
        self._functions['count'] = len
        self._functions['product'] = lambda x: math.prod(x) if x else 0
        
        # =====================================================================
        # STRING FUNCTIONS
        # =====================================================================
        self._functions['upper'] = lambda s: s.upper() if s else ''
        self._functions['lower'] = lambda s: s.lower() if s else ''
        self._functions['trim'] = lambda s: s.strip() if s else ''
        self._functions['ltrim'] = lambda s: s.lstrip() if s else ''
        self._functions['rtrim'] = lambda s: s.rstrip() if s else ''
        self._functions['length'] = lambda s: len(s) if s else 0
        self._functions['string_length'] = lambda s: len(s) if s else 0
        self._functions['substring'] = self._substring
        self._functions['contains'] = lambda s, sub: sub in s if s and sub else False
        self._functions['starts_with'] = lambda s, prefix: s.startswith(prefix) if s else False
        self._functions['ends_with'] = lambda s, suffix: s.endswith(suffix) if s else False
        self._functions['replace'] = lambda s, old, new: s.replace(old, new) if s else ''
        self._functions['split'] = lambda s, sep=' ': s.split(sep) if s else []
        self._functions['concat'] = lambda *args: ''.join(str(a) for a in args if a is not None)
        self._functions['string_join'] = lambda lst, sep='': sep.join(str(x) for x in lst)
        self._functions['matches'] = lambda s, pattern: bool(re.match(pattern, s)) if s else False
        self._functions['capitalize'] = lambda s: s.capitalize() if s else ''
        self._functions['title'] = lambda s: s.title() if s else ''
        
        # =====================================================================
        # DATE/TIME FUNCTIONS
        # =====================================================================
        self._functions['today'] = lambda: date.today()
        self._functions['now'] = lambda: datetime.now(timezone.utc)
        self._functions['date'] = self._make_date
        self._functions['time'] = self._make_time
        self._functions['date_time'] = self._make_datetime
        self._functions['year'] = lambda d: d.year if d else None
        self._functions['month'] = lambda d: d.month if d else None
        self._functions['day'] = lambda d: d.day if d else None
        self._functions['hour'] = lambda t: t.hour if hasattr(t, 'hour') else None
        self._functions['minute'] = lambda t: t.minute if hasattr(t, 'minute') else None
        self._functions['second'] = lambda t: t.second if hasattr(t, 'second') else None
        self._functions['weekday'] = lambda d: d.weekday() if d else None
        self._functions['day_of_week'] = lambda d: d.isoweekday() if d else None
        self._functions['day_of_year'] = lambda d: d.timetuple().tm_yday if d else None
        self._functions['week_of_year'] = lambda d: d.isocalendar()[1] if d else None
        self._functions['days_between'] = lambda d1, d2: (d2 - d1).days if d1 and d2 else 0
        self._functions['years_between'] = lambda d1, d2: (d2.year - d1.year) if d1 and d2 else 0
        self._functions['months_between'] = lambda d1, d2: (d2.year - d1.year) * 12 + (d2.month - d1.month) if d1 and d2 else 0
        self._functions['add_days'] = lambda d, n: d + timedelta(days=n) if d else None
        self._functions['add_months'] = self._add_months
        self._functions['add_years'] = self._add_years
        
        # =====================================================================
        # LIST FUNCTIONS
        # =====================================================================
        self._functions['append'] = lambda lst, item: list(lst) + [item] if lst else [item]
        self._functions['prepend'] = lambda lst, item: [item] + list(lst) if lst else [item]
        self._functions['flatten'] = self._flatten
        self._functions['distinct'] = lambda lst: list(dict.fromkeys(lst)) if lst else []
        self._functions['unique'] = lambda lst: list(dict.fromkeys(lst)) if lst else []
        self._functions['sort'] = lambda lst, reverse=False: sorted(lst, reverse=reverse) if lst else []
        self._functions['reverse'] = lambda lst: list(reversed(lst)) if lst else []
        self._functions['first'] = lambda lst: lst[0] if lst else None
        self._functions['last'] = lambda lst: lst[-1] if lst else None
        self._functions['index_of'] = lambda lst, item: lst.index(item) if item in lst else -1
        self._functions['list_contains'] = lambda lst, item: item in lst if lst else False
        self._functions['sublist'] = lambda lst, start, length=None: lst[start:start+length] if length else lst[start:]
        self._functions['remove'] = lambda lst, item: [x for x in lst if x != item]
        self._functions['insert_before'] = lambda lst, idx, item: lst[:idx] + [item] + lst[idx:]
        self._functions['union'] = lambda *lsts: list(set().union(*lsts))
        self._functions['intersection'] = lambda *lsts: list(set(lsts[0]).intersection(*lsts[1:])) if lsts else []
        self._functions['except'] = lambda lst1, lst2: [x for x in lst1 if x not in lst2]
        
        # =====================================================================
        # NULL HANDLING
        # =====================================================================
        self._functions['is_null'] = lambda x: x is None
        self._functions['is_not_null'] = lambda x: x is not None
        self._functions['is_defined'] = lambda x: x is not None
        self._functions['coalesce'] = lambda *args: next((a for a in args if a is not None), None)
        self._functions['default_if_null'] = lambda x, default: x if x is not None else default
        self._functions['get_or_else'] = lambda x, default: x if x is not None else default
        self._functions['nvl'] = lambda x, default: x if x is not None else default  # Oracle style
        self._functions['ifnull'] = lambda x, default: x if x is not None else default  # MySQL style
        
        # =====================================================================
        # TYPE CONVERSION
        # =====================================================================
        self._functions['number'] = self._to_number
        self._functions['string'] = lambda x: str(x) if x is not None else ''
        self._functions['boolean'] = self._to_boolean
        self._functions['int'] = lambda x: int(float(x)) if x is not None else 0
        self._functions['float'] = lambda x: float(x) if x is not None else 0.0
        
        # =====================================================================
        # BOOLEAN FUNCTIONS
        # =====================================================================
        self._functions['all'] = all
        self._functions['any'] = any
        self._functions['none'] = lambda lst: not any(lst)
        
        # =====================================================================
        # RANGE FUNCTIONS
        # =====================================================================
        self._functions['range'] = lambda start, end: list(range(start, end + 1))
        self._functions['between'] = lambda x, low, high: low <= x <= high if x is not None else False
        
        # =====================================================================
        # UTILITY FUNCTIONS
        # =====================================================================
        self._functions['format'] = lambda template, *args: template.format(*args)
        self._functions['printf'] = lambda template, *args: template % args
    
    # =========================================================================
    # HELPER FUNCTIONS
    # =========================================================================
    
    def _median(self, lst: List) -> Any:
        """Calculate median of a list."""
        if not lst:
            return 0
        sorted_lst = sorted(lst)
        n = len(sorted_lst)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_lst[mid - 1] + sorted_lst[mid]) / 2
        return sorted_lst[mid]
    
    def _substring(self, s: str, start: int, length: Optional[int] = None) -> str:
        """Extract substring (1-indexed like FEEL)."""
        if not s:
            return ''
        # FEEL uses 1-based indexing
        start_idx = max(0, start - 1)
        if length is None:
            return s[start_idx:]
        return s[start_idx:start_idx + length]
    
    def _make_date(self, *args) -> date:
        """Create a date from arguments."""
        if len(args) == 1:
            # Parse ISO string
            if isinstance(args[0], str):
                return date.fromisoformat(args[0])
            return args[0]
        elif len(args) == 3:
            return date(args[0], args[1], args[2])
        raise ValueError("date() requires ISO string or (year, month, day)")
    
    def _make_time(self, *args) -> time:
        """Create a time from arguments."""
        if len(args) == 1:
            if isinstance(args[0], str):
                return time.fromisoformat(args[0])
            return args[0]
        elif len(args) >= 2:
            return time(args[0], args[1], args[2] if len(args) > 2 else 0)
        raise ValueError("time() requires ISO string or (hour, minute[, second])")
    
    def _make_datetime(self, *args) -> datetime:
        """Create a datetime from arguments."""
        if len(args) == 1:
            if isinstance(args[0], str):
                return datetime.fromisoformat(args[0])
            return args[0]
        elif len(args) >= 3:
            return datetime(*args)
        raise ValueError("date_time() requires ISO string or datetime components")
    
    def _add_months(self, d: date, months: int) -> date:
        """Add months to a date."""
        if not d:
            return None
        month = d.month + months
        year = d.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(d.day, [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return d.replace(year=year, month=month, day=day)
    
    def _add_years(self, d: date, years: int) -> date:
        """Add years to a date."""
        if not d:
            return None
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            # Handle Feb 29 on non-leap year
            return d.replace(year=d.year + years, day=28)
    
    def _flatten(self, lst: List) -> List:
        """Flatten nested lists."""
        result = []
        for item in lst:
            if isinstance(item, (list, tuple)):
                result.extend(self._flatten(item))
            else:
                result.append(item)
        return result
    
    def _to_number(self, x: Any) -> float:
        """Convert to number."""
        if x is None:
            return 0
        if isinstance(x, bool):
            return 1 if x else 0
        if isinstance(x, (int, float)):
            return float(x)
        if isinstance(x, str):
            # Remove currency symbols and commas
            cleaned = re.sub(r'[$€£¥,]', '', x.strip())
            return float(cleaned) if cleaned else 0
        return 0
    
    def _to_boolean(self, x: Any) -> bool:
        """Convert to boolean."""
        if x is None:
            return False
        if isinstance(x, bool):
            return x
        if isinstance(x, str):
            return x.lower() in ('true', 'yes', '1', 'on', 'y')
        return bool(x)
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a custom function."""
        self._functions[name] = func
    
    def unregister_function(self, name: str) -> bool:
        """Unregister a function."""
        if name in self._functions:
            del self._functions[name]
            return True
        return False
    
    def evaluate(self, expression: str, context: Dict[str, Any]) -> Any:
        """
        Evaluate an expression with given context.
        
        Args:
            expression: Expression string
            context: Variable context (inputs)
            
        Returns:
            Evaluated result
        """
        if not expression:
            return None
        
        # Build evaluation namespace
        namespace = {
            **self._functions,
            **context,
            # Boolean literals
            'true': True,
            'false': False,
            'True': True,
            'False': False,
            # Null
            'null': None,
            'None': None,
            # Math constants
            'pi': math.pi,
            'e': math.e,
        }
        
        try:
            # Handle FEEL-like syntax conversions
            expr = self._convert_feel_syntax(expression)
            
            # Evaluate safely with restricted builtins
            safe_builtins = {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'range': range,
                'sorted': sorted,
                'reversed': reversed,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'isinstance': isinstance,
                'type': type,
            }
            
            result = eval(expr, {"__builtins__": safe_builtins}, namespace)
            return result
            
        except Exception as e:
            logger.warning(f"Expression evaluation failed: {expression} -> {e}")
            raise ValueError(f"Invalid expression: {expression} - {e}") from e
    
    def _convert_feel_syntax(self, expr: str) -> str:
        """Convert FEEL-like syntax to Python."""
        result = expr
        
        # If-then-else (must be done first, before other replacements)
        # Pattern: if condition then value1 else value2
        result = re.sub(
            r'\bif\s+(.+?)\s+then\s+(.+?)\s+else\s+(\S+)',
            r'(\2) if (\1) else (\3)',
            result,
            flags=re.IGNORECASE
        )
        
        # Logical operators
        result = re.sub(r'\band\b', ' and ', result)
        result = re.sub(r'\bor\b', ' or ', result)
        result = re.sub(r'\bnot\b', ' not ', result)
        
        # Between syntax: x between a and b
        result = re.sub(
            r'(\w+)\s+between\s+(\S+)\s+and\s+(\S+)',
            r'between(\1, \2, \3)',
            result,
            flags=re.IGNORECASE
        )
        
        # In list syntax
        result = re.sub(
            r'(\w+)\s+in\s+\[([^\]]+)\]',
            r'\1 in [\2]',
            result
        )
        
        # Null handling
        result = re.sub(r'\bnull\b', 'None', result, flags=re.IGNORECASE)
        
        # Boolean literals  
        result = re.sub(r'\btrue\b', 'True', result, flags=re.IGNORECASE)
        result = re.sub(r'\bfalse\b', 'False', result, flags=re.IGNORECASE)
        
        # String methods with dot notation
        # e.g., name.length -> length(name)
        # But be careful not to convert function calls
        
        # Power operator (** is already Python)
        # Modulo (% is already Python)
        
        return result
    
    def validate(self, expression: str) -> Dict[str, Any]:
        """
        Validate an expression without evaluating it.
        
        Returns dict with 'valid', 'error', 'variables' keys.
        """
        try:
            # Convert syntax
            converted = self._convert_feel_syntax(expression)
            
            # Try to compile
            compile(converted, '<expression>', 'eval')
            
            # Extract variable references
            variables = self._extract_variables(expression)
            
            return {
                'valid': True,
                'error': None,
                'variables': variables,
                'converted': converted,
            }
            
        except SyntaxError as e:
            return {
                'valid': False,
                'error': str(e),
                'variables': [],
                'converted': None,
            }
    
    def _extract_variables(self, expression: str) -> List[str]:
        """Extract variable names from expression."""
        # Remove strings
        expr = re.sub(r'"[^"]*"', '', expression)
        expr = re.sub(r"'[^']*'", '', expr)
        
        # Find identifiers
        identifiers = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', expr))
        
        # Remove function names and keywords
        reserved = set(self._functions.keys()) | {
            'true', 'false', 'null', 'and', 'or', 'not', 'if', 'then', 'else',
            'in', 'between', 'True', 'False', 'None',
        }
        
        return sorted(identifiers - reserved)
