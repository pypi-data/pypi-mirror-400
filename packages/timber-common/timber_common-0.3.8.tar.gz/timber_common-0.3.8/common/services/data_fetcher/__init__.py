"""
Data fetcher services for external APIs.

This module provides a unified interface for fetching stock market data
from multiple sources (yfinance, Alpha Vantage, Polygon.io) with automatic
fallback and source prioritization based on environment configuration.

Usage:
    from timber_common.services.data_fetcher import stock_data_service, curated_data_loader
    
    # Fetch historical data
    df, error = stock_data_service.fetch_historical_data('AAPL', period='1y')
    
    # Get company info
    info, error = stock_data_service.fetch_company_info('AAPL')
    
    # Load curated companies
    companies, error = curated_data_loader.get_companies_by_sector('S&P 500', 'Technology')
"""

# Base classes
from .base import BaseDataFetcher

# Individual fetchers
from .yfinance import YFinanceDataFetcher
from .alphavantage import AlphaVantageDataFetcher
from .polygon import PolygonDataFetcher

# High-level services (singletons)
from .stock import StockDataService, stock_data_service
from .curated_data import CuratedDataLoader, curated_data_loader

__all__ = [
    # Base class
    'BaseDataFetcher',
    
    # Individual fetchers
    'YFinanceDataFetcher',
    'AlphaVantageDataFetcher',
    'PolygonDataFetcher',
    
    # Service classes
    'StockDataService',
    'CuratedDataLoader',
    
    # Singleton instances (recommended for most use cases)
    'stock_data_service',
    'curated_data_loader',
]