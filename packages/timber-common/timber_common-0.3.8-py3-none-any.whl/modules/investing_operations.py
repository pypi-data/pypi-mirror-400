"""
Stock and Index Operations - COMPLETE IMPLEMENTATION

This module registers operations for stock and index data fetching/processing.
These operations can be called from configuration files.

COMPLETED: All TODOs replaced with actual implementations using your existing common library.
"""

import pandas as pd
from typing import Tuple, Optional, List, Dict, Any
from datetime import datetime

from common.engine.operation_registry import registry, fetch_operation, transform_operation

# Import your actual services
from common.services import stock_data_service
from common.services import data_processor  # Adjust if your path is different

# Try to import curated_data_loader, but don't fail if it's not available
try:
    from common.services import curated_data_loader
    HAS_CURATED_LOADER = True
except ImportError:
    try:
        from common.services import curated_data_loader
        HAS_CURATED_LOADER = True
    except ImportError:
        try:
            from common import curated_data_loader
            HAS_CURATED_LOADER = True
        except ImportError:
            # No curated data loader available - we'll use fallback implementations
            HAS_CURATED_LOADER = False
            curated_data_loader = None
            print("⚠️  Warning: curated_data_loader not found. Using fallback implementations.")


# ============================================================================
# STOCK OPERATIONS - Using your actual common library
# ============================================================================

@fetch_operation(
    name="fetch_stock_info",
    description="Retrieves comprehensive information for a given stock symbol",
    tags=["stock", "info"]
)
def get_stock_info(symbol: str) -> Tuple[dict, Optional[str]]:
    """
    Retrieves comprehensive information for a given stock symbol.
    Uses stock_data_service from your common library.
    """
    return stock_data_service.fetch_company_info(symbol)


@fetch_operation(
    name="fetch_stock_news",
    description="Retrieves recent news articles for a given stock symbol",
    tags=["stock", "news"]
)
def get_stock_news(symbol: str, limit: int = 10) -> Tuple[List[dict], Optional[str]]:
    """
    Retrieves recent news articles for a given stock symbol.
    Uses stock_data_service from your common library.
    """
    return stock_data_service.fetch_news(symbol, limit=limit)


@fetch_operation(
    name="fetch_stock_data_by_period",
    description="Retrieves historical stock prices for a given symbol by period",
    tags=["stock", "historical", "prices"]
)
def get_stock_values_by_period(symbol: str, period: str) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Retrieves historical stock prices for a given symbol by period.
    Uses stock_data_service from your common library.
    """
    history, error = stock_data_service.fetch_historical_data(symbol, period=period)
    print(f"Fetched {len(history)} rows for {symbol} over period '{period}'")
    if error:
        print(f"Error: {error}")
    return history, error


@fetch_operation(
    name="fetch_stock_data_by_date_range",
    description="Retrieves historical stock prices for a given symbol within a date range",
    tags=["stock", "historical", "prices"]
)
def get_stock_values(
    symbol: str,
    start_date_str: str,
    end_date_str: Optional[str] = None
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Retrieves historical stock prices for a given symbol within a specified date range.
    Uses stock_data_service from your common library.
    """
    end = end_date_str if end_date_str else datetime.now().strftime('%Y-%m-%d')
    return stock_data_service.fetch_historical_data(
        symbol, 
        start_date=start_date_str, 
        end_date=end
    )


@fetch_operation(
    name="fetch_stock_financials",
    description="Retrieves financial statements for a given stock symbol",
    tags=["stock", "financials"]
)
def get_stock_financials(
    symbol: str, 
    period: str = 'yearly'
) -> Tuple[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame], Optional[str]]:
    """
    Retrieves financial statements (income, balance, cashflow).
    Uses stock_data_service from your common library.
    """
    income, balance, cashflow, error = stock_data_service.fetch_financials(symbol, period=period)
    if error:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame()), error
    return (income, balance, cashflow), None


# ============================================================================
# INDEX OPERATIONS - Integrating with your existing infrastructure
# ============================================================================

