"""
Data Processor Package

Provides data processing and transformation functions for financial data.
"""

# Import all functions from sub-modules
from .standardization import (
    standardize_dataframe,
    clean_data,
    resample_data
)

from .returns import (
    calculate_returns,
    calculate_cumulative_returns,
    calculate_rolling_returns
)

from .risk_metrics import (
    calculate_volatility,
    calculate_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_var
)

from .technical_indicators import (
    calculate_moving_averages,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_stochastic,
    _ensure_dataframe # Imported to use in umbrella function
)

from .portfolio_metrics import (
    calculate_wealth_index,
    calculate_correlation,
    calculate_beta,
    calculate_alpha,
    calculate_information_ratio,
    calculate_treynor_ratio
)


# ============================================================================
# Umbrella Functions
# ============================================================================

def calculate_technical_indicators(
    df,
    ma_windows=None,
    ema_windows=None,
    rsi_window=None,
    macd_fast=None,
    macd_slow=None,
    macd_signal=None,
    bb_window=None,
    bb_std=None,
    atr_window=None,
    stoch_k_window=None,
    stoch_d_window=None,
    price_column=None
):
    """
    Umbrella function that calculates all technical indicators at once.
    Handles input normalization (JSON/Dict -> DataFrame).
    """
    # Apply defaults for None values (allows resolver to pass None for missing optional inputs)
    ma_windows = ma_windows if ma_windows is not None else [20, 50, 200]
    ema_windows = ema_windows if ema_windows is not None else [12, 26]
    rsi_window = rsi_window if rsi_window is not None else 14
    macd_fast = macd_fast if macd_fast is not None else 12
    macd_slow = macd_slow if macd_slow is not None else 26
    macd_signal = macd_signal if macd_signal is not None else 9
    bb_window = bb_window if bb_window is not None else 20
    bb_std = bb_std if bb_std is not None else 2.0
    atr_window = atr_window if atr_window is not None else 14
    stoch_k_window = stoch_k_window if stoch_k_window is not None else 14
    stoch_d_window = stoch_d_window if stoch_d_window is not None else 3
    price_column = price_column if price_column is not None else 'Close'
    
    results = {
        'success': True,
        'columns_added': [],
        'errors': {},
        'indicators': {}
    }
    
    # 1. Normalize Input
    df_clean, error = _ensure_dataframe(df)
    if error:
        results['success'] = False
        results['errors']['input'] = error
        # Return original input if conversion failed, to avoid downstream type errors
        return df, results
    
    # Use the clean DataFrame
    df = df_clean
    original_columns = set(df.columns)
    
    # 2. Run Calculations
    
    # Moving Averages
    df, error = calculate_moving_averages(df, windows=ma_windows, price_column=price_column)
    if error:
        results['errors']['moving_averages'] = error
        results['success'] = False
    else:
        results['indicators']['moving_averages'] = {
            'windows': ma_windows,
            'columns': [f'MA_{w}' for w in ma_windows]
        }
    
    # Exponential Moving Averages
    df, error = calculate_ema(df, windows=ema_windows, price_column=price_column)
    if error:
        results['errors']['ema'] = error
        results['success'] = False
    else:
        results['indicators']['ema'] = {
            'windows': ema_windows,
            'columns': [f'EMA_{w}' for w in ema_windows]
        }
    
    # RSI
    df, error = calculate_rsi(df, window=rsi_window, price_column=price_column)
    if error:
        results['errors']['rsi'] = error
        results['success'] = False
    else:
        results['indicators']['rsi'] = {
            'window': rsi_window,
            'column': 'RSI'
        }
    
    # MACD
    df, error = calculate_macd(
        df, 
        fast=macd_fast, 
        slow=macd_slow, 
        signal=macd_signal, 
        price_column=price_column
    )
    if error:
        results['errors']['macd'] = error
        results['success'] = False
    else:
        results['indicators']['macd'] = {
            'fast': macd_fast,
            'slow': macd_slow,
            'signal': macd_signal,
            'columns': ['MACD', 'MACD_Signal', 'MACD_Histogram']
        }
    
    # Bollinger Bands
    df, error = calculate_bollinger_bands(
        df, 
        window=bb_window, 
        num_std=bb_std, 
        price_column=price_column
    )
    if error:
        results['errors']['bollinger_bands'] = error
        results['success'] = False
    else:
        results['indicators']['bollinger_bands'] = {
            'window': bb_window,
            'std': bb_std,
            'columns': ['BB_Middle', 'BB_Upper', 'BB_Lower', 'BB_Width']
        }
    
    # ATR (requires OHLC data)
    df, error = calculate_atr(df, window=atr_window)
    if error:
        results['errors']['atr'] = error
        # ATR failure is not critical if OHLC data is missing
    else:
        results['indicators']['atr'] = {
            'window': atr_window,
            'column': 'ATR'
        }
    
    # Stochastic (requires OHLC data)
    df, error = calculate_stochastic(df, k_window=stoch_k_window, d_window=stoch_d_window)
    if error:
        results['errors']['stochastic'] = error
        # Stochastic failure is not critical if OHLC data is missing
    else:
        results['indicators']['stochastic'] = {
            'k_window': stoch_k_window,
            'd_window': stoch_d_window,
            'columns': ['Stochastic_K', 'Stochastic_D']
        }
    
    # Determine which columns were added
    new_columns = set(df.columns) - original_columns
    results['columns_added'] = sorted(list(new_columns))
    
    return df, results


