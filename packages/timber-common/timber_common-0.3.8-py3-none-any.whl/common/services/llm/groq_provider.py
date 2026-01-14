# timber/common/services/llm/groq_provider.py
"""
Groq Provider - Fast and affordable LLM inference

Groq provides ultra-fast inference with competitive pricing.
Default provider for the system.
"""

from typing import Optional, List, Dict, Any
import requests
import logging

from .base import (
    BaseLLMProvider,
    LLMProvider,
    LLMResponse,
    RateLimitError,
    AuthenticationError,
    ProviderUnavailableError
)

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """
    Groq LLM provider implementation.
    
    Supports models:
    - llama-3.3-70b-versatile (recommended, default)
    - llama-3.1-70b-versatile
    - mixtral-8x7b-32768
    - gemma-7b-it
    """
    
    BASE_URL = "https://api.groq.com/openai/v1"
    
    # Pricing per 1M tokens (as of late 2024)
    PRICING = {
        "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
        "llama-3.1-70b-versatile": {"input": 0.59, "output": 0.79},
        "mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
        "gemma-7b-it": {"input": 0.07, "output": 0.07},
    }
    
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None, **kwargs):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key
            default_model: Default model to use (from config or hardcoded fallback)
            **kwargs: Additional configuration
        """
        self._default_model = default_model or "llama-3.3-70b-versatile"
        super().__init__(api_key, **kwargs)
    
    def _validate_config(self):
        """Validate Groq configuration"""
        if not self.api_key:
            logger.warning("Groq API key not provided")
    
    def get_provider_name(self) -> LLMProvider:
        """Get the provider enum"""
        return LLMProvider.GROQ
    
    def get_available_models(self) -> List[str]:
        """Get list of available Groq models"""
        return list(self.PRICING.keys())
    
    def get_default_model(self) -> str:
        """Get the default Groq model (configurable via environment)"""
        return self._default_model
    
    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from Groq"""
        if not self.is_available():
            raise ProviderUnavailableError("Groq API key not configured")
        
        model = model or self.get_default_model()
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                },
                timeout=30
            )
            
            if response.status_code == 429:
                raise RateLimitError(f"Groq rate limit exceeded: {response.text}")
            elif response.status_code == 401:
                raise AuthenticationError(f"Groq authentication failed: {response.text}")
            elif response.status_code != 200:
                raise ProviderUnavailableError(
                    f"Groq API error ({response.status_code}): {response.text}"
                )
            
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["text"],
                provider=self.get_provider_name(),
                model=model,
                usage=data.get("usage"),
                metadata={"finish_reason": data["choices"][0].get("finish_reason")}
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq request failed: {e}")
            raise ProviderUnavailableError(f"Groq request failed: {e}")
    
    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion from Groq"""
        if not self.is_available():
            raise ProviderUnavailableError("Groq API key not configured")
        
        model = model or self.get_default_model()
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                },
                timeout=30
            )
            
            if response.status_code == 429:
                raise RateLimitError(f"Groq rate limit exceeded: {response.text}")
            elif response.status_code == 401:
                raise AuthenticationError(f"Groq authentication failed: {response.text}")
            elif response.status_code != 200:
                raise ProviderUnavailableError(
                    f"Groq API error ({response.status_code}): {response.text}"
                )
            
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider=self.get_provider_name(),
                model=model,
                usage=data.get("usage"),
                metadata={
                    "finish_reason": data["choices"][0].get("finish_reason"),
                    "message_role": data["choices"][0]["message"].get("role")
                }
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq request failed: {e}")
            raise ProviderUnavailableError(f"Groq request failed: {e}")
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """Estimate cost for Groq request"""
        model = model or self.get_default_model()
        
        if model not in self.PRICING:
            logger.warning(f"Unknown model {model}, using default pricing")
            model = self.get_default_model()
        
        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost