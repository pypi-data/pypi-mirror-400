"""
Data Serialization Utility for Timber

Provides serialization functions for converting complex data types
(DataFrames, datetime objects, numpy types) into JSON-serializable formats.

UPDATED: Now includes reverse-direction functions for parsing stringified JSON
back to native types, completing the bidirectional serialization utilities.

This utility is designed to be used across all applications in the Oak ecosystem
that need to serialize data for API responses, Celery tasks, or database storage.
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Union
from datetime import datetime, date, time
import logging
import json
import ast

logger = logging.getLogger(__name__)


def serialize_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Serialize a DataFrame to a JSON-compatible format.
    
    Handles:
    - DatetimeIndex → ISO format strings
    - Timestamp objects → ISO format strings  
    - NaN/NA values → None
    - Numpy types → Python native types
    
    Args:
        df: pandas DataFrame to serialize
        
    Returns:
        Dict with serialized data in format:
        {
            'type': 'dataframe',
            'data': [...],  # List of row dicts
            'columns': [...],  # Column names
            'index_name': 'Date',  # If datetime index
            'shape': (rows, cols)
        }
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
    
    try:
        # Handle DatetimeIndex by resetting it to a column
        if isinstance(df.index, pd.DatetimeIndex):
            df_copy = df.reset_index()
            index_name = df.index.name or 'Date'
        else:
            df_copy = df.copy()
            index_name = None
        
        # Convert to dict with records orientation
        data = df_copy.to_dict('records')
        
        # Clean up each record
        for record in data:
            for key, value in list(record.items()):
                # Convert pandas Timestamp to ISO string
                if isinstance(value, pd.Timestamp):
                    record[key] = value.isoformat()
                # Convert datetime to ISO string
                elif isinstance(value, (datetime, date)):
                    record[key] = value.isoformat()
                # Convert NaN/NA to None
                elif pd.isna(value):
                    record[key] = None
                # Convert numpy types to Python native
                elif isinstance(value, (np.integer, np.floating)):
                    record[key] = value.item()
        
        return {
            'type': 'dataframe',
            'data': data,
            'columns': df.columns.tolist(),
            'index_name': index_name,
            'shape': list(df.shape),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
    except Exception as e:
        logger.error(f"Failed to serialize DataFrame: {e}", exc_info=True)
        # Fallback: use pandas JSON serialization
        try:
            return {
                'type': 'dataframe',
                'data': df.to_json(orient='records', date_format='iso'),
                'shape': list(df.shape),
                'serialization': 'json_string',
                'warning': 'Fallback serialization used'
            }
        except Exception as e2:
            # Last resort: string representation
            logger.error(f"Fallback serialization also failed: {e2}")
            return {
                'type': 'dataframe',
                'data': str(df)[:1000],  # Limit size
                'shape': list(df.shape),
                'error': f"Serialization failed: {str(e)}"
            }


def serialize_datetime(dt: Union[datetime, date, time, pd.Timestamp]) -> str:
    """
    Serialize datetime objects to ISO format strings.
    
    Args:
        dt: datetime, date, time, or pandas Timestamp object
        
    Returns:
        ISO format string
    """
    if isinstance(dt, pd.Timestamp):
        return dt.isoformat()
    elif hasattr(dt, 'isoformat'):
        return dt.isoformat()
    else:
        raise TypeError(f"Expected datetime-like object, got {type(dt).__name__}")


def serialize_numpy(value: Union[np.ndarray, np.generic]) -> Union[List, Any]:
    """
    Serialize numpy arrays and scalars to JSON-compatible types.
    
    Args:
        value: numpy array or scalar
        
    Returns:
        Python native list or scalar
    """
    if isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, (np.integer, np.floating)):
        return value.item()
    elif isinstance(value, np.bool_):
        return bool(value)
    else:
        return value


def serialize_value(value: Any) -> Any:
    """
    Recursively serialize any value to JSON-compatible format.
    
    Handles:
    - DataFrames → dict with metadata
    - datetime objects → ISO strings
    - numpy types → Python natives
    - Nested dicts/lists → recursively serialized
    - NaN/NA → None
    
    Args:
        value: Any value to serialize
        
    Returns:
        JSON-serializable version of the value
    """
    # Handle None
    if value is None:
        return None
    
    # Handle NaN/NA
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass  # Not a pandas type
    
    # Handle DataFrame
    if isinstance(value, pd.DataFrame):
        return serialize_dataframe(value)
    
    # Handle pandas Series
    if isinstance(value, pd.Series):
        return serialize_value(value.to_dict())
    
    # Handle datetime types
    if isinstance(value, (pd.Timestamp, datetime, date, time)):
        return serialize_datetime(value)
    
    # Handle numpy types
    if isinstance(value, (np.ndarray, np.generic)):
        return serialize_numpy(value)
    
    # Handle dict - recursively serialize BOTH keys and values
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            # Serialize the key (handles Timestamp, datetime, etc. as keys)
            if isinstance(k, (pd.Timestamp, datetime, date, time)):
                serialized_key = serialize_datetime(k)
            elif isinstance(k, (np.integer, np.floating)):
                serialized_key = str(k.item())
            elif not isinstance(k, (str, int, float, bool, type(None))):
                # Convert any other non-JSON-safe key type to string
                serialized_key = str(k)
            else:
                serialized_key = k
            
            # Serialize the value
            result[serialized_key] = serialize_value(v)
        
        return result
    
    # Handle list/tuple - recursively serialize items
    if isinstance(value, (list, tuple)):
        serialized = [serialize_value(item) for item in value]
        return serialized if isinstance(value, list) else tuple(serialized)
    
    # Handle set
    if isinstance(value, set):
        return [serialize_value(item) for item in value]
    
    # Return as-is for primitive types (str, int, float, bool)
    return value


def deserialize_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Deserialize a DataFrame from the format created by serialize_dataframe.
    
    Args:
        data: Dict with 'type': 'dataframe' and serialized data
        
    Returns:
        Reconstructed pandas DataFrame
    """
    if data.get('type') != 'dataframe':
        raise ValueError("Data is not a serialized DataFrame")
    
    # Handle json_string serialization
    if data.get('serialization') == 'json_string':
        import json
        df = pd.read_json(json.loads(data['data']), orient='records')
        return df
    
    # Standard deserialization
    df = pd.DataFrame(data['data'])
    
    # Restore datetime index if it was present
    if data.get('index_name'):
        index_col = data['index_name']
        if index_col in df.columns:
            df[index_col] = pd.to_datetime(df[index_col])
            df = df.set_index(index_col)
    
    return df


