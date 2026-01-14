# timber/common/services/persistence/session.py
"""
Session Management Service

Handles workflow session operations including state transitions,
research data updates, and session lifecycle management.

This service uses dynamic model loading - no hard-coded imports to
workflow-specific models. All models are accessed via the registry.
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timezone 
from sqlalchemy.orm import load_only, make_transient # Added for robust detachment

logger = logging.getLogger(__name__)


class SessionPersistenceService:
    """
    Singleton service for managing workflow sessions.
    
    Handles:
    - Session creation and retrieval
    - State machine transitions
    - Research data updates
    - Session lifecycle management
    - Task tracking
    
    Note: All model access is dynamic via the registry to support
    config-driven model loading and extensibility.
    """
    
    _instance: Optional['SessionPersistenceService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionPersistenceService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        logger.info("Session Service initialized")
    
    # ===== Session Creation =====
    
    def create_session(
        self,
        session_type: str,
        user_id: str,
        initial_state: str = 'initialized',
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[str]:
        """
        Create a new workflow session.
        
        Args:
            session_type: Type of session (e.g., 'stock_research', 'index_analysis')
            user_id: User ID
            initial_state: Initial state (default: 'initialized')
            metadata: Additional session metadata
            **kwargs: Additional session fields (e.g., ticker, index_symbol)
            
        Returns:
            Session ID if successful, None otherwise
            
        Example:
            session_id = session_service.create_session(
                session_type='stock_research',
                user_id='user_123',
                initial_state='initialized',
                metadata={'initiated_at': datetime.now()},
                ticker='AAPL'
            )
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model
            
            session_model = get_session_model(session_type)
            
            if not session_model:
                logger.error(f"Unknown session type: {session_type}")
                return None
            
            with db_service.session_scope() as db_session:
                # Build session data
                session_data = {
                    'user_id': user_id,
                    'state': initial_state,
                    **kwargs
                }
                
                # Add metadata if model supports it
                # Determine which metadata field exists
                metadata_field = None
                if hasattr(session_model, 'session_metadata'):
                    metadata_field = 'session_metadata'
                elif hasattr(session_model, 'metadata'):
                    metadata_field = 'metadata'

                if metadata_field:
                    session_data['session_metadata'] = metadata
                
                # Create session instance
                new_session = session_model(**session_data)
                
                db_session.add(new_session)
                db_session.flush()
                
                session_id = str(new_session.id)
                
                logger.info(f"Created {session_type} session: {session_id}")
                return session_id
                
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return None
    
    # ===== Session Retrieval =====
    
    def get_session(
        self,
        session_id: str,
        session_type: str
    ) -> Optional[Any]:
        """
        Retrieve a session by ID and type.
        
        Args:
            session_id: Session ID
            session_type: Session type
            
        Returns:
            Session object if found, None otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model
            
            session_model = get_session_model(session_type)
            
            if not session_model:
                logger.error(f"Unknown session type: {session_type}")
                return None
            
            with db_service.session_scope() as db_session:
                session = db_session.query(session_model).filter_by(id=session_id).first()
                
                if session:
                    # FIX 1 (Updated): Force detachment (expunge) of the object 
                    # from the session before the session closes to resolve DetachedInstanceError.
                    db_session.expunge(session)
                    logger.debug(f"Retrieved {session_type} session: {session_id}")
                else:
                    logger.warning(f"Session not found: {session_id}")
                
                return session
                
        except Exception as e:
            logger.error(f"Failed to retrieve session: {e}")
            return None
    
    # ===== State Management =====
    
    def transition_state(
        self,
        session_id: str,
        session_type: str,
        new_state: str,
        log_transition: bool = True
    ) -> bool:
        """
        Transition a workflow session to a new state.
        
        Args:
            session_id: Session ID
            session_type: Type of session
            new_state: New state to transition to
            log_transition: Whether to log the transition as a workflow event
            
        Returns:
            True if transition successful, False otherwise
            
        Example:
            success = session_service.transition_state(
                session_id='abc-123',
                session_type='stock_research',
                new_state='processing'
            )
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model
            
            session_model = get_session_model(session_type)
            
            if not session_model:
                logger.error(f"Unknown session type: {session_type}")
                return False
            
            with db_service.session_scope() as db_session:
                session = db_session.query(session_model).filter_by(id=session_id).first()
                
                if not session:
                    logger.error(f"Session not found: {session_id}")
                    return False
                
                old_state = session.state
                session.state = new_state
                session.updated_at = datetime.now(timezone.utc) 
                
                logger.info(
                    f"{session_type} session {session_id}: "
                    f"{old_state} → {new_state}"
                )
                
                # Optionally log workflow event
                if log_transition:
                    self._log_state_transition(
                        session_id,
                        session_type,
                        old_state,
                        new_state,
                        db_session
                    )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to transition state: {e}")
            return False
    
    def _log_state_transition(
        self,
        session_id: str,
        session_type: str,
        old_state: str,
        new_state: str,
        db_session
    ):
        """
        Log a state transition as a workflow event.
        
        This method uses dynamic model loading to find WorkflowEvent.
        If the model is not registered, it fails gracefully without
        breaking the session transition.
        
        Note: WorkflowEvent should be defined in your application
        (e.g., Grove) via YAML config, not in Timber common library.
        """
        try:
            from common.models.registry import get_model
            
            # Try to get WorkflowEvent model dynamically
            workflow_event_model = get_model('WorkflowEvent')
            
            if not workflow_event_model:
                # Model not registered - event logging is optional
                logger.debug(
                    "WorkflowEvent model not found - skipping event logging. "
                    "To enable, register WorkflowEvent via YAML config."
                )
                return
            
            # FIX 2: Remove 'message' argument and pass auxiliary data in 'details' dict.
            # FIX 3: Use timezone-aware datetime.now(timezone.utc)
            event_timestamp = datetime.now(timezone.utc)
            
            # Create event instance
            event = workflow_event_model(
                session_id=session_id,
                session_type=session_type,
                event_type='STATE_TRANSITION',
                status='COMPLETE',
                timestamp=event_timestamp,
                details={
                    'old_state': old_state,
                    'new_state': new_state,
                    'message': f"State transitioned from {old_state} to {new_state}",
                    'timestamp': event_timestamp.isoformat()
                }
            )
            
            db_session.add(event)
            logger.debug(f"Logged state transition event for session {session_id}")
            
        except Exception as e:
            # Fail gracefully - event logging should never break session operations
            logger.warning(f"Failed to log state transition event: {e}")
    
    # ===== Research Data Management =====
    
    def update_research_data(
        self,
        session_id: str,
        session_type: str,
        data: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """
        Update research data for a session.
        
        Args:
            session_id: Session ID
            session_type: Type of session
            data: Research data to update
            merge: If True, merge with existing data; if False, replace
            
        Returns:
            True if update successful, False otherwise
            
        Example:
            session_service.update_research_data(
                session_id='abc-123',
                session_type='stock_research',
                data={
                    'financial_analysis': {...},
                    'sentiment_score': 0.75
                },
                merge=True
            )
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model
            
            session_model = get_session_model(session_type)
            
            if not session_model:
                logger.error(f"Unknown session type: {session_type}")
                return False
            
            with db_service.session_scope() as db_session:
                session = db_session.query(session_model).filter_by(id=session_id).first()
                
                if not session:
                    logger.error(f"Session not found: {session_id}")
                    return False
                
                # Check if model has research_data field
                if not hasattr(session, 'research_data'):
                    logger.warning(
                        f"Session model {session_type} has no research_data field. "
                        f"Trying to set as individual attributes..."
                    )
                    # Try to set as individual attributes
                    for key, value in data.items():
                        if hasattr(session, key):
                            setattr(session, key, value)
                    # FIX 3: Use timezone-aware datetime.now(timezone.utc)
                    session.updated_at = datetime.now(timezone.utc)
                    return True
                
                # Update research_data field
                if merge:
                    # Merge with existing data
                    current_data = session.research_data or {}
                    current_data.update(data)
                    session.research_data = current_data
                else:
                    # Replace data
                    session.research_data = data
                
                # Flag as modified for SQLAlchemy
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(session, 'research_data')
                
                # FIX 3: Use timezone-aware datetime.now(timezone.utc)
                session.updated_at = datetime.now(timezone.utc)
                
                logger.info(f"Updated research data for session {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update research data: {e}")
            return False
    
    def get_research_data(
        self,
        session_id: str,
        session_type: str,
        key: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get research data from a session.
        
        Args:
            session_id: Session ID
            session_type: Type of session
            key: Optional key to get specific data; if None, returns all data
            
        Returns:
            Research data or None if not found
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model
            
            session_model = get_session_model(session_type)
            
            if not session_model:
                logger.error(f"Unknown session type: {session_type}")
                return None
            
            with db_service.session_scope() as db_session:
                session = db_session.query(session_model).filter_by(id=session_id).first()
                
                if not session:
                    logger.error(f"Session not found: {session_id}")
                    return None
                
                # FIX 1 (Updated): Force detachment (expunge) before accessing
                db_session.expunge(session)
                
                if not hasattr(session, 'research_data'):
                    logger.warning(f"Session has no research_data field")
                    return None
                
                data = session.research_data or {}
                
                if key:
                    return data.get(key)
                else:
                    return data
                    
        except Exception as e:
            logger.error(f"Failed to get research data: {e}")
            return None
    
    # ===== Task Management =====
    
    def update_task_ids(
        self,
        session_id: str,
        session_type: str,
        task_ids: List[str],
        append: bool = False
    ) -> bool:
        """
        Update task IDs for a session.
        
        Args:
            session_id: Session ID
            session_type: Type of session
            task_ids: List of task IDs
            append: If True, append to existing tasks; if False, replace
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model
            
            session_model = get_session_model(session_type)
            
            if not session_model:
                logger.error(f"Unknown session type: {session_type}")
                return False
            
            with db_service.session_scope() as db_session:
                session = db_session.query(session_model).filter_by(id=session_id).first()
                
                if not session:
                    logger.error(f"Session not found: {session_id}")
                    return False
                
                if not hasattr(session, 'task_ids'):
                    logger.warning(f"Session model has no task_ids field")
                    return False
                
                if append and session.task_ids:
                    # Append to existing tasks
                    existing_tasks = session.task_ids or []
                    session.task_ids = existing_tasks + task_ids
                else:
                    # Replace tasks
                    session.task_ids = task_ids
                
                # FIX 3: Use timezone-aware datetime.now(timezone.utc)
                session.updated_at = datetime.now(timezone.utc)
                
                logger.info(f"Updated task IDs for session {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update task IDs: {e}")
            return False
    
    # ===== Session Metadata =====
    
    def update_session_metadata(
        self,
        session_id: str,
        session_type: str,
        metadata: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """
        Update session metadata.
        
        Args:
            session_id: Session ID
            session_type: Session type
            metadata: Metadata to update
            merge: If True, merge with existing; if False, replace
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model
            
            session_model = get_session_model(session_type)
            
            if not session_model:
                logger.error(f"Unknown session type: {session_type}")
                return False
            
            with db_service.session_scope() as db_session:
                session = db_session.query(session_model).filter_by(id=session_id).first()
                
                if not session:
                    logger.error(f"Session not found: {session_id}")
                    return False
                
                # Support both 'session_metadata' (new) and 'metadata' (legacy)
                metadata_field = None
                if hasattr(session, 'session_metadata'):
                    metadata_field = 'session_metadata'
                elif hasattr(session, 'metadata'):
                    metadata_field = 'metadata'
                
                if metadata_field:
                    if merge:
                        current_metadata = getattr(session, metadata_field) or {}
                        current_metadata.update(metadata)
                        setattr(session, metadata_field, current_metadata)
                    else:
                        setattr(session, metadata_field, metadata)
                    
                    # Flag as modified
                    from sqlalchemy.orm.attributes import flag_modified
                    flag_modified(session, metadata_field)
                    
                    session.updated_at = datetime.now(timezone.utc)
                    logger.debug(f"Updated {metadata_field} for session: {session_id}")
                    return True
                else:
                    logger.warning(f"Session model {session_type} has no metadata or session_metadata field")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to update session metadata: {e}")
            return False
    
    def update_session(
        self,
        session_id: str,
        session_type: str,
        **updates
    ) -> bool:
        """
        Update a session with arbitrary field updates.
        
        This is a general-purpose update method that can update any session field.
        For specific operations, prefer specialized methods:
        - update_research_data() for research_data field
        - update_session_metadata() for metadata field  
        - transition_state() for state changes
        
        Args:
            session_id: Session ID
            session_type: Session type (e.g., 'stock_research')
            **updates: Field names and values to update
            
        Returns:
            True if successful, False otherwise
            
        Example:
            session_service.update_session(
                session_id='abc-123',
                session_type='stock_research',
                state='completed',
                progress=100,
                result={'data': 'value'}
            )
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model
            from sqlalchemy.orm.attributes import flag_modified
            
            session_model = get_session_model(session_type)
            
            if not session_model:
                logger.error(f"Unknown session type: {session_type}")
                return False
            
            with db_service.session_scope() as db_session:
                session = db_session.query(session_model).filter_by(id=session_id).first()
                
                if not session:
                    logger.error(f"Session not found: {session_id}")
                    return False
                
                # Track JSONB fields for proper update handling
                jsonb_fields = []
                
                # Update all provided fields
                for field_name, value in updates.items():
                    if not hasattr(session, field_name):
                        logger.warning(
                            f"Field '{field_name}' does not exist on {session_type} model, skipping"
                        )
                        continue
                    
                    # Check if field is JSONB type (needs flag_modified)
                    column = getattr(session_model, field_name, None)
                    if column is not None and hasattr(column, 'type'):
                        from sqlalchemy.dialects.postgresql import JSONB
                        if isinstance(column.type, JSONB):
                            jsonb_fields.append(field_name)
                    
                    # Set the value
                    setattr(session, field_name, value)
                
                # Flag JSONB fields as modified
                for field_name in jsonb_fields:
                    flag_modified(session, field_name)
                
                # Always update timestamp
                session.updated_at = datetime.now(timezone.utc)
                
                logger.info(
                    f"Updated {session_type} session {session_id}: "
                    f"{', '.join(updates.keys())}"
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to update session: {e}", exc_info=True)
            return False
        
    # ===== Session Queries =====
    
    def get_user_sessions(
        self,
        user_id: str,
        session_type: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 50
    ) -> List[Any]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User ID
            session_type: Optional session type filter
            state: Optional state filter
            limit: Maximum number of sessions to return
            
        Returns:
            List of session objects
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model, model_registry
            
            # If specific session type requested
            if session_type:
                session_types = [session_type]
            else:
                # Get all registered session types
                session_types = model_registry.list_session_types()
            
            all_sessions = []
            
            for st in session_types:
                session_model = get_session_model(st)
                
                if not session_model:
                    continue
                
                try:
                    with db_service.session_scope() as db_session:
                        query = db_session.query(session_model).filter_by(user_id=user_id)
                        
                        if state:
                            query = query.filter_by(state=state)
                        
                        sessions = query.order_by(
                            session_model.created_at.desc()
                        ).limit(limit).all()
                        
                        # FIX 1 (Updated): Expunge all loaded sessions
                        for session in sessions:
                            db_session.expunge(session)
                        
                        all_sessions.extend(sessions)
                        
                except Exception as e:
                    logger.error(f"Error querying {st} sessions: {e}")
            
            # Sort by creation date
            if all_sessions:
                all_sessions.sort(key=lambda s: s.created_at, reverse=True)
            
            logger.debug(f"Found {len(all_sessions)} sessions for user {user_id}")
            return all_sessions[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    # ===== Session Deletion =====
    
    def delete_session(
        self,
        session_id: str,
        session_type: str,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
            session_type: Session type
            soft_delete: If True and model supports it, use soft delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_session_model
            
            session_model = get_session_model(session_type)
            
            if not session_model:
                logger.error(f"Unknown session type: {session_type}")
                return False
            
            with db_service.session_scope() as db_session:
                session = db_session.query(session_model).filter_by(id=session_id).first()
                
                if not session:
                    logger.warning(f"Session not found: {session_id}")
                    return False
                
                if soft_delete and hasattr(session, 'soft_delete'):
                    # Use soft delete if available
                    session.soft_delete()
                    logger.info(f"Soft deleted {session_type} session: {session_id}")
                else:
                    # Hard delete
                    db_session.delete(session)
                    logger.info(f"Deleted {session_type} session: {session_id}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False


# Singleton instance
session_persistence_service = SessionPersistenceService()