@fetch_operation(
    name="get_major_indices",
    description="Returns the curated list of major world indices",
    tags=["index", "reference"]
)
def get_major_indices() -> Tuple[Dict[str, str], None]:
    # Try to load from your curated data if available
    try:
        indices = curated_data_loader.get_available_indices()
        if indices:
            return {name: name for name in indices}, None
    except Exception:
        pass
    
    # Fallback to hardcoded list
    MAJOR_INDICES = {
        "S&P 500": "^GSPC",
        "Dow Jones Industrial Average": "^DJI",
        "NASDAQ Composite": "^IXIC",
        "Russell 2000": "^RUT",
        "FTSE 100": "^FTSE",
        "DAX": "^GDAXI",
        "CAC 40": "^FCHI",
        "Nikkei 225": "^N225",
        "Hang Seng Index": "^HSI",
    }
    return MAJOR_INDICES, None


@fetch_operation(
    name="fetch_index_performance",
    description="Fetches historical performance data for a given index symbol",
    tags=["index", "performance", "historical"]
)
def get_index_performance(symbol: str, period: str = "1y") -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Fetches and processes historical performance data for a given index symbol.
    Uses stock_data_service and data_processor from your common library.
    """
    # Fetch raw data
    df, error = stock_data_service.fetch_historical_data(symbol, period=period)
    if error:
        return pd.DataFrame(), f"Failed to fetch performance for index {symbol}: {error}"
    
    # Process data using your data_processor
    df = data_processor.standardize_dataframe(df)
    df, _ = data_processor.calculate_returns(df)
    df, _ = data_processor.calculate_cumulative_returns(df)
    df, _ = data_processor.calculate_wealth_index(df)
    df, _ = data_processor.calculate_drawdown(df)
    
    return df, None


@fetch_operation(
    name="fetch_index_news",
    description="Fetches recent news for a given index symbol",
    tags=["index", "news"]
)
def get_index_news(symbol: str, limit: int = 20) -> Tuple[List[dict], Optional[str]]:
    """
    Fetches recent news for a given index symbol.
    Uses stock_data_service from your common library.
    """
    return stock_data_service.fetch_news(symbol, limit=limit)


@fetch_operation(
    name="fetch_index_components",
    description="Fetches constituent companies for a given index",
    tags=["index", "components", "constituents"]
)
def get_index_components(index_name: str) -> Tuple[pd.DataFrame, Optional[str]]:
    try:
        # Try to get companies from curated data
        companies, error = curated_data_loader.get_companies_by_index(index_name)
        if error:
            return pd.DataFrame(), error
        
        # Convert to DataFrame if it's a list
        if isinstance(companies, list):
            df = pd.DataFrame(companies)
        else:
            df = companies
        
        return df, None
        
    except Exception as e:
        return pd.DataFrame(), f"Component lookup for '{index_name}' failed: {str(e)}"


@fetch_operation(
    name="fetch_index_info",
    description="Fetches general information for a given index",
    tags=["index", "info"]
)
def get_index_info(symbol: str) -> Tuple[dict, Optional[str]]:
    """
    Fetches general information for a given index.
    Uses stock_data_service from your common library.
    """
    return stock_data_service.fetch_company_info(symbol)


# ============================================================================
# DATA TRANSFORMATION OPERATIONS - Using your data_processor
# ============================================================================

@transform_operation(
    name="standardize_dataframe",
    description="Standardizes a DataFrame to a common format",
    tags=["transform", "dataframe"]
)
def standardize_dataframe_op(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes a DataFrame to a common format.
    Uses data_processor from your common library.
    """
    return data_processor.standardize_dataframe(df)


@transform_operation(
    name="calculate_returns",
    description="Calculates returns for a price DataFrame",
    tags=["transform", "returns", "analysis"]
)
def calculate_returns_op(df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates returns for a price DataFrame.
    Uses data_processor from your common library.
    """
    return data_processor.calculate_returns(df)


@transform_operation(
    name="calculate_cumulative_returns",
    description="Calculates cumulative returns for a price DataFrame",
    tags=["transform", "returns", "analysis"]
)
def calculate_cumulative_returns_op(df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates cumulative returns for a price DataFrame.
    Uses data_processor from your common library.
    """
    return data_processor.calculate_cumulative_returns(df)


@transform_operation(
    name="calculate_wealth_index",
    description="Calculates wealth index for a returns DataFrame",
    tags=["transform", "wealth", "analysis"]
)
def calculate_wealth_index_op(
    df: pd.DataFrame, 
    initial_investment: float = 1000
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates wealth index for a returns DataFrame.
    Uses data_processor from your common library.
    """
    return data_processor.calculate_wealth_index(df, initial_investment=initial_investment)


@transform_operation(
    name="calculate_drawdown",
    description="Calculates drawdown for a price DataFrame",
    tags=["transform", "drawdown", "risk", "analysis"]
)
def calculate_drawdown_op(df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates drawdown for a price DataFrame.
    Uses data_processor from your common library.
    """
    return data_processor.calculate_drawdown(df)


# ============================================================================
# ADVANCED OPERATIONS - Additional useful operations
# ============================================================================

@transform_operation(
    name="calculate_volatility",
    description="Calculates rolling volatility for a returns DataFrame",
    tags=["transform", "volatility", "risk", "analysis"]
)
def calculate_volatility(
    df: pd.DataFrame, 
    window: int = 20,
    annualize: bool = True
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates rolling volatility.
    """
    if 'Returns' not in df.columns:
        return df, "DataFrame must have 'Returns' column"
    
    df['Volatility'] = df['Returns'].rolling(window=window).std()
    
    if annualize:
        df['Volatility'] = df['Volatility'] * (252 ** 0.5)  # Annualize
    
    return df, None


@transform_operation(
    name="calculate_sharpe_ratio",
    description="Calculates Sharpe ratio for a returns DataFrame",
    tags=["transform", "sharpe", "risk", "analysis"]
)
def calculate_sharpe_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = 0.02,
    window: int = 252
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates rolling Sharpe ratio.
    """
    if 'Returns' not in df.columns:
        return df, "DataFrame must have 'Returns' column"
    
    # Calculate rolling mean returns
    rolling_returns = df['Returns'].rolling(window=window).mean() * 252  # Annualize
    
    # Calculate rolling volatility
    rolling_vol = df['Returns'].rolling(window=window).std() * (252 ** 0.5)  # Annualize
    
    # Calculate Sharpe ratio
    df['Sharpe_Ratio'] = (rolling_returns - risk_free_rate) / rolling_vol
    
    return df, None


@fetch_operation(
    name="batch_fetch_stock_data",
    description="Fetches historical data for multiple symbols in batch",
    tags=["stock", "batch", "historical"]
)
def batch_fetch_stock_data(
    symbols: List[str],
    period: str = "1y"
) -> Tuple[Dict[str, pd.DataFrame], Optional[str]]:
    """
    Fetches data for multiple symbols.
    Returns dict mapping symbol to DataFrame.
    """
    results = {}
    errors = []
    
    for symbol in symbols:
        df, error = stock_data_service.fetch_historical_data(symbol, period=period)
        if error:
            errors.append(f"{symbol}: {error}")
        else:
            results[symbol] = df
    
    error_msg = "; ".join(errors) if errors else None
    return results, error_msg


# ============================================================================
# VALIDATION OPERATIONS
# ============================================================================

@transform_operation(
    name="validate_price_data",
    description="Validates price data for quality issues",
    tags=["validate", "quality", "data"]
)
def validate_price_data(df: pd.DataFrame) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Validates price data and returns quality metrics.
    """
    from common.utils import validate_price_data
    
    validation_results = {
        "is_valid": False,
        "row_count": len(df),
        "has_nulls": df.isnull().any().any(),
        "has_negative_prices": False,
        "date_range": None
    }
    
    try:
        # Use your validator
        is_valid = validate_price_data(df, raise_error=False)
        validation_results["is_valid"] = is_valid
        
        # Additional checks
        if 'Close' in df.columns:
            validation_results["has_negative_prices"] = (df['Close'] < 0).any()
        
        if 'Date' in df.columns:
            validation_results["date_range"] = (
                str(df['Date'].min()),
                str(df['Date'].max())
            )
        
        return validation_results, None
        
    except Exception as e:
        return validation_results, str(e)