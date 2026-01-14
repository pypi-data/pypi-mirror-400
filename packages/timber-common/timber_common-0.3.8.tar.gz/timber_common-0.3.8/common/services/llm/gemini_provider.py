# timber/common/services/llm/gemini_provider.py
"""
Gemini Provider - Google's advanced LLM

Gemini provides Google's latest AI capabilities with multimodal support.
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


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini provider implementation.
    
    Supports models:
    - gemini-2.0-flash-exp (recommended, default)
    - gemini-1.5-pro
    - gemini-1.5-flash
    """
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    # Pricing per 1M tokens (as of late 2024)
    PRICING = {
        "gemini-2.0-flash-exp": {"input": 0.00, "output": 0.00},  # Free during preview
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    }
    
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None, **kwargs):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key
            default_model: Default model to use (from config or hardcoded fallback)
            **kwargs: Additional configuration
        """
        self._default_model = default_model or "gemini-2.0-flash-exp"
        super().__init__(api_key, **kwargs)
    
    def _validate_config(self):
        """Validate Gemini configuration"""
        if not self.api_key:
            logger.warning("Gemini API key not provided")
    
    def get_provider_name(self) -> LLMProvider:
        """Get the provider enum"""
        return LLMProvider.GEMINI
    
    def get_available_models(self) -> List[str]:
        """Get list of available Gemini models"""
        return list(self.PRICING.keys())
    
    def get_default_model(self) -> str:
        """Get the default Gemini model (configurable via environment)"""
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
        Generate completion from Gemini.
        
        Note: Gemini uses a different API structure, so we convert
        to their format.
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
        """Generate chat completion from Gemini"""
        if not self.is_available():
            raise ProviderUnavailableError("Gemini API key not configured")
        
        model = model or self.get_default_model()
        
        # Convert messages to Gemini format
        gemini_contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        # Build generation config
        generation_config = {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "topP": kwargs.get("top_p", 0.95),
            "topK": kwargs.get("top_k", 40),
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/models/{model}:generateContent",
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "contents": gemini_contents,
                    "generationConfig": generation_config,
                    "safetySettings": kwargs.get("safety_settings", [])
                },
                timeout=30
            )
            
            if response.status_code == 429:
                raise RateLimitError(f"Gemini rate limit exceeded: {response.text}")
            elif response.status_code == 401 or response.status_code == 403:
                raise AuthenticationError(f"Gemini authentication failed: {response.text}")
            elif response.status_code != 200:
                raise ProviderUnavailableError(
                    f"Gemini API error ({response.status_code}): {response.text}"
                )
            
            data = response.json()
            
            # Extract response
            if not data.get("candidates"):
                raise ProviderUnavailableError("Gemini returned no candidates")
            
            candidate = data["candidates"][0]
            content = candidate["content"]["parts"][0]["text"]
            
            # Extract usage metadata
            usage_metadata = data.get("usageMetadata", {})
            usage = {
                "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
                "total_tokens": usage_metadata.get("totalTokenCount", 0)
            }
            
            return LLMResponse(
                content=content,
                provider=self.get_provider_name(),
                model=model,
                usage=usage,
                metadata={
                    "finish_reason": candidate.get("finishReason"),
                    "safety_ratings": candidate.get("safetyRatings", [])
                }
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini request failed: {e}")
            raise ProviderUnavailableError(f"Gemini request failed: {e}")
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """Estimate cost for Gemini request"""
        model = model or self.get_default_model()
        
        if model not in self.PRICING:
            logger.warning(f"Unknown model {model}, using default pricing")
            model = self.get_default_model()
        
        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost