# timber/common/services/gdpr/deletion.py
"""
GDPR Deletion Service

Handles GDPR-compliant user data deletion including data export,
cascade deletion, and audit trail creation.
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)

class GDPRDeletionService:
    """
    Singleton service for GDPR-compliant data deletion.
    
    Handles:
    - Complete user data deletion
    - Data export before deletion
    - Cascade deletion across related tables
    - Audit trail creation
    - Anonymization options
    """
    
    _instance: Optional['GDPRDeletionService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GDPRDeletionService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        logger.info("GDPR Deletion Service initialized")
    
    def export_user_data(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Export all user data in GDPR-compliant format.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing all user data, or None if error
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import model_registry
            
            export_data = {
                "user_id": user_id,
                "export_date": datetime.now(timezone.utc).isoformat(),
                "data": {}
            }
            
            with db_service.session_scope() as db_session:
                # Get all registered models
                for model_name in model_registry.list_models():
                    model_class = model_registry.get_model(model_name)
                    
                    if not model_class:
                        continue
                    
                    # Check if model has user_id field
                    if hasattr(model_class, 'user_id'):
                        records = db_session.query(model_class).filter_by(
                            user_id=user_id
                        ).all()
                        
                        if records:
                            export_data["data"][model_name] = [
                                self._serialize_record(record)
                                for record in records
                            ]
                            
                            logger.info(
                                f"Exported {len(records)} records from {model_name}"
                            )
            
            logger.info(f"User data export completed for user {user_id}")
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export user data: {e}")
            return None
    
    def _serialize_record(self, record: Any) -> Dict[str, Any]:
        """
        Serialize a database record to dictionary.
        
        Args:
            record: Database record
            
        Returns:
            Dictionary representation
        """
        try:
            from sqlalchemy.inspection import inspect
            
            serialized = {}
            
            for column in inspect(record).mapper.column_attrs:
                value = getattr(record, column.key)
                
                # Handle special types
                if isinstance(value, datetime):
                    serialized[column.key] = value.isoformat()
                elif isinstance(value, (dict, list)):
                    serialized[column.key] = value
                elif value is not None:
                    serialized[column.key] = str(value)
                else:
                    serialized[column.key] = None
            
            return serialized
            
        except Exception as e:
            logger.error(f"Failed to serialize record: {e}")
            return {}
    
    def delete_user_data(
        self,
        user_id: str,
        export_before_delete: bool = True,
        create_audit_record: bool = True
    ) -> Dict[str, Any]:
        """
        Delete all data for a user.
        
        Args:
            user_id: User ID
            export_before_delete: Whether to export data before deletion
            create_audit_record: Whether to create an audit record
            
        Returns:
            Dictionary with deletion results
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import model_registry
            
            result = {
                "user_id": user_id,
                "deletion_date": datetime.now(timezone.utc).isoformat(),
                "exported": False,
                "export_data": None,
                "deleted_records": {},
                "errors": []
            }
            
            # Export data if requested
            if export_before_delete:
                export_data = self.export_user_data(user_id)
                if export_data:
                    result["exported"] = True
                    result["export_data"] = export_data
                    logger.info(f"Data exported before deletion for user {user_id}")
                else:
                    result["errors"].append("Failed to export data before deletion")
            
            # Delete user data from all models
            with db_service.session_scope() as db_session:
                for model_name in model_registry.list_models():
                    model_class = model_registry.get_model(model_name)
                    
                    if not model_class:
                        continue
                    
                    # Check if model has user_id field
                    if hasattr(model_class, 'user_id'):
                        try:
                            deleted_count = db_session.query(model_class).filter_by(
                                user_id=user_id
                            ).delete(synchronize_session=False)
                            
                            if deleted_count > 0:
                                result["deleted_records"][model_name] = deleted_count
                                logger.info(
                                    f"Deleted {deleted_count} records from {model_name}"
                                )
                        
                        except Exception as e:
                            error_msg = f"Error deleting from {model_name}: {str(e)}"
                            result["errors"].append(error_msg)
                            logger.error(error_msg)
            
            # Create audit record if requested
            if create_audit_record:
                self._create_audit_record(user_id, result)
            
            total_deleted = sum(result["deleted_records"].values())
            logger.info(
                f"GDPR deletion completed for user {user_id}: "
                f"{total_deleted} records deleted"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete user data: {e}")
            return {
                "user_id": user_id,
                "deletion_date": datetime.now(timezone.utc).isoformat(),
                "exported": False,
                "deleted_records": {},
                "errors": [str(e)]
            }
    
    def anonymize_user_data(
        self,
        user_id: str,
        anonymization_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Anonymize user data instead of deleting.
        
        Replaces identifiable information with anonymized values.
        
        Args:
            user_id: User ID
            anonymization_map: Optional mapping of fields to anonymization strategies
            
        Returns:
            Dictionary with anonymization results
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import model_registry
            
            result = {
                "user_id": user_id,
                "anonymization_date": datetime.now(timezone.utc).isoformat(),
                "anonymized_records": {},
                "errors": []
            }
            
            # Default anonymization values
            anon_values = anonymization_map or {
                "email": f"anonymized_{user_id}@deleted.local",
                "name": "Anonymized User",
                "phone": None,
                "address": None
            }
            
            with db_service.session_scope() as db_session:
                for model_name in model_registry.list_models():
                    model_class = model_registry.get_model(model_name)
                    
                    if not model_class:
                        continue
                    
                    # Check if model has user_id field
                    if hasattr(model_class, 'user_id'):
                        try:
                            records = db_session.query(model_class).filter_by(
                                user_id=user_id
                            ).all()
                            
                            anonymized_count = 0
                            
                            for record in records:
                                # Apply anonymization
                                for field, anon_value in anon_values.items():
                                    if hasattr(record, field):
                                        setattr(record, field, anon_value)
                                        anonymized_count += 1
                            
                            if anonymized_count > 0:
                                result["anonymized_records"][model_name] = anonymized_count
                                logger.info(
                                    f"Anonymized {anonymized_count} fields in {model_name}"
                                )
                        
                        except Exception as e:
                            error_msg = f"Error anonymizing {model_name}: {str(e)}"
                            result["errors"].append(error_msg)
                            logger.error(error_msg)
            
            logger.info(f"Anonymization completed for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to anonymize user data: {e}")
            return {
                "user_id": user_id,
                "anonymization_date": datetime.now(timezone.utc).isoformat(),
                "anonymized_records": {},
                "errors": [str(e)]
            }
    
    def _create_audit_record(
        self,
        user_id: str,
        deletion_result: Dict[str, Any]
    ) -> bool:
        """
        Create an audit record for data deletion.
        
        Args:
            user_id: User ID
            deletion_result: Result of deletion operation
            
        Returns:
            True if audit record created successfully
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            audit_model = get_model('GDPRAuditLog')
            
            if not audit_model:
                logger.warning("GDPRAuditLog model not found - skipping audit")
                return False
            
            with db_service.session_scope() as db_session:
                audit_record = audit_model(
                    user_id=user_id,
                    action='data_deletion',
                    details=deletion_result,
                    created_at=datetime.now(timezone.utc)
                )
                
                db_session.add(audit_record)
            
            logger.info(f"Created GDPR audit record for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create audit record: {e}")
            return False
    
    def get_user_data_summary(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get a summary of all user data without full export.
        
        Args:
            user_id: User ID
            
        Returns:
            Summary of user data across all tables
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import model_registry
            
            summary = {
                "user_id": user_id,
                "summary_date": datetime.now(timezone.utc).isoformat(),
                "record_counts": {}
            }
            
            with db_service.session_scope() as db_session:
                for model_name in model_registry.list_models():
                    model_class = model_registry.get_model(model_name)
                    
                    if not model_class:
                        continue
                    
                    # Check if model has user_id field
                    if hasattr(model_class, 'user_id'):
                        count = db_session.query(model_class).filter_by(
                            user_id=user_id
                        ).count()
                        
                        if count > 0:
                            summary["record_counts"][model_name] = count
            
            total_records = sum(summary["record_counts"].values())
            summary["total_records"] = total_records
            
            logger.info(f"Generated data summary for user {user_id}: {total_records} records")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate user data summary: {e}")
            return {
                "user_id": user_id,
                "summary_date": datetime.now(timezone.utc).isoformat(),
                "record_counts": {},
                "total_records": 0,
                "error": str(e)
            }
    
    def verify_deletion(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Verify that all user data has been deleted.
        
        Args:
            user_id: User ID
            
        Returns:
            Verification results
        """
        summary = self.get_user_data_summary(user_id)
        
        verification = {
            "user_id": user_id,
            "verification_date": datetime.now(timezone.utc).isoformat(),
            "deletion_complete": summary["total_records"] == 0,
            "remaining_records": summary["record_counts"]
        }
        
        if verification["deletion_complete"]:
            logger.info(f"Deletion verified for user {user_id}: Complete")
        else:
            logger.warning(
                f"Deletion verification for user {user_id}: "
                f"{summary['total_records']} records remaining"
            )
        
        return verification


# Singleton instance
gdpr_deletion_service = GDPRDeletionService()