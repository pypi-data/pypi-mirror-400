# timber/common/services/vector/auto_ingestion.py
"""
Auto Ingestion Service

Handles automatic data ingestion for LLM agentic capabilities.
Processes embeddings in batches and can be triggered asynchronously via Celery.
Compatible with FastEmbed (nomic-ai/nomic-embed-text-v1.5).
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class AutoIngestionService:
    """
    Singleton service for automatic data ingestion and embedding generation.
    
    Handles:
    - Batch embedding generation
    - Automatic content ingestion
    - Document processing
    - Vector index management
    
    Note: This service can be called both synchronously and via Celery tasks.
    """
    
    _instance: Optional['AutoIngestionService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutoIngestionService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Initialize FastEmbed model
        try:
            from fastembed import TextEmbedding
            from common.config import config, Config
            
            self.embedding_model = TextEmbedding(model_name=config.EMBEDDING_MODEL)
            self.embedding_dimension = config.EMBEDDING_DIMENSION
            self.batch_size = config.BATCH_SIZE
            logger.info(f"Auto Ingestion Service initialized with {config.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.embedding_model = None
            self.embedding_dimension = 768
            self.batch_size = 10
        
        self._initialized = True
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                for i in range(end, max(start + chunk_size // 2, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return chunks
    
    def _process_and_insert_batch(
        self,
        chunks: List[str],
        source_type: str,
        source_id: str,
        metadata: Dict[str, Any]
    ) -> int:
        """
        Process a batch of chunks: generate embeddings and insert.
        
        Args:
            chunks: List of text chunks
            source_type: Type of source
            source_id: ID of source
            metadata: Metadata for chunks
            
        Returns:
            Number of chunks inserted
        """
        try:
            if not self.embedding_model:
                logger.error("Embedding model not initialized")
                return 0
            
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            embedding_model = get_model('TextEmbedding')
            
            if not embedding_model:
                logger.error("TextEmbedding model not found in registry")
                return 0
            
            # Generate embeddings with nomic-embed prefix for documents
            prefixed_chunks = [f"search_document: {chunk}" for chunk in chunks]
            embeddings = list(self.embedding_model.embed(prefixed_chunks))
            
            with db_service.session_scope() as db_session:
                for chunk, embedding in zip(chunks, embeddings):
                    text_embedding = embedding_model(
                        id=str(uuid.uuid4()),
                        content_text=chunk,
                        embedding=embedding.tolist(),
                        source_type=source_type,
                        source_id=source_id,
                        metadata=metadata,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    
                    db_session.add(text_embedding)
            
            logger.info(f"Inserted {len(chunks)} chunks for {source_type}:{source_id}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Failed to process and insert batch: {e}")
            return 0
    
    def ingest_document(
        self,
        document_id: str,
        content: str,
        source_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Ingest a document with batch processing.
        
        Args:
            document_id: Document ID
            content: Document content
            source_type: Type of document
            metadata: Additional metadata
            
        Returns:
            Number of chunks created
        """
        try:
            logger.info(f"Ingesting document: {document_id}")
            
            chunks = self.chunk_text(content, chunk_size=500, overlap=50)
            total_chunks = len(chunks)
            
            logger.info(f"Processing {total_chunks} chunks in batches of {self.batch_size}")
            
            chunk_metadata = metadata or {}
            chunk_metadata.update({
                "document_id": document_id,
                "ingested_at": datetime.now(timezone.utc).isoformat()
            })
            
            total_inserted = 0
            
            for batch_start in range(0, total_chunks, self.batch_size):
                batch_end = min(batch_start + self.batch_size, total_chunks)
                batch_chunks = chunks[batch_start:batch_end]
                
                batch_num = batch_start // self.batch_size + 1
                total_batches = (total_chunks + self.batch_size - 1) // self.batch_size
                
                logger.info(f"Processing batch {batch_num}/{total_batches}")
                
                inserted = self._process_and_insert_batch(
                    batch_chunks,
                    source_type,
                    document_id,
                    chunk_metadata
                )
                
                total_inserted += inserted
            
            logger.info(f"Successfully ingested {total_inserted} chunks total")
            return total_inserted
            
        except Exception as e:
            logger.error(f"Failed to ingest document: {e}")
            return 0
    
    def ingest_stock_research(
        self,
        session_id: str,
        ticker: str,
        research_summary: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Ingest stock research summary.
        
        Args:
            session_id: Research session ID
            ticker: Stock ticker
            research_summary: Research content
            metadata: Additional metadata
            
        Returns:
            Number of chunks created
        """
        try:
            logger.info(f"Ingesting stock research for {ticker}")
            
            chunk_metadata = metadata or {}
            chunk_metadata.update({
                "ticker": ticker,
                "session_id": session_id,
                "ingested_at": datetime.now(timezone.utc).isoformat()
            })
            
            return self.ingest_document(
                document_id=session_id,
                content=research_summary,
                source_type="stock_research",
                metadata=chunk_metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to ingest stock research: {e}")
            return 0
    
    def ingest_index_analysis(
        self,
        session_id: str,
        index_symbol: str,
        analysis_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Ingest index analysis.
        
        Args:
            session_id: Analysis session ID
            index_symbol: Index symbol
            analysis_text: Analysis content
            metadata: Additional metadata
            
        Returns:
            Number of chunks created
        """
        try:
            logger.info(f"Ingesting index analysis for {index_symbol}")
            
            chunk_metadata = metadata or {}
            chunk_metadata.update({
                "index_symbol": index_symbol,
                "session_id": session_id,
                "ingested_at": datetime.now(timezone.utc).isoformat()
            })
            
            return self.ingest_document(
                document_id=session_id,
                content=analysis_text,
                source_type="index_analysis",
                metadata=chunk_metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to ingest index analysis: {e}")
            return 0
    
    def ingest_news_article(
        self,
        article_id: str,
        title: str,
        content: str,
        ticker: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Ingest news article.
        
        Args:
            article_id: Article ID
            title: Article title
            content: Article content
            ticker: Optional stock ticker
            metadata: Additional metadata
            
        Returns:
            Number of chunks created
        """
        try:
            logger.info(f"Ingesting news article: {title[:50]}...")
            
            full_text = f"{title}\n\n{content}"
            
            chunk_metadata = metadata or {}
            chunk_metadata.update({
                "title": title,
                "article_id": article_id,
                "ingested_at": datetime.now(timezone.utc).isoformat()
            })
            
            if ticker:
                chunk_metadata["ticker"] = ticker
            
            return self.ingest_document(
                document_id=article_id,
                content=full_text,
                source_type="news_article",
                metadata=chunk_metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to ingest news article: {e}")
            return 0
    
    def auto_ingest_from_session(
        self,
        session_id: str,
        session_type: str
    ) -> bool:
        """
        Automatically ingest data from a completed session.
        
        This is typically called after a research session completes.
        
        Args:
            session_id: Session ID
            session_type: Type of session
            
        Returns:
            True if ingestion successful, False otherwise
        """
        try:
            from common.services.persistence.session import session_service
            
            # Get the session
            session = session_service.get_session(session_id, session_type)
            
            if not session:
                logger.error(f"Session not found: {session_id}")
                return False
            
            # Extract content based on session type
            if session_type == 'stock_research':
                if hasattr(session, 'final_report') and session.final_report:
                    ticker = getattr(session, 'ticker', 'UNKNOWN')
                    self.ingest_stock_research(
                        session_id=session_id,
                        ticker=ticker,
                        research_summary=session.final_report,
                        metadata={
                            'user_id': getattr(session, 'user_id', None),
                            'state': getattr(session, 'state', None)
                        }
                    )
                    return True
            
            elif session_type == 'index_analysis':
                if hasattr(session, 'analysis_report') and session.analysis_report:
                    symbol = getattr(session, 'index_symbol', 'UNKNOWN')
                    self.ingest_index_analysis(
                        session_id=session_id,
                        index_symbol=symbol,
                        analysis_text=session.analysis_report,
                        metadata={
                            'user_id': getattr(session, 'user_id', None),
                            'state': getattr(session, 'state', None)
                        }
                    )
                    return True
            
            logger.warning(f"No content to ingest from {session_type} session: {session_id}")
            return False
            
        except Exception as e:
            logger.error(f"Auto ingestion from session failed: {e}")
            return False


# Singleton instance
auto_ingestion_service = AutoIngestionService()


# ===== Celery Task Wrappers =====
# These can be imported and used as Celery tasks in Grove

def ingest_document_task(
    document_id: str,
    content: str,
    source_type: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Celery task wrapper for document ingestion.
    
    Usage in Grove:
        from common.services.vector.auto_ingestion import ingest_document_task
        
        @celery_app.task
        def ingest_doc(doc_id, content, source_type, metadata):
            return ingest_document_task(doc_id, content, source_type, metadata)
    """
    return auto_ingestion_service.ingest_document(
        document_id, content, source_type, metadata
    )


def auto_ingest_from_session_task(
    session_id: str,
    session_type: str
):
    """
    Celery task wrapper for auto-ingestion from session.
    
    Usage in Grove:
        from common.services.vector.auto_ingestion import auto_ingest_from_session_task
        
        @celery_app.task
        def auto_ingest_session(session_id, session_type):
            return auto_ingest_from_session_task(session_id, session_type)
    """
    return auto_ingestion_service.auto_ingest_from_session(
        session_id, session_type
    )