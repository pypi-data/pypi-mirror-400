"""
Data Standardization Module

Handles data cleaning, formatting, and standardization.
"""

import pandas as pd
import numpy as np
from typing import Optional


def standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes a DataFrame to a consistent format.
    
    Ensures:
    - Date column is datetime
    - Numeric columns are float
    - Standard column names
    - Sorted by date
    
    Args:
        df: Input DataFrame
        
    Returns:
        Standardized DataFrame
    """
    # Type check - should be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"Input must be a pandas DataFrame, got {type(df).__name__}. "
            f"If you're passing data through a pipeline, make sure you're accessing "
            f"the DataFrame correctly (e.g., {{ raw_data[0] }} not {{ raw_data }})."
        )
    
    if df.empty:
        return df
    
    df = df.copy()
    
    # Standardize date column
    if 'Date' in df.columns:
        # Check if it's already a datetime type
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            # Try different date parsing strategies
            try:
                df['Date'] = pd.to_datetime(df['Date'], format='ISO8601')
            except:
                try:
                    df['Date'] = pd.to_datetime(df['Date'], format='mixed')
                except:
                    # Last resort - let pandas infer
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Set as index if not already
        if df.index.name != 'Date':
            df = df.set_index('Date')
    
    # Ensure numeric columns are float
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Sort by date
    df = df.sort_index()
    
    # Remove duplicates
    df = df[~df.index.duplicated(keep='first')]
    
    return df


def clean_data(df: pd.DataFrame, method: str = 'forward') -> pd.DataFrame:
    """
    Cleans data by handling missing values.
    
    Args:
        df: Input DataFrame
        method: 'forward', 'backward', 'interpolate', or 'drop'
        
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    if method == 'forward':
        df = df.fillna(method='ffill')
    elif method == 'backward':
        df = df.fillna(method='bfill')
    elif method == 'interpolate':
        df = df.interpolate(method='linear')
    elif method == 'drop':
        df = df.dropna()
    
    return df


def resample_data(
    df: pd.DataFrame,
    freq: str = 'D',
    price_column: str = 'Close'
) -> pd.DataFrame:
    """
    Resamples data to a different frequency.
    
    Args:
        df: Input DataFrame with datetime index
        freq: Frequency ('D'=daily, 'W'=weekly, 'M'=monthly, 'Q'=quarterly, 'Y'=yearly)
        price_column: Column to use for OHLC aggregation
        
    Returns:
        Resampled DataFrame
    """
    df = df.copy()
    
    # Create OHLC if we have the price column
    if price_column in df.columns:
        resampled = df.resample(freq).agg({
            price_column: 'last',
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Volume': 'sum'
        })
    else:
        resampled = df.resample(freq).last()
    
    return resampled