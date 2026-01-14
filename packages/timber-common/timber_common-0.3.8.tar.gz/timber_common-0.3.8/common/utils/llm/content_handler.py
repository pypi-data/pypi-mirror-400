"""
Content Handler - Multi-Strategy Content Processing System

This module implements an intelligent content handling system that progressively
applies different strategies to reduce content size for LLM processing:

1. Full Content - Use as-is if within token limits
2. Chunking with Aggregation - Process in chunks, aggregate results
3. Hierarchical Summarization - Summarize at each nesting level
4. Content Condensing - Extract key data, remove duplicates
5. Emergency Truncation - Last resort with warning message

Each strategy is tried in sequence until the content fits within token limits.
"""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import tiktoken

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of content processing operation."""
    content: Any
    strategy_used: str
    original_size: int
    final_size: int
    original_tokens: int
    final_tokens: int
    reduction_pct: float
    metadata: Dict[str, Any]
    warning: Optional[str] = None


class TokenEstimator:
    """Estimates token count for content."""
    
    def __init__(self, model: str = "gpt-4"):
        """Initialize with encoding for model."""
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def estimate_tokens(self, content: Any) -> int:
        """
        Estimate token count for any content type.
        
        Args:
            content: Content to estimate (dict, list, str, etc.)
            
        Returns:
            Estimated token count
        """
        if content is None:
            return 0
        
        # Convert to string representation
        if isinstance(content, (dict, list)):
            text = json.dumps(content, default=str)
        else:
            text = str(content)
        
        # Count tokens
        try:
            tokens = len(self.encoding.encode(text))
            return tokens
        except Exception as e:
            logger.warning(f"Token estimation failed: {e}, using char count / 4")
            return len(text) // 4  # Rough approximation


class ChunkingAggregator:
    """
    Processes large datasets in chunks and aggregates results.
    
    This strategy is ideal for:
    - Large lists of similar items (news articles, financial data)
    - Sequential data that can be processed independently
    - Situations where you need comprehensive coverage
    """
    
    def __init__(self, llm_service, chunk_size: int = 20):
        """
        Initialize chunking aggregator.
        
        Args:
            llm_service: LLM service for processing chunks
            chunk_size: Number of items per chunk
        """
        self.llm_service = llm_service
        self.chunk_size = chunk_size
    
    def process(
        self,
        content: Any,
        task_type: str,
        max_tokens: int = 8000
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process content in chunks and aggregate results.
        
        Args:
            content: Content to process
            task_type: Type of task (for prompt customization)
            max_tokens: Maximum tokens per chunk
            
        Returns:
            Tuple of (aggregated_summary, metadata)
        """
        chunks = self._create_chunks(content)
        
        if not chunks:
            return str(content), {"chunks_processed": 0}
        
        logger.info(f"Processing {len(chunks)} chunks for aggregation")
        
        # Process each chunk
        chunk_summaries = []
        total_tokens = 0
        
        for i, chunk in enumerate(chunks):
            try:
                prompt = self._build_chunk_prompt(chunk, task_type, i + 1, len(chunks))
                
                response = self.llm_service.generate_completion(
                    prompt=prompt,
                    max_tokens=500,  # Each chunk summary should be concise
                    temperature=0.3
                )
                
                summary = response.get('response', '')
                chunk_summaries.append(summary)
                total_tokens += response.get('usage', {}).get('total_tokens', 0)
                
            except Exception as e:
                logger.error(f"Error processing chunk {i + 1}: {e}")
                chunk_summaries.append(f"[Chunk {i + 1} processing failed]")
        
        # Aggregate all chunk summaries
        aggregated = self._aggregate_summaries(chunk_summaries, task_type)
        
        metadata = {
            "chunks_processed": len(chunks),
            "chunk_size": self.chunk_size,
            "total_tokens_used": total_tokens,
            "summaries_generated": len(chunk_summaries)
        }
        
        return aggregated, metadata
    
    def _create_chunks(self, content: Any) -> List[Any]:
        """Create chunks from content."""
        if isinstance(content, list):
            # Chunk lists by size
            return [
                content[i:i + self.chunk_size]
                for i in range(0, len(content), self.chunk_size)
            ]
        
        elif isinstance(content, dict):
            # For dicts, chunk by top-level keys
            items = list(content.items())
            return [
                dict(items[i:i + self.chunk_size])
                for i in range(0, len(items), self.chunk_size)
            ]
        
        elif isinstance(content, str) and len(content) > 10000:
            # Chunk very long strings by paragraphs or sentences
            paragraphs = content.split('\n\n')
            if len(paragraphs) > 1:
                return [
                    '\n\n'.join(paragraphs[i:i + 5])
                    for i in range(0, len(paragraphs), 5)
                ]
            else:
                # Fallback: chunk by character count
                return [
                    content[i:i + 5000]
                    for i in range(0, len(content), 5000)
                ]
        
        # Can't chunk this content
        return []
    
    def _build_chunk_prompt(
        self,
        chunk: Any,
        task_type: str,
        chunk_num: int,
        total_chunks: int
    ) -> str:
        """Build prompt for processing a single chunk."""
        chunk_str = json.dumps(chunk, indent=2, default=str) if isinstance(chunk, (dict, list)) else str(chunk)
        
        return f"""Analyze this data chunk ({chunk_num} of {total_chunks}):

{chunk_str}

Task: {task_type}

Provide a concise summary of the key information in this chunk.
Focus on:
- Main findings or trends
- Important metrics or numbers
- Critical events or developments
- Key entities mentioned

Keep your summary under 200 words."""
    
    def _aggregate_summaries(self, summaries: List[str], task_type: str) -> str:
        """Aggregate individual chunk summaries into final summary."""
        combined = "\n\n".join([
            f"Chunk {i + 1}: {summary}"
            for i, summary in enumerate(summaries)
        ])
        
        # If we have many chunks, we might need to summarize the summaries
        if len(summaries) > 10:
            try:
                prompt = f"""Synthesize these chunk summaries into a comprehensive final summary:

{combined}

Task: {task_type}

Create a unified summary that:
1. Identifies major themes across all chunks
2. Highlights key metrics and trends
3. Notes important developments
4. Provides overall conclusions

Keep the final summary under 500 words."""
                
                response = self.llm_service.generate_completion(
                    prompt=prompt,
                    max_tokens=800,
                    temperature=0.3
                )
                
                return response.get('response', combined)
                
            except Exception as e:
                logger.error(f"Error aggregating summaries: {e}")
                return combined
        
        return combined


class HierarchicalSummarizer:
    """
    Creates hierarchical summaries of nested data structures.
    
    This strategy is ideal for:
    - Deeply nested JSON/dict structures
    - Complex hierarchical data
    - Situations where structure matters
    """
    
    def __init__(self, llm_service, max_depth: int = 3):
        """
        Initialize hierarchical summarizer.
        
        Args:
            llm_service: LLM service for generating summaries
            max_depth: Maximum depth to preserve in hierarchy
        """
        self.llm_service = llm_service
        self.max_depth = max_depth
    
    def process(
        self,
        content: Any,
        preserve_structure: bool = True,
        max_tokens: int = 8000
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Create hierarchical summary of content.
        
        Args:
            content: Content to summarize
            preserve_structure: Whether to maintain hierarchy
            max_tokens: Target token limit
            
        Returns:
            Tuple of (summarized_content, metadata)
        """
        logger.info("Creating hierarchical summary")
        
        summarized, stats = self._summarize_recursive(content, depth=0, max_tokens=max_tokens)
        
        metadata = {
            "levels_processed": stats.get('max_depth', 0),
            "nodes_summarized": stats.get('nodes_summarized', 0),
            "nodes_preserved": stats.get('nodes_preserved', 0),
            "structure_preserved": preserve_structure
        }
        
        return summarized, metadata
    
    def _summarize_recursive(
        self,
        content: Any,
        depth: int = 0,
        max_tokens: int = 8000
    ) -> Tuple[Any, Dict[str, Any]]:
        """Recursively summarize nested structures."""
        stats = {
            'max_depth': depth,
            'nodes_summarized': 0,
            'nodes_preserved': 0
        }
        
        # Base case: primitive types or max depth reached
        if not isinstance(content, (dict, list)) or depth >= self.max_depth:
            stats['nodes_preserved'] += 1
            return content, stats
        
        # Handle dictionaries
        if isinstance(content, dict):
            result = {}
            
            for key, value in content.items():
                # Recursively process nested structures
                if isinstance(value, (dict, list)) and depth < self.max_depth - 1:
                    summarized, sub_stats = self._summarize_recursive(
                        value,
                        depth + 1,
                        max_tokens // len(content) if len(content) > 0 else max_tokens
                    )
                    result[key] = summarized
                    
                    # Update stats
                    stats['max_depth'] = max(stats['max_depth'], sub_stats['max_depth'])
                    stats['nodes_summarized'] += sub_stats['nodes_summarized']
                    stats['nodes_preserved'] += sub_stats['nodes_preserved']
                
                # Summarize large text fields
                elif isinstance(value, str) and len(value) > 1000:
                    result[key] = self._summarize_text(value, key)
                    stats['nodes_summarized'] += 1
                
                # Preserve small values
                else:
                    result[key] = value
                    stats['nodes_preserved'] += 1
            
            return result, stats
        
        # Handle lists
        elif isinstance(content, list):
            # If list is too long, sample or summarize
            if len(content) > 50:
                # Take first 25 and last 25 items
                sampled = content[:25] + content[-25:]
                stats['nodes_summarized'] += 1
                
                # Add summary note
                result = {
                    "_summary": f"List truncated from {len(content)} to 50 items (first 25 and last 25)",
                    "_original_length": len(content),
                    "items": sampled
                }
                return result, stats
            
            else:
                # Process each item
                result = []
                for item in content:
                    if isinstance(item, (dict, list)):
                        summarized, sub_stats = self._summarize_recursive(
                            item,
                            depth + 1,
                            max_tokens // len(content) if len(content) > 0 else max_tokens
                        )
                        result.append(summarized)
                        
                        stats['max_depth'] = max(stats['max_depth'], sub_stats['max_depth'])
                        stats['nodes_summarized'] += sub_stats['nodes_summarized']
                        stats['nodes_preserved'] += sub_stats['nodes_preserved']
                    else:
                        result.append(item)
                        stats['nodes_preserved'] += 1
                
                return result, stats
        
        return content, stats
    
    def _summarize_text(self, text: str, field_name: str = "") -> str:
        """Summarize a long text field."""
        # Extract key information
        if len(text) < 2000:
            return text
        
        # For very long text, extract key sentences
        sentences = text.split('. ')
        
        if len(sentences) > 10:
            # Keep first 3 and last 2 sentences
            summary = '. '.join(sentences[:3] + ['...'] + sentences[-2:])
            return f"{summary} [Summarized from {len(text)} chars]"
        
        return text[:500] + f"... [Truncated from {len(text)} chars]"


class ContentHandler:
    """
    Main content handler that orchestrates multi-strategy processing.
    
    Strategy sequence:
    1. Full Content - If within limits
    2. Chunking with Aggregation - For large datasets
    3. Hierarchical Summarization - For nested structures
    4. Content Condensing - Extract key data
    5. Emergency Truncation - Last resort
    """
    
    def __init__(
        self,
        llm_service=None,
        default_max_tokens: int = 8000,
        emergency_max_tokens: int = 100000
    ):
        """
        Initialize content handler.
        
        Args:
            llm_service: LLM service for processing (required for chunking)
            default_max_tokens: Target token limit for processed content
            emergency_max_tokens: Absolute maximum before truncation
        """
        self.llm_service = llm_service
        self.default_max_tokens = default_max_tokens
        self.emergency_max_tokens = emergency_max_tokens
        self.token_estimator = TokenEstimator()
        
        # Initialize strategy handlers
        if llm_service:
            self.chunking_aggregator = ChunkingAggregator(llm_service)
        else:
            self.chunking_aggregator = None
            
        self.hierarchical_summarizer = HierarchicalSummarizer(llm_service) if llm_service else None
        
        # Import content condenser
        try:
            from common.utils.llm.content_condenser import ContentCondenser
            self.content_condenser = ContentCondenser()
        except ImportError:
            logger.warning("ContentCondenser not available, will skip condensing strategy")
            self.content_condenser = None
    
    def process_content(
        self,
        content: Any,
        task_type: str = "analysis",
        max_tokens: Optional[int] = None,
        preserve_keys: List[str] = None
    ) -> ProcessingResult:
        """
        Process content using the most appropriate strategy.
        
        Args:
            content: Content to process
            task_type: Type of task (for prompt customization)
            max_tokens: Maximum tokens (uses default if not specified)
            preserve_keys: Keys to always preserve (for condensing)
            
        Returns:
            ProcessingResult with processed content and metadata
        """
        if max_tokens is None:
            max_tokens = self.default_max_tokens
        
        if preserve_keys is None:
            preserve_keys = []
        
        # Estimate initial token count
        original_tokens = self.token_estimator.estimate_tokens(content)
        original_size = len(json.dumps(content, default=str)) if isinstance(content, (dict, list)) else len(str(content))
        
        logger.info(f"Processing content: {original_tokens} tokens, {original_size} chars")
        
        # Strategy 1: Use full content if within limits
        if original_tokens <= max_tokens:
            logger.info("✓ Strategy 1: Using full content (within token limits)")
            return ProcessingResult(
                content=content,
                strategy_used="full_content",
                original_size=original_size,
                final_size=original_size,
                original_tokens=original_tokens,
                final_tokens=original_tokens,
                reduction_pct=0.0,
                metadata={"reason": "Content within token limits"}
            )
        
        logger.info(f"Content exceeds {max_tokens} tokens, trying advanced strategies...")
        
        # Strategy 2: Chunking with Aggregation
        if self.chunking_aggregator and self._is_chunkable(content):
            try:
                logger.info("→ Strategy 2: Trying chunking with aggregation")
                processed, metadata = self.chunking_aggregator.process(
                    content,
                    task_type,
                    max_tokens
                )
                
                # Validate result size
                final_tokens = self.token_estimator.estimate_tokens(processed)
                final_size = len(str(processed))
                
                if final_tokens <= max_tokens:
                    logger.info(f"✓ Strategy 2: Chunking successful ({original_tokens} → {final_tokens} tokens)")
                    return ProcessingResult(
                        content=processed,
                        strategy_used="chunking_aggregation",
                        original_size=original_size,
                        final_size=final_size,
                        original_tokens=original_tokens,
                        final_tokens=final_tokens,
                        reduction_pct=((original_tokens - final_tokens) / original_tokens * 100),
                        metadata=metadata
                    )
                else:
                    logger.info(f"✗ Strategy 2: Still too large ({final_tokens} tokens), trying next strategy")
                    
            except Exception as e:
                logger.error(f"✗ Strategy 2 failed: {e}, trying next strategy")
        
        # Strategy 3: Hierarchical Summarization
        if self.hierarchical_summarizer and isinstance(content, (dict, list)):
            try:
                logger.info("→ Strategy 3: Trying hierarchical summarization")
                processed, metadata = self.hierarchical_summarizer.process(
                    content,
                    preserve_structure=True,
                    max_tokens=max_tokens
                )
                
                # Validate result size
                final_tokens = self.token_estimator.estimate_tokens(processed)
                final_size = len(json.dumps(processed, default=str)) if isinstance(processed, (dict, list)) else len(str(processed))
                
                if final_tokens <= max_tokens:
                    logger.info(f"✓ Strategy 3: Hierarchical summarization successful ({original_tokens} → {final_tokens} tokens)")
                    return ProcessingResult(
                        content=processed,
                        strategy_used="hierarchical_summarization",
                        original_size=original_size,
                        final_size=final_size,
                        original_tokens=original_tokens,
                        final_tokens=final_tokens,
                        reduction_pct=((original_tokens - final_tokens) / original_tokens * 100),
                        metadata=metadata
                    )
                else:
                    logger.info(f"✗ Strategy 3: Still too large ({final_tokens} tokens), trying next strategy")
                    
            except Exception as e:
                logger.error(f"✗ Strategy 3 failed: {e}, trying next strategy")
        
        # Strategy 4: Content Condensing
        if self.content_condenser:
            try:
                logger.info("→ Strategy 4: Trying content condensing")
                processed, stats = self.content_condenser.condense_task_output(
                    content,
                    max_tokens=max_tokens,
                    preserve_keys=preserve_keys
                )
                
                # Validate result size
                final_tokens = self.token_estimator.estimate_tokens(processed)
                final_size = stats.get('final_size', len(str(processed)))
                
                if final_tokens <= max_tokens:
                    logger.info(f"✓ Strategy 4: Content condensing successful ({original_tokens} → {final_tokens} tokens)")
                    return ProcessingResult(
                        content=processed,
                        strategy_used="content_condensing",
                        original_size=original_size,
                        final_size=final_size,
                        original_tokens=original_tokens,
                        final_tokens=final_tokens,
                        reduction_pct=stats.get('reduction_pct', 0),
                        metadata=stats
                    )
                else:
                    logger.info(f"✗ Strategy 4: Still too large ({final_tokens} tokens), using emergency truncation")
                    
            except Exception as e:
                logger.error(f"✗ Strategy 4 failed: {e}, using emergency truncation")
        
        # Strategy 5: Emergency Truncation
        logger.warning("⚠ All strategies failed, using emergency truncation")
        processed, warning = self._emergency_truncate(content, self.emergency_max_tokens)
        final_tokens = self.token_estimator.estimate_tokens(processed)
        final_size = len(str(processed))
        
        return ProcessingResult(
            content=processed,
            strategy_used="emergency_truncation",
            original_size=original_size,
            final_size=final_size,
            original_tokens=original_tokens,
            final_tokens=final_tokens,
            reduction_pct=((original_tokens - final_tokens) / original_tokens * 100),
            metadata={"truncation_point": len(str(processed))},
            warning=warning
        )
    
    def _is_chunkable(self, content: Any) -> bool:
        """Determine if content is suitable for chunking."""
        if isinstance(content, list) and len(content) > 10:
            return True
        
        if isinstance(content, dict) and len(content) > 5:
            return True
        
        if isinstance(content, str) and len(content) > 10000:
            return True
        
        return False
    
    def _emergency_truncate(self, content: Any, max_chars: int) -> Tuple[str, str]:
        """
        Emergency truncation as last resort.
        
        Args:
            content: Content to truncate
            max_chars: Maximum characters
            
        Returns:
            Tuple of (truncated_content, warning_message)
        """
        content_str = json.dumps(content, indent=2, default=str) if isinstance(content, (dict, list)) else str(content)
        
        if len(content_str) <= max_chars:
            return content_str, None
        
        # Calculate how much we're removing
        removed_pct = ((len(content_str) - max_chars) / len(content_str) * 100)
        
        warning = f"""
⚠️ EMERGENCY TRUNCATION APPLIED ⚠️

This dataset was too large for all available processing strategies.
- Original size: {len(content_str):,} characters
- Truncated to: {max_chars:,} characters
- Removed: {removed_pct:.1f}% of data

IMPORTANT: This analysis is based on incomplete data.
Further analysis is required to consider the entire dataset.

Recommendations:
1. Reduce source data (fetch fewer items, shorter time ranges)
2. Increase token limits if provider allows
3. Use time-based filtering or sampling at source
4. Consider processing dataset in multiple separate analyses
"""
        
        # Truncate and add warning
        truncated = content_str[:max_chars - len(warning)]
        result = truncated + warning
        
        return result, warning


def create_content_handler(llm_service=None, **kwargs) -> ContentHandler:
    """
    Factory function to create a ContentHandler instance.
    
    Args:
        llm_service: LLM service instance
        **kwargs: Additional configuration options
        
    Returns:
        Configured ContentHandler instance
    """
    return ContentHandler(llm_service=llm_service, **kwargs)