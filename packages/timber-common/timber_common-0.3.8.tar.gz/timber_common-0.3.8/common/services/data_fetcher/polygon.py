"""
Polygon.io data fetcher.

Note: Uses the /vX/reference/financials endpoint which is marked as deprecated
but still accessible with current subscription level. The newer separate endpoints
(/stocks/financials/v1/balance-sheets, income-statements, cash-flow-statements)
require advanced subscription tiers.
"""
import pandas as pd
from typing import Tuple, Optional, Any
from datetime import datetime

from .base import BaseDataFetcher
from common.utils.config import config


class PolygonDataFetcher(BaseDataFetcher):
    """Fetches stock data from Polygon.io API."""
    
    def __init__(self):
        super().__init__(api_config=config.get_polygon_config())
    
    def _make_polygon_request(
        self, 
        endpoint: str, 
        params: Optional[dict] = None
    ) -> Tuple[Optional[dict], Optional[str]]:
        """Make request to Polygon API with API key."""
        is_valid, error = self._check_api_key()
        if not is_valid:
            return None, error
        
        if params is None:
            params = {}
        params['apiKey'] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        data, error = self._make_request(url, params=params)
        
        if error:
            return None, error
        
        # Check for Polygon specific errors
        if data.get("status") == "ERROR" or "error" in data:
            return None, f"Polygon error: {data.get('error', data.get('status'))}"
        
        if data.get("resultsCount", 0) == 0 and not data.get("results"):
            return None, "No data found"
        
        return data, None
    
    def fetch_data(
        self, 
        symbol: str,
        start_date: str,
        end_date: str
    ) -> Tuple[pd.DataFrame, Optional[str]]:
        """Fetch historical aggregates (bars) data."""
        endpoint = f"/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
        params = {"adjusted": "true", "sort": "asc"}
        
        data, error = self._make_polygon_request(endpoint, params)
        if error or not data or not data.get("results"):
            return pd.DataFrame(), error or f"No data for {symbol}"
        
        df = pd.DataFrame(data["results"])
        
        # Rename columns to standard format
        df.rename(columns={
            't': 'Date',
            'o': 'Open',
            'h': 'High',
            'l': 'Low',
            'c': 'Close',
            'v': 'Volume',
            'vw': 'vwap',
            'n': 'number_of_transactions'
        }, inplace=True)
        
        # Convert timestamp to datetime
        try:
            df['Date'] = pd.to_datetime(df['Date'], unit='ms', errors='coerce')
        except TypeError:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        df.dropna(subset=['Date'], inplace=True)
        df.set_index('Date', inplace=True)
        
        # Add missing columns for consistency
        df['Dividends'] = 0.0
        df['Stock Splits'] = 0.0
        df['Adj Close'] = df['Close']
        
        # Select standard columns
        expected_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Dividends', 'Stock Splits']
        existing_cols = [col for col in expected_cols if col in df.columns]
        
        df = df[existing_cols].reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        
        self._log_info(f"Fetched {len(df)} rows for {symbol}")
        return df, None
    
    def fetch_info(self, symbol: str) -> Tuple[dict, Optional[str]]:
        """Fetch ticker details and financials."""
        # Get basic ticker info
        endpoint = f"/v3/reference/tickers/{symbol}"
        ticker_data, error = self._make_polygon_request(endpoint, params={})
        
        if error or not ticker_data or not ticker_data.get("results"):
            return {}, error or "Ticker info not found"
        
        basic_info = ticker_data["results"]
        
        # Get financial data using the vX endpoint
        financials_endpoint = "/vX/reference/financials"
        financials_params = {
            "ticker": symbol,
            "limit": 1,
            "order": "desc",
            "sort": "filing_date"
        }
        financials_data, fin_error = self._make_polygon_request(financials_endpoint, financials_params)
        
        financials_results = {}
        if not fin_error and financials_data and "results" in financials_data:
            if len(financials_data["results"]) > 0:
                financials_results = financials_data["results"][0].get("financials", {})
        
        # Extract metrics
        market_cap = self._extract_metric(financials_results.get("balance_sheet", {}), "market_capitalization")
        net_income = self._extract_metric(financials_results.get("income_statement", {}), "net_income_loss")
        
        # Fallback to ticker details for market cap if not in financials
        if not market_cap:
            market_cap = basic_info.get("market_cap")
        
        pe_ratio = self._calculate_pe_ratio(market_cap, net_income)
        
        # Build standardized info dict
        info = {
            "symbol": symbol,
            "longName": basic_info.get("name"),
            "longBusinessSummary": basic_info.get("description"),
            "website": basic_info.get("homepage_url"),
            "sector": basic_info.get("sic_description"),
            "industry": basic_info.get("sic_description"),
            "address1": basic_info.get("address", {}).get("address1"),
            "city": basic_info.get("address", {}).get("city"),
            "state": basic_info.get("address", {}).get("state"),
            "zip": basic_info.get("address", {}).get("postal_code"),
            "country": basic_info.get("address", {}).get("country"),
            "phone": basic_info.get("phone_number"),
            "marketCapitalization": market_cap,
            "peRatio": pe_ratio,
        }
        
        return info, None
    
    def fetch_news(self, symbol: str, limit: int = 10) -> Tuple[list, Optional[str]]:
        """Fetch recent news articles."""
        endpoint = "/v2/reference/news"
        params = {
            "ticker": symbol,
            "limit": limit,
            "sort": "published_utc"
        }
        
        data, error = self._make_polygon_request(endpoint, params)
        if error or not data or not data.get("results"):
            return [], error or f"No news for {symbol}"
        
        return data["results"], None
    
    def fetch_financials(
        self, 
        symbol: str, 
        period: str = "annual"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Optional[str]]:
        """Fetch financial statements using vX/reference/financials endpoint."""
        endpoint = "/vX/reference/financials"
        
        # The endpoint uses 'order' and 'sort' instead of 'timeframe'
        # Note: This endpoint returns all periods, we'll filter by timeframe in processing
        params = {
            "ticker": symbol,
            "order": "desc",
            "sort": "filing_date",
            "limit": 100
        }
        
        data, error = self._make_polygon_request(endpoint, params)
        if error or not data or not data.get("results"):
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                   error or f"No financials for {symbol}")
        
        statements = data.get("results", [])
        
        # Filter by timeframe if specified
        if period == "annual":
            statements = [s for s in statements if s.get("timeframe") == "annual"]
        elif period == "quarterly":
            statements = [s for s in statements if s.get("timeframe") == "quarterly"]
        
        income_list, balance_list, cashflow_list = [], [], []
        
        for statement in statements:
            financials = statement.get("financials", {})
            if "income_statement" in financials:
                income_list.append(financials["income_statement"])
            if "balance_sheet" in financials:
                balance_list.append(financials["balance_sheet"])
            if "cash_flow_statement" in financials:
                cashflow_list.append(financials["cash_flow_statement"])
        
        # Convert to DataFrames
        income_stmt = self._process_financial_df(pd.DataFrame(income_list))
        balance_sheet = self._process_financial_df(pd.DataFrame(balance_list))
        cash_flow = self._process_financial_df(pd.DataFrame(cashflow_list))
        
        if income_stmt.empty and balance_sheet.empty and cash_flow.empty:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                   f"No financial data for {symbol}")
        
        return income_stmt, balance_sheet, cash_flow, None
    
    def fetch_daily_summary(self, symbol: str, date: datetime) -> Tuple[dict, Optional[str]]:
        """Fetch daily open/close summary for a specific date."""
        date_str = date.strftime('%Y-%m-%d')
        endpoint = f"/v1/open-close/{symbol}/{date_str}"
        params = {"adjusted": "true"}
        
        data, error = self._make_polygon_request(endpoint, params)
        if error or not data:
            return {}, error or f"No summary for {symbol} on {date_str}"
        
        return data, None
    
    # Helper methods
    def _extract_metric(self, data: dict, key: str) -> Any:
        """Extract value from nested financial dict."""
        try:
            return data.get(key, {}).get("value")
        except:
            return None
    
    def _calculate_pe_ratio(self, market_cap: float, net_income: float) -> Optional[float]:
        """Calculate P/E ratio."""
        if not market_cap or not net_income or net_income == 0:
            return None
        try:
            return market_cap / net_income
        except:
            return None
    
    def _process_financial_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize financial DataFrame."""
        if df.empty:
            return df
        
        # The data comes as nested dicts with 'value', 'label', 'unit' keys
        # We need to extract just the values and clean up column names
        processed_data = {}
        
        for col in df.columns:
            try:
                # Extract values from the nested structure
                if df[col].dtype == 'object':
                    # Check if this column contains dicts with 'value' key
                    first_valid = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
                    if isinstance(first_valid, dict) and 'value' in first_valid:
                        processed_data[col] = df[col].apply(lambda x: x.get('value') if isinstance(x, dict) else x)
                    else:
                        processed_data[col] = df[col]
                else:
                    processed_data[col] = df[col]
            except:
                processed_data[col] = df[col]
        
        df = pd.DataFrame(processed_data)
        
        # Clean column names
        df.columns = [col.replace("_", " ").title() for col in df.columns]
        
        return df