"""
Technical Indicators Module

Handles calculation of technical indicators like moving averages, RSI, Bollinger Bands, etc.
Robustly handles various input formats (DataFrame, JSON, Dict, List).
"""

import pandas as pd
import numpy as np
import json
import logging
from typing import Tuple, Optional, List, Any, Union

# Attempt to import Timber serialization helper, handle gracefully if missing
try:
    from common.utils.serialization_helpers import deserialize_dataframe
except ImportError:
    deserialize_dataframe = None

logger = logging.getLogger(__name__)

def _ensure_dataframe(data: Any) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Internal helper to normalize input into a pandas DataFrame.
    
    Handles:
    - Existing DataFrame (returns copy)
    - JSON String
    - List of Dictionaries
    - Timber Serialized Dict ({'type': 'dataframe', 'data': ...})
    
    Returns:
        Tuple (DataFrame, Error Message)
    """
    if data is None:
        return None, "Input data is None"

    # 1. Already a DataFrame
    if isinstance(data, pd.DataFrame):
        return data.copy(), None

    try:
        # 2. Handle JSON String (common in API/Celery payloads)
        if isinstance(data, str):
            # Clean string if necessary
            data = data.strip()
            try:
                # Try parsing as JSON first
                parsed_data = json.loads(data)
                # Recursively check the parsed result
                return _ensure_dataframe(parsed_data)
            except json.JSONDecodeError:
                return None, "Input string is not valid JSON"

        # 3. Handle Timber Serialization Format
        if isinstance(data, dict) and data.get('type') == 'dataframe':
            if deserialize_dataframe:
                try:
                    return deserialize_dataframe(data), None
                except Exception as e:
                    return None, f"Failed to deserialize Timber format: {str(e)}"
            else:
                # Fallback if helper not imported: treat 'data' key as records
                if 'data' in data:
                    return _ensure_dataframe(data['data'])

        # 4. Handle List of Dicts or Dict of Lists
        if isinstance(data, (list, dict)):
            df = pd.DataFrame(data)
            
            # Basic Date Parsing Attempt
            # If 'Date' or 'date' exists, ensure it's datetime objects
            for col in df.columns:
                if col.lower() == 'date':
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except:
                        pass # Keep as is if parsing fails
            return df, None

        return None, f"Unsupported input type: {type(data)}"

    except Exception as e:
        return None, f"Data conversion error: {str(e)}"


def calculate_moving_averages(
    df: Union[pd.DataFrame, List[dict], str],
    windows: List[int] = [20, 50, 200],
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates simple moving averages for specified windows.
    """
    # Normalize Input
    df_clean, error = _ensure_dataframe(df)
    if error:
        return (df if isinstance(df, pd.DataFrame) else pd.DataFrame()), error

    try:
        if price_column not in df_clean.columns:
            return df_clean, f"Column '{price_column}' not found in DataFrame"
        
        for window in windows:
            # Ensure window is valid int
            try:
                win_int = int(window)
                df_clean[f'MA_{win_int}'] = df_clean[price_column].rolling(window=win_int).mean()
            except ValueError:
                continue
        
        return df_clean, None
        
    except Exception as e:
        return df_clean, f"Error calculating moving averages: {str(e)}"


