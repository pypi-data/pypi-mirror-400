# timber/common/services/vector/tag_embedding.py
"""
Tag Embedding Service

Handles tag-based vector embeddings for semantic search and classification.
Integrates with FastEmbed for generating embeddings.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class TagEmbeddingService:
    """
    Singleton service for managing tag embeddings and semantic tag operations.
    
    Handles:
    - Tag embedding generation
    - Tag similarity search
    - Tag clustering
    - Auto-tagging content based on embeddings
    """
    
    _instance: Optional['TagEmbeddingService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TagEmbeddingService, cls).__new__(cls)
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
            logger.info(f"Tag embedding service initialized with {config.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.embedding_model = None
            self.embedding_dimension = 768
        
        self._initialized = True
    
    def create_tag_embedding(
        self,
        tag_name: str,
        tag_category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create or update a tag embedding.
        
        Args:
            tag_name: Name of the tag
            tag_category: Optional category (e.g., 'sector', 'strategy', 'sentiment')
            metadata: Additional metadata
            
        Returns:
            Tag ID if successful, None otherwise
        """
        try:
            if not self.embedding_model:
                logger.error("Embedding model not initialized")
                return None
            
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tag_model = get_model('Tag')
            
            if not tag_model:
                logger.error("Tag model not found in registry")
                return None
            
            # Generate embedding with nomic-embed prefix for clustering
            prefixed_tag = f"clustering: {tag_name}"
            embedding = list(self.embedding_model.embed([prefixed_tag]))[0].tolist()
            
            with db_service.session_scope() as db_session:
                # Check if tag exists
                existing_tag = db_session.query(tag_model).filter_by(
                    name=tag_name
                ).first()
                
                if existing_tag:
                    # Update existing tag
                    existing_tag.embedding = embedding
                    existing_tag.updated_at = datetime.now(timezone.utc)
                    
                    if tag_category:
                        existing_tag.category = tag_category
                    
                    if metadata:
                        existing_tag.metadata = metadata
                    
                    tag_id = existing_tag.id
                    logger.info(f"Updated tag embedding: {tag_name}")
                else:
                    # Create new tag
                    new_tag = tag_model(
                        id=str(uuid.uuid4()),
                        name=tag_name,
                        category=tag_category,
                        embedding=embedding,
                        metadata=metadata or {},
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    
                    db_session.add(new_tag)
                    db_session.flush()
                    
                    tag_id = new_tag.id
                    logger.info(f"Created tag embedding: {tag_name}")
                
                return tag_id
                
        except Exception as e:
            logger.error(f"Failed to create tag embedding: {e}")
            return None
    
    def find_similar_tags(
        self,
        query_text: str,
        category: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[str, float]]:
        """
        Find tags similar to query text.
        
        Args:
            query_text: Text to find similar tags for
            category: Optional category filter
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of (tag_name, similarity_score) tuples
        """
        try:
            if not self.embedding_model:
                logger.error("Embedding model not initialized")
                return []
            
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tag_model = get_model('Tag')
            
            if not tag_model:
                logger.error("Tag model not found in registry")
                return []
            
            # Generate query embedding with nomic-embed prefix for search queries
            prefixed_query = f"search_query: {query_text}"
            query_embedding = list(self.embedding_model.embed([prefixed_query]))[0].tolist()
            
            with db_service.session_scope() as db_session:
                # Build query
                query = db_session.query(
                    tag_model.name,
                    (1 - tag_model.embedding.cosine_distance(query_embedding)).label('similarity')
                ).filter(
                    (1 - tag_model.embedding.cosine_distance(query_embedding)) >= similarity_threshold
                )
                
                if category:
                    query = query.filter_by(category=category)
                
                results = query.order_by('similarity DESC').limit(limit).all()
                
                similar_tags = [(name, float(similarity)) for name, similarity in results]
                
                logger.debug(f"Found {len(similar_tags)} similar tags for: {query_text}")
                return similar_tags
                
        except Exception as e:
            logger.error(f"Failed to find similar tags: {e}")
            return []
    
    def auto_tag_content(
        self,
        content: str,
        category: Optional[str] = None,
        max_tags: int = 5,
        similarity_threshold: float = 0.75
    ) -> List[str]:
        """
        Automatically tag content based on similarity to existing tags.
        
        Args:
            content: Content to tag
            category: Optional category filter
            max_tags: Maximum number of tags to return
            similarity_threshold: Minimum similarity for tag assignment
            
        Returns:
            List of tag names
        """
        try:
            similar_tags = self.find_similar_tags(
                query_text=content,
                category=category,
                limit=max_tags,
                similarity_threshold=similarity_threshold
            )
            
            tag_names = [tag_name for tag_name, _ in similar_tags]
            
            logger.info(f"Auto-tagged content with {len(tag_names)} tags")
            return tag_names
            
        except Exception as e:
            logger.error(f"Failed to auto-tag content: {e}")
            return []
    
    def batch_create_tag_embeddings(
        self,
        tags: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create embeddings for multiple tags in batch.
        
        Args:
            tags: List of tag dictionaries with 'name', optional 'category', 'metadata'
            
        Returns:
            Dictionary with creation results
        """
        try:
            if not self.embedding_model:
                logger.error("Embedding model not initialized")
                return {'success': 0, 'failed': 0, 'errors': []}
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            # Generate all embeddings at once for efficiency with nomic-embed clustering prefix
            tag_names = [tag['name'] for tag in tags]
            prefixed_names = [f"clustering: {name}" for name in tag_names]
            embeddings = list(self.embedding_model.embed(prefixed_names))
            
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tag_model = get_model('Tag')
            
            if not tag_model:
                logger.error("Tag model not found in registry")
                return results
            
            with db_service.session_scope() as db_session:
                for tag_data, embedding in zip(tags, embeddings):
                    try:
                        tag_name = tag_data['name']
                        tag_category = tag_data.get('category')
                        metadata = tag_data.get('metadata', {})
                        
                        # Check if exists
                        existing = db_session.query(tag_model).filter_by(
                            name=tag_name
                        ).first()
                        
                        if existing:
                            existing.embedding = embedding.tolist()
                            existing.updated_at = datetime.now(timezone.utc)
                            if tag_category:
                                existing.category = tag_category
                            if metadata:
                                existing.metadata = metadata
                        else:
                            new_tag = tag_model(
                                id=str(uuid.uuid4()),
                                name=tag_name,
                                category=tag_category,
                                embedding=embedding.tolist(),
                                metadata=metadata,
                                created_at=datetime.now(timezone.utc),
                                updated_at=datetime.now(timezone.utc)
                            )
                            db_session.add(new_tag)
                        
                        results['success'] += 1
                        
                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append({
                            'tag': tag_data.get('name'),
                            'error': str(e)
                        })
            
            logger.info(
                f"Batch tag embedding complete: "
                f"{results['success']} success, {results['failed']} failed"
            )
            return results
            
        except Exception as e:
            logger.error(f"Batch tag embedding failed: {e}")
            return {'success': 0, 'failed': len(tags), 'errors': [str(e)]}
    
    def get_tag_by_name(
        self,
        tag_name: str
    ) -> Optional[Any]:
        """
        Get a tag by name.
        
        Args:
            tag_name: Tag name
            
        Returns:
            Tag object if found, None otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tag_model = get_model('Tag')
            
            if not tag_model:
                logger.error("Tag model not found in registry")
                return None
            
            with db_service.session_scope() as db_session:
                tag = db_session.query(tag_model).filter_by(name=tag_name).first()
                
                if tag:
                    logger.debug(f"Retrieved tag: {tag_name}")
                else:
                    logger.debug(f"Tag not found: {tag_name}")
                
                return tag
                
        except Exception as e:
            logger.error(f"Failed to get tag: {e}")
            return None
    
    def delete_tag(
        self,
        tag_name: str
    ) -> bool:
        """
        Delete a tag.
        
        Args:
            tag_name: Tag name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tag_model = get_model('Tag')
            
            if not tag_model:
                logger.error("Tag model not found in registry")
                return False
            
            with db_service.session_scope() as db_session:
                tag = db_session.query(tag_model).filter_by(name=tag_name).first()
                
                if not tag:
                    logger.warning(f"Tag not found: {tag_name}")
                    return False
                
                db_session.delete(tag)
                logger.info(f"Deleted tag: {tag_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete tag: {e}")
            return False


# Singleton instance
tag_embedding_service = TagEmbeddingService()