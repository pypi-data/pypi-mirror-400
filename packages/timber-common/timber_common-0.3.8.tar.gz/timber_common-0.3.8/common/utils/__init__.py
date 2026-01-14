"""
Utility functions and helpers for the Timber Common library.
"""

from .helpers import (
    parse_natural_period_to_dates,
    validate_symbol,
    standardize_symbol,
    format_currency,
    calculate_returns,
)

from .validators import (
    validate_stock_symbol,
    validate_date_string,
    validate_date_range,
    validate_dataframe,
    validate_price_data,
    validate_api_key,
    validate_period_string,
)

from .time_helpers import (
    current_utc,
    utc_plus_5min,
    utc_plus_1hour,
)

from .serialization_helpers import (
    serialize_dataframe,
    serialize_datetime,
    serialize_numpy,
    serialize_value,
    to_json_serializable
)

from .config import config
from .db_utils import db_manager

__all__ = [
    # Date and string helpers
    'parse_natural_period_to_dates',
    'validate_symbol',
    'standardize_symbol',
    'format_currency',
    'calculate_returns',
    
    # Validators
    'validate_stock_symbol',
    'validate_date_string',
    'validate_date_range',
    'validate_dataframe',
    'validate_price_data',
    'validate_api_key',
    'validate_period_string',
    
    # Configuration
    'config',
    'db_manager',
    
    # Time helpers
    'current_utc',
    'utc_plus_5min',
    'utc_plus_1hour',
    
    # Serialization helpers
    'serialize_dataframe',
    'serialize_datetime',
    'serialize_numpy',
    'serialize_value',
    'to_json_serializable'
]