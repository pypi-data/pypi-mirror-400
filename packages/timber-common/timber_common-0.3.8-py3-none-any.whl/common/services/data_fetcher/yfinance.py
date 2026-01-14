"""
Yahoo Finance data fetcher using yfinance library.
"""
import pandas as pd
import yfinance as yf
from typing import Tuple, Optional
from datetime import datetime

from .base import BaseDataFetcher


class YFinanceDataFetcher(BaseDataFetcher):
    """Fetches stock data from Yahoo Finance."""
    
    def __init__(self):
        # yfinance doesn't need API key
        super().__init__(api_config=None)
    
    def fetch_data(
        self, 
        symbol: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Optional[str]]:
        """
        Fetch historical stock data for a given symbol.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Tuple of (DataFrame, error_message)
        """
        try:
            _start_date = pd.to_datetime(start_date).date() if start_date else None
            _end_date = pd.to_datetime(end_date).date() if end_date else None

            df = yf.download(symbol, start=_start_date, end=_end_date, progress=False, auto_adjust=True)

            if not isinstance(df, pd.DataFrame) or df.empty:
                return pd.DataFrame(), f"No data found for {symbol}"

            # Handle multi-index columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)

            # Reset index if Date is in index
            if 'Date' not in df.columns and df.index.name == 'Date':
                df = df.reset_index()

            # Use adjusted close as Close
            if 'Adj Close' in df.columns:
                df['Close'] = df['Adj Close']

            if 'Close' not in df.columns:
                return pd.DataFrame(), f"Missing 'Close' column for {symbol}"

            # Clean and validate data
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
            df.dropna(subset=['Date', 'Close'], inplace=True)

            # Select expected columns
            expected_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            existing_cols = [col for col in expected_cols if col in df.columns]
            df = df[existing_cols]

            self._log_info(f"Fetched {len(df)} rows for {symbol}")
            return df, None

        except Exception as e:
            error_msg = f"Error fetching data for {symbol}: {e}"
            self._log_error(error_msg, symbol)
            return pd.DataFrame(), error_msg
    
    def fetch_info(self, symbol: str) -> Tuple[dict, Optional[str]]:
        """Fetch company information."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or info.get('symbol') != symbol or len(info) <= 1:
                return {}, f"No info found for {symbol}"
            
            return info, None
            
        except Exception as e:
            error_msg = f"Error fetching info for {symbol}: {e}"
            self._log_error(error_msg, symbol)
            return {}, error_msg
    
    def fetch_news(self, symbol: str, limit: int = 10) -> Tuple[list, Optional[str]]:
        """Fetch recent news articles."""
        try:
            ticker = yf.Ticker(symbol)
            
            # Try new API first, fall back to old
            try:
                news = ticker.get_news(count=limit, tab='all')
            except:
                news = ticker.news
            
            if not news:
                return [], f"No news found for {symbol}"
            
            return news[:limit], None
            
        except Exception as e:
            error_msg = f"Error fetching news for {symbol}: {e}"
            self._log_error(error_msg, symbol)
            return [], error_msg
    
    def fetch_financials(
        self, 
        symbol: str, 
        period: str = "yearly"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Optional[str]]:
        """
        Fetch financial statements.
        
        Args:
            symbol: Stock ticker symbol
            period: 'yearly' or 'quarterly'
            
        Returns:
            Tuple of (income_stmt, balance_sheet, cash_flow, error_message)
        """
        try:
            ticker = yf.Ticker(symbol)
            
            if period == "yearly":
                income_stmt = ticker.financials
                balance_sheet = ticker.balance_sheet
                cash_flow = ticker.cashflow
            elif period == "quarterly":
                income_stmt = ticker.quarterly_financials
                balance_sheet = ticker.quarterly_balance_sheet
                cash_flow = ticker.quarterly_cashflow
            else:
                return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                       "Invalid period. Use 'yearly' or 'quarterly'")

            if income_stmt.empty and balance_sheet.empty and cash_flow.empty:
                return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                       f"No financial data available for {symbol}")

            return income_stmt, balance_sheet, cash_flow, None
            
        except Exception as e:
            error_msg = f"Error fetching financials for {symbol}: {e}"
            self._log_error(error_msg, symbol)
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), error_msg