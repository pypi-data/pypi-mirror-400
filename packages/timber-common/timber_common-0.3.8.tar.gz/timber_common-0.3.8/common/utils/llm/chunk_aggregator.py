# chunk_aggregator.py
"""
Chunking with Aggregation Strategy

Processes large content by:
1. Splitting into manageable chunks
2. Summarizing each chunk in parallel
3. Aggregating chunk summaries into final result

This enables processing of unlimited data while maintaining quality.

FIXED: Use correct LLMService method names (generate_task_summary, not generate_completion)
"""

import json
import logging
import asyncio
import inspect
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ChunkAggregator:
    """
    Processes large content through chunking and aggregation.
    
    Strategy:
    - Split content into chunks of max_size tokens
    - Process chunks in parallel (or sequentially if needed)
    - Summarize each chunk using LLM
    - Aggregate chunk summaries into final summary
    """
    
    def __init__(self, llm_service):
        """
        Initialize chunk aggregator.
        
        Args:
            llm_service: LLM service for generating summaries
        """
        self.llm_service = llm_service
        self.default_chunk_size = 5000  # tokens
        self.max_parallel = 5  # Process 5 chunks at once
        
        # FIXED: Check for the correct method name (generate_task_summary)
        # The LLMService uses generate_task_summary, not generate_completion
        try:
            self.is_async = inspect.iscoroutinefunction(
                getattr(self.llm_service, 'generate_task_summary', None)
            )
        except:
            self.is_async = False
        
    async def process_in_chunks(
        self,
        content: Dict[str, Any],
        task_name: str,
        task_description: str,
        chunk_size: int = 5000,
        max_chunks: int = 50
    ) -> Optional[Dict[str, Any]]:
        """
        Process content by chunking and aggregation.
        
        Args:
            content: Content to process
            task_name: Task name for context
            task_description: Task description
            chunk_size: Target chunk size in tokens
            max_chunks: Maximum number of chunks to process
            
        Returns:
            Aggregated result or None if processing fails
        """
        logger.info(f"🔄 Starting chunk aggregation: chunk_size={chunk_size}, max_chunks={max_chunks}")
        
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Split content into chunks
            chunks = self._split_into_chunks(content, chunk_size, max_chunks)
            
            if not chunks:
                logger.warning("⚠️ No chunks created, content might be empty")
                return None
            
            logger.info(f"Processing {len(chunks)} chunks for aggregation")
            
            # Step 2: Process each chunk (summarize)
            chunk_summaries = await self._process_chunks_parallel(
                chunks, task_name, task_description
            )
            
            if not chunk_summaries:
                logger.warning("⚠️ No chunk summaries generated")
                return None
            
            logger.info(f"✅ Generated {len(chunk_summaries)} chunk summaries")
            
            # Step 3: Aggregate chunk summaries
            final_summary = await self._aggregate_summaries(
                chunk_summaries, task_name, task_description
            )
            
            if not final_summary:
                logger.warning("⚠️ Failed to aggregate chunk summaries")
                return None
            
            # Add metadata
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                'aggregated_summary': final_summary,
                'chunk_count': len(chunks),
                'summary_count': len(chunk_summaries),
                '_metadata': {
                    'processing_tier': 'CHUNKING_AGGREGATION',
                    'chunks_processed': len(chunks),
                    'llm_calls': len(chunks) + 1,  # One per chunk + aggregation
                    'processing_time_seconds': processing_time,
                    'chunk_size_tokens': chunk_size,
                    'parallel_processing': True
                }
            }
            
            logger.info(f"✅ Chunk aggregation complete: {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Chunk aggregation failed: {e}", exc_info=True)
            return None
    
    def _split_into_chunks(
        self,
        content: Dict[str, Any],
        chunk_size: int,
        max_chunks: int
    ) -> List[Dict[str, Any]]:
        """
        Split content into chunks.
        
        Strategy depends on content structure:
        - List of items: chunk by items
        - Dict with sections: chunk by sections
        - Large strings: chunk by characters
        """
        chunks = []
        
        try:
            # Strategy 1: Content is a list
            if isinstance(content, list):
                chunks = self._chunk_list(content, chunk_size, max_chunks)
            
            # Strategy 2: Content is a dict with list values
            elif isinstance(content, dict):
                # Check if any values are lists
                has_lists = any(isinstance(v, list) for v in content.values())
                
                if has_lists:
                    # Chunk each list separately
                    for key, value in content.items():
                        if isinstance(value, list) and len(value) > 10:
                            list_chunks = self._chunk_list(value, chunk_size, max_chunks)
                            for i, chunk in enumerate(list_chunks):
                                chunks.append({
                                    f'{key}_chunk_{i}': chunk,
                                    '_chunk_info': {
                                        'original_key': key,
                                        'chunk_index': i,
                                        'total_chunks': len(list_chunks)
                                    }
                                })
                        else:
                            # Small value, keep as is
                            if not chunks or len(chunks) == 0:
                                chunks.append({key: value})
                            else:
                                chunks[0][key] = value
                else:
                    # Dict with primitive values - chunk by keys
                    chunks = self._chunk_dict(content, chunk_size, max_chunks)
            
            else:
                # Single primitive value, wrap in chunk
                chunks = [{'content': content}]
            
            # Limit to max_chunks
            if len(chunks) > max_chunks:
                logger.warning(f"⚠️ Limiting chunks from {len(chunks)} to {max_chunks}")
                chunks = chunks[:max_chunks]
                
                # Add notice to last chunk
                chunks.append({
                    '_truncation_notice': {
                        'message': f'Content truncated to {max_chunks} chunks',
                        'original_chunks': len(chunks),
                        'chunks_processed': max_chunks
                    }
                })
        
        except Exception as e:
            logger.error(f"❌ Error splitting into chunks: {e}", exc_info=True)
            chunks = []
        
        return chunks
    
    def _chunk_list(
        self,
        items: List[Any],
        chunk_size: int,
        max_chunks: int
    ) -> List[List[Any]]:
        """Chunk a list into smaller lists."""
        # Estimate items per chunk (rough: 500 tokens per item on average)
        items_per_chunk = max(1, chunk_size // 500)
        
        chunks = []
        for i in range(0, len(items), items_per_chunk):
            chunk = items[i:i + items_per_chunk]
            chunks.append(chunk)
            
            if len(chunks) >= max_chunks:
                break
        
        return chunks
    
    def _chunk_dict(
        self,
        data: Dict[str, Any],
        chunk_size: int,
        max_chunks: int
    ) -> List[Dict[str, Any]]:
        """Chunk a dictionary by grouping keys."""
        chunks = []
        current_chunk = {}
        current_size = 0
        
        for key, value in data.items():
            try:
                # Estimate size
                value_json = json.dumps(value, default=str)
                value_size = len(value_json) // 4  # Rough token estimate
                
                if current_size + value_size > chunk_size and current_chunk:
                    # Current chunk full, start new one
                    chunks.append(current_chunk)
                    current_chunk = {}
                    current_size = 0
                    
                    if len(chunks) >= max_chunks:
                        break
                
                current_chunk[key] = value
                current_size += value_size
            except Exception as e:
                logger.warning(f"⚠️ Error processing key {key}: {e}")
                continue
        
        # Add final chunk
        if current_chunk and len(chunks) < max_chunks:
            chunks.append(current_chunk)
        
        return chunks
    
    async def _process_chunks_parallel(
        self,
        chunks: List[Any],
        task_name: str,
        task_description: str
    ) -> List[str]:
        """
        Process chunks in parallel.
        
        Processes up to max_parallel chunks at once for speed.
        """
        chunk_summaries = []
        
        try:
            # Process in batches
            for i in range(0, len(chunks), self.max_parallel):
                batch = chunks[i:i + self.max_parallel]
                
                logger.debug(f"🔄 Processing chunk batch {i // self.max_parallel + 1}/{(len(chunks) + self.max_parallel - 1) // self.max_parallel}")
                
                # Process batch in parallel
                tasks = [
                    self._summarize_chunk(chunk, idx + i, task_name, task_description)
                    for idx, chunk in enumerate(batch)
                ]
                
                batch_summaries = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter out errors and collect results
                for idx, summary in enumerate(batch_summaries):
                    if isinstance(summary, Exception):
                        logger.error(f"Error processing chunk {i + idx + 1}: {summary}")
                    elif summary:
                        chunk_summaries.append(summary)
        
        except Exception as e:
            logger.error(f"❌ Error processing chunks in parallel: {e}", exc_info=True)
        
        return chunk_summaries
    
    async def _summarize_chunk(
        self,
        chunk: Any,
        chunk_index: int,
        task_name: str,
        task_description: str
    ) -> Optional[str]:
        """
        Summarize a single chunk using LLM.
        
        FIXED: Uses generate_task_summary method (not generate_completion).
        
        Args:
            chunk: Chunk data
            chunk_index: Index of this chunk
            task_name: Task name
            task_description: Task description
            
        Returns:
            Summary text or None if failed
        """
        try:
            # Build summarization request
            chunk_task_name = f"{task_name} - Chunk {chunk_index + 1}"
            chunk_task_desc = f"{task_description}\n\nThis is chunk {chunk_index + 1} of the data. Summarize the key findings from this chunk."
            chunk_output = {'chunk_data': chunk}
            
            # FIXED: Call the correct method - generate_task_summary, not generate_completion
            if self.is_async:
                result = await self.llm_service.generate_task_summary(
                    task_name=chunk_task_name,
                    task_description=chunk_task_desc,
                    task_output=chunk_output,
                    context={}
                )
            else:
                # Synchronous call, run in executor to not block
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.llm_service.generate_task_summary(
                        task_name=chunk_task_name,
                        task_description=chunk_task_desc,
                        task_output=chunk_output,
                        context={}
                    )
                )
            
            if result:
                # Handle both dict and string responses
                if isinstance(result, dict):
                    summary = result.get('summary') or result.get('analysis') or str(result)
                else:
                    summary = str(result)
                
                logger.debug(f"✅ Chunk {chunk_index + 1} summarized ({len(summary)} chars)")
                return summary
            else:
                logger.warning(f"⚠️ Chunk {chunk_index + 1} returned empty result")
                return None
                
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_index + 1}: {e}")
            return None
    
    async def _aggregate_summaries(
        self,
        chunk_summaries: List[str],
        task_name: str,
        task_description: str
    ) -> Optional[str]:
        """
        Aggregate chunk summaries into final summary.
        
        FIXED: Uses generate_task_summary method (not generate_completion).
        
        Args:
            chunk_summaries: List of chunk summaries
            task_name: Task name
            task_description: Task description
            
        Returns:
            Final aggregated summary
        """
        try:
            # Combine chunk summaries
            combined_summaries = {
                f'chunk_{i+1}_summary': summary
                for i, summary in enumerate(chunk_summaries)
            }
            
            # Build aggregation request
            agg_task_name = f"{task_name} - Final Aggregation"
            agg_task_desc = f"{task_description}\n\nThese are summaries from {len(chunk_summaries)} chunks of data. Provide a comprehensive final summary that synthesizes all chunks."
            
            # FIXED: Call the correct method - generate_task_summary, not generate_completion
            if self.is_async:
                result = await self.llm_service.generate_task_summary(
                    task_name=agg_task_name,
                    task_description=agg_task_desc,
                    task_output=combined_summaries,
                    context={'chunk_count': len(chunk_summaries)}
                )
            else:
                # Synchronous call, run in executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.llm_service.generate_task_summary(
                        task_name=agg_task_name,
                        task_description=agg_task_desc,
                        task_output=combined_summaries,
                        context={'chunk_count': len(chunk_summaries)}
                    )
                )
            
            if result:
                # Handle both dict and string responses
                if isinstance(result, dict):
                    final_summary = result.get('summary') or result.get('analysis') or str(result)
                else:
                    final_summary = str(result)
                
                logger.info(f"✅ Final aggregation complete ({len(final_summary)} chars)")
                return final_summary
            else:
                logger.warning("⚠️ Final aggregation returned empty result")
                return None
                
        except Exception as e:
            logger.error(f"Error aggregating summaries: {e}")
            return None