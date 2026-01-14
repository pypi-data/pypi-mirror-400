# content_condenser.py
"""
Intelligent Content Condenser for LLM Input

Instead of truncating and losing data, this module intelligently condenses
large content to fit within token limits while preserving critical information.

Strategies:
1. Extract structured data (metrics, dates, headlines)
2. Deduplicate repetitive content
3. Summarize long text sections
4. Prioritize recent/important information
5. Preserve key financial metrics
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class ContentCondenser:
    """
    Intelligently condenses large content for LLM processing.
    
    Instead of truncating data, this class:
    - Extracts key information from structured data
    - Removes duplicates and repetition
    - Summarizes verbose sections
    - Preserves critical metrics and dates
    """
    
    def __init__(self):
        """Initialize the content condenser."""
        self.extraction_enabled = True
        self.dedup_enabled = True
        self.summarization_enabled = True
    
    def condense_task_output(
        self,
        task_output: Dict[str, Any],
        max_tokens: int = 10000,
        preserve_keys: Optional[List[str]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Intelligently condense task output to fit token limits.
        
        Args:
            task_output: Original task output dictionary
            max_tokens: Target token limit (~4 chars per token)
            preserve_keys: Keys that must be preserved (never condensed)
            
        Returns:
            Tuple of (condensed_output, condensation_stats)
        """
        max_chars = max_tokens * 4  # Rough approximation
        preserve_keys = preserve_keys or []
        
        # Calculate original size
        original_json = json.dumps(task_output, indent=2, default=str)
        original_size = len(original_json)
        
        if original_size <= max_chars:
            logger.debug(f"Content within limits ({original_size} chars)")
            return task_output, {
                'condensed': False,
                'original_size': original_size,
                'final_size': original_size,
                'reduction': 0
            }
        
        logger.info(f"Condensing content from {original_size} chars to ~{max_chars} chars")
        
        condensed = {}
        stats = {
            'condensed': True,
            'original_size': original_size,
            'methods_applied': [],
            'items_preserved': 0,
            'items_extracted': 0,
            'items_deduplicated': 0,
            'items_summarized': 0
        }
        
        for key, value in task_output.items():
            # Always preserve specified keys
            if key in preserve_keys:
                condensed[key] = value
                stats['items_preserved'] += 1
                continue
            
            # Apply intelligent condensing based on data type and content
            if isinstance(value, dict):
                condensed[key], item_stats = self._condense_dict(value, key)
                self._merge_stats(stats, item_stats)
            
            elif isinstance(value, list):
                condensed[key], item_stats = self._condense_list(value, key)
                self._merge_stats(stats, item_stats)
            
            elif isinstance(value, str):
                condensed[key], item_stats = self._condense_string(value, key)
                self._merge_stats(stats, item_stats)
            
            else:
                # Primitive types - keep as is
                condensed[key] = value
        
        # Calculate final size
        final_json = json.dumps(condensed, indent=2, default=str)
        final_size = len(final_json)
        stats['final_size'] = final_size
        stats['reduction'] = original_size - final_size
        stats['reduction_pct'] = (stats['reduction'] / original_size) * 100
        
        # If still too large, apply aggressive summarization
        if final_size > max_chars:
            logger.warning(f"Still too large ({final_size} chars), applying aggressive condensing")
            condensed, aggressive_stats = self._aggressive_condense(condensed, max_chars)
            stats['aggressive_applied'] = True
            self._merge_stats(stats, aggressive_stats)
            
            final_json = json.dumps(condensed, indent=2, default=str)
            stats['final_size'] = len(final_json)
        
        logger.info(
            f"Condensed: {original_size} → {stats['final_size']} chars "
            f"({stats['reduction_pct']:.1f}% reduction)"
        )
        
        return condensed, stats
    
    def _condense_dict(self, data: Dict[str, Any], key_name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Condense dictionary data intelligently."""
        stats = defaultdict(int)
        
        # Special handling for news/article data
        if any(k in key_name.lower() for k in ['news', 'article', 'story']):
            condensed, article_stats = self._condense_news_data(data)
            stats['items_extracted'] += article_stats.get('items_extracted', 0)
            stats['items_summarized'] += article_stats.get('items_summarized', 0)
            return condensed, dict(stats)
        
        # Special handling for financial metrics
        if any(k in key_name.lower() for k in ['fundamental', 'metric', 'financial', 'price']):
            condensed, metric_stats = self._condense_metrics_data(data)
            stats['items_extracted'] += metric_stats.get('items_extracted', 0)
            return condensed, dict(stats)
        
        # General dict condensing
        condensed = {}
        for k, v in data.items():
            if isinstance(v, str) and len(v) > 500:
                condensed[k], _ = self._condense_string(v, k)
                stats['items_summarized'] += 1
            elif isinstance(v, list) and len(v) > 10:
                condensed[k], _ = self._condense_list(v, k)
                stats['items_extracted'] += 1
            else:
                condensed[k] = v
        
        return condensed, dict(stats)
    
    def _condense_news_data(self, news_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Intelligently condense news/article data.
        
        Extracts: headline, summary, date, source, key metrics
        Discards: Full article text, repetitive content
        """
        stats = {'items_extracted': 0, 'items_summarized': 0}
        
        condensed = {}
        
        # Always keep these fields (high value, low size)
        priority_fields = [
            'headline', 'title', 'summary', 'description',
            'date', 'published', 'publishedDate', 'timestamp',
            'source', 'provider', 'publisher',
            'symbol', 'symbols', 'ticker', 'tickers',
            'sentiment', 'score', 'rating'
        ]
        
        # Extract priority fields
        for field in priority_fields:
            if field in news_dict:
                condensed[field] = news_dict[field]
                stats['items_extracted'] += 1
        
        # Extract key metrics from content if present
        if 'content' in news_dict or 'text' in news_dict:
            content = news_dict.get('content') or news_dict.get('text', '')
            if isinstance(content, str):
                # Extract numbers, percentages, dates from content
                metrics = self._extract_key_metrics(content)
                if metrics:
                    condensed['extracted_metrics'] = metrics
                    stats['items_extracted'] += 1
                
                # Keep first 200 chars of content as preview
                if len(content) > 200:
                    condensed['content_preview'] = content[:200] + "..."
                    stats['items_summarized'] += 1
                else:
                    condensed['content'] = content
        
        return condensed, stats
    
    def _condense_metrics_data(self, metrics_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Condense financial metrics data.
        
        Keeps: All numeric metrics, ratios, percentages
        Discards: Verbose descriptions, metadata
        """
        stats = {'items_extracted': 0}
        
        condensed = {}
        
        for key, value in metrics_dict.items():
            # Keep all numeric values (they're compact)
            if isinstance(value, (int, float, bool)):
                condensed[key] = value
                stats['items_extracted'] += 1
            
            # Keep short strings (likely codes, symbols, labels)
            elif isinstance(value, str) and len(value) < 100:
                condensed[key] = value
                stats['items_extracted'] += 1
            
            # For long strings, extract metrics
            elif isinstance(value, str):
                metrics = self._extract_key_metrics(value)
                if metrics:
                    condensed[f"{key}_metrics"] = metrics
                    stats['items_extracted'] += 1
            
            # Keep nested dicts if they're small
            elif isinstance(value, dict):
                dict_size = len(json.dumps(value, default=str))
                if dict_size < 500:
                    condensed[key] = value
                else:
                    # Recursively condense
                    condensed[key], _ = self._condense_metrics_data(value)
                stats['items_extracted'] += 1
        
        return condensed, stats
    
    def _condense_list(self, data: List[Any], key_name: str) -> Tuple[List[Any], Dict[str, Any]]:
        """Condense list data intelligently."""
        stats = {'items_deduplicated': 0, 'items_extracted': 0}
        
        if not data:
            return data, stats
        
        # For lists of news articles - keep most recent
        if any(k in key_name.lower() for k in ['news', 'article', 'story']):
            # Sort by date if possible, keep top 10
            sorted_list = self._sort_by_date(data)
            condensed = sorted_list[:10]  # Keep 10 most recent
            if len(data) > 10:
                stats['items_extracted'] = len(data) - 10
            return condensed, stats
        
        # Deduplicate list items
        if len(data) > 20:
            condensed = self._deduplicate_list(data)
            stats['items_deduplicated'] = len(data) - len(condensed)
            
            # If still too many, sample evenly
            if len(condensed) > 50:
                condensed = self._sample_list(condensed, 50)
                stats['items_extracted'] = len(data) - 50
            
            return condensed, stats
        
        return data, stats
    
    def _condense_string(self, text: str, key_name: str) -> Tuple[str, Dict[str, Any]]:
        """Condense long string data."""
        stats = {'items_summarized': 0}
        
        if len(text) < 500:
            return text, stats
        
        # Extract key metrics from long text
        metrics = self._extract_key_metrics(text)
        
        if metrics:
            # Create condensed version with metrics
            condensed = f"[Condensed: {len(text)} chars] Key metrics: {json.dumps(metrics)}"
            stats['items_summarized'] = 1
            return condensed, stats
        
        # Otherwise, keep first 300 chars
        condensed = text[:300] + f"... [+{len(text)-300} chars]"
        stats['items_summarized'] = 1
        return condensed, stats
    
    def _extract_key_metrics(self, text: str) -> Dict[str, Any]:
        """Extract key metrics from text (numbers, percentages, dates)."""
        if not isinstance(text, str):
            return {}
        
        metrics = {}
        
        # Extract percentages (e.g., "23.5%", "-5.2%")
        percentages = re.findall(r'[-+]?\d+\.?\d*%', text)
        if percentages:
            metrics['percentages'] = percentages[:5]  # Keep top 5
        
        # Extract dollar amounts (e.g., "$1.23M", "$45.67B")
        amounts = re.findall(r'\$\d+\.?\d*[KMB]?', text, re.IGNORECASE)
        if amounts:
            metrics['amounts'] = amounts[:5]
        
        # Extract dates (YYYY-MM-DD format)
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
        if dates:
            metrics['dates'] = dates[:3]
        
        # Extract large numbers (with commas)
        numbers = re.findall(r'\d{1,3}(?:,\d{3})+', text)
        if numbers:
            metrics['numbers'] = numbers[:5]
        
        return metrics
    
    def _sort_by_date(self, items: List[Any]) -> List[Any]:
        """Sort items by date field (most recent first)."""
        def get_date(item):
            if not isinstance(item, dict):
                return datetime.min
            
            # Try various date field names
            for field in ['date', 'published', 'publishedDate', 'timestamp', 'created']:
                if field in item:
                    try:
                        if isinstance(item[field], str):
                            return datetime.fromisoformat(item[field].replace('Z', '+00:00'))
                        return datetime.min
                    except:
                        pass
            return datetime.min
        
        try:
            return sorted(items, key=get_date, reverse=True)
        except:
            return items
    
    def _deduplicate_list(self, items: List[Any]) -> List[Any]:
        """Remove duplicate items from list."""
        if not items:
            return items
        
        # For simple types
        if isinstance(items[0], (str, int, float)):
            return list(dict.fromkeys(items))  # Preserves order
        
        # For dicts, deduplicate by key fields
        if isinstance(items[0], dict):
            seen = set()
            deduped = []
            
            for item in items:
                # Create hash from title/headline/id
                key_fields = ['id', 'title', 'headline', 'url']
                key = None
                for field in key_fields:
                    if field in item:
                        key = item[field]
                        break
                
                if key and key not in seen:
                    seen.add(key)
                    deduped.append(item)
                elif not key:
                    deduped.append(item)  # Can't deduplicate
            
            return deduped
        
        return items
    
    def _sample_list(self, items: List[Any], max_items: int) -> List[Any]:
        """Sample list to keep max_items, evenly distributed."""
        if len(items) <= max_items:
            return items
        
        step = len(items) / max_items
        indices = [int(i * step) for i in range(max_items)]
        return [items[i] for i in indices]
    
    def _aggressive_condense(
        self,
        data: Dict[str, Any],
        max_chars: int
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Apply aggressive condensing when gentle methods aren't enough."""
        stats = {'items_summarized': 0}
        
        condensed = {}
        remaining_chars = max_chars
        
        # Sort keys by importance (heuristic)
        priority_order = []
        normal_order = []
        
        for key in data.keys():
            if any(p in key.lower() for p in ['symbol', 'date', 'price', 'metric', 'summary']):
                priority_order.append(key)
            else:
                normal_order.append(key)
        
        keys_ordered = priority_order + normal_order
        
        for key in keys_ordered:
            value = data[key]
            value_json = json.dumps(value, default=str)
            value_size = len(value_json)
            
            if value_size < remaining_chars * 0.5:  # Use at most 50% for one key
                condensed[key] = value
                remaining_chars -= value_size
            else:
                # Create very condensed version
                if isinstance(value, dict):
                    condensed[key] = {
                        '_condensed': True,
                        '_original_keys': len(value),
                        '_note': 'Content condensed for token limits'
                    }
                elif isinstance(value, list):
                    condensed[key] = f"[List of {len(value)} items - condensed]"
                else:
                    condensed[key] = f"[Condensed: {value_size} chars]"
                
                stats['items_summarized'] += 1
            
            if remaining_chars < 1000:  # Reserve some space
                break
        
        return condensed, stats
    
    def _merge_stats(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Merge statistics from source into target."""
        for key, value in source.items():
            if key in target and isinstance(value, (int, float)):
                target[key] += value
            else:
                target[key] = value


# Singleton instance
content_condenser = ContentCondenser()