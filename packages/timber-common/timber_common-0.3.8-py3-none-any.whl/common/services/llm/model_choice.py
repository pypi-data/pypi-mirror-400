# common/services/llm/model_choice.py
"""
Enhanced LLM Service - Multi-provider with backward compatibility

Provides both new multi-provider API and backward-compatible methods
for existing code using LangChain-style interface.

Usage (New API):
    from timber.common.services.llm import llm_service
    response = llm_service.complete("Your prompt")

Usage (Legacy API - still works):
    from timber.common.services.llm import llm_service
    summary = llm_service.generate_task_summary(...)
"""

from typing import Optional, List, Dict, Any, Tuple
import logging
import json
from datetime import datetime

from .base import (
    LLMProvider,
    LLMResponse,
    ProviderStatus,
    LLMError,
    RateLimitError,
    AuthenticationError,
    ProviderUnavailableError
)
from .groq_provider import GroqProvider
from .perplexity_provider import PerplexityProvider
from .gemini_provider import GeminiProvider
from .claude_provider import ClaudeProvider

logger = logging.getLogger(__name__)


class LLMService:
    """
    Enhanced singleton LLM service with multi-provider support and backward compatibility.
    
    New API:
        response = llm_service.complete("prompt")
        response = llm_service.chat_complete(messages=[...])
    
    Legacy API (backward compatible):
        summary = llm_service.generate_task_summary(...)
        response = llm_service.generate_response(...)
    """
    
    _instance: Optional['LLMService'] = None
    
    # Default fallback order (Groq is cheapest, so it's first)
    DEFAULT_FALLBACK_ORDER = [
        LLMProvider.GROQ,
        LLMProvider.GEMINI,
        LLMProvider.PERPLEXITY,
        LLMProvider.CLAUDE
    ]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Initialize providers dictionary
        self._providers: Dict[LLMProvider, Any] = {}
        self._provider_status: Dict[LLMProvider, ProviderStatus] = {}
        
        # Track last request for cost estimation
        self._last_response: Optional[LLMResponse] = None
        
        # Configuration
        self._fallback_order = self.DEFAULT_FALLBACK_ORDER.copy()
        self._enable_fallback = True
        self._max_retries = 3
        self._auto_configured = False
        
        # Try to auto-configure from environment
        self._try_auto_configure()
        
        self._initialized = True
        
        logger.info("LLM Service initialized")
    
    def _try_auto_configure(self):
        """Try to automatically configure from environment/config."""
        try:
            from common.utils.config import config
            
            # Only auto-configure if at least one API key is available
            if config.has_any_llm_provider():
                self.configure_providers(
                    groq_api_key=config.GROQ_API_KEY,
                    perplexity_api_key=config.PERPLEXITY_API_KEY,
                    gemini_api_key=config.GEMINI_API_KEY,
                    claude_api_key=config.ANTHROPIC_API_KEY,
                    # Pass default models from config
                    groq_default_model=config.GROQ_DEFAULT_MODEL,
                    gemini_default_model=config.GEMINI_DEFAULT_MODEL,
                    perplexity_default_model=config.PERPLEXITY_DEFAULT_MODEL,
                    claude_default_model=config.CLAUDE_DEFAULT_MODEL
                )
                
                # Set default provider from config
                try:
                    default_provider = LLMProvider(config.DEFAULT_LLM.lower())
                    # Move default provider to front of fallback order
                    if default_provider in self._fallback_order:
                        self._fallback_order.remove(default_provider)
                    self._fallback_order.insert(0, default_provider)
                except ValueError:
                    pass  # Invalid provider name, use default order
                
                # Apply other settings
                self._enable_fallback = config.LLM_ENABLE_FALLBACK
                
                self._auto_configured = True
                logger.info(f"Auto-configured from environment (default: {config.DEFAULT_LLM})")
            else:
                logger.warning("No LLM providers configured in environment")
                
        except ImportError:
            logger.debug("Config not available, manual configuration required")
        except Exception as e:
            logger.debug(f"Auto-configuration failed: {e}")
    
    def configure_providers(
        self,
        groq_api_key: Optional[str] = None,
        perplexity_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        claude_api_key: Optional[str] = None,
        groq_default_model: Optional[str] = None,
        gemini_default_model: Optional[str] = None,
        perplexity_default_model: Optional[str] = None,
        claude_default_model: Optional[str] = None,
        **kwargs
    ):
        """
        Configure LLM providers with API keys and default models.
        
        Args:
            groq_api_key: Groq API key
            perplexity_api_key: Perplexity API key
            gemini_api_key: Gemini API key
            claude_api_key: Claude (Anthropic) API key
            groq_default_model: Default model for Groq (from config)
            gemini_default_model: Default model for Gemini (from config)
            perplexity_default_model: Default model for Perplexity (from config)
            claude_default_model: Default model for Claude (from config)
            **kwargs: Additional provider-specific configuration
        """
        # Initialize providers
        if groq_api_key:
            self._providers[LLMProvider.GROQ] = GroqProvider(
                api_key=groq_api_key,
                default_model=groq_default_model,
                **kwargs.get('groq_config', {})
            )
            self._provider_status[LLMProvider.GROQ] = ProviderStatus(LLMProvider.GROQ)
            logger.info(f"Groq provider configured (default model: {groq_default_model or 'llama-3.3-70b-versatile'})")
        
        if perplexity_api_key:
            self._providers[LLMProvider.PERPLEXITY] = PerplexityProvider(
                api_key=perplexity_api_key,
                default_model=perplexity_default_model,
                **kwargs.get('perplexity_config', {})
            )
            self._provider_status[LLMProvider.PERPLEXITY] = ProviderStatus(LLMProvider.PERPLEXITY)
            logger.info(f"Perplexity provider configured (default model: {perplexity_default_model or 'llama-3.1-sonar-large-128k-online'})")
        
        if gemini_api_key:
            self._providers[LLMProvider.GEMINI] = GeminiProvider(
                api_key=gemini_api_key,
                default_model=gemini_default_model,
                **kwargs.get('gemini_config', {})
            )
            self._provider_status[LLMProvider.GEMINI] = ProviderStatus(LLMProvider.GEMINI)
            logger.info(f"Gemini provider configured (default model: {gemini_default_model or 'gemini-2.0-flash-exp'})")
        
        if claude_api_key:
            self._providers[LLMProvider.CLAUDE] = ClaudeProvider(
                api_key=claude_api_key,
                default_model=claude_default_model,
                **kwargs.get('claude_config', {})
            )
            self._provider_status[LLMProvider.CLAUDE] = ProviderStatus(LLMProvider.CLAUDE)
            logger.info(f"Claude provider configured (default model: {claude_default_model or 'claude-sonnet-4-20250514'})")
        
        if not self._providers:
            logger.warning("No LLM providers configured! Service will not be functional.")
    
    def configure_from_env(self):
        """Configure providers from environment variables."""
        import os
        
        self.configure_providers(
            groq_api_key=os.getenv('GROQ_API_KEY'),
            perplexity_api_key=os.getenv('PERPLEXITY_API_KEY'),
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
            claude_api_key=os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')
        )
    
    def set_fallback_order(self, order: List[LLMProvider]):
        """Set custom fallback order for providers."""
        self._fallback_order = order
        logger.info(f"Fallback order set to: {[p.value for p in order]}")
    
    def enable_fallback(self, enable: bool = True):
        """Enable or disable automatic fallback."""
        self._enable_fallback = enable
        logger.info(f"Automatic fallback {'enabled' if enable else 'disabled'}")
    
    def is_available(self) -> bool:
        """
        Check if LLM service is available (backward compatible method).
        
        Returns:
            True if at least one provider is configured
        """
        return len(self._providers) > 0
    
    def _get_available_providers(
        self,
        preferred_provider: Optional[LLMProvider] = None
    ) -> List[LLMProvider]:
        """Get list of available providers in fallback order."""
        providers = []
        
        # Add preferred provider first if specified and available
        if preferred_provider and preferred_provider in self._providers:
            status = self._provider_status.get(preferred_provider)
            if status and not status.is_in_cooldown():
                providers.append(preferred_provider)
        
        # Add fallback providers
        if self._enable_fallback:
            for provider in self._fallback_order:
                if provider in self._providers and provider not in providers:
                    status = self._provider_status.get(provider)
                    if status and not status.is_in_cooldown():
                        providers.append(provider)
        
        return providers
    
    def _try_provider(
        self,
        provider: LLMProvider,
        method: str,
        *args,
        **kwargs
    ) -> Tuple[Optional[LLMResponse], Optional[Exception]]:
        """Try to get a response from a provider."""
        provider_obj = self._providers[provider]
        status = self._provider_status[provider]
        
        try:
            logger.info(f"Trying {provider.value} for {method}...")
            
            # Call the appropriate method
            if method == 'complete':
                response = provider_obj.complete(*args, **kwargs)
            elif method == 'chat_complete':
                response = provider_obj.chat_complete(*args, **kwargs)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # Mark success
            status.mark_success()
            self._last_response = response
            
            logger.info(f"✓ {provider.value} succeeded")
            return response, None
            
        except (RateLimitError, AuthenticationError, ProviderUnavailableError) as e:
            logger.warning(f"✗ {provider.value} failed: {e}")
            status.mark_failure(str(e))
            return None, e
        except Exception as e:
            logger.error(f"✗ {provider.value} unexpected error: {e}")
            status.mark_failure(str(e))
            return None, e
    
    # =========================================================================
    # NEW API - Multi-provider interface
    # =========================================================================
    
    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        preferred_provider: Optional[LLMProvider] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion with automatic fallback.
        
        Args:
            prompt: Input prompt
            model: Model to use (if None, uses provider's default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            preferred_provider: Preferred provider (falls back if unavailable)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse with completion
            
        Raises:
            LLMError: If all providers fail
        """
        providers = self._get_available_providers(preferred_provider)
        
        if not providers:
            raise LLMError("No LLM providers available")
        
        last_error = None
        is_preferred_provider = True
        
        for provider in providers:
            # Only pass model to preferred provider; fallbacks use their defaults
            provider_model = model if is_preferred_provider else None
            
            response, error = self._try_provider(
                provider,
                'complete',
                prompt,
                model=provider_model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            if response:
                return response
            
            last_error = error
            is_preferred_provider = False
        
        # All providers failed
        raise LLMError(f"All providers failed. Last error: {last_error}")
    
    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        preferred_provider: Optional[LLMProvider] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion with automatic fallback.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (if None, uses provider's default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            preferred_provider: Preferred provider (falls back if unavailable)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse with completion
            
        Raises:
            LLMError: If all providers fail
        """
        providers = self._get_available_providers(preferred_provider)
        
        if not providers:
            raise LLMError("No LLM providers available")
        
        last_error = None
        is_preferred_provider = True
        
        for provider in providers:
            # Only pass model to preferred provider; fallbacks use their defaults
            provider_model = model if is_preferred_provider else None
            
            response, error = self._try_provider(
                provider,
                'chat_complete',
                messages,
                model=provider_model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            if response:
                return response
            
            last_error = error
            is_preferred_provider = False
        
        # All providers failed
        raise LLMError(f"All providers failed. Last error: {last_error}")
    
    # =========================================================================
    # LEGACY API - Backward compatible methods
    # =========================================================================
    
    def generate_task_summary(
        self,
        task_name: str,
        task_description: str,
        task_output: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        return_metadata: bool = False
    ) -> Optional[Any]:
        """
        Generate a human-readable summary of task execution results.
        
        BACKWARD COMPATIBLE METHOD - Uses new multi-provider backend.
        
        Args:
            task_name: Name of the task
            task_description: Description from task definition
            task_output: Structured JSON output from task
            context: Additional context (inputs, session data, etc.)
            return_metadata: If True, returns (summary, metadata) tuple (default: False)
            
        Returns:
            If return_metadata=False: Natural language summary or None if generation fails
            If return_metadata=True: Tuple of (summary_text, metadata_dict) or (None, None)
            
        Metadata dict includes:
            - model_used: Actual model name (e.g., "llama-3.3-70b-versatile")
            - provider_used: Provider name (e.g., "groq")
            - model_strengths: List of model strengths
            - model_considerations: List of considerations
            - tokens_used: Token usage info (if available)
            - cost_estimate: Estimated cost (if available)
        """
        if not self.is_available():
            logger.warning("LLM service not available - cannot generate summary")
            return (None, None) if return_metadata else None
        
        try:
            # Build prompt using legacy format
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_task_summary_prompt(
                task_name=task_name,
                task_description=task_description,
                task_output=task_output,
                context=context
            )
            
            # Use new chat_complete method
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.chat_complete(
                messages=messages,
                max_tokens=500,
                temperature=0.3  # Lower temp for factual summaries
            )
            
            logger.info(f"✓ Generated AI summary for task: {task_name}")
            summary_text = response.content.strip()
            
            # Return based on metadata flag
            if return_metadata:
                metadata = self._build_response_metadata(response)
                return (summary_text, metadata)
            else:
                return summary_text
            
        except Exception as e:
            logger.error(f"Failed to generate task summary: {e}", exc_info=True)
            return (None, None) if return_metadata else None
    
    def generate_response(
        self,
        system_prompt: str,
        user_query: str,
        chat_history: Optional[List[Any]] = None  # Accepts both BaseMessage and dicts
    ) -> str:
        """
        Generate a general text response (for non-task uses).
        
        BACKWARD COMPATIBLE METHOD - Uses new multi-provider backend.
        Accepts both LangChain BaseMessage objects and plain dicts for chat_history.
        
        Args:
            system_prompt: System instructions
            user_query: User's query
            chat_history: Optional conversation history 
                         (list of LangChain BaseMessage objects OR dicts with 'role' and 'content')
            
        Returns:
            Generated response text
        """
        if not self.is_available():
            return "Error: LLM service is unavailable."
        
        try:
            # Build messages array
            messages = [{"role": "system", "content": system_prompt}]
            
            if chat_history:
                # Handle both BaseMessage objects and plain dicts
                for msg in chat_history:
                    if isinstance(msg, dict):
                        # Already a dict, use as-is
                        messages.append(msg)
                    else:
                        # Assume it's a LangChain BaseMessage object
                        # Convert to dict format
                        try:
                            # LangChain messages have .type and .content attributes
                            # SystemMessage -> system, HumanMessage -> user, AIMessage -> assistant
                            role_mapping = {
                                'system': 'system',
                                'human': 'user',
                                'ai': 'assistant',
                                'assistant': 'assistant',
                                'user': 'user'
                            }
                            
                            msg_type = getattr(msg, 'type', 'user')
                            msg_content = getattr(msg, 'content', str(msg))
                            msg_role = role_mapping.get(msg_type, 'user')
                            
                            messages.append({"role": msg_role, "content": msg_content})
                        except Exception as e:
                            logger.warning(f"Failed to convert message object, skipping: {e}")
                            continue
            
            messages.append({"role": "user", "content": user_query})
            
            # Use new chat_complete method
            response = self.chat_complete(
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error invoking LLM: {e}")
            return "An error occurred during LLM communication."
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for task summarization (legacy method)."""
        return """You are a financial analysis assistant that creates concise, 
human-readable summaries of automated task results.

Your summaries should:
1. Be 2-4 sentences long
2. Highlight the most important findings
3. Use clear, professional language
4. Focus on actionable insights
5. Avoid technical jargon unless necessary
6. Be objective and fact-based

Format: Plain text paragraphs, no markdown."""
    
    def _process_content_advanced(
        self,
        task_output: Dict[str, Any],
        max_tokens: int,
        task_name: str,
        task_description: str
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Process content using advanced multi-tier strategy.
        
        Multi-tier processing (auto-selects best tier):
        - Tier 0: Full content (if fits)
        - Tier 1: Chunking with aggregation
        - Tier 2: Hierarchical summarization
        - Tier 3: Intelligent condensing
        - Tier 4: Truncation (last resort)
        
        Args:
            task_output: Task output dictionary
            max_tokens: Target token limit
            task_name: Task name for context
            task_description: Task description for context
            
        Returns:
            Tuple of (processed_output, processing_stats)
        """
        try:
            from common.utils.llm.content_handler import ContentHandler
            
            # Initialize handler with LLM service reference
            handler = ContentHandler(
                llm_service=self,
                default_max_tokens=max_tokens
            )
            
            # Process content through multi-tier pipeline
            result = handler.process_content(
                content=task_output,
                task_type="task_summary",
                max_tokens=max_tokens
            )
            
            # Log processing strategy used
            logger.info(f"Content processing: Strategy {result.strategy_used}")
            logger.info(f"Size: {result.original_size} → {result.final_size} chars ({result.reduction_pct:.1f}% reduction)")
            logger.info(f"Tokens: {result.original_tokens} → {result.final_tokens}")
            
            # Build stats dict for backward compatibility
            stats = {
                'condensed': result.strategy_used != 'full_content',
                'original_size': result.original_size,
                'final_size': result.final_size,
                'reduction_pct': result.reduction_pct,
                'tier_used': result.strategy_used.upper(),
                'metadata': result.metadata,
                'warning': result.warning
            }
            
            return result.content, stats
            
        except ImportError as e:
            logger.warning(f"ContentHandler not available: {e}")
            # Fallback to simple condensing
            return self._condense_task_output_fallback(task_output, max_tokens)
        except Exception as e:
            logger.error(f"Error in advanced content processing: {e}", exc_info=True)
            # Fallback to simple condensing
            return self._condense_task_output_fallback(task_output, max_tokens)
    
    def _condense_task_output_fallback(
        self,
        task_output: Dict[str, Any],
        max_tokens: int = 10000
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Fallback: Simple intelligent condensing (Tier 3 only).
        
        Used if advanced multi-tier processor is not available.
        """
        try:
            from common.utils.llm.content_condenser import content_condenser
            
            condensed, stats = content_condenser.condense_task_output(
                task_output=task_output,
                max_tokens=max_tokens
            )
            
            if stats['condensed']:
                logger.info(
                    f"Content condensed: {stats['original_size']} → {stats['final_size']} chars "
                    f"({stats['reduction_pct']:.1f}% reduction)"
                )
                logger.debug(f"   Extraction: {stats.get('items_extracted', 0)} items")
                logger.debug(f"   Deduplication: {stats.get('items_deduplicated', 0)} items")
                logger.debug(f"   Summarization: {stats.get('items_summarized', 0)} items")
            
            return condensed, stats
            
        except ImportError:
            logger.warning("Content condenser not available, using simple truncation")
            # Final fallback to simple truncation
            return self._truncate_task_output_simple(task_output, max_tokens * 4), None
    
    def _condense_task_output(
        self,
        task_output: Dict[str, Any],
        max_tokens: int = 10000,
        task_name: str = "Unknown Task",
        task_description: str = ""
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Intelligently condense task output using multi-tier processing.
        
        Uses ContentHandler which automatically selects best strategy:
        1. Full content (if fits)
        2. Chunking with aggregation
        3. Hierarchical summarization
        4. Content condensing
        5. Emergency truncation
        
        Args:
            task_output: Task output dictionary
            max_tokens: Target token limit
            task_name: Task name (for advanced processing)
            task_description: Task description (for advanced processing)
            
        Returns:
            Tuple of (processed_output, processing_stats)
        """
        # Try to use advanced multi-tier processing
        try:
            processed, stats = self._process_content_advanced(
                task_output, max_tokens, task_name, task_description
            )
            return processed, stats
        except Exception as e:
            logger.debug(f"Could not use advanced processing: {e}")
            # Fallback to synchronous simple condensing
            return self._condense_task_output_fallback(task_output, max_tokens)
    
    def _truncate_task_output_simple(
        self,
        task_output: Dict[str, Any],
        max_output_chars: int = 40000
    ) -> Dict[str, Any]:
        """
        Simple truncation (only used as final fallback).
        
        This is less intelligent than condensing but better than nothing.
        """
        import json
        
        try:
            output_json = json.dumps(task_output, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to serialize task output: {e}")
            return {"error": "Failed to serialize output"}
        
        if len(output_json) <= max_output_chars:
            return task_output
        
        # Simple truncation as last resort
        truncated = {}
        remaining_chars = max_output_chars
        
        for key, value in task_output.items():
            try:
                value_json = json.dumps(value, indent=2, default=str)
                value_len = len(value_json)
                
                if value_len < remaining_chars:
                    truncated[key] = value
                    remaining_chars -= value_len
                else:
                    truncated[key] = f"[Truncated - original size: {value_len} chars]"
                    break
            except Exception:
                truncated[key] = "[Failed to serialize]"
        
        logger.warning(
            f"Task output truncated from {len(output_json)} to ~{max_output_chars} chars "
            f"(fallback method - data may be lost)"
        )
        
        return truncated
    
    def _build_task_summary_prompt(
        self,
        task_name: str,
        task_description: str,
        task_output: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build user prompt for task summarization.
        
        ADVANCED: Uses multi-tier intelligent content processing.
        Automatically selects best processing tier for content size.
        """
        # Intelligently condense task output (uses multi-tier processing)
        condensed_output, condense_stats = self._condense_task_output(
            task_output,
            max_tokens=8000,  # Reserve tokens for prompt structure
            task_name=task_name,
            task_description=task_description
        )
        
        # Format the output
        output_json = json.dumps(condensed_output, indent=2, default=str)
        
        # Build context section if available
        context_section = ""
        if context:
            # Also condense context if too large
            condensed_context, _ = self._condense_task_output(
                context, 
                max_tokens=2000,
                task_name=f"{task_name} (context)",
                task_description="Context information"
            )
            context_json = json.dumps(condensed_context, indent=2, default=str)
            context_section = f"\n\nContext:\n{context_json}"
        
        # Add processing notice if advanced tier was used
        processing_notice = ""
        if condense_stats and condense_stats.get('condensed'):
            tier_name = condense_stats.get('tier_used', 'PROCESSING')
            
            processing_notice = f"""

NOTE: Content processed using {tier_name.replace('_', ' ').title()}.
Original size: {condense_stats['original_size']} chars, Processed size: {condense_stats['final_size']} chars
Reduction: {condense_stats['reduction_pct']:.1f}%"""
            
            # Add tier-specific messages
            if 'TRUNCATION' in tier_name or 'EMERGENCY' in tier_name:
                processing_notice += """

⚠️  CRITICAL WARNING: Content was truncated due to size constraints.
This summary may be incomplete. Manual review recommended for comprehensive analysis."""
            
            elif 'CHUNKING' in tier_name or 'HIERARCHICAL' in tier_name:
                metadata = condense_stats.get('metadata', {})
                llm_calls = metadata.get('llm_calls', 0)
                if llm_calls > 0:
                    processing_notice += f"""
Processing involved {llm_calls} LLM calls to aggregate information.
All key information has been preserved through intelligent summarization."""
            
            # Add warning if present
            if condense_stats.get('warning'):
                processing_notice += f"""

⚠️  Warning: {condense_stats['warning']}"""
        
        prompt = f"""Task: {task_name}
Description: {task_description}

Output:
{output_json}{context_section}{processing_notice}

Provide a concise, human-readable summary of these results. Focus on what was 
accomplished and the key findings."""
        
        # Final safety check - prevent massive prompts
        if len(prompt) > 100000:  # ~25k tokens
            logger.warning(f"Prompt still very large after processing: {len(prompt)} chars")
            # Emergency truncation as absolute last resort
            prompt = prompt[:100000] + "\n\n[Emergency truncation applied - contact support if this occurs frequently]"
        
        return prompt
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _build_response_metadata(self, response: LLMResponse) -> Dict[str, Any]:
        """
        Build metadata dictionary from LLM response.
        
        Args:
            response: LLMResponse object
            
        Returns:
            Dict with model info, strengths, considerations, and usage
        """
        metadata = {
            'model_used': response.model,
            'provider_used': response.provider.value,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Add token usage if available
        if response.usage:
            metadata['tokens_used'] = response.usage
            metadata['prompt_tokens'] = response.usage.get('prompt_tokens', 0)
            metadata['completion_tokens'] = response.usage.get('completion_tokens', 0)
            metadata['total_tokens'] = response.usage.get('total_tokens', 0)
        
        # Add cost estimate if available
        cost = self.estimate_last_request_cost()
        if cost is not None:
            metadata['cost_estimate'] = cost
            metadata['cost_estimate_usd'] = f"${cost:.6f}"
        
        # Add model strengths and considerations
        model_info = self.get_model_metadata(response.provider, response.model)
        if model_info:
            metadata['model_strengths'] = model_info.get('strengths', [])
            metadata['model_considerations'] = model_info.get('considerations', [])
            metadata['model_best_for'] = model_info.get('best_for', [])
        
        return metadata
    
    def get_model_metadata(
        self,
        provider: LLMProvider,
        model: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a specific model.
        
        Args:
            provider: LLM provider enum
            model: Model name
            
        Returns:
            Dict with model strengths, considerations, and use cases
        """
        # Model metadata database
        # This could be moved to a config file later
        metadata_db = {
            # Groq models
            (LLMProvider.GROQ, 'llama-3.3-70b-versatile'): {
                'strengths': [
                    'Very fast inference',
                    'Cost-effective',
                    'Good at reasoning',
                    'Strong multilingual support'
                ],
                'considerations': [
                    'May be less creative than GPT-4 or Claude',
                    'Best for structured tasks'
                ],
                'best_for': [
                    'Task summaries',
                    'Data analysis',
                    'Quick responses',
                    'High-volume applications'
                ]
            },
            (LLMProvider.GROQ, 'mixtral-8x7b-32768'): {
                'strengths': [
                    'Cheapest option ($0.24/$0.24)',
                    'Large 32k context',
                    'Fast inference',
                    'Good for simple tasks'
                ],
                'considerations': [
                    'Less capable than 70B models',
                    'May struggle with complex reasoning'
                ],
                'best_for': [
                    'Simple summaries',
                    'Classification',
                    'Cost-sensitive applications'
                ]
            },
            (LLMProvider.GROQ, 'gemma-7b-it'): {
                'strengths': [
                    'Extremely cheap ($0.07/$0.07)',
                    'Very fast',
                    'Lightweight'
                ],
                'considerations': [
                    'Smallest model - limited capabilities',
                    'Best for very simple tasks only'
                ],
                'best_for': [
                    'Simple extraction',
                    'Basic classification',
                    'High-volume simple tasks'
                ]
            },
            
            # Gemini models
            (LLMProvider.GEMINI, 'gemini-2.0-flash-exp'): {
                'strengths': [
                    'FREE (experimental)',
                    'Latest Google model',
                    'Multimodal capabilities',
                    'Fast inference'
                ],
                'considerations': [
                    'Experimental - may have rate limits',
                    'Availability may change',
                    'Preview version'
                ],
                'best_for': [
                    'Testing and development',
                    'Cost-free experimentation',
                    'Multimodal tasks'
                ]
            },
            (LLMProvider.GEMINI, 'gemini-1.5-pro'): {
                'strengths': [
                    'Excellent reasoning',
                    'Large 2M context window',
                    'Multimodal',
                    'Strong on complex tasks'
                ],
                'considerations': [
                    'More expensive ($1.25/$5.00)',
                    'Slower than Flash models'
                ],
                'best_for': [
                    'Complex analysis',
                    'Long-context tasks',
                    'Research summaries',
                    'Document analysis'
                ]
            },
            (LLMProvider.GEMINI, 'gemini-1.5-flash'): {
                'strengths': [
                    'Balanced cost/performance',
                    '1M context window',
                    'Fast inference',
                    'Good at summaries'
                ],
                'considerations': [
                    'Less capable than Pro',
                    'Better for focused tasks'
                ],
                'best_for': [
                    'Task summaries',
                    'Quick analysis',
                    'High-volume tasks'
                ]
            },
            
            # Perplexity models  
            (LLMProvider.PERPLEXITY, 'llama-3.1-sonar-large-128k-online'): {
                'strengths': [
                    'Web search integration',
                    'Real-time data access',
                    'Up-to-date information',
                    'Citations included'
                ],
                'considerations': [
                    'Higher cost due to web search',
                    'Slower due to search step',
                    'Requires internet connectivity'
                ],
                'best_for': [
                    'Research tasks',
                    'Current events',
                    'Fact-checking',
                    'Market analysis'
                ]
            },
            (LLMProvider.PERPLEXITY, 'llama-3.1-sonar-small-128k-online'): {
                'strengths': [
                    'Web search at lower cost',
                    'Real-time data',
                    'Good for simple research'
                ],
                'considerations': [
                    'Less capable than large model',
                    'Still includes web search overhead'
                ],
                'best_for': [
                    'Simple research',
                    'Quick fact lookups',
                    'News summaries'
                ]
            },
            
            # Claude models
            (LLMProvider.CLAUDE, 'claude-sonnet-4-20250514'): {
                'strengths': [
                    'Excellent reasoning',
                    'Strong at writing',
                    'Good at code',
                    'Nuanced understanding',
                    'Best-in-class for many tasks'
                ],
                'considerations': [
                    'More expensive ($3.00/$15.00)',
                    'API may have rate limits',
                    'Overkill for simple tasks'
                ],
                'best_for': [
                    'Complex analysis',
                    'Creative writing',
                    'Code generation',
                    'High-stakes summaries'
                ]
            },
            (LLMProvider.CLAUDE, 'claude-3-5-haiku-20241022'): {
                'strengths': [
                    'Fast inference',
                    'Good value ($0.80/$4.00)',
                    'Still quite capable',
                    'Claude quality at lower cost'
                ],
                'considerations': [
                    'Less capable than Sonnet',
                    'May struggle with very complex tasks'
                ],
                'best_for': [
                    'Quick summaries',
                    'Standard tasks',
                    'Cost-conscious Claude usage'
                ]
            },
        }
        
        # Look up metadata
        key = (provider, model)
        if key in metadata_db:
            return metadata_db[key]
        
        # Default metadata for unknown models
        return {
            'strengths': ['General purpose model'],
            'considerations': ['Model metadata not available'],
            'best_for': ['General tasks']
        }
    
    def estimate_last_request_cost(self) -> Optional[float]:
        """Estimate cost of the last request."""
        if not self._last_response or not self._last_response.usage:
            return None
        
        provider = self._last_response.provider
        if provider not in self._providers:
            return None
        
        provider_obj = self._providers[provider]
        usage = self._last_response.usage
        
        return provider_obj.estimate_cost(
            input_tokens=usage.get('prompt_tokens', 0),
            output_tokens=usage.get('completion_tokens', 0),
            model=self._last_response.model
        )
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        status = {}
        
        for provider, provider_status in self._provider_status.items():
            status[provider.value] = {
                'available': provider_status.available,
                'in_cooldown': provider_status.is_in_cooldown(),
                'consecutive_failures': provider_status.consecutive_failures,
                'last_error': provider_status.last_error,
                'last_error_time': provider_status.last_error_time.isoformat() 
                    if provider_status.last_error_time else None,
                'cooldown_until': provider_status.cooldown_until.isoformat() 
                    if provider_status.cooldown_until else None
            }
        
        return status
    
    def reset_provider_status(self, provider: Optional[LLMProvider] = None):
        """Reset provider status (clear errors and cooldowns)."""
        if provider:
            if provider in self._provider_status:
                self._provider_status[provider].mark_success()
                logger.info(f"Reset status for {provider.value}")
        else:
            for status in self._provider_status.values():
                status.mark_success()
            logger.info("Reset status for all providers")


# Singleton instance
llm_service = LLMService()