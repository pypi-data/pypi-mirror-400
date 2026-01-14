# timber/common/services/persistence/tracker.py
"""
Tracker Service

Handles tracker status updates and event logging for goal tracking and monitoring.
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class TrackerPersistenceService:
    """
    Singleton service for managing trackers and tracking events.
    
    Handles:
    - Tracker status updates
    - Event logging
    - Tracker creation and retrieval
    - Goal tracking
    """
    
    _instance: Optional['TrackerPersistenceService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TrackerPersistenceService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        logger.info("Tracker Service initialized")
    
    def create_tracker(
        self,
        user_id: str,
        goal_id: int,
        stock_symbol: str,
        tracker_type: str,
        conditions: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a new tracker.
        
        Args:
            user_id: User ID
            goal_id: Associated goal ID
            stock_symbol: Stock symbol to track
            tracker_type: Type of tracker (e.g., 'price_alert', 'performance_monitor')
            conditions: Tracking conditions
            metadata: Additional metadata
            
        Returns:
            Tracker ID if successful, None otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tracker_model = get_model('Tracker')
            
            if not tracker_model:
                logger.error("Tracker model not found in registry")
                return None
            
            with db_service.session_scope() as db_session:
                tracker = tracker_model(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    goal_id=goal_id,
                    stock_symbol=stock_symbol,
                    tracker_type=tracker_type,
                    conditions=conditions,
                    metadata=metadata or {},
                    status='active',
                    created_at=datetime.now(timezone.utc),
                    last_checked_at=None
                )
                
                db_session.add(tracker)
                db_session.flush()
                
                tracker_id = tracker.id
                
                logger.info(
                    f"Created {tracker_type} tracker for {stock_symbol}: {tracker_id}"
                )
                return tracker_id
                
        except Exception as e:
            logger.error(f"Failed to create tracker: {e}")
            return None
    
    def get_tracker(
        self,
        tracker_id: str
    ) -> Optional[Any]:
        """
        Retrieve a tracker by ID.
        
        Args:
            tracker_id: Tracker ID
            
        Returns:
            Tracker object if found, None otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tracker_model = get_model('Tracker')
            
            if not tracker_model:
                logger.error("Tracker model not found in registry")
                return None
            
            with db_service.session_scope() as db_session:
                tracker = db_session.query(tracker_model).filter_by(id=tracker_id).first()
                
                if tracker:
                    logger.debug(f"Retrieved tracker: {tracker_id}")
                else:
                    logger.warning(f"Tracker not found: {tracker_id}")
                
                return tracker
                
        except Exception as e:
            logger.error(f"Failed to retrieve tracker: {e}")
            return None
    
    def update_status(
        self,
        tracker_id: str,
        new_status: str
    ) -> bool:
        """
        Update tracker status.
        
        Args:
            tracker_id: Tracker ID
            new_status: New status ('active', 'paused', 'triggered', 'completed', 'cancelled')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tracker_model = get_model('Tracker')
            
            if not tracker_model:
                logger.error("Tracker model not found in registry")
                return False
            
            with db_service.session_scope() as db_session:
                tracker = db_session.query(tracker_model).filter_by(id=tracker_id).first()
                
                if not tracker:
                    logger.error(f"Tracker not found: {tracker_id}")
                    return False
                
                old_status = tracker.status
                tracker.status = new_status
                tracker.updated_at = datetime.now(timezone.utc)
                
                logger.info(f"Tracker {tracker_id}: {old_status} → {new_status}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update tracker status: {e}")
            return False
    
    def log_event(
        self,
        tracker_id: str,
        event_data: Dict[str, Any],
        event_type: str = 'check',
        triggered: bool = False
    ) -> Optional[str]:
        """
        Log a tracker monitoring event.
        
        Args:
            tracker_id: Tracker ID
            event_data: Event data (e.g., price, volume, conditions met)
            event_type: Type of event ('check', 'trigger', 'error')
            triggered: Whether the tracker was triggered
            
        Returns:
            Event ID if successful, None otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tracker_event_model = get_model('TrackerEvent')
            tracker_model = get_model('Tracker')
            
            if not tracker_event_model or not tracker_model:
                logger.error("TrackerEvent or Tracker model not found in registry")
                return None
            
            with db_service.session_scope() as db_session:
                # Create event
                event = tracker_event_model(
                    id=str(uuid.uuid4()),
                    tracker_id=tracker_id,
                    event_type=event_type,
                    event_data=event_data,
                    triggered=triggered,
                    created_at=datetime.now(timezone.utc)
                )
                
                db_session.add(event)
                
                # Update tracker's last_checked_at
                tracker = db_session.query(tracker_model).filter_by(id=tracker_id).first()
                if tracker:
                    tracker.last_checked_at = datetime.now(timezone.utc)
                    
                    # If triggered, update status
                    if triggered and tracker.status == 'active':
                        tracker.status = 'triggered'
                        logger.info(f"Tracker {tracker_id} triggered")
                
                db_session.flush()
                
                event_id = event.id
                
                logger.debug(
                    f"Logged {event_type} event for tracker {tracker_id}: {event_id}"
                )
                return event_id
                
        except Exception as e:
            logger.error(f"Failed to log tracker event: {e}")
            return None
    
    def get_tracker_events(
        self,
        tracker_id: str,
        limit: int = 50,
        event_type: Optional[str] = None
    ) -> List[Any]:
        """
        Get events for a tracker.
        
        Args:
            tracker_id: Tracker ID
            limit: Maximum number of events to return
            event_type: Optional event type filter
            
        Returns:
            List of tracker event objects
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tracker_event_model = get_model('TrackerEvent')
            
            if not tracker_event_model:
                logger.error("TrackerEvent model not found in registry")
                return []
            
            with db_service.session_scope() as db_session:
                query = db_session.query(tracker_event_model).filter_by(
                    tracker_id=tracker_id
                )
                
                if event_type:
                    query = query.filter_by(event_type=event_type)
                
                events = query.order_by(
                    tracker_event_model.created_at.desc()
                ).limit(limit).all()
                
                logger.debug(f"Retrieved {len(events)} events for tracker {tracker_id}")
                return events
                
        except Exception as e:
            logger.error(f"Failed to get tracker events: {e}")
            return []
    
    def get_user_trackers(
        self,
        user_id: str,
        status: Optional[str] = None,
        stock_symbol: Optional[str] = None
    ) -> List[Any]:
        """
        Get all trackers for a user.
        
        Args:
            user_id: User ID
            status: Optional status filter
            stock_symbol: Optional stock symbol filter
            
        Returns:
            List of tracker objects
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tracker_model = get_model('Tracker')
            
            if not tracker_model:
                logger.error("Tracker model not found in registry")
                return []
            
            with db_service.session_scope() as db_session:
                query = db_session.query(tracker_model).filter_by(user_id=user_id)
                
                if status:
                    query = query.filter_by(status=status)
                
                if stock_symbol:
                    query = query.filter_by(stock_symbol=stock_symbol)
                
                trackers = query.order_by(
                    tracker_model.created_at.desc()
                ).all()
                
                logger.debug(f"Retrieved {len(trackers)} trackers for user {user_id}")
                return trackers
                
        except Exception as e:
            logger.error(f"Failed to get user trackers: {e}")
            return []
    
    def delete_tracker(
        self,
        tracker_id: str,
        delete_events: bool = True
    ) -> bool:
        """
        Delete a tracker.
        
        Args:
            tracker_id: Tracker ID
            delete_events: Whether to also delete associated events
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tracker_model = get_model('Tracker')
            tracker_event_model = get_model('TrackerEvent')
            
            if not tracker_model:
                logger.error("Tracker model not found in registry")
                return False
            
            with db_service.session_scope() as db_session:
                # Delete events if requested
                if delete_events and tracker_event_model:
                    db_session.query(tracker_event_model).filter_by(
                        tracker_id=tracker_id
                    ).delete()
                
                # Delete tracker
                tracker = db_session.query(tracker_model).filter_by(id=tracker_id).first()
                
                if not tracker:
                    logger.warning(f"Tracker not found: {tracker_id}")
                    return False
                
                db_session.delete(tracker)
                logger.info(f"Deleted tracker: {tracker_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete tracker: {e}")
            return False
    
    def update_conditions(
        self,
        tracker_id: str,
        new_conditions: Dict[str, Any]
    ) -> bool:
        """
        Update tracker conditions.
        
        Args:
            tracker_id: Tracker ID
            new_conditions: New tracking conditions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            tracker_model = get_model('Tracker')
            
            if not tracker_model:
                logger.error("Tracker model not found in registry")
                return False
            
            with db_service.session_scope() as db_session:
                tracker = db_session.query(tracker_model).filter_by(id=tracker_id).first()
                
                if not tracker:
                    logger.error(f"Tracker not found: {tracker_id}")
                    return False
                
                tracker.conditions = new_conditions
                tracker.updated_at = datetime.now(timezone.utc)
                
                logger.info(f"Updated conditions for tracker {tracker_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update tracker conditions: {e}")
            return False


# Singleton instance
tracker_persistence_service = TrackerPersistenceService()