# timber/common/services/persistence/base.py
"""
Base Persistence Service

Defines the interface and common functionality for all persistence services.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BasePersistenceService(ABC):
    """
    Abstract base class for persistence services.
    
    All specialized persistence services should inherit from this
    and implement the required methods.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"{self.__class__.__name__} initialized")
    
    @abstractmethod
    def persist(self, data: Dict[str, Any]) -> bool:
        """
        Persist data to storage.
        
        Args:
            data: Data to persist
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def retrieve(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from storage.
        
        Args:
            identifier: Unique identifier for the data
        
        Returns:
            Retrieved data or None if not found
        """
        pass
    
    def _log_operation(self, operation: str, details: str):
        """Log a persistence operation."""
        self.logger.info(f"{operation}: {details}")
    
    def _handle_error(self, operation: str, error: Exception):
        """Handle and log persistence errors."""
        self.logger.error(f"{operation} failed: {str(error)}", exc_info=True)


# ============================================================
# GDPR Compliance Service
# ============================================================

from typing import List, Set
from sqlalchemy.orm import Session
from common.models.registry import model_registry

logger = logging.getLogger(__name__)


class GDPRComplianceService:
    """
    Service for GDPR compliance operations.
    
    Handles:
    - User data deletion (right to be forgotten)
    - Data export (right to data portability)
    - Data anonymization
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GDPRComplianceService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        logger.info("GDPR Compliance Service initialized")
    
    def delete_user_data(
        self,
        user_id: str,
        db_session: Session,
        anonymize: bool = False,
        export_before_delete: bool = True
    ) -> Dict[str, Any]:
        """
        Delete all data associated with a user.
        
        Args:
            user_id: The user ID to delete data for
            db_session: SQLAlchemy session
            anonymize: If True, anonymize instead of delete
            export_before_delete: If True, export data before deletion
        
        Returns:
            Dictionary with deletion summary and export data
        """
        logger.info(f"Starting GDPR deletion for user {user_id}")
        
        result = {
            'user_id': user_id,
            'deleted_models': [],
            'record_counts': {},
            'export_data': None,
            'errors': []
        }
        
        # Export data if requested
        if export_before_delete:
            try:
                result['export_data'] = self.export_user_data(user_id, db_session)
            except Exception as e:
                logger.error(f"Data export failed: {e}")
                result['errors'].append(f"Export failed: {str(e)}")
        
        # Get all models that support GDPR
        gdpr_models = self._get_gdpr_compliant_models()
        
        # Delete/anonymize data from each model
        for model_class in gdpr_models:
            model_name = model_class.__name__
            
            try:
                # Find all records for this user
                records = self._find_user_records(model_class, user_id, db_session)
                count = len(records)
                
                if count > 0:
                    if anonymize:
                        self._anonymize_records(records, db_session)
                        logger.info(f"Anonymized {count} records in {model_name}")
                    else:
                        # Check if model supports soft delete
                        if hasattr(model_class, 'soft_delete'):
                            for record in records:
                                record.soft_delete()
                            logger.info(f"Soft deleted {count} records in {model_name}")
                        else:
                            for record in records:
                                db_session.delete(record)
                            logger.info(f"Hard deleted {count} records in {model_name}")
                    
                    result['deleted_models'].append(model_name)
                    result['record_counts'][model_name] = count
                
            except Exception as e:
                logger.error(f"Failed to delete from {model_name}: {e}")
                result['errors'].append(f"{model_name}: {str(e)}")
        
        # Commit all deletions
        try:
            db_session.commit()
            logger.info(f"GDPR deletion completed for user {user_id}")
        except Exception as e:
            db_session.rollback()
            logger.error(f"Failed to commit deletions: {e}")
            result['errors'].append(f"Commit failed: {str(e)}")
        
        return result
    
    def export_user_data(self, user_id: str, db_session: Session) -> Dict[str, Any]:
        """
        Export all data for a user.
        
        Args:
            user_id: The user ID to export data for
            db_session: SQLAlchemy session
        
        Returns:
            Dictionary with all user data organized by model
        """
        logger.info(f"Exporting data for user {user_id}")
        
        export_data = {
            'user_id': user_id,
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {}
        }
        
        # Get all models that support GDPR
        gdpr_models = self._get_gdpr_compliant_models()
        
        for model_class in gdpr_models:
            model_name = model_class.__name__
            
            try:
                records = self._find_user_records(model_class, user_id, db_session)
                
                if records:
                    # Use model's export_data method if available
                    if hasattr(records[0], 'export_data'):
                        export_data['data'][model_name] = [
                            record.export_data() for record in records
                        ]
                    else:
                        # Fallback to dict conversion
                        export_data['data'][model_name] = [
                            self._record_to_dict(record) for record in records
                        ]
                
            except Exception as e:
                logger.error(f"Failed to export from {model_name}: {e}")
        
        logger.info(f"Export completed for user {user_id}")
        return export_data
    
    def _get_gdpr_compliant_models(self) -> List:
        """Get all models that support GDPR compliance."""
        models = []
        
        for model_name in model_registry.list_models():
            model_class = model_registry.get_model(model_name)
            
            # Check if model has GDPR configuration
            if hasattr(model_class, '_config'):
                config = model_class._config
                if 'gdpr' in config and config['gdpr'].get('user_field'):
                    models.append(model_class)
            
            # Or has GDPRComplianceMixin
            elif hasattr(model_class, 'get_user_id'):
                models.append(model_class)
        
        return models
    
    def _find_user_records(self, model_class, user_id: str, db_session: Session) -> List:
        """Find all records for a user in a model."""
        # Get user field name from config
        if hasattr(model_class, '_config') and 'gdpr' in model_class._config:
            user_field = model_class._config['gdpr'].get('user_field', 'user_id')
        else:
            user_field = 'user_id'
        
        # Query for records
        if hasattr(model_class, user_field):
            return db_session.query(model_class).filter(
                getattr(model_class, user_field) == user_id
            ).all()
        
        return []
    
    def _anonymize_records(self, records: List, db_session: Session):
        """Anonymize user records instead of deleting them."""
        for record in records:
            # Get fields to anonymize from config
            if hasattr(record, '_config') and 'gdpr' in record._config:
                fields_to_clear = record._config['gdpr'].get('anonymize_fields', [])
            else:
                # Default: clear common user-identifying fields
                fields_to_clear = ['name', 'email', 'phone', 'address']
            
            for field in fields_to_clear:
                if hasattr(record, field):
                    setattr(record, field, '[ANONYMIZED]')
            
            # Mark as anonymized
            if hasattr(record, 'is_anonymized'):
                record.is_anonymized = True
    
    def _record_to_dict(self, record) -> Dict[str, Any]:
        """Convert a SQLAlchemy record to dictionary."""
        from sqlalchemy import inspect
        
        mapper = inspect(record.__class__)
        data = {}
        
        for column in mapper.columns:
            value = getattr(record, column.name, None)
            
            # Convert datetime to ISO format
            if isinstance(value, datetime):
                value = value.isoformat()
            
            data[column.name] = value
        
        return data


# Singleton instance
gdpr_service = GDPRComplianceService()