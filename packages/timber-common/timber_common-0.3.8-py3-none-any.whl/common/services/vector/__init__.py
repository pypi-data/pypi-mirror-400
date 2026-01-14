# timber/common/services/vector/__init__.py
"""
Vector Services

Vector embedding and auto-ingestion services for semantic search and LLM capabilities.
"""

from .tag_embedding import tag_embedding_service, TagEmbeddingService
from .auto_ingestion import (
    auto_ingestion_service,
    AutoIngestionService,
    ingest_document_task,
    auto_ingest_from_session_task
)
from .search import vector_search_service
__all__ = [
    'tag_embedding_service',
    'TagEmbeddingService',
    'auto_ingestion_service',
    'AutoIngestionService',
    'ingest_document_task',
    'auto_ingest_from_session_task',
    'vector_search_service',
]