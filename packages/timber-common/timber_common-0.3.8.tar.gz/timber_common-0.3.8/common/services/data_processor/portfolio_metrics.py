"""
Portfolio Metrics Module

Handles portfolio-level calculations like wealth index, beta, correlation, etc.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def calculate_wealth_index(
    df: pd.DataFrame,
    initial_investment: float = 1000.0,
    returns_column: str = 'Returns'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates wealth index showing portfolio value over time.
    
    Args:
        df: DataFrame with returns
        initial_investment: Starting investment amount
        returns_column: Column with returns data
        
    Returns:
        Tuple of (DataFrame with Wealth_Index column, error message)
    """
    try:
        df = df.copy()
        
        if returns_column not in df.columns:
            return df, f"Column '{returns_column}' not found in DataFrame"
        
        # Calculate wealth index
        df['Wealth_Index'] = initial_investment * (1 + df[returns_column]).cumprod()
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating wealth index: {str(e)}"


def calculate_correlation(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    window: int = 30,
    column: str = 'Returns'
) -> Tuple[pd.Series, Optional[str]]:
    """
    Calculates rolling correlation between two DataFrames.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        window: Rolling window size
        column: Column to correlate
        
    Returns:
        Tuple of (Series with correlation values, error message)
    """
    try:
        if column not in df1.columns or column not in df2.columns:
            return pd.Series(), f"Column '{column}' not found in one or both DataFrames"
        
        # Align the dataframes by index
        df1_aligned, df2_aligned = df1[column].align(df2[column], join='inner')
        
        # Calculate rolling correlation
        correlation = df1_aligned.rolling(window=window).corr(df2_aligned)
        
        return correlation, None
        
    except Exception as e:
        return pd.Series(), f"Error calculating correlation: {str(e)}"


def calculate_beta(
    stock_df: pd.DataFrame,
    market_df: pd.DataFrame,
    window: int = 252,
    returns_column: str = 'Returns'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates rolling beta (systematic risk relative to market).
    
    Beta = Covariance(Stock, Market) / Variance(Market)
    
    Args:
        stock_df: DataFrame with stock returns
        market_df: DataFrame with market returns
        window: Rolling window size
        returns_column: Column with returns data
        
    Returns:
        Tuple of (DataFrame with Beta column, error message)
    """
    try:
        stock_df = stock_df.copy()
        
        if returns_column not in stock_df.columns:
            return stock_df, f"Column '{returns_column}' not found in stock DataFrame"
        if returns_column not in market_df.columns:
            return stock_df, f"Column '{returns_column}' not found in market DataFrame"
        
        # Align dataframes
        stock_returns, market_returns = stock_df[returns_column].align(
            market_df[returns_column], 
            join='inner'
        )
        
        # Calculate rolling covariance and variance
        covariance = stock_returns.rolling(window=window).cov(market_returns)
        variance = market_returns.rolling(window=window).var()
        
        # Calculate beta
        stock_df['Beta'] = covariance / variance
        
        return stock_df, None
        
    except Exception as e:
        return stock_df, f"Error calculating beta: {str(e)}"


def calculate_alpha(
    stock_df: pd.DataFrame,
    market_df: pd.DataFrame,
    risk_free_rate: float = 0.02,
    window: int = 252,
    returns_column: str = 'Returns',
    trading_days: int = 252
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Jensen's Alpha (excess return above CAPM prediction).
    
    Alpha = Stock Return - (Risk Free Rate + Beta * (Market Return - Risk Free Rate))
    
    Args:
        stock_df: DataFrame with stock returns and beta
        market_df: DataFrame with market returns
        risk_free_rate: Annual risk-free rate
        window: Rolling window size
        returns_column: Column with returns data
        trading_days: Number of trading days per year
        
    Returns:
        Tuple of (DataFrame with Alpha column, error message)
    """
    try:
        stock_df = stock_df.copy()
        
        # Ensure we have beta calculated
        if 'Beta' not in stock_df.columns:
            stock_df, error = calculate_beta(stock_df, market_df, window, returns_column)
            if error:
                return stock_df, error
        
        # Align dataframes
        stock_returns, market_returns = stock_df[returns_column].align(
            market_df[returns_column], 
            join='inner'
        )
        
        # Calculate rolling returns (annualized)
        stock_rolling = stock_returns.rolling(window=window).mean() * trading_days
        market_rolling = market_returns.rolling(window=window).mean() * trading_days
        
        # Calculate alpha
        expected_return = risk_free_rate + stock_df['Beta'] * (market_rolling - risk_free_rate)
        stock_df['Alpha'] = stock_rolling - expected_return
        
        return stock_df, None
        
    except Exception as e:
        return stock_df, f"Error calculating alpha: {str(e)}"


def calculate_information_ratio(
    portfolio_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    window: int = 252,
    returns_column: str = 'Returns'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Information Ratio (excess return per unit of tracking error).
    
    IR = (Portfolio Return - Benchmark Return) / Tracking Error
    
    Args:
        portfolio_df: DataFrame with portfolio returns
        benchmark_df: DataFrame with benchmark returns
        window: Rolling window size
        returns_column: Column with returns data
        
    Returns:
        Tuple of (DataFrame with Information_Ratio column, error message)
    """
    try:
        portfolio_df = portfolio_df.copy()
        
        # Align dataframes
        port_returns, bench_returns = portfolio_df[returns_column].align(
            benchmark_df[returns_column], 
            join='inner'
        )
        
        # Calculate excess returns
        excess_returns = port_returns - bench_returns
        
        # Calculate tracking error (std dev of excess returns)
        tracking_error = excess_returns.rolling(window=window).std()
        
        # Calculate average excess return
        avg_excess = excess_returns.rolling(window=window).mean()
        
        # Calculate Information Ratio
        portfolio_df['Information_Ratio'] = avg_excess / tracking_error
        
        return portfolio_df, None
        
    except Exception as e:
        return portfolio_df, f"Error calculating Information Ratio: {str(e)}"


def calculate_treynor_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = 0.02,
    window: int = 252,
    returns_column: str = 'Returns',
    trading_days: int = 252
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Treynor Ratio (excess return per unit of systematic risk).
    
    Treynor = (Return - Risk Free Rate) / Beta
    
    Args:
        df: DataFrame with returns and beta
        risk_free_rate: Annual risk-free rate
        window: Rolling window size
        returns_column: Column with returns data
        trading_days: Number of trading days per year
        
    Returns:
        Tuple of (DataFrame with Treynor_Ratio column, error message)
    """
    try:
        df = df.copy()
        
        if 'Beta' not in df.columns:
            return df, "DataFrame must have 'Beta' column. Calculate beta first."
        
        # Calculate rolling returns (annualized)
        rolling_returns = df[returns_column].rolling(window=window).mean() * trading_days
        
        # Calculate Treynor ratio
        df['Treynor_Ratio'] = (rolling_returns - risk_free_rate) / df['Beta']
        
        return df, None
        
    except Exception as e:
        return df, f"Error calculating Treynor ratio: {str(e)}"