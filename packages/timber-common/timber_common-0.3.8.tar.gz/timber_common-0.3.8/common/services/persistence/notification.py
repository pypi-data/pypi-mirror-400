# timber/common/services/persistence/notification.py
"""
Notification Service

Handles creation and management of user notifications including
simulation results, tracker events, and research completion alerts.
"""

from typing import Optional, Dict, Any
import logging
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class NotificationPersistenceService:
    """
    Singleton service for managing user notifications.
    
    Handles:
    - Portfolio simulation notifications
    - Tracker event notifications
    - Research completion notifications
    - Custom notification creation
    """
    
    _instance: Optional['NotificationPersistenceService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationPersistenceService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        logger.info("Notification Service initialized")
    
    def create_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        priority: str = 'normal'
    ) -> Optional[str]:
        """
        Create a generic notification.
        
        Args:
            user_id: User ID
            notification_type: Type of notification
            title: Notification title
            content: Notification content (HTML supported)
            metadata: Additional metadata
            priority: Priority level ('low', 'normal', 'high')
            
        Returns:
            Notification ID if successful, None otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            # Get the Notification model dynamically
            notification_model = get_model('Notification')
            
            if not notification_model:
                logger.error("Notification model not found in registry")
                return None
            
            with db_service.session_scope() as db_session:
                notification = notification_model(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    notification_type=notification_type,
                    title=title,
                    content=content,
                    metadata=metadata or {},
                    priority=priority,
                    is_read=False,
                    created_at=datetime.now(timezone.utc)
                )
                
                db_session.add(notification)
                db_session.flush()
                
                notification_id = notification.id
                
                logger.info(
                    f"Created {notification_type} notification for user {user_id}: {notification_id}"
                )
                return notification_id
                
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return None
    
    def create_simulation_notification(
        self,
        user_id: str,
        results: Dict[str, Any],
        years_to_simulate: int,
        original_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a portfolio simulation notification.
        
        Args:
            user_id: User ID
            results: Simulation results dictionary
            years_to_simulate: Number of years simulated
            original_prompt: Optional original user prompt
            
        Returns:
            Notification ID if successful, None otherwise
        """
        try:
            # Format results for display
            median_value = results.get('median_final_value', 0)
            percentile_25 = results.get('percentile_25', 0)
            percentile_75 = results.get('percentile_75', 0)
            
            title = f"Portfolio Simulation Complete ({years_to_simulate} Years)"
            
            content = (
                f"<div class='notification-content simulation'>"
                f"<p>Your portfolio simulation for {years_to_simulate} years is complete.</p>"
                f"<blockquote>"
                f"<p>The projected median value is <strong>${median_value:,.2f}</strong>.</p>"
                f"<p>The likely range is between <strong>${percentile_25:,.2f}</strong> "
                f"and <strong>${percentile_75:,.2f}</strong>.</p>"
                f"</blockquote>"
            )
            
            if original_prompt:
                content += f"<p><em>Original request: {original_prompt}</em></p>"
            
            content += "</div>"
            
            metadata = {
                'simulation_results': results,
                'years_simulated': years_to_simulate,
                'original_prompt': original_prompt
            }
            
            return self.create_notification(
                user_id=user_id,
                notification_type='simulation_complete',
                title=title,
                content=content,
                metadata=metadata,
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"Failed to create simulation notification: {e}")
            return None
    
    def create_tracker_notification(
        self,
        user_id: str,
        content: str,
        goal_id: int,
        stock_symbol: str,
        event_type: str = 'tracker_event'
    ) -> Optional[str]:
        """
        Create a tracker event notification.
        
        Args:
            user_id: User ID
            content: Notification content
            goal_id: Associated goal ID
            stock_symbol: Stock symbol being tracked
            event_type: Type of tracker event
            
        Returns:
            Notification ID if successful, None otherwise
        """
        try:
            title = f"Tracker Alert: {stock_symbol}"
            
            formatted_content = (
                f"<div class='notification-content tracker'>"
                f"<p><strong>{stock_symbol}</strong> tracker event:</p>"
                f"<p>{content}</p>"
                f"</div>"
            )
            
            metadata = {
                'goal_id': goal_id,
                'stock_symbol': stock_symbol,
                'event_type': event_type
            }
            
            return self.create_notification(
                user_id=user_id,
                notification_type='tracker_alert',
                title=title,
                content=formatted_content,
                metadata=metadata,
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"Failed to create tracker notification: {e}")
            return None
    
    def create_research_complete_notification(
        self,
        user_id: str,
        session_id: str,
        session_type: str,
        summary: str,
        ticker_or_symbol: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a research completion notification.
        
        Args:
            user_id: User ID
            session_id: Research session ID
            session_type: Type of research (e.g., 'stock_research', 'index_analysis')
            summary: Research summary text
            ticker_or_symbol: Optional ticker or index symbol
            
        Returns:
            Notification ID if successful, None otherwise
        """
        try:
            # Determine title based on session type
            if ticker_or_symbol:
                title = f"Research Complete: {ticker_or_symbol}"
            else:
                title = f"Research Complete ({session_type})"
            
            content = (
                f"<div class='notification-content research'>"
                f"<p>Your {session_type.replace('_', ' ')} is complete.</p>"
                f"<blockquote>"
                f"<p>{summary}</p>"
                f"</blockquote>"
                f"<p><a href='/research/{session_id}'>View full research report</a></p>"
                f"</div>"
            )
            
            metadata = {
                'session_id': session_id,
                'session_type': session_type,
                'ticker_or_symbol': ticker_or_symbol
            }
            
            return self.create_notification(
                user_id=user_id,
                notification_type='research_complete',
                title=title,
                content=content,
                metadata=metadata,
                priority='normal'
            )
            
        except Exception as e:
            logger.error(f"Failed to create research notification: {e}")
            return None
    
    def mark_as_read(
        self,
        notification_id: str
    ) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            notification_model = get_model('Notification')
            
            if not notification_model:
                logger.error("Notification model not found in registry")
                return False
            
            with db_service.session_scope() as db_session:
                notification = db_session.query(notification_model).filter_by(
                    id=notification_id
                ).first()
                
                if not notification:
                    logger.warning(f"Notification not found: {notification_id}")
                    return False
                
                notification.is_read = True
                notification.read_at = datetime.now(timezone.utc)
                
                logger.debug(f"Marked notification as read: {notification_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> list:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            unread_only: If True, only return unread notifications
            limit: Maximum number of notifications to return
            
        Returns:
            List of notification objects
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            notification_model = get_model('Notification')
            
            if not notification_model:
                logger.error("Notification model not found in registry")
                return []
            
            with db_service.session_scope() as db_session:
                query = db_session.query(notification_model).filter_by(user_id=user_id)
                
                if unread_only:
                    query = query.filter_by(is_read=False)
                
                notifications = query.order_by(
                    notification_model.created_at.desc()
                ).limit(limit).all()
                
                logger.debug(f"Retrieved {len(notifications)} notifications for user {user_id}")
                return notifications
                
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
    
    def delete_notification(
        self,
        notification_id: str
    ) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from common.services.db_service import db_service
            from common.models.registry import get_model
            
            notification_model = get_model('Notification')
            
            if not notification_model:
                logger.error("Notification model not found in registry")
                return False
            
            with db_service.session_scope() as db_session:
                notification = db_session.query(notification_model).filter_by(
                    id=notification_id
                ).first()
                
                if not notification:
                    logger.warning(f"Notification not found: {notification_id}")
                    return False
                
                db_session.delete(notification)
                logger.info(f"Deleted notification: {notification_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete notification: {e}")
            return False


# Singleton instance
notification_persistence_service = NotificationPersistenceService()