# ============================================================================
# Aggregated Data Processor Class (for backward compatibility)
# ============================================================================

class DataProcessor:
    """
    Aggregated data processor that provides access to all functions.
    """
    
    # Standardization
    @staticmethod
    def standardize_dataframe(df):
        return standardize_dataframe(df)
    
    @staticmethod
    def clean_data(df, method='forward'):
        return clean_data(df, method)
    
    @staticmethod
    def resample_data(df, freq='D', price_column='Close'):
        return resample_data(df, freq, price_column)
    
    # Returns
    @staticmethod
    def calculate_returns(df, price_column='Close', method='simple'):
        return calculate_returns(df, price_column, method)
    
    @staticmethod
    def calculate_cumulative_returns(df, returns_column='Returns'):
        return calculate_cumulative_returns(df, returns_column)
    
    @staticmethod
    def calculate_rolling_returns(df, window=20, returns_column='Returns', annualize=False, trading_days=252):
        return calculate_rolling_returns(df, window, returns_column, annualize, trading_days)
    
    # Risk Metrics
    @staticmethod
    def calculate_volatility(df, window=20, returns_column='Returns', annualize=True, trading_days=252):
        return calculate_volatility(df, window, returns_column, annualize, trading_days)
    
    @staticmethod
    def calculate_drawdown(df, price_column='Close'):
        return calculate_drawdown(df, price_column)
    
    @staticmethod
    def calculate_sharpe_ratio(df, risk_free_rate=0.02, window=252, returns_column='Returns', trading_days=252):
        return calculate_sharpe_ratio(df, risk_free_rate, window, returns_column, trading_days)
    
    @staticmethod
    def calculate_sortino_ratio(df, risk_free_rate=0.02, window=252, returns_column='Returns', trading_days=252):
        return calculate_sortino_ratio(df, risk_free_rate, window, returns_column, trading_days)
    
    @staticmethod
    def calculate_max_drawdown(df, price_column='Close'):
        return calculate_max_drawdown(df, price_column)
    
    @staticmethod
    def calculate_var(df, confidence_level=0.95, returns_column='Returns'):
        return calculate_var(df, confidence_level, returns_column)
    
    # Technical Indicators
    @staticmethod
    def calculate_moving_averages(df, windows=[20, 50, 200], price_column='Close'):
        return calculate_moving_averages(df, windows, price_column)
    
    @staticmethod
    def calculate_ema(df, windows=[12, 26], price_column='Close'):
        return calculate_ema(df, windows, price_column)
    
    @staticmethod
    def calculate_rsi(df, window=14, price_column='Close'):
        return calculate_rsi(df, window, price_column)
    
    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9, price_column='Close'):
        return calculate_macd(df, fast, slow, signal, price_column)
    
    @staticmethod
    def calculate_bollinger_bands(df, window=20, num_std=2.0, price_column='Close'):
        return calculate_bollinger_bands(df, window, num_std, price_column)
    
    @staticmethod
    def calculate_atr(df, window=14):
        return calculate_atr(df, window)
    
    @staticmethod
    def calculate_stochastic(df, k_window=14, d_window=3):
        return calculate_stochastic(df, k_window, d_window)
    
    @staticmethod
    def calculate_technical_indicators(
        df,
        ma_windows=None,
        ema_windows=None,
        rsi_window=None,
        macd_fast=None,
        macd_slow=None,
        macd_signal=None,
        bb_window=None,
        bb_std=None,
        atr_window=None,
        stoch_k_window=None,
        stoch_d_window=None,
        price_column=None
    ):
        """Umbrella function that calculates all technical indicators."""
        return calculate_technical_indicators(
            df,
            ma_windows=ma_windows,
            ema_windows=ema_windows,
            rsi_window=rsi_window,
            macd_fast=macd_fast,
            macd_slow=macd_slow,
            macd_signal=macd_signal,
            bb_window=bb_window,
            bb_std=bb_std,
            atr_window=atr_window,
            stoch_k_window=stoch_k_window,
            stoch_d_window=stoch_d_window,
            price_column=price_column
        )
    
    # Portfolio Metrics
    @staticmethod
    def calculate_wealth_index(df, initial_investment=1000.0, returns_column='Returns'):
        return calculate_wealth_index(df, initial_investment, returns_column)
    
    @staticmethod
    def calculate_correlation(df1, df2, window=30, column='Returns'):
        return calculate_correlation(df1, df2, window, column)
    
    @staticmethod
    def calculate_beta(stock_df, market_df, window=252, returns_column='Returns'):
        return calculate_beta(stock_df, market_df, window, returns_column)
    
    @staticmethod
    def calculate_alpha(stock_df, market_df, risk_free_rate=0.02, window=252, returns_column='Returns', trading_days=252):
        return calculate_alpha(stock_df, market_df, risk_free_rate, window, returns_column, trading_days)
    
    @staticmethod
    def calculate_information_ratio(portfolio_df, benchmark_df, window=252, returns_column='Returns'):
        return calculate_information_ratio(portfolio_df, benchmark_df, window, returns_column)
    
    @staticmethod
    def calculate_treynor_ratio(df, risk_free_rate=0.02, window=252, returns_column='Returns', trading_days=252):
        return calculate_treynor_ratio(df, risk_free_rate, window, returns_column, trading_days)


# Create singleton instance for convenience
data_processor = DataProcessor()


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Main object
    'data_processor',
    'DataProcessor',
    
    # Standardization
    'standardize_dataframe',
    'clean_data',
    'resample_data',
    
    # Returns
    'calculate_returns',
    'calculate_cumulative_returns',
    'calculate_rolling_returns',
    
    # Risk Metrics
    'calculate_volatility',
    'calculate_drawdown',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
    'calculate_max_drawdown',
    'calculate_var',
    
    # Technical Indicators
    'calculate_moving_averages',
    'calculate_ema',
    'calculate_rsi',
    'calculate_macd',
    'calculate_bollinger_bands',
    'calculate_atr',
    'calculate_stochastic',
    'calculate_technical_indicators',  # Umbrella function
    
    # Portfolio Metrics
    'calculate_wealth_index',
    'calculate_correlation',
    'calculate_beta',
    'calculate_alpha',
    'calculate_information_ratio',
    'calculate_treynor_ratio',
]