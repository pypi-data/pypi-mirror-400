"""
Stock data orchestration layer.
Intelligently routes requests to the appropriate data source based on configuration.
"""
import pandas as pd
from typing import Tuple, Optional, List
from datetime import datetime
import logging

from .yfinance import YFinanceDataFetcher
from .alphavantage import AlphaVantageDataFetcher
from .polygon import PolygonDataFetcher
from common.utils.config import config
from common.utils.helpers import parse_natural_period_to_dates, standardize_symbol

logger = logging.getLogger(__name__)


class StockDataService:
    """
    Unified interface for fetching stock data from multiple sources.
    Handles fallback logic and source prioritization.
    """
    
    def __init__(self):
        # Initialize fetchers
        self.yfinance = YFinanceDataFetcher()
        self.alphavantage = AlphaVantageDataFetcher()
        self.polygon = PolygonDataFetcher()
        
        # Determine primary and fallback sources based on API key availability
        api_keys = config.validate_api_keys()
        
        if api_keys['polygon']:
            # If Polygon is configured, use it as primary
            self.primary_source = self.polygon
            self.fallback_source = self.yfinance
            self.primary_name = 'polygon'
            self.fallback_name = 'yfinance'
            logger.info("Using Polygon.io as primary data source with yfinance fallback")
        else:
            # Otherwise use yfinance (free, no key required)
            self.primary_source = self.yfinance
            self.fallback_source = self.polygon if api_keys['polygon'] else self.alphavantage
            self.primary_name = 'yfinance'
            self.fallback_name = 'polygon' if api_keys['polygon'] else 'alphavantage'
            logger.info(f"Using yfinance as primary data source with {self.fallback_name} fallback")
    
    def fetch_historical_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Optional[str]]:
        """
        Fetch historical stock data with automatic fallback.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            period: Period string (e.g., '1y', '6mo', 'ytd')
            
        Returns:
            Tuple of (DataFrame, error_message)
        """
        symbol = standardize_symbol(symbol)
        
        # If period is provided, convert to dates
        if period:
            start_date, end_date = parse_natural_period_to_dates(period)
        
        # Try primary source
        try:
            df, error = self.primary_source.fetch_data(symbol, start_date, end_date)
            if not df.empty:
                print(f"✓ Fetched data for {symbol} from {self.primary_name}")
                return df, None
            if error:
                raise Exception(error)
        except Exception as e:
            print(f"⚠ Primary source ({self.primary_name}) failed for {symbol}: {e}")
        
        # Try fallback source
        try:
            df, error = self.fallback_source.fetch_data(symbol, start_date, end_date)
            if not df.empty:
                print(f"✓ Fetched data for {symbol} from {self.fallback_name} (fallback)")
                return df, None
            if error:
                raise Exception(error)
        except Exception as e:
            print(f"✗ Fallback source ({self.fallback_name}) failed for {symbol}: {e}")
        
        return pd.DataFrame(), f"Failed to fetch data for {symbol} from all sources"
    
    def fetch_company_info(self, symbol: str) -> Tuple[dict, Optional[str]]:
        """
        Fetch company information with automatic fallback.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Tuple of (info_dict, error_message)
        """
        symbol = standardize_symbol(symbol)
        
        # Try primary source
        try:
            info, error = self.primary_source.fetch_info(symbol)
            if info:
                print(f"✓ Fetched info for {symbol} from {self.primary_name}")
                return self._standardize_info(info, self.primary_name), None
            if error:
                raise Exception(error)
        except Exception as e:
            print(f"⚠ Primary source ({self.primary_name}) failed for {symbol}: {e}")
        
        # Try fallback source
        try:
            info, error = self.fallback_source.fetch_info(symbol)
            if info:
                print(f"✓ Fetched info for {symbol} from {self.fallback_name} (fallback)")
                return self._standardize_info(info, self.fallback_name), None
            if error:
                raise Exception(error)
        except Exception as e:
            print(f"✗ Fallback source ({self.fallback_name}) failed for {symbol}: {e}")
        
        return {}, f"Failed to fetch info for {symbol} from all sources"
    
    def fetch_news(self, symbol: str, limit: int = 10) -> Tuple[List[dict], Optional[str]]:
        """
        Fetch recent news with automatic fallback.
        
        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of articles
            
        Returns:
            Tuple of (news_list, error_message)
        """
        symbol = standardize_symbol(symbol)
        
        # Try primary source
        try:
            news, error = self.primary_source.fetch_news(symbol, limit)
            if news:
                print(f"✓ Fetched news for {symbol} from {self.primary_name}")
                return self._standardize_news(news, self.primary_name), None
            if error:
                raise Exception(error)
        except Exception as e:
            print(f"⚠ Primary source ({self.primary_name}) failed for {symbol}: {e}")
        
        # Try fallback source
        try:
            news, error = self.fallback_source.fetch_news(symbol, limit)
            if news:
                print(f"✓ Fetched news for {symbol} from {self.fallback_name} (fallback)")
                return self._standardize_news(news, self.fallback_name), None
            if error:
                raise Exception(error)
        except Exception as e:
            print(f"✗ Fallback source ({self.fallback_name}) failed for {symbol}: {e}")
        
        return [], f"Failed to fetch news for {symbol} from all sources"
    
    def fetch_financials(
        self,
        symbol: str,
        period: str = "yearly"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Optional[str]]:
        """
        Fetch financial statements with automatic fallback.
        
        Args:
            symbol: Stock ticker symbol
            period: 'yearly' or 'quarterly'
            
        Returns:
            Tuple of (income_stmt, balance_sheet, cash_flow, error_message)
        """
        symbol = standardize_symbol(symbol)
        
        # Try primary source
        try:
            income, balance, cashflow, error = self.primary_source.fetch_financials(symbol, period)
            if not (income.empty and balance.empty and cashflow.empty):
                print(f"✓ Fetched financials for {symbol} from {self.primary_name}")
                return income, balance, cashflow, None
            if error:
                raise Exception(error)
        except Exception as e:
            print(f"⚠ Primary source ({self.primary_name}) failed for {symbol}: {e}")
        
        # Try fallback source
        try:
            income, balance, cashflow, error = self.fallback_source.fetch_financials(symbol, period)
            if not (income.empty and balance.empty and cashflow.empty):
                print(f"✓ Fetched financials for {symbol} from {self.fallback_name} (fallback)")
                return income, balance, cashflow, None
            if error:
                raise Exception(error)
        except Exception as e:
            print(f"✗ Fallback source ({self.fallback_name}) failed for {symbol}: {e}")
        
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
               f"Failed to fetch financials for {symbol} from all sources")
    
    # Standardization helpers
    def _standardize_info(self, info: dict, source: str) -> dict:
        """Standardize company info format across sources."""
        if source == 'polygon':
            # Polygon format is different, map it to yfinance-like format
            return {
                'symbol': info.get('symbol'),
                'longName': info.get('longName'),
                'longBusinessSummary': info.get('longBusinessSummary'),
                'website': info.get('website'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'city': info.get('city'),
                'state': info.get('state'),
                'country': info.get('country'),
                'phone': info.get('phone'),
                'marketCap': info.get('marketCapitalization'),
                'peRatio': info.get('peRatio'),
            }
        return info
    
    def _standardize_news(self, news: list, source: str) -> List[dict]:
        """Standardize news format across sources."""
        standardized = []
        
        for item in news:
            if source == 'yfinance':
                standardized_item = {
                    'id': item.get('uuid'),
                    'title': item.get('title'),
                    'summary': item.get('summary'),
                    'publisher': item.get('publisher'),
                    'published_utc': datetime.fromtimestamp(
                        item.get('providerPublishTime', 0)
                    ).isoformat() if item.get('providerPublishTime') else None,
                    'article_url': item.get('link'),
                }
            elif source == 'polygon':
                standardized_item = {
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'summary': item.get('description'),
                    'publisher': item.get('publisher', {}).get('name'),
                    'published_utc': item.get('published_utc'),
                    'article_url': item.get('article_url'),
                }
            else:
                continue
            
            standardized.append(standardized_item)
        
        return standardized


# Create a singleton instance for easy access
stock_data_service = StockDataService()