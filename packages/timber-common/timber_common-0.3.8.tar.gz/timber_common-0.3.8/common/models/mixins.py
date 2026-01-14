# timber/common/models/mixins.py
"""
Enhanced Model Mixins

Provides reusable mixins for common model functionality:
- Timestamps
- Soft Delete
- Field Encryption
- GDPR Compliance
- Searchable Content
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, DateTime, Boolean, Text
from sqlalchemy.orm import declared_attr
from sqlalchemy.ext.declarative import declarative_base
import logging

logger = logging.getLogger(__name__)


class TimestampMixin:
    """
    Adds created_at and updated_at timestamp columns.
    
    Automatically maintains updated_at on each modification.
    """
    
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            default=datetime.now(timezone.utc),
            nullable=False,
            index=True
        )
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
            index=True
        )


class SoftDeleteMixin:
    """
    Enables soft deletion of records.
    
    Records are marked as deleted rather than physically removed.
    Useful for audit trails and GDPR compliance.
    """
    
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), nullable=True, index=True)
    
    @declared_attr
    def is_deleted(cls):
        return Column(Boolean, default=False, nullable=False, index=True)
    
    def soft_delete(self):
        """Mark record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
    
    @classmethod
    def active_only(cls, query):
        """Filter query to only include non-deleted records."""
        return query.filter(cls.is_deleted == False)


class EncryptedFieldMixin:
    """
    Provides field-level encryption capabilities.
    
    Fields marked for encryption in the model config will be
    automatically encrypted before storage and decrypted on retrieval.
    
    Note: This is a marker mixin. Actual encryption is handled by
    the EncryptionService using SQLAlchemy events.
    """
    
    @declared_attr
    def _encrypted_fields_list(cls):
        """
        Store which fields are encrypted.
        This is populated by the model factory based on config.
        """
        return []
    
    def get_encrypted_fields(self) -> List[str]:
        """Return list of fields that are encrypted."""
        if hasattr(self, '_config') and 'encryption' in self._config:
            return self._config['encryption'].get('fields', [])
        return getattr(self, '_encrypted_fields_list', [])


class GDPRComplianceMixin:
    """
    Adds GDPR compliance features.
    
    - Marks which field contains user_id
    - Provides data export method
    - Enables cascading deletion tracking
    """
    
    def get_user_id(self) -> Optional[str]:
        """
        Return the user_id associated with this record.
        
        Looks for user_id field in model config or as direct attribute.
        """
        if hasattr(self, '_config') and 'gdpr' in self._config:
            user_field = self._config['gdpr'].get('user_field', 'user_id')
            return getattr(self, user_field, None)
        
        return getattr(self, 'user_id', None)
    
    def export_data(self) -> Dict[str, Any]:
        """
        Export data for GDPR compliance.
        
        Returns only fields specified in config or all serializable fields.
        """
        if hasattr(self, '_config') and 'gdpr' in self._config:
            export_fields = self._config['gdpr'].get('export_fields', [])
            if export_fields:
                return {
                    field: getattr(self, field, None)
                    for field in export_fields
                }
        
        # Default: export all columns except encrypted/sensitive ones
        from sqlalchemy import inspect
        mapper = inspect(self.__class__)
        
        data = {}
        for column in mapper.columns:
            col_name = column.name
            
            # Skip sensitive fields
            if col_name.endswith('_hash') or col_name.startswith('_'):
                continue
            
            value = getattr(self, col_name, None)
            
            # Convert datetime to ISO format
            if isinstance(value, datetime):
                value = value.isoformat()
            
            data[col_name] = value
        
        return data