def calculate_ema(
    df: Union[pd.DataFrame, List[dict], str],
    windows: List[int] = [12, 26],
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates exponential moving averages.
    """
    df_clean, error = _ensure_dataframe(df)
    if error:
        return (df if isinstance(df, pd.DataFrame) else pd.DataFrame()), error

    try:
        if price_column not in df_clean.columns:
            return df_clean, f"Column '{price_column}' not found in DataFrame"
        
        for window in windows:
            try:
                win_int = int(window)
                df_clean[f'EMA_{win_int}'] = df_clean[price_column].ewm(span=win_int, adjust=False).mean()
            except ValueError:
                continue
        
        return df_clean, None
        
    except Exception as e:
        return df_clean, f"Error calculating EMA: {str(e)}"


def calculate_rsi(
    df: Union[pd.DataFrame, List[dict], str],
    window: int = 14,
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Relative Strength Index (RSI).
    """
    df_clean, error = _ensure_dataframe(df)
    if error:
        return (df if isinstance(df, pd.DataFrame) else pd.DataFrame()), error

    try:
        if price_column not in df_clean.columns:
            return df_clean, f"Column '{price_column}' not found in DataFrame"
        
        window = int(window)
        
        # Calculate price changes
        delta = df_clean[price_column].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate rolling average of gains and losses
        avg_gains = gains.rolling(window=window).mean()
        avg_losses = losses.rolling(window=window).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        df_clean['RSI'] = 100 - (100 / (1 + rs))
        
        return df_clean, None
        
    except Exception as e:
        return df_clean, f"Error calculating RSI: {str(e)}"


def calculate_macd(
    df: Union[pd.DataFrame, List[dict], str],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates MACD (Moving Average Convergence Divergence).
    """
    df_clean, error = _ensure_dataframe(df)
    if error:
        return (df if isinstance(df, pd.DataFrame) else pd.DataFrame()), error

    try:
        if price_column not in df_clean.columns:
            return df_clean, f"Column '{price_column}' not found in DataFrame"
        
        fast, slow, signal = int(fast), int(slow), int(signal)

        # Calculate EMAs
        ema_fast = df_clean[price_column].ewm(span=fast, adjust=False).mean()
        ema_slow = df_clean[price_column].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD line
        df_clean['MACD'] = ema_fast - ema_slow
        
        # Calculate signal line
        df_clean['MACD_Signal'] = df_clean['MACD'].ewm(span=signal, adjust=False).mean()
        
        # Calculate histogram
        df_clean['MACD_Histogram'] = df_clean['MACD'] - df_clean['MACD_Signal']
        
        return df_clean, None
        
    except Exception as e:
        return df_clean, f"Error calculating MACD: {str(e)}"


def calculate_bollinger_bands(
    df: Union[pd.DataFrame, List[dict], str],
    window: int = 20,
    num_std: float = 2.0,
    price_column: str = 'Close'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Bollinger Bands.
    """
    df_clean, error = _ensure_dataframe(df)
    if error:
        return (df if isinstance(df, pd.DataFrame) else pd.DataFrame()), error

    try:
        if price_column not in df_clean.columns:
            return df_clean, f"Column '{price_column}' not found in DataFrame"
        
        window = int(window)
        num_std = float(num_std)

        # Calculate middle band (moving average)
        df_clean['BB_Middle'] = df_clean[price_column].rolling(window=window).mean()
        
        # Calculate standard deviation
        rolling_std = df_clean[price_column].rolling(window=window).std()
        
        # Calculate upper and lower bands
        df_clean['BB_Upper'] = df_clean['BB_Middle'] + (rolling_std * num_std)
        df_clean['BB_Lower'] = df_clean['BB_Middle'] - (rolling_std * num_std)
        
        # Calculate bandwidth
        df_clean['BB_Width'] = (df_clean['BB_Upper'] - df_clean['BB_Lower']) / df_clean['BB_Middle']
        
        return df_clean, None
        
    except Exception as e:
        return df_clean, f"Error calculating Bollinger Bands: {str(e)}"


def calculate_atr(
    df: Union[pd.DataFrame, List[dict], str],
    window: int = 14
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Average True Range (ATR).
    """
    df_clean, error = _ensure_dataframe(df)
    if error:
        return (df if isinstance(df, pd.DataFrame) else pd.DataFrame()), error

    try:
        required_cols = ['High', 'Low', 'Close']
        # Convert column names to title case to handle 'close' vs 'Close'
        df_cols_map = {c.title(): c for c in df_clean.columns}
        
        missing = [c for c in required_cols if c not in df_cols_map]
        if missing:
            return df_clean, f"DataFrame must have {missing} columns (case-insensitive)"
        
        # Use actual column names found
        high_col = df_cols_map['High']
        low_col = df_cols_map['Low']
        close_col = df_cols_map['Close']

        window = int(window)

        # Calculate True Range
        high_low = df_clean[high_col] - df_clean[low_col]
        high_close = abs(df_clean[high_col] - df_clean[close_col].shift())
        low_close = abs(df_clean[low_col] - df_clean[close_col].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # Calculate ATR
        df_clean['ATR'] = true_range.rolling(window=window).mean()
        
        return df_clean, None
        
    except Exception as e:
        return df_clean, f"Error calculating ATR: {str(e)}"


def calculate_stochastic(
    df: Union[pd.DataFrame, List[dict], str],
    k_window: int = 14,
    d_window: int = 3
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Calculates Stochastic Oscillator.
    """
    df_clean, error = _ensure_dataframe(df)
    if error:
        return (df if isinstance(df, pd.DataFrame) else pd.DataFrame()), error

    try:
        required_cols = ['High', 'Low', 'Close']
        # Convert column names to title case to handle 'close' vs 'Close'
        df_cols_map = {c.title(): c for c in df_clean.columns}
        
        missing = [c for c in required_cols if c not in df_cols_map]
        if missing:
            return df_clean, f"DataFrame must have {missing} columns"
            
        high_col = df_cols_map['High']
        low_col = df_cols_map['Low']
        close_col = df_cols_map['Close']

        k_window = int(k_window)
        d_window = int(d_window)

        # Calculate %K
        low_min = df_clean[low_col].rolling(window=k_window).min()
        high_max = df_clean[high_col].rolling(window=k_window).max()
        
        # Avoid division by zero
        denom = high_max - low_min
        denom = denom.replace(0, np.nan)
        
        df_clean['Stochastic_K'] = 100 * (df_clean[close_col] - low_min) / denom
        
        # Calculate %D (moving average of %K)
        df_clean['Stochastic_D'] = df_clean['Stochastic_K'].rolling(window=d_window).mean()
        
        return df_clean, None
        
    except Exception as e:
        return df_clean, f"Error calculating Stochastic: {str(e)}"