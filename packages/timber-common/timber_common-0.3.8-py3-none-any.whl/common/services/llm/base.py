# timber/common/services/llm/base.py
"""
Base LLM Service - Multi-provider support with automatic fallback

Provides a unified interface for multiple LLM providers:
- Groq (default, cheapest)
- Perplexity
- Gemini (Google)
- Claude (Anthropic)

Includes automatic fallback when providers are unavailable or over limits.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GROQ = "groq"
    PERPLEXITY = "perplexity"
    GEMINI = "gemini"
    CLAUDE = "claude"


class LLMError(Exception):
    """Base exception for LLM errors"""
    pass


class RateLimitError(LLMError):
    """Raised when API rate limit is exceeded"""
    pass


class AuthenticationError(LLMError):
    """Raised when API authentication fails"""
    pass


class ProviderUnavailableError(LLMError):
    """Raised when provider is unavailable"""
    pass


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    provider: LLMProvider
    model: str
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if response was successful"""
        return self.error is None


@dataclass
class ProviderStatus:
    """Track provider availability and health"""
    provider: LLMProvider
    available: bool = True
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    consecutive_failures: int = 0
    cooldown_until: Optional[datetime] = None
    
    def is_in_cooldown(self) -> bool:
        """Check if provider is in cooldown period"""
        if self.cooldown_until is None:
            return False
        return datetime.utcnow() < self.cooldown_until
    
    def mark_failure(self, error: str, cooldown_minutes: int = 5):
        """Mark a failure and potentially enter cooldown"""
        self.last_error = error
        self.last_error_time = datetime.utcnow()
        self.consecutive_failures += 1
        
        # Enter cooldown after 3 consecutive failures
        if self.consecutive_failures >= 3:
            self.available = False
            self.cooldown_until = datetime.utcnow() + timedelta(minutes=cooldown_minutes)
            logger.warning(
                f"{self.provider} marked unavailable after {self.consecutive_failures} "
                f"failures. Cooldown until {self.cooldown_until}"
            )
    
    def mark_success(self):
        """Mark a successful request"""
        self.consecutive_failures = 0
        self.available = True
        self.cooldown_until = None
        self.last_error = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All provider implementations must inherit from this class.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize provider.
        
        Args:
            api_key: API key for the provider
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self):
        """Validate provider configuration"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> LLMProvider:
        """Get the provider enum"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Get the default model for this provider"""
        pass
    
    @abstractmethod
    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from the provider.
        
        Args:
            prompt: Input prompt
            model: Model to use (defaults to provider's default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse with completion and metadata
            
        Raises:
            RateLimitError: If rate limit exceeded
            AuthenticationError: If authentication fails
            ProviderUnavailableError: If provider is unavailable
        """
        pass
    
    @abstractmethod
    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion from the provider.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to provider's default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse with completion and metadata
            
        Raises:
            RateLimitError: If rate limit exceeded
            AuthenticationError: If authentication fails
            ProviderUnavailableError: If provider is unavailable
        """
        pass
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """
        Estimate cost for the request.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model being used
            
        Returns:
            Estimated cost in USD
        """
        # Override in subclasses with actual pricing
        return 0.0
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.api_key is not None