def to_json_serializable(obj: Any) -> Any:
    """
    Convert any object to a JSON-serializable format.
    
    This is the main entry point for serialization. Use this function
    when you need to prepare data for JSON encoding.
    
    Args:
        obj: Any object to serialize
        
    Returns:
        JSON-serializable version of the object
        
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, 2, 3]})
        >>> serializable = to_json_serializable(df)
        >>> import json
        >>> json.dumps(serializable)  # Works!
    """
    return serialize_value(obj)


# ============================================================================
# NEW FUNCTIONS - Reverse Direction (Parsing Stringified → Native JSON)
# ============================================================================
# These functions complete the bidirectional serialization utilities by
# handling the reverse direction: parsing stringified JSON back to native types.
# ============================================================================


def parse_json_string(s: str) -> Any:
    """
    Parse a string that might contain JSON or Python literal data.
    
    Attempts to parse in order:
    1. JSON (double quotes) using json.loads()
    2. Python literal (single quotes) using ast.literal_eval()
    3. Return original if neither works
    
    Args:
        s: String that might contain JSON/dict data
        
    Returns:
        Parsed object if successful, original string if not parseable
        
    Example:
        >>> parse_json_string('{"key": "value"}')  # JSON
        {'key': 'value'}
        >>> parse_json_string("{'key': 'value'}")  # Python literal
        {'key': 'value'}
        >>> parse_json_string('just a string')     # Not parseable
        'just a string'
    """
    if not isinstance(s, str):
        return s
    
    # Skip if it doesn't look like a data structure
    s_stripped = s.strip()
    if not (s_stripped.startswith('{') or s_stripped.startswith('[')):
        return s
    
    # Try JSON first (handles double quotes)
    try:
        return json.loads(s_stripped)
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Try Python literal_eval (handles single quotes)
    try:
        return ast.literal_eval(s_stripped)
    except (ValueError, SyntaxError, MemoryError):
        pass
    
    # Can't parse - return original
    return s


def ensure_native_json(obj: Any, max_depth: int = 20, _current_depth: int = 0) -> Any:
    """
    Ensure object is in native JSON types (dict, list, str, int, float, bool, None).
    
    This function:
    1. Parses any stringified dicts/lists back to native types
    2. Recursively processes nested structures
    3. Keeps everything as native Python types suitable for JSON
    
    Use this when:
    - Reading from database (might contain stringified data)
    - Processing workflow variables (might be stringified)
    - Preparing API responses (ensure clean JSON)
    
    Args:
        obj: Object to convert to native JSON
        max_depth: Maximum recursion depth (prevents infinite loops)
        _current_depth: Internal recursion tracker
        
    Returns:
        Object with all data as native JSON types
        
    Example:
        >>> ensure_native_json("{'key': 'value'}")  # Stringified dict
        {'key': 'value'}
        >>> ensure_native_json({'outer': "{'inner': 'value'}"})  # Nested stringified
        {'outer': {'inner': 'value'}}
    """
    # Prevent infinite recursion
    if _current_depth > max_depth:
        logger.warning(f"Max depth {max_depth} reached during JSON cleaning")
        return obj
    
    # None stays None
    if obj is None:
        return None
    
    # Strings - try to parse if they contain JSON/dict structures
    if isinstance(obj, str):
        parsed = parse_json_string(obj)
        if parsed != obj:  # Successfully parsed
            # Recursively clean the parsed result
            return ensure_native_json(parsed, max_depth, _current_depth + 1)
        return obj
    
    # Primitives - already JSON compatible
    if isinstance(obj, (bool, int, float)):
        return obj
    
    # Datetime handling - convert to ISO string
    if isinstance(obj, (pd.Timestamp, datetime, date, time)):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
    
    # DataFrame handling - use existing serializer
    if isinstance(obj, pd.DataFrame):
        return serialize_dataframe(obj)
    
    # Dictionaries - recursively ensure native JSON for all values
    if isinstance(obj, dict):
        return {
            key: ensure_native_json(value, max_depth, _current_depth + 1)
            for key, value in obj.items()
        }
    
    # Lists/tuples - recursively ensure native JSON for all items
    if isinstance(obj, (list, tuple)):
        cleaned = [
            ensure_native_json(item, max_depth, _current_depth + 1)
            for item in obj
        ]
        return cleaned  # Always return as list (JSON doesn't distinguish tuple)
    
    # Sets - convert to list
    if isinstance(obj, set):
        return [
            ensure_native_json(item, max_depth, _current_depth + 1)
            for item in obj
        ]
    
    # Other types - convert to string as last resort
    logger.warning(f"Converting unsupported type {type(obj).__name__} to string")
    return str(obj)


def validate_json_serializable(obj: Any, path: str = "root") -> bool:
    """
    Validate that an object is JSON serializable.
    
    Use this before:
    - Storing data in database JSONB fields
    - Sending data via API
    - Passing data to Celery tasks
    
    Args:
        obj: Object to validate
        path: Current path in object tree (for error messages)
        
    Returns:
        True if valid JSON, False otherwise (logs errors)
        
    Example:
        >>> validate_json_serializable({'key': 'value'})
        True
        >>> import pandas as pd
        >>> validate_json_serializable(pd.DataFrame())  # Not directly serializable
        False
    """
    try:
        # Attempt actual JSON serialization
        json.dumps(obj)
        return True
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization validation failed at {path}: {e}")
        
        # Provide more detail for dicts/lists
        if isinstance(obj, dict):
            for key, value in obj.items():
                if not validate_json_serializable(value, f"{path}.{key}"):
                    return False
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                if not validate_json_serializable(item, f"{path}[{idx}]"):
                    return False
        
        return False


def prepare_for_jsonb_storage(data: Any) -> Any:
    """
    Prepare data for storage in PostgreSQL JSONB fields.
    
    This is the main function to use before saving to database.
    It combines serialization and validation:
    1. Converts complex types to JSON (to_json_serializable)
    2. Ensures native JSON types (ensure_native_json)
    3. Validates JSON serializability
    
    Args:
        data: Data to prepare for database
        
    Returns:
        Clean JSON-ready data
        
    Raises:
        ValueError: If data cannot be made JSON serializable
        
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, 2]})
        >>> clean = prepare_for_jsonb_storage({'dataframe': df})
        >>> # Result: {'dataframe': {'type': 'dataframe', 'data': [...]}}
    """
    logger.debug("Preparing data for JSONB storage")
    
    # Step 1: Serialize complex types (DataFrames, datetime, etc.)
    serialized = to_json_serializable(data)
    
    # Step 2: Ensure all stringified dicts are parsed back to native
    cleaned = ensure_native_json(serialized)
    
    # Step 3: Validate it's actually JSON serializable
    if not validate_json_serializable(cleaned):
        logger.error("Data is not JSON serializable after cleaning!")
        raise ValueError("Data cannot be made JSON serializable")
    
    logger.debug("Data successfully prepared for JSONB storage")
    return cleaned


# Export main functions
__all__ = [
    # Original serialization functions
    'serialize_dataframe',
    'serialize_datetime',
    'serialize_numpy',
    'serialize_value',
    'deserialize_dataframe',
    'to_json_serializable',
    # New reverse-direction functions
    'parse_json_string',
    'ensure_native_json',
    'validate_json_serializable',
    'prepare_for_jsonb_storage'
]