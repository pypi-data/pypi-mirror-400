"""
LLM Service for Timber

Provides AI text generation capabilities using LangChain and Google Gemini.
Follows the singleton service pattern used throughout Timber.
"""

import logging
from typing import Optional, Dict, Any, List
from functools import lru_cache

from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

logger = logging.getLogger(__name__)


class LLMService:
    """
    Singleton service for LLM interactions using LangChain.
    
    Responsibilities:
    - Initialize and manage LLM connection
    - Generate summaries and analyses
    - Handle prompt templates
    - Error handling and fallbacks
    """
    
    _instance: Optional['LLMService'] = None
    _chat_model: Optional[ChatGoogleGenerativeAI] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize LLM service on first instantiation."""
        if not self._initialized:
            self._initialize()
            self._initialized = True
    
    def _initialize(self):
        """Initialize LangChain LLM."""
        from common.utils.config import config
        
        api_key = config.LLM_API_KEY
        model_name = config.LLM_MODEL_NAME or "gemini-2.5-flash" #"gemini-1.5-flash"
        
        if not api_key:
            logger.warning("LLM_API_KEY not configured - LLM service will be unavailable")
            self._chat_model = None
            return
        
        try:
            self._chat_model = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.3  # Lower temp for factual summaries
            )
            logger.info(f"✓ LLM Service initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            self._chat_model = None
    
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self._chat_model is not None
    
    def generate_task_summary(
        self,
        task_name: str,
        task_description: str,
        task_output: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Generate a human-readable summary of task execution results.
        
        Args:
            task_name: Name of the task
            task_description: Description from task definition
            task_output: Structured JSON output from task
            context: Additional context (inputs, session data, etc.)
            
        Returns:
            Natural language summary or None if generation fails
        """
        if not self.is_available():
            logger.warning("LLM service not available - cannot generate summary")
            return None
        
        try:
            # Build prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_task_summary_prompt(
                task_name=task_name,
                task_description=task_description,
                task_output=task_output,
                context=context
            )
            
            # Generate summary
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self._chat_model.invoke(messages)
            summary = response.content.strip()
            
            logger.info(f"✓ Generated AI summary for task: {task_name}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate task summary: {e}", exc_info=True)
            return None
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for task summarization."""
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
    
    def _build_task_summary_prompt(
        self,
        task_name: str,
        task_description: str,
        task_output: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build user prompt for task summarization."""
        import json
        
        # Format the output nicely
        output_json = json.dumps(task_output, indent=2, default=str)
        
        # Build context section if available
        context_section = ""
        if context:
            context_json = json.dumps(context, indent=2, default=str)
            context_section = f"\n\nContext:\n{context_json}"
        
        prompt = f"""Task: {task_name}
Description: {task_description}

Output:
{output_json}{context_section}

Provide a concise, human-readable summary of these results. Focus on what was 
accomplished and the key findings."""
        
        return prompt
    
    def generate_response(
        self,
        system_prompt: str,
        user_query: str,
        chat_history: Optional[List[BaseMessage]] = None
    ) -> str:
        """
        Generate a general text response (for non-task uses).
        
        Args:
            system_prompt: System instructions
            user_query: User's query
            chat_history: Optional conversation history
            
        Returns:
            Generated response text
        """
        if not self.is_available():
            return "Error: LLM service is unavailable."
        
        try:
            messages = [SystemMessage(content=system_prompt)]
            
            if chat_history:
                messages.extend(chat_history)
            
            messages.append(HumanMessage(content=user_query))
            
            response = self._chat_model.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error invoking LLM: {e}")
            return "An error occurred during LLM communication."


# Singleton instance
llm_service = LLMService()


# Export
__all__ = ['LLMService', 'llm_service']