"""
Helper utility functions for data processing and date handling.
"""
from datetime import datetime, timedelta
from typing import Tuple, Optional
import re


def parse_natural_period_to_dates(period: str) -> Tuple[str, str]:
    """
    Convert period strings to start and end dates.
    
    Supports formats like:
    - '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'ytd', 'max'
    - 'last 6 months', 'past year', 'last 2 years'
    
    Args:
        period: Period string
        
    Returns:
        Tuple of (start_date, end_date) as strings in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = None
    
    period = period.lower().strip()
    
    # Handle yfinance-style periods
    if period == '1d':
        start_date = end_date - timedelta(days=1)
    elif period == '5d':
        start_date = end_date - timedelta(days=5)
    elif period == '1mo':
        start_date = end_date - timedelta(days=30)
    elif period == '3mo':
        start_date = end_date - timedelta(days=90)
    elif period == '6mo':
        start_date = end_date - timedelta(days=180)
    elif period == '1y':
        start_date = end_date - timedelta(days=365)
    elif period == '2y':
        start_date = end_date - timedelta(days=730)
    elif period == '5y':
        start_date = end_date - timedelta(days=1825)
    elif period == '10y':
        start_date = end_date - timedelta(days=3650)
    elif period == 'ytd':
        start_date = datetime(end_date.year, 1, 1)
    elif period == 'max':
        start_date = datetime(1970, 1, 1)
    
    # Handle natural language periods
    else:
        # Try to extract number and unit
        match = re.search(r'(\d+)\s*(day|week|month|year)s?', period)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'day':
                start_date = end_date - timedelta(days=num)
            elif unit == 'week':
                start_date = end_date - timedelta(weeks=num)
            elif unit == 'month':
                start_date = end_date - timedelta(days=num * 30)
            elif unit == 'year':
                start_date = end_date - timedelta(days=num * 365)
    
    # If we couldn't parse it, default to 1 year
    if start_date is None:
        start_date = end_date - timedelta(days=365)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def validate_symbol(symbol: str) -> bool:
    """
    Validate a stock ticker symbol.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol:
        return False
    
    # Basic validation: 1-5 uppercase letters, optionally with a dot for class shares
    pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'
    return bool(re.match(pattern, symbol.upper()))


def standardize_symbol(symbol: str) -> str:
    """
    Standardize a stock ticker symbol to uppercase.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Standardized symbol
    """
    return symbol.upper().strip()


def format_currency(value: float, currency: str = "USD") -> str:
    """
    Format a number as currency.
    
    Args:
        value: Numeric value
        currency: Currency code (default: USD)
        
    Returns:
        Formatted currency string
    """
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"


def calculate_returns(prices: list) -> list:
    """
    Calculate percentage returns from a list of prices.
    
    Args:
        prices: List of prices
        
    Returns:
        List of percentage returns
    """
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            ret = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
            returns.append(ret)
        else:
            returns.append(0.0)
    
    return returns