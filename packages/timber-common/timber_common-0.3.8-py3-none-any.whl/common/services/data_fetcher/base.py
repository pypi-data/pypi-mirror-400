"""
Base class for all data fetchers with common functionality.
"""
import requests
from typing import Any, Optional, Tuple, Dict
from abc import ABC, abstractmethod
import logging

from common.utils.config import config

logger = logging.getLogger(__name__)


class BaseDataFetcher(ABC):
    """Abstract base class for all data fetchers."""
    
    def __init__(self, api_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data fetcher with configuration.
        
        Args:
            api_config: Dictionary containing api_key, base_url, and timeout
        """
        if api_config:
            self.api_key = api_config.get('api_key')
            self.base_url = api_config.get('base_url')
            self.timeout = api_config.get('timeout', config.API_REQUEST_TIMEOUT)
        else:
            self.api_key = None
            self.base_url = None
            self.timeout = config.API_REQUEST_TIMEOUT
        
        self.max_retries = config.MAX_RETRIES
    
    def _check_api_key(self) -> Tuple[bool, Optional[str]]:
        """Check if API key is configured."""
        if not self.api_key or 'use_env' in str(self.api_key):
            return False, f"{self.__class__.__name__} API key is not configured."
        return True, None
    
    def _make_request(
        self, 
        url: str, 
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        method: str = "GET"
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        Generic request handler with error handling and retries.
        
        Args:
            url: Request URL
            params: Query parameters or JSON body
            headers: HTTP headers
            method: HTTP method (GET or POST)
            
        Returns:
            Tuple of (data, error_message)
        """
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    response = requests.get(
                        url, 
                        params=params, 
                        headers=headers, 
                        timeout=self.timeout
                    )
                elif method.upper() == "POST":
                    response = requests.post(
                        url, 
                        json=params, 
                        headers=headers, 
                        timeout=self.timeout
                    )
                else:
                    return None, f"Unsupported HTTP method: {method}"
                
                response.raise_for_status()
                
                # Try to parse as JSON
                try:
                    data = response.json()
                    return data, None
                except ValueError:
                    return {"text": response.text}, None
                    
            except requests.exceptions.Timeout:
                error_msg = f"Request timed out after {self.timeout} seconds"
                if attempt < self.max_retries - 1:
                    logger.warning(f"{error_msg}, retrying... (attempt {attempt + 1}/{self.max_retries})")
                    continue
                return None, error_msg
                
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: {e}"
                if attempt < self.max_retries - 1:
                    logger.warning(f"{error_msg}, retrying... (attempt {attempt + 1}/{self.max_retries})")
                    continue
                return None, error_msg
                
            except requests.exceptions.HTTPError as e:
                return None, f"HTTP error: {e}"
                
            except requests.exceptions.RequestException as e:
                return None, f"Request error: {e}"
                
            except Exception as e:
                return None, f"Unexpected error: {e}"
        
        return None, f"Failed after {self.max_retries} attempts"
    
    @abstractmethod
    def fetch_data(self, symbol: str, **kwargs) -> Tuple[Any, Optional[str]]:
        """Fetch data for a given symbol. Must be implemented by subclasses."""
        pass
    
    def _log_error(self, error: str, symbol: str = None) -> None:
        """Log errors consistently."""
        if symbol:
            logger.error(f"[{self.__class__.__name__}] Error for {symbol}: {error}")
        else:
            logger.error(f"[{self.__class__.__name__}] Error: {error}")
    
    def _log_info(self, message: str) -> None:
        """Log info messages consistently."""
        logger.info(f"[{self.__class__.__name__}] {message}")