class SearchableMixin:
    """
    Marks content that should be ingested into vector database.
    
    Models with this mixin will have their searchable fields
    automatically ingested into the text_embeddings table.
    """
    
    @declared_attr
    def _searchable_fields(cls):
        """List of fields to ingest into vector database."""
        return []
    
    def get_searchable_content(self) -> Optional[str]:
        """
        Return combined content from searchable fields.
        
        This content will be chunked and embedded for semantic search.
        """
        # Get searchable fields from config
        searchable_fields = []
        
        if hasattr(self, '_config'):
            for col_config in self._config.get('columns', []):
                if col_config.get('searchable'):
                    searchable_fields.append(col_config['name'])
        
        if not searchable_fields:
            searchable_fields = getattr(self, '_searchable_fields', [])
        
        # Combine content from all searchable fields
        content_parts = []
        for field in searchable_fields:
            value = getattr(self, field, None)
            if value:
                content_parts.append(str(value))
        
        return '\n\n'.join(content_parts) if content_parts else None
    
    def get_search_metadata(self) -> Dict[str, Any]:
        """
        Return metadata to store with embeddings.
        
        Useful for filtering search results.
        """
        metadata = {
            'model': self.__class__.__name__,
            'record_id': str(self.id) if hasattr(self, 'id') else None,
        }
        
        # Add user_id if available
        if hasattr(self, 'user_id'):
            metadata['user_id'] = self.user_id
        
        # Add any custom metadata from config
        if hasattr(self, '_config') and 'search_metadata' in self._config:
            metadata.update(self._config['search_metadata'])
        
        return metadata


class CacheableMixin:
    """
    Marks models that should be cached.
    
    Provides cache key generation and TTL management.
    """
    
    def get_cache_key(self) -> str:
        """Generate a unique cache key for this record."""
        model_name = self.__class__.__name__
        record_id = getattr(self, 'id', 'unknown')
        return f"{model_name}:{record_id}"
    
    def get_cache_ttl(self) -> Optional[int]:
        """
        Return cache TTL in seconds.
        
        Returns None if caching is disabled for this model.
        """
        if hasattr(self, '_config') and 'cache_strategy' in self._config:
            cache_config = self._config['cache_strategy']
            if cache_config.get('enabled'):
                ttl_hours = cache_config.get('ttl_hours', 24)
                return ttl_hours * 3600
        
        return None
    
    def should_invalidate_cache_on_update(self) -> bool:
        """Check if cache should be invalidated when record is updated."""
        if hasattr(self, '_config') and 'cache_strategy' in self._config:
            return self._config['cache_strategy'].get('invalidate_on_update', True)
        
        return True


class AuditMixin(TimestampMixin):
    """
    Enhanced audit trail with user tracking.
    
    Extends TimestampMixin with created_by and updated_by fields.
    """
    
    @declared_attr
    def created_by(cls):
        return Column(Text, nullable=True)
    
    @declared_attr
    def updated_by(cls):
        return Column(Text, nullable=True)
    
    def set_created_by(self, user_id: str):
        """Set the user who created this record."""
        self.created_by = user_id
    
    def set_updated_by(self, user_id: str):
        """Set the user who last updated this record."""
        self.updated_by = user_id


# Mixin registry for factory lookup
MIXIN_REGISTRY = {
    'TimestampMixin': TimestampMixin,
    'SoftDeleteMixin': SoftDeleteMixin,
    'EncryptedFieldMixin': EncryptedFieldMixin,
    'GDPRComplianceMixin': GDPRComplianceMixin,
    'SearchableMixin': SearchableMixin,
    'CacheableMixin': CacheableMixin,
    'AuditMixin': AuditMixin,
}


def get_mixin_class(mixin_name: str):
    """
    Retrieve a mixin class by name.
    
    Args:
        mixin_name: Name of the mixin
    
    Returns:
        Mixin class or None if not found
    """
    mixin = MIXIN_REGISTRY.get(mixin_name)
    
    if not mixin:
        logger.warning(f"Mixin '{mixin_name}' not found in registry")
    
    return mixin


def register_mixin(name: str, mixin_class):
    """
    Register a custom mixin.
    
    Allows applications to define their own mixins.
    
    Args:
        name: Name to register the mixin under
        mixin_class: The mixin class
    """
    MIXIN_REGISTRY[name] = mixin_class
    logger.info(f"Registered custom mixin: {name}")