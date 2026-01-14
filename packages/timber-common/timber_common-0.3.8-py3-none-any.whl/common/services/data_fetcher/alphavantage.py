"""
Alpha Vantage data fetcher.
"""
import pandas as pd
from typing import Tuple, Optional
from datetime import datetime

from .base import BaseDataFetcher
from common.utils.config import config


class AlphaVantageDataFetcher(BaseDataFetcher):
    """Fetches stock data from Alpha Vantage API."""
    
    def __init__(self):
        super().__init__(api_config=config.get_alpha_vantage_config())
    
    def _make_av_request(self, params: dict) -> Tuple[Optional[dict], Optional[str]]:
        """Make request to Alpha Vantage API with API key."""
        is_valid, error = self._check_api_key()
        if not is_valid:
            return None, error
        
        params["apikey"] = self.api_key
        data, error = self._make_request(self.base_url, params=params)
        
        if error:
            return None, error
        
        # Check for Alpha Vantage specific errors
        if "Error Message" in data:
            return None, f"Alpha Vantage error: {data['Error Message']}"
        if "Note" in data:
            self._log_info(f"Rate limit note: {data['Note']}")
            return None, f"Rate limit: {data['Note']}"
        
        return data, None
    
    def fetch_data(
        self, 
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Optional[str]]:
        """Fetch historical daily data."""
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full"
        }
        
        data, error = self._make_av_request(params)
        if error:
            return pd.DataFrame(), error
        
        if "Time Series (Daily)" not in data:
            return pd.DataFrame(), f"No time series data for {symbol}"
        
        time_series = data["Time Series (Daily)"]
        df_data = []
        
        for date_str, values in time_series.items():
            try:
                current_date = pd.to_datetime(date_str)
                
                # Filter by date range if provided
                if start_date and current_date < pd.to_datetime(start_date):
                    continue
                if end_date and current_date > pd.to_datetime(end_date):
                    continue
                
                df_data.append({
                    "Date": current_date,
                    "Open": float(values.get("1. open")),
                    "High": float(values.get("2. high")),
                    "Low": float(values.get("3. low")),
                    "Close": float(values.get("4. close")),
                    "Adj Close": float(values.get("5. adjusted close")),
                    "Volume": int(values.get("6. volume")),
                    "Dividends": float(values.get("7. dividend amount", 0.0)),
                    "Stock Splits": float(values.get("8. split coefficient", 1.0))
                })
            except (ValueError, KeyError) as e:
                self._log_error(f"Error parsing data for {date_str}: {e}", symbol)
                continue
        
        if not df_data:
            return pd.DataFrame(), f"No data in date range for {symbol}"
        
        df = pd.DataFrame(df_data).sort_values('Date').reset_index(drop=True)
        
        # Use adjusted close as primary close
        if 'Adj Close' in df.columns:
            df['Close'] = df['Adj Close']
        
        # Clean stock splits (1.0 means no split)
        df['Stock Splits'] = df['Stock Splits'].apply(lambda x: x if x != 1.0 else 0.0)
        
        self._log_info(f"Fetched {len(df)} rows for {symbol}")
        return df, None
    
    def fetch_info(self, symbol: str) -> Tuple[dict, Optional[str]]:
        """Fetch company overview information."""
        params = {
            "function": "OVERVIEW",
            "symbol": symbol
        }
        
        data, error = self._make_av_request(params)
        if error:
            return {}, error
        
        if not data or len(data) <= 1:
            return {}, f"No info found for {symbol}"
        
        # Map to standardized format
        info = {
            "symbol": data.get("Symbol"),
            "assetType": data.get("AssetType"),
            "name": data.get("Name"),
            "description": data.get("Description"),
            "exchange": data.get("Exchange"),
            "currency": data.get("Currency"),
            "country": data.get("Country"),
            "sector": data.get("Sector"),
            "industry": data.get("Industry"),
            "address": data.get("Address"),
            "fullTimeEmployees": data.get("FullTimeEmployees"),
            "marketCapitalization": float(data.get("MarketCapitalization", 0)),
            "peRatio": float(data.get("PERatio", 0)),
            "beta": float(data.get("Beta", 0)),
            "dividendYield": float(data.get("DividendYield", 0)),
            "52WeekHigh": float(data.get("52WeekHigh", 0)),
            "52WeekLow": float(data.get("52WeekLow", 0)),
        }
        
        return info, None
    
    def fetch_financials(
        self, 
        symbol: str, 
        period: str = "yearly"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Optional[str]]:
        """Fetch financial statements."""
        statements = {
            "income": {"function": "INCOME_STATEMENT"},
            "balance": {"function": "BALANCE_SHEET"},
            "cashflow": {"function": "CASH_FLOW"}
        }
        
        results = {}
        for stmt_type, params in statements.items():
            params["symbol"] = symbol
            data, error = self._make_av_request(params)
            
            if error:
                self._log_error(f"Error fetching {stmt_type}: {error}", symbol)
                results[stmt_type] = pd.DataFrame()
                continue
            
            # Get the appropriate report type
            report_key = "annualReports" if period == "yearly" else "quarterlyReports"
            
            if data and report_key in data:
                df = pd.DataFrame(data[report_key])
                
                # Standardize date column
                if 'fiscalDateEnding' in df.columns:
                    df['Date'] = pd.to_datetime(df['fiscalDateEnding'])
                    df.set_index('Date', inplace=True)
                    df.drop(columns=['fiscalDateEnding'], errors='ignore', inplace=True)
                
                # Convert numeric columns
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df.sort_index(inplace=True)
                results[stmt_type] = df
            else:
                results[stmt_type] = pd.DataFrame()
        
        income_stmt = results.get("income", pd.DataFrame())
        balance_sheet = results.get("balance", pd.DataFrame())
        cash_flow = results.get("cashflow", pd.DataFrame())
        
        if income_stmt.empty and balance_sheet.empty and cash_flow.empty:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                   f"No financial data for {symbol}")
        
        return income_stmt, balance_sheet, cash_flow, None