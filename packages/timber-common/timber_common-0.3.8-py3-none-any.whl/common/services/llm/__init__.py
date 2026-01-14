# timber/common/services/llm/__init__.py
"""
LLM Service Package

Multi-provider LLM service with automatic fallback and backward compatibility.

NEW API (Multi-Provider):
    from common.services.llm import llm_service, LLMProvider
    
    # Automatic configuration from environment
    response = llm_service.complete("Your prompt")
    
    # Chat completion
    response = llm_service.chat_complete(
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    # Specify provider
    response = llm_service.complete(
        "Your prompt",
        preferred_provider=LLMProvider.CLAUDE
    )

LEGACY API (Backward Compatible):
    from common.services.llm import llm_service
    
    # Task summarization (still works!)
    summary = llm_service.generate_task_summary(
        task_name="Analysis",
        task_description="Analyze data",
        task_output={"result": "..."}
    )
    
    # General response (still works!)
    response = llm_service.generate_response(
        system_prompt="You are a helpful assistant",
        user_query="What is AI?"
    )

CONFIGURATION:
    The service auto-configures from environment variables:
    - DEFAULT_LLM or LLM_DEFAULT_PROVIDER (default: "groq")
    - GROQ_API_KEY, GEMINI_API_KEY, PERPLEXITY_API_KEY, ANTHROPIC_API_KEY
    - GROQ_DEFAULT_MODEL, GEMINI_DEFAULT_MODEL, etc.
    
    Set DEFAULT_LLM in .env to change default provider:
        DEFAULT_LLM=claude  # Use Claude by default
        DEFAULT_LLM=gemini  # Use Gemini by default
    
    Set default models in .env:
        GROQ_DEFAULT_MODEL=mixtral-8x7b-32768
        GEMINI_DEFAULT_MODEL=gemini-1.5-pro
    
    If DEFAULT_LLM is not set, defaults to Groq (cheapest/fastest).

FEATURES:
    - Automatic provider fallback
    - Configurable default models (no staleness!)
    - Cost estimation
    - Provider health monitoring
    - Backward compatible with LangChain-style API
    - Works seamlessly with existing code
"""

from .base import (
    LLMProvider,
    LLMResponse,
    LLMError,
    RateLimitError,
    AuthenticationError,
    ProviderUnavailableError,
    ProviderStatus
)

# Import the enhanced service with backward compatibility
from .model_choice import llm_service, LLMService

__all__ = [
    # Main service (singleton instance - use this!)
    'llm_service',
    
    # Service class (for type hints or manual instantiation)
    'LLMService',
    
    # Enums and data classes
    'LLMProvider',
    'LLMResponse',
    'ProviderStatus',
    
    # Exceptions
    'LLMError',
    'RateLimitError',
    'AuthenticationError',
    'ProviderUnavailableError',
]

# Note: llm_service is already instantiated as a singleton in model_choice.py
# and auto-configures from environment on first import.
# 
# This means existing code like:
#     from common.services.llm import llm_service
#     summary = llm_service.generate_task_summary(...)
# 
# Will work seamlessly without any changes!