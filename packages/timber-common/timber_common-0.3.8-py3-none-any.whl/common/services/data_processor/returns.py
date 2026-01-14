"""
Returns Calculation Module

Handles calculation of simple returns, log returns, and cumulative returns.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def calculate_returns(
    df: pd.DataFrame,
    price_column: str = 'Close',
    method: str = 'simple'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates returns from price data.
    
    Args:
        df: DataFrame with price data
        price_column: Column to use for calculations (default: 'Close')
        method: 'simple' or 'log' returns
        
    Returns:
        Tuple of (DataFrame with Returns column, error message)
    """
    try:
        df = df.copy()
        
        if price_column not in df.columns:
            return df, f"Column '{price_column}' not found in DataFrame"
        
        if method == 'simple':
            df['Returns'] = df[price_column].pct_change()
        elif method == 'log':
            df['Returns'] = np.log(df[price_column] / df[price_column].shift(1))
        else:
            return df, f"Unknown method: {method}. Use 'simple' or 'log'"
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating returns: {str(e)}"


def calculate_cumulative_returns(
    df: pd.DataFrame,
    returns_column: str = 'Returns'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates cumulative returns.
    
    Args:
        df: DataFrame with returns
        returns_column: Column with returns data
        
    Returns:
        Tuple of (DataFrame with Cumulative_Returns column, error message)
    """
    try:
        df = df.copy()
        
        if returns_column not in df.columns:
            return df, f"Column '{returns_column}' not found in DataFrame"
        
        # Calculate cumulative returns: (1 + r1) * (1 + r2) * ... - 1
        df['Cumulative_Returns'] = (1 + df[returns_column]).cumprod() - 1
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating cumulative returns: {str(e)}"


def calculate_rolling_returns(
    df: pd.DataFrame,
    window: int = 20,
    returns_column: str = 'Returns',
    annualize: bool = False,
    trading_days: int = 252
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates rolling returns over a specified window.
    
    Args:
        df: DataFrame with returns
        window: Rolling window size
        returns_column: Column with returns data
        annualize: Whether to annualize the returns
        trading_days: Number of trading days per year
        
    Returns:
        Tuple of (DataFrame with Rolling_Returns column, error message)
    """
    try:
        df = df.copy()
        
        if returns_column not in df.columns:
            return df, f"Column '{returns_column}' not found in DataFrame"
        
        # Calculate rolling mean
        df[f'Rolling_Returns_{window}'] = df[returns_column].rolling(window=window).mean()
        
        # Annualize if requested
        if annualize:
            df[f'Rolling_Returns_{window}'] = df[f'Rolling_Returns_{window}'] * trading_days
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating rolling returns: {str(e)}"