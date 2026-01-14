# timber/common/services/llm/claude_provider.py
"""
Claude Provider - Anthropic's advanced AI assistant

Claude provides excellent reasoning, analysis, and coding capabilities.
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


class ClaudeProvider(BaseLLMProvider):
    """
    Anthropic Claude provider implementation.
    
    Supports models:
    - claude-sonnet-4-20250514 (recommended, default)
    - claude-3-5-sonnet-20241022
    - claude-3-5-haiku-20241022
    - claude-3-opus-20240229
    """
    
    BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"
    
    # Pricing per 1M tokens (as of late 2024)
    PRICING = {
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    }
    
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None, **kwargs):
        """
        Initialize Claude provider.
        
        Args:
            api_key: Claude API key
            default_model: Default model to use (from config or hardcoded fallback)
            **kwargs: Additional configuration
        """
        self._default_model = default_model or "claude-sonnet-4-20250514"
        super().__init__(api_key, **kwargs)
    
    def _validate_config(self):
        """Validate Claude configuration"""
        if not self.api_key:
            logger.warning("Claude API key not provided")
    
    def get_provider_name(self) -> LLMProvider:
        """Get the provider enum"""
        return LLMProvider.CLAUDE
    
    def get_available_models(self) -> List[str]:
        """Get list of available Claude models"""
        return list(self.PRICING.keys())
    
    def get_default_model(self) -> str:
        """Get the default Claude model (configurable via environment)"""
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
        Generate completion from Claude.
        
        Note: Claude uses messages API, so we convert the prompt.
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
        """Generate chat completion from Claude"""
        if not self.is_available():
            raise ProviderUnavailableError("Claude API key not configured")
        
        model = model or self.get_default_model()
        
        # Extract system message if present
        system_message = None
        filtered_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)
        
        payload = {
            "model": model,
            "messages": filtered_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        if system_message:
            payload["system"] = system_message
        
        # Add optional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            payload["top_k"] = kwargs["top_k"]
        if "stop_sequences" in kwargs:
            payload["stop_sequences"] = kwargs["stop_sequences"]
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self.API_VERSION,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            )
            
            if response.status_code == 429:
                raise RateLimitError(f"Claude rate limit exceeded: {response.text}")
            elif response.status_code == 401:
                raise AuthenticationError(f"Claude authentication failed: {response.text}")
            elif response.status_code != 200:
                raise ProviderUnavailableError(
                    f"Claude API error ({response.status_code}): {response.text}"
                )
            
            data = response.json()
            
            # Extract content from response
            content = ""
            for block in data.get("content", []):
                if block["type"] == "text":
                    content += block["text"]
            
            # Build usage info
            usage = {
                "prompt_tokens": data["usage"]["input_tokens"],
                "completion_tokens": data["usage"]["output_tokens"],
                "total_tokens": data["usage"]["input_tokens"] + data["usage"]["output_tokens"]
            }
            
            return LLMResponse(
                content=content,
                provider=self.get_provider_name(),
                model=data.get("model", model),
                usage=usage,
                metadata={
                    "stop_reason": data.get("stop_reason"),
                    "stop_sequence": data.get("stop_sequence"),
                    "message_id": data.get("id")
                }
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Claude request failed: {e}")
            raise ProviderUnavailableError(f"Claude request failed: {e}")
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """Estimate cost for Claude request"""
        model = model or self.get_default_model()
        
        if model not in self.PRICING:
            logger.warning(f"Unknown model {model}, using default pricing")
            model = self.get_default_model()
        
        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost