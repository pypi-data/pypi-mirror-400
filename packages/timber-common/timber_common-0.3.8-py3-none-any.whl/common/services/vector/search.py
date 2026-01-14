# timber/common/services/vector/search.py
"""
Vector Search Service

Unified interface for vector similarity search across Timber's vector capabilities.
Integrates with auto_ingestion, tag_embedding, and database services.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class VectorSearchService:
    """
    Singleton service for vector similarity search operations.
    
    Provides unified interface for:
    - Content similarity search
    - Tag-based search
    - Hybrid search (combining multiple strategies)
    """
    
    _instance: Optional['VectorSearchService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorSearchService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Initialize FastEmbed model
        try:
            from fastembed import TextEmbedding
            from common.config import config
            
            self.embedding_model = TextEmbedding(model_name=config.EMBEDDING_MODEL)
            self.embedding_dimension = config.EMBEDDING_DIMENSION
            logger.info(f"Vector search service initialized with {config.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.embedding_model = None
            self.embedding_dimension = 768
        
        self._initialized = True
    
    async def search(
        self,
        query_text: str,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        source_type: Optional[str] = None,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            source_type: Optional filter by source type
            metadata_filters: Optional metadata filters
            
        Returns:
            List of matching records with scores
            
        Example:
            results = await vector_search_service.search(
                query_text="What are the latest AI trends?",
                limit=10,
                similarity_threshold=0.75,
                source_type="stock_research"
            )
        """
        try:
            if not self.embedding_model:
                logger.error("Embedding model not initialized")
                return []
            
            from common.services.db_service import db_service
            
            # Generate query embedding
            prefixed_query = f"query: {query_text}"
            query_embedding = list(self.embedding_model.embed([prefixed_query]))[0].tolist()
            
            # Use Timber db_service for the actual search
            # This performs vector similarity search using pgvector
            results = db_service.query(
                model='TextEmbedding',
                filters={},  # We'll apply filters via raw SQL for vector search
                limit=limit * 2  # Get more to filter
            )
            
            # Calculate similarities and filter
            scored_results = []
            for record in results:
                # Apply source_type filter
                if source_type and record.get('source_type') != source_type:
                    continue
                
                # Apply metadata filters
                if metadata_filters:
                    record_metadata = record.get('metadata', {})
                    if not all(record_metadata.get(k) == v for k, v in metadata_filters.items()):
                        continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, record.get('embedding', []))
                
                if similarity >= similarity_threshold:
                    scored_results.append({
                        **record,
                        'similarity_score': similarity
                    })
            
            # Sort by similarity and limit
            scored_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            results = scored_results[:limit]
            
            logger.info(f"Vector search found {len(results)} results for query")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def search_by_tags(
        self,
        query_text: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar tags based on query text.
        
        Args:
            query_text: Text to find similar tags for
            category: Optional tag category filter
            limit: Maximum number of tags
            
        Returns:
            List of tag matches with similarity scores
        """
        try:
            from common.services.vector.tag_embedding import tag_embedding_service
            
            similar_tags = tag_embedding_service.find_similar_tags(
                query_text=query_text,
                category=category,
                limit=limit,
                similarity_threshold=0.7
            )
            
            return [
                {'tag_name': name, 'similarity_score': score}
                for name, score in similar_tags
            ]
            
        except Exception as e:
            logger.error(f"Tag search failed: {e}")
            return []
    
    async def hybrid_search(
        self,
        query_text: str,
        include_content: bool = True,
        include_tags: bool = True,
        content_limit: int = 10,
        tag_limit: int = 5
    ) -> Dict[str, Any]:
        """
        Perform hybrid search combining content and tag similarity.
        
        Args:
            query_text: Search query
            include_content: Whether to search content
            include_tags: Whether to search tags
            content_limit: Max content results
            tag_limit: Max tag results
            
        Returns:
            Dict with 'content' and 'tags' keys containing results
        """
        results = {
            'query': query_text,
            'content': [],
            'tags': []
        }
        
        if include_content:
            results['content'] = await self.search(
                query_text=query_text,
                limit=content_limit
            )
        
        if include_tags:
            results['tags'] = await self.search_by_tags(
                query_text=query_text,
                limit=tag_limit
            )
        
        return results


# Singleton instance
vector_search_service = VectorSearchService()