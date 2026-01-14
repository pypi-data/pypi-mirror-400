"""
Validation functions for data integrity and business logic.
"""
import re
from typing import Any, Optional
from datetime import datetime
import pandas as pd


def validate_stock_symbol(symbol: str, raise_error: bool = False) -> bool:
    """
    Validate a stock ticker symbol.
    
    Args:
        symbol: Stock ticker symbol
        raise_error: If True, raises ValueError on invalid symbol
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValueError: If symbol is invalid and raise_error=True
    """
    if not symbol or not isinstance(symbol, str):
        if raise_error:
            raise ValueError("Symbol must be a non-empty string")
        return False
    
    # Allow 1-5 uppercase letters, optionally with a dot for class shares
    pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'
    is_valid = bool(re.match(pattern, symbol.upper()))
    
    if not is_valid and raise_error:
        raise ValueError(f"Invalid stock symbol: {symbol}")
    
    return is_valid


def validate_date_string(date_str: str, raise_error: bool = False) -> bool:
    """
    Validate a date string in YYYY-MM-DD format.
    
    Args:
        date_str: Date string
        raise_error: If True, raises ValueError on invalid date
        
    Returns:
        True if valid, False otherwise
    """
    if not date_str or not isinstance(date_str, str):
        if raise_error:
            raise ValueError("Date must be a non-empty string")
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError as e:
        if raise_error:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
        return False


def validate_date_range(start_date: str, end_date: str, raise_error: bool = False) -> bool:
    """
    Validate that start_date is before end_date.
    
    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        raise_error: If True, raises ValueError on invalid range
        
    Returns:
        True if valid, False otherwise
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start > end:
            if raise_error:
                raise ValueError(f"Start date {start_date} is after end date {end_date}")
            return False
        
        return True
    except ValueError as e:
        if raise_error:
            raise
        return False


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: Optional[list] = None,
    min_rows: int = 0,
    raise_error: bool = False
) -> bool:
    """
    Validate a pandas DataFrame.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        min_rows: Minimum number of rows required
        raise_error: If True, raises ValueError on validation failure
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(df, pd.DataFrame):
        if raise_error:
            raise ValueError("Input must be a pandas DataFrame")
        return False
    
    if df.empty and min_rows > 0:
        if raise_error:
            raise ValueError(f"DataFrame is empty (minimum {min_rows} rows required)")
        return False
    
    if len(df) < min_rows:
        if raise_error:
            raise ValueError(f"DataFrame has {len(df)} rows (minimum {min_rows} required)")
        return False
    
    if required_columns:
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            if raise_error:
                raise ValueError(f"Missing required columns: {missing_cols}")
            return False
    
    return True


def validate_price_data(df: pd.DataFrame, raise_error: bool = False) -> bool:
    """
    Validate stock price DataFrame.
    
    Args:
        df: Price DataFrame
        raise_error: If True, raises ValueError on validation failure
        
    Returns:
        True if valid, False otherwise
    """
    required_cols = ['Date', 'Close']
    
    if not validate_dataframe(df, required_columns=required_cols, min_rows=1, raise_error=raise_error):
        return False
    
    # Check for negative prices
    if (df['Close'] < 0).any():
        if raise_error:
            raise ValueError("DataFrame contains negative prices")
        return False
    
    # Check for null values in critical columns
    if df[['Date', 'Close']].isnull().any().any():
        if raise_error:
            raise ValueError("DataFrame contains null values in Date or Close columns")
        return False
    
    return True


def validate_api_key(api_key: Optional[str], service_name: str = "API", raise_error: bool = False) -> bool:
    """
    Validate that an API key is configured.
    
    Args:
        api_key: API key string
        service_name: Name of the service (for error messages)
        raise_error: If True, raises ValueError on invalid key
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key or 'use_env_variables' in str(api_key):
        if raise_error:
            raise ValueError(f"{service_name} API key is not configured")
        return False
    
    return True


def validate_period_string(period: str, raise_error: bool = False) -> bool:
    """
    Validate a period string.
    
    Args:
        period: Period string (e.g., '1d', '1mo', '1y', 'ytd', 'max')
        raise_error: If True, raises ValueError on invalid period
        
    Returns:
        True if valid, False otherwise
    """
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    
    # Check exact matches first
    if period.lower() in valid_periods:
        return True
    
    # Check natural language patterns
    pattern = r'^\d+\s*(day|week|month|year)s?$'
    if re.match(pattern, period.lower()):
        return True
    
    if raise_error:
        raise ValueError(f"Invalid period: {period}. Valid formats: {valid_periods} or '3 months', '2 years', etc.")
    
    return False