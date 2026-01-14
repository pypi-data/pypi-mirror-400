# timber/common/services/llm/perplexity_provider.py
"""
Perplexity Provider - Search-augmented LLM responses

Perplexity provides LLM responses with real-time search capabilities.
Excellent for queries requiring current information.
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


class PerplexityProvider(BaseLLMProvider):
    """
    Perplexity AI provider implementation.
    
    Supports models:
    - llama-3.1-sonar-large-128k-online (recommended, default)
    - llama-3.1-sonar-small-128k-online
    - llama-3.1-sonar-large-128k-chat
    - llama-3.1-sonar-small-128k-chat
    """
    
    BASE_URL = "https://api.perplexity.ai"
    
    # Pricing per 1M tokens
    PRICING = {
        "llama-3.1-sonar-large-128k-online": {"input": 1.00, "output": 1.00},
        "llama-3.1-sonar-small-128k-online": {"input": 0.20, "output": 0.20},
        "llama-3.1-sonar-large-128k-chat": {"input": 1.00, "output": 1.00},
        "llama-3.1-sonar-small-128k-chat": {"input": 0.20, "output": 0.20},
    }
    
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None, **kwargs):
        """
        Initialize Perplexity provider.
        
        Args:
            api_key: Perplexity API key
            default_model: Default model to use (from config or hardcoded fallback)
            **kwargs: Additional configuration
        """
        self._default_model = default_model or "llama-3.1-sonar-large-128k-online"
        super().__init__(api_key, **kwargs)
    
    def _validate_config(self):
        """Validate Perplexity configuration"""
        if not self.api_key:
            logger.warning("Perplexity API key not provided")
    
    def get_provider_name(self) -> LLMProvider:
        """Get the provider enum"""
        return LLMProvider.PERPLEXITY
    
    def get_available_models(self) -> List[str]:
        """Get list of available Perplexity models"""
        return list(self.PRICING.keys())
    
    def get_default_model(self) -> str:
        """Get the default Perplexity model (configurable via environment)"""
        return self._default_model
    
    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from Perplexity.
        
        Note: Perplexity primarily uses chat interface, so we convert
        the prompt to a chat message.
        """
        return self.chat_complete(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
    
    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion from Perplexity"""
        if not self.is_available():
            raise ProviderUnavailableError("Perplexity API key not configured")
        
        model = model or self.get_default_model()
        
        # Extract search-specific parameters
        search_domain_filter = kwargs.pop("search_domain_filter", None)
        return_citations = kwargs.pop("return_citations", True)
        return_images = kwargs.pop("return_images", False)
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        # Add search parameters if using online model
        if "online" in model:
            if search_domain_filter:
                payload["search_domain_filter"] = search_domain_filter
            payload["return_citations"] = return_citations
            payload["return_images"] = return_images
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60  # Longer timeout for search-augmented responses
            )
            
            if response.status_code == 429:
                raise RateLimitError(f"Perplexity rate limit exceeded: {response.text}")
            elif response.status_code == 401:
                raise AuthenticationError(f"Perplexity authentication failed: {response.text}")
            elif response.status_code != 200:
                raise ProviderUnavailableError(
                    f"Perplexity API error ({response.status_code}): {response.text}"
                )
            
            data = response.json()
            
            # Extract citations if available
            citations = data.get("citations", [])
            images = data.get("images", [])
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider=self.get_provider_name(),
                model=model,
                usage=data.get("usage"),
                metadata={
                    "finish_reason": data["choices"][0].get("finish_reason"),
                    "citations": citations,
                    "images": images,
                    "message_role": data["choices"][0]["message"].get("role")
                }
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity request failed: {e}")
            raise ProviderUnavailableError(f"Perplexity request failed: {e}")
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """Estimate cost for Perplexity request"""
        model = model or self.get_default_model()
        
        if model not in self.PRICING:
            logger.warning(f"Unknown model {model}, using default pricing")
            model = self.get_default_model()
        
        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost