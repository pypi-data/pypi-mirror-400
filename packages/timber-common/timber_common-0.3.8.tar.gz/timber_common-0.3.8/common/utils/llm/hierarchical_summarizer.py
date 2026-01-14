# hierarchical_summarizer.py
"""
Hierarchical Summarization Strategy

Processes large nested content by:
1. Summarizing leaf nodes (bottom-up)
2. Summarizing groups of summaries
3. Building summary tree until final summary

This maintains hierarchical structure and relationships between data.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class HierarchicalSummarizer:
    """
    Processes content through hierarchical summarization.
    
    Strategy:
    - Identify structure levels in content
    - Summarize at each level (bottom-up)
    - Aggregate level summaries
    - Build final summary from top-level summaries
    """
    
    def __init__(self, llm_service):
        """
        Initialize hierarchical summarizer.
        
        Args:
            llm_service: LLM service for generating summaries
        """
        self.llm_service = llm_service
        self.max_levels = 5  # Maximum hierarchy depth
        self.items_per_group = 5  # Items to summarize together
        
    async def summarize_hierarchical(
        self,
        content: Dict[str, Any],
        task_name: str,
        task_description: str,
        max_tokens: int = 10000
    ) -> Optional[Dict[str, Any]]:
        """
        Summarize content hierarchically.
        
        Args:
            content: Content to summarize
            task_name: Task name for context
            task_description: Task description
            max_tokens: Target token limit
            
        Returns:
            Hierarchically summarized content
        """
        logger.info("Starting hierarchical summarization")
        
        start_time = datetime.utcnow()
        llm_calls = 0
        
        # Step 1: Analyze structure
        structure = self._analyze_structure(content)
        levels = structure['levels']
        
        logger.info(f"Detected {levels} hierarchy levels")
        
        if levels <= 1:
            # Flat structure, use different strategy
            logger.info("Flat structure detected, using grouped summarization")
            result = await self._summarize_flat_structure(
                content, task_name, task_description
            )
            llm_calls = 1  # Estimate
        else:
            # True hierarchical structure
            logger.info("Hierarchical structure detected, processing bottom-up")
            result, llm_calls = await self._summarize_hierarchical_structure(
                content, structure, task_name, task_description, levels
            )
        
        if not result:
            logger.warning("Hierarchical summarization failed")
            return None
        
        # Check if result fits within token limit
        result_json = json.dumps(result, indent=2, default=str)
        result_tokens = len(result_json) // 4
        
        if result_tokens > max_tokens:
            logger.warning(
                f"Hierarchical result still too large: {result_tokens} > {max_tokens} tokens"
            )
            return None
        
        # Add metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        result['_metadata'] = {
            'processing_tier': 'HIERARCHICAL_SUMMARY',
            'levels': levels,
            'llm_calls': llm_calls,
            'processing_time_seconds': processing_time,
            'hierarchical': True
        }
        
        logger.info(f"Hierarchical summarization complete: {processing_time:.2f}s")
        
        return result
    
    def _analyze_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content structure to determine hierarchy depth.
        
        Returns:
            Dict with structure info: {'levels': int, 'type': str, ...}
        """
        def get_depth(obj, current_depth=1):
            """Recursively find maximum depth."""
            if not isinstance(obj, (dict, list)):
                return current_depth
            
            if isinstance(obj, list):
                if not obj:
                    return current_depth
                return max(get_depth(item, current_depth + 1) for item in obj)
            
            if isinstance(obj, dict):
                if not obj:
                    return current_depth
                return max(get_depth(value, current_depth + 1) for value in obj.values())
            
            return current_depth
        
        depth = get_depth(content)
        
        # Determine structure type
        if isinstance(content, dict):
            structure_type = 'nested_dict'
        elif isinstance(content, list):
            structure_type = 'list'
        else:
            structure_type = 'primitive'
        
        return {
            'levels': depth,
            'type': structure_type,
            'keys': list(content.keys()) if isinstance(content, dict) else None
        }
    
    async def _summarize_flat_structure(
        self,
        content: Dict[str, Any],
        task_name: str,
        task_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Summarize flat (non-hierarchical) structure.
        
        Groups items and summarizes groups, then aggregates.
        """
        # Group content items
        if isinstance(content, dict):
            items = list(content.items())
        elif isinstance(content, list):
            items = list(enumerate(content))
        else:
            items = [('content', content)]
        
        # Process in groups
        group_summaries = []
        
        for i in range(0, len(items), self.items_per_group):
            group = items[i:i + self.items_per_group]
            group_dict = dict(group)
            
            # Summarize group
            summary = await self._summarize_section(
                group_dict,
                f"{task_name} - Group {i // self.items_per_group + 1}",
                task_description
            )
            
            if summary:
                group_summaries.append({
                    'group_index': i // self.items_per_group,
                    'summary': summary
                })
        
        # Aggregate group summaries
        if not group_summaries:
            return None
        
        final_summary = await self._aggregate_section_summaries(
            group_summaries,
            task_name,
            task_description
        )
        
        return {
            'summary': final_summary,
            'groups_processed': len(group_summaries),
            'structure': 'flat'
        }
    
    async def _summarize_hierarchical_structure(
        self,
        content: Dict[str, Any],
        structure: Dict[str, Any],
        task_name: str,
        task_description: str,
        levels: int
    ) -> Tuple[Optional[Dict[str, Any]], int]:
        """
        Summarize true hierarchical structure (bottom-up).
        
        Returns:
            Tuple of (result, llm_calls_count)
        """
        llm_calls = 0
        
        # Build summary tree bottom-up
        current_level = content
        level_summaries = {}
        
        # Process each level
        for level in range(levels, 0, -1):
            logger.debug(f"Processing level {level}")
            
            # Extract items at this level
            level_items = self._extract_level_items(current_level, level)
            
            if not level_items:
                continue
            
            # Summarize items at this level
            summaries = []
            for item_key, item_value in level_items.items():
                summary = await self._summarize_section(
                    {item_key: item_value},
                    f"{task_name} - Level {level} - {item_key}",
                    task_description
                )
                
                if summary:
                    summaries.append({
                        'key': item_key,
                        'summary': summary
                    })
                    llm_calls += 1
            
            level_summaries[f'level_{level}'] = summaries
        
        # Build final summary from all levels
        final_summary = await self._build_final_hierarchical_summary(
            level_summaries,
            task_name,
            task_description
        )
        llm_calls += 1
        
        result = {
            'final_summary': final_summary,
            'level_summaries': level_summaries,
            'structure': 'hierarchical'
        }
        
        return result, llm_calls
    
    def _extract_level_items(
        self,
        content: Any,
        target_level: int,
        current_level: int = 1
    ) -> Dict[str, Any]:
        """
        Extract items at specific hierarchy level.
        
        Args:
            content: Content to traverse
            target_level: Target level to extract
            current_level: Current traversal level
            
        Returns:
            Dict of items at target level
        """
        items = {}
        
        if current_level == target_level:
            # At target level
            if isinstance(content, dict):
                return content
            elif isinstance(content, list):
                return {f'item_{i}': item for i, item in enumerate(content)}
            else:
                return {'value': content}
        
        # Not at target level yet, recurse
        if isinstance(content, dict):
            for key, value in content.items():
                sub_items = self._extract_level_items(value, target_level, current_level + 1)
                for sub_key, sub_value in sub_items.items():
                    items[f'{key}.{sub_key}'] = sub_value
        
        elif isinstance(content, list):
            for i, item in enumerate(content):
                sub_items = self._extract_level_items(item, target_level, current_level + 1)
                for sub_key, sub_value in sub_items.items():
                    items[f'[{i}].{sub_key}'] = sub_value
        
        return items
    
    async def _summarize_section(
        self,
        section: Dict[str, Any],
        section_name: str,
        task_description: str
    ) -> Optional[str]:
        """
        Summarize a single section using LLM.
        
        Args:
            section: Section data to summarize
            section_name: Name of this section
            task_description: Overall task description
            
        Returns:
            Summary text or None
        """
        try:
            summary = self.llm_service.generate_task_summary(
                task_name=section_name,
                task_description=f"{task_description}\n\nSummarize this section's key findings.",
                task_output=section,
                context={},
                return_metadata=False
            )
            
            if summary:
                logger.debug(f"✓ Section summarized: {section_name}")
                return summary
            else:
                logger.warning(f"✗ Section summary failed: {section_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error summarizing section {section_name}: {e}")
            return None
    
    async def _aggregate_section_summaries(
        self,
        section_summaries: List[Dict[str, Any]],
        task_name: str,
        task_description: str
    ) -> Optional[str]:
        """
        Aggregate multiple section summaries.
        
        Args:
            section_summaries: List of section summary dicts
            task_name: Task name
            task_description: Task description
            
        Returns:
            Aggregated summary
        """
        try:
            # Combine summaries
            combined = {
                item.get('key', f'section_{i}'): item['summary']
                for i, item in enumerate(section_summaries)
            }
            
            # Generate aggregated summary
            aggregated = self.llm_service.generate_task_summary(
                task_name=f"{task_name} - Aggregation",
                task_description=f"{task_description}\n\nSynthesize these section summaries into a comprehensive overview.",
                task_output=combined,
                context={'section_count': len(section_summaries)},
                return_metadata=False
            )
            
            if aggregated:
                logger.debug(f"✓ Sections aggregated: {len(section_summaries)} sections")
                return aggregated
            else:
                logger.warning("✗ Section aggregation failed")
                return None
                
        except Exception as e:
            logger.error(f"Error aggregating sections: {e}")
            return None
    
    async def _build_final_hierarchical_summary(
        self,
        level_summaries: Dict[str, List[Dict[str, Any]]],
        task_name: str,
        task_description: str
    ) -> Optional[str]:
        """
        Build final summary from all hierarchy levels.
        
        Args:
            level_summaries: Summaries organized by level
            task_name: Task name
            task_description: Task description
            
        Returns:
            Final hierarchical summary
        """
        try:
            # Combine all levels
            all_summaries = {}
            
            for level_key, summaries in level_summaries.items():
                for summary_item in summaries:
                    key = f"{level_key}.{summary_item['key']}"
                    all_summaries[key] = summary_item['summary']
            
            # Generate final summary
            final = self.llm_service.generate_task_summary(
                task_name=f"{task_name} - Final Hierarchical Summary",
                task_description=f"{task_description}\n\nThese are summaries from multiple hierarchy levels. Provide a comprehensive final summary that captures the overall structure and key findings.",
                task_output=all_summaries,
                context={'hierarchy_levels': len(level_summaries)},
                return_metadata=False
            )
            
            if final:
                logger.info("✓ Final hierarchical summary complete")
                return final
            else:
                logger.warning("✗ Final hierarchical summary failed")
                return None
                
        except Exception as e:
            logger.error(f"Error building final hierarchical summary: {e}")
            return None