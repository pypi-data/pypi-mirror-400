"""
Risk Metrics Module

Handles calculation of volatility, drawdown, Sharpe ratio, and other risk metrics.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def calculate_volatility(
    df: pd.DataFrame,
    window: int = 20,
    returns_column: str = 'Returns',
    annualize: bool = True,
    trading_days: int = 252
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates rolling volatility (standard deviation of returns).
    
    Args:
        df: DataFrame with returns
        window: Rolling window size
        returns_column: Column with returns data
        annualize: Whether to annualize the volatility
        trading_days: Number of trading days per year (for annualization)
        
    Returns:
        Tuple of (DataFrame with Volatility column, error message)
    """
    try:
        df = df.copy()
        
        if returns_column not in df.columns:
            return df, f"Column '{returns_column}' not found in DataFrame"
        
        # Calculate rolling standard deviation
        df['Volatility'] = df[returns_column].rolling(window=window).std()
        
        # Annualize if requested
        if annualize:
            df['Volatility'] = df['Volatility'] * np.sqrt(trading_days)
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating volatility: {str(e)}"


def calculate_drawdown(
    df: pd.DataFrame,
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates drawdown from peak.
    
    Args:
        df: DataFrame with price data
        price_column: Column to use for calculations
        
    Returns:
        Tuple of (DataFrame with Drawdown and Peak columns, error message)
    """
    try:
        df = df.copy()
        
        if price_column not in df.columns:
            return df, f"Column '{price_column}' not found in DataFrame"
        
        # Calculate running peak
        df['Peak'] = df[price_column].cummax()
        
        # Calculate drawdown as percentage from peak
        df['Drawdown'] = (df[price_column] - df['Peak']) / df['Peak']
        
        # Also calculate max drawdown (most negative value)
        df['Max_Drawdown'] = df['Drawdown'].cummin()
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating drawdown: {str(e)}"


def calculate_sharpe_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = 0.02,
    window: int = 252,
    returns_column: str = 'Returns',
    trading_days: int = 252
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates rolling Sharpe ratio.
    
    Sharpe Ratio = (Average Return - Risk Free Rate) / Standard Deviation
    
    Args:
        df: DataFrame with returns
        risk_free_rate: Annual risk-free rate (default: 2%)
        window: Rolling window size
        returns_column: Column with returns data
        trading_days: Number of trading days per year
        
    Returns:
        Tuple of (DataFrame with Sharpe_Ratio column, error message)
    """
    try:
        df = df.copy()
        
        if returns_column not in df.columns:
            return df, f"Column '{returns_column}' not found in DataFrame"
        
        # Calculate rolling mean return (annualized)
        rolling_returns = df[returns_column].rolling(window=window).mean() * trading_days
        
        # Calculate rolling volatility (annualized)
        rolling_vol = df[returns_column].rolling(window=window).std() * np.sqrt(trading_days)
        
        # Calculate Sharpe ratio
        df['Sharpe_Ratio'] = (rolling_returns - risk_free_rate) / rolling_vol
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating Sharpe ratio: {str(e)}"


def calculate_sortino_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = 0.02,
    window: int = 252,
    returns_column: str = 'Returns',
    trading_days: int = 252
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates rolling Sortino ratio (like Sharpe but uses downside deviation).
    
    Args:
        df: DataFrame with returns
        risk_free_rate: Annual risk-free rate
        window: Rolling window size
        returns_column: Column with returns data
        trading_days: Number of trading days per year
        
    Returns:
        Tuple of (DataFrame with Sortino_Ratio column, error message)
    """
    try:
        df = df.copy()
        
        if returns_column not in df.columns:
            return df, f"Column '{returns_column}' not found in DataFrame"
        
        # Calculate rolling mean return (annualized)
        rolling_returns = df[returns_column].rolling(window=window).mean() * trading_days
        
        # Calculate downside deviation (only negative returns)
        downside = df[returns_column].copy()
        downside[downside > 0] = 0
        downside_dev = downside.rolling(window=window).std() * np.sqrt(trading_days)
        
        # Calculate Sortino ratio
        df['Sortino_Ratio'] = (rolling_returns - risk_free_rate) / downside_dev
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating Sortino ratio: {str(e)}"


def calculate_max_drawdown(
    df: pd.DataFrame,
    price_column: str = 'Close'
) -> Tuple[float, Optional[str]]:
    """
    Calculates the maximum drawdown over the entire period.
    
    Args:
        df: DataFrame with price data
        price_column: Column to use for calculations
        
    Returns:
        Tuple of (maximum drawdown value, error message)
    """
    try:
        if price_column not in df.columns:
            return 0.0, f"Column '{price_column}' not found in DataFrame"
        
        # Calculate running peak
        peak = df[price_column].cummax()
        
        # Calculate drawdown
        drawdown = (df[price_column] - peak) / peak
        
        # Return the maximum (most negative) drawdown
        max_dd = drawdown.min()
        
        return max_dd, None
        
    except Exception as e:
        return 0.0, f"Error calculating max drawdown: {str(e)}"


def calculate_var(
    df: pd.DataFrame,
    confidence_level: float = 0.95,
    returns_column: str = 'Returns'
) -> Tuple[float, Optional[str]]:
    """
    Calculates Value at Risk (VaR).
    
    Args:
        df: DataFrame with returns
        confidence_level: Confidence level (e.g., 0.95 for 95%)
        returns_column: Column with returns data
        
    Returns:
        Tuple of (VaR value, error message)
    """
    try:
        if returns_column not in df.columns:
            return 0.0, f"Column '{returns_column}' not found in DataFrame"
        
        # Calculate VaR as the percentile
        var = df[returns_column].quantile(1 - confidence_level)
        
        return var, None
        
    except Exception as e:
        return 0.0, f"Error calculating VaR: {str(e)}"