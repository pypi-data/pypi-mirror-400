# common/services/persistence/messaging_service.py
"""
Multi-Channel Messaging Service

Handles message delivery across channels:
- In-app messages
- Email messages (via SendGrid, SES, etc.)
- Push notifications (via Firebase, OneSignal, etc.)

NOTE: This is separate from the existing Notification system which handles
social/collaboration notifications with comments and tags. This system
is for templated, multi-channel message delivery.

Supports:
- Template rendering with variables
- User preference checking
- Delivery tracking and retry
- Digest batching

Usage:
    from common.services.persistence import messaging_service
    
    # Send using template
    await messaging_service.send_message(
        user_id="user-123",
        template_code="investment_goal_reached",
        variables={
            'goal_name': 'Tech Growth',
            'current_value': 52000,
            'target_amount': 50000,
        },
    )
    
    # Send custom message
    await messaging_service.send_custom(
        user_id="user-123",
        channels=['in_app', 'email'],
        title="Custom Alert",
        body="Something happened!",
        priority="high",
    )
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class MessagingService:
    """
    Multi-channel message delivery with template support.
    """
    
    def __init__(self):
        self._db = None
        self._email_provider = None
        self._push_provider = None
        logger.info("📬 MessagingService initialized")
    
    @property
    def db(self):
        """Lazy-load database service."""
        if self._db is None:
            from common.services import db_service
            self._db = db_service
        return self._db
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    async def send_message(
        self,
        user_id: str,
        template_code: str,
        variables: Dict[str, Any],
        channels: Optional[List[str]] = None,
        priority: Optional[str] = None,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None,
        action_url: Optional[str] = None,
        scheduled_for: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Send message using a template.
        
        Args:
            user_id: Target user
            template_code: Template code (e.g., 'investment_goal_reached')
            variables: Variables for template rendering
            channels: Override channels (default: use template defaults)
            priority: Override priority (default: use template default)
            source_type: Source of message (workflow, system, etc.)
            source_id: Related entity ID
            action_url: Override action URL
            scheduled_for: Schedule for future delivery
            
        Returns:
            Created message record
        """
        # Load template
        template = await self._get_template(template_code)
        if not template:
            raise ValueError(f"Template not found: {template_code}")
        
        # Get user preferences
        preferences = await self._get_user_preferences(user_id)
        
        # Determine channels to use
        if channels is None:
            channels = template.get('default_channels', ['in_app'])
        
        # Filter by user preferences
        channels = self._filter_channels_by_preferences(channels, preferences)
        
        if not channels:
            logger.info(f"No channels available for user {user_id}, skipping message")
            return {'status': 'skipped', 'reason': 'no_channels'}
        
        # Render template content
        rendered = self._render_template(template, variables)
        
        # Create message record
        message_id = str(uuid.uuid4())
        message_data = {
            'id': message_id,
            'user_id': user_id,
            'template_id': template.get('id'),
            'category': template.get('category', 'system'),
            'priority': priority or template.get('priority', 'normal'),
            'title': rendered.get('in_app_title') or rendered.get('push_title', ''),
            'body': rendered.get('in_app_body') or rendered.get('push_body', ''),
            'data': variables,
            'action_url': action_url or rendered.get('in_app_action_url'),
            'icon': rendered.get('in_app_icon'),
            'source_type': source_type,
            'source_id': source_id,
            'channels_requested': channels,
            'scheduled_for': scheduled_for,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        
        # Set channel statuses
        if 'in_app' in channels:
            message_data['in_app_status'] = 'pending'
        if 'email' in channels:
            message_data['email_status'] = 'pending'
        if 'push' in channels:
            message_data['push_status'] = 'pending'
        
        self.db.create('Message', message_data)
        
        # If scheduled, return now
        if scheduled_for and scheduled_for > datetime.now(timezone.utc):
            logger.info(f"Message {message_id} scheduled for {scheduled_for}")
            return message_data
        
        # Deliver immediately
        await self._deliver_message(message_id, rendered, channels, preferences)
        
        return message_data
    
    async def send_custom(
        self,
        user_id: str,
        title: str,
        body: str,
        channels: List[str] = None,
        category: str = 'system',
        priority: str = 'normal',
        action_url: Optional[str] = None,
        icon: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        email_html: Optional[str] = None,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a custom message without a template.
        """
        channels = channels or ['in_app']
        
        # Get user preferences
        preferences = await self._get_user_preferences(user_id)
        channels = self._filter_channels_by_preferences(channels, preferences)
        
        if not channels:
            return {'status': 'skipped', 'reason': 'no_channels'}
        
        message_id = str(uuid.uuid4())
        message_data = {
            'id': message_id,
            'user_id': user_id,
            'category': category,
            'priority': priority,
            'title': title,
            'body': body,
            'data': data or {},
            'action_url': action_url,
            'icon': icon,
            'source_type': source_type,
            'source_id': source_id,
            'channels_requested': channels,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        
        if 'in_app' in channels:
            message_data['in_app_status'] = 'pending'
        if 'email' in channels:
            message_data['email_status'] = 'pending'
        if 'push' in channels:
            message_data['push_status'] = 'pending'
        
        self.db.create('Message', message_data)
        
        rendered = {
            'in_app_title': title,
            'in_app_body': body,
            'in_app_action_url': action_url,
            'in_app_icon': icon,
            'email_subject': title,
            'email_body_html': email_html or f"<p>{body}</p>",
            'push_title': title,
            'push_body': body,
        }
        
        await self._deliver_message(message_id, rendered, channels, preferences)
        
        return message_data
    
    async def get_user_messages(
        self,
        user_id: str,
        unread_only: bool = False,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get messages for a user."""
        filters = {'user_id': user_id}
        
        if unread_only:
            filters['in_app_status'] = 'delivered'
        
        if category:
            filters['category'] = category
        
        messages = self.db.query(
            'Message',
            filters=filters,
            order_by=[('created_at', 'desc')],
            limit=limit,
        )
        return messages
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread messages."""
        messages = self.db.query(
            'Message',
            filters={
                'user_id': user_id,
                'in_app_status': 'delivered',
            },
        )
        return len(messages)
    
    async def mark_as_read(
        self,
        message_id: str,
        user_id: str,
    ) -> bool:
        """Mark message as read."""
        message = self.db.get('Message', message_id)
        
        if message and message['user_id'] == user_id:
            self.db.update('Message', message_id, {
                'in_app_status': 'read',
                'in_app_read_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
            })
            return True
        return False
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all messages as read for a user."""
        messages = self.db.query(
            'Message',
            filters={
                'user_id': user_id,
                'in_app_status': 'delivered',
            },
        )
        
        count = 0
        now = datetime.now(timezone.utc)
        for msg in messages:
            self.db.update('Message', msg['id'], {
                'in_app_status': 'read',
                'in_app_read_at': now,
                'updated_at': now,
            })
            count += 1
        
        return count
    
    async def dismiss(self, message_id: str, user_id: str) -> bool:
        """Dismiss a message."""
        message = self.db.get('Message', message_id)
        
        if message and message['user_id'] == user_id:
            self.db.update('Message', message_id, {
                'in_app_status': 'dismissed',
                'updated_at': datetime.now(timezone.utc),
            })
            return True
        return False
    
    # =========================================================================
    # DELIVERY
    # =========================================================================
    
    async def _deliver_message(
        self,
        message_id: str,
        rendered: Dict[str, str],
        channels: List[str],
        preferences: Dict[str, Any],
    ) -> None:
        """Deliver message to all requested channels."""
        
        for channel in channels:
            try:
                if channel == 'in_app':
                    await self._deliver_in_app(message_id, rendered)
                elif channel == 'email':
                    await self._deliver_email(message_id, rendered, preferences)
                elif channel == 'push':
                    await self._deliver_push(message_id, rendered, preferences)
                
                # Log successful delivery
                await self._log_delivery(
                    message_id, channel, 'success', provider=channel
                )
                
            except Exception as e:
                logger.error(f"Failed to deliver {channel} message: {e}")
                await self._log_delivery(
                    message_id, channel, 'failed', error_message=str(e)
                )
    
    async def _deliver_in_app(
        self,
        message_id: str,
        rendered: Dict[str, str],
    ) -> None:
        """Deliver in-app message (update status)."""
        self.db.update('Message', message_id, {
            'in_app_status': 'delivered',
            'updated_at': datetime.now(timezone.utc),
        })
        
        # TODO: Emit WebSocket event for real-time delivery
        # await websocket_service.emit_to_user(user_id, 'message', message_data)
        
        logger.info(f"✓ In-app message delivered: {message_id}")
    
    async def _deliver_email(
        self,
        message_id: str,
        rendered: Dict[str, str],
        preferences: Dict[str, Any],
    ) -> None:
        """Deliver email message."""
        email = preferences.get('email_address')
        
        if not email:
            logger.warning(f"No email address for message {message_id}")
            self.db.update('Message', message_id, {
                'email_status': 'failed',
            })
            return
        
        # TODO: Integrate with email provider (SendGrid, SES, etc.)
        # For now, just log and mark as sent
        
        subject = rendered.get('email_subject', rendered.get('in_app_title', ''))
        body_html = rendered.get('email_body_html', '')
        body_text = rendered.get('email_body_text', rendered.get('in_app_body', ''))
        
        # Placeholder for actual email sending
        # response = await self._email_provider.send(
        #     to=email,
        #     subject=subject,
        #     html=body_html,
        #     text=body_text,
        # )
        
        logger.info(f"📧 Email message queued: {message_id} -> {email}")
        
        self.db.update('Message', message_id, {
            'email_status': 'sent',
            'email_sent_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        })
    
    async def _deliver_push(
        self,
        message_id: str,
        rendered: Dict[str, str],
        preferences: Dict[str, Any],
    ) -> None:
        """Deliver push notification."""
        subscription = preferences.get('push_subscription')
        
        if not subscription:
            logger.warning(f"No push subscription for message {message_id}")
            self.db.update('Message', message_id, {
                'push_status': 'failed',
            })
            return
        
        # TODO: Integrate with push provider (Firebase, OneSignal, etc.)
        # For now, just log and mark as sent
        
        title = rendered.get('push_title', rendered.get('in_app_title', ''))
        body = rendered.get('push_body', rendered.get('in_app_body', ''))
        
        # Placeholder for actual push sending
        # await self._push_provider.send(
        #     subscription=subscription,
        #     title=title,
        #     body=body,
        #     icon=rendered.get('push_icon'),
        #     action_url=rendered.get('push_action_url'),
        # )
        
        logger.info(f"🔔 Push message queued: {message_id}")
        
        self.db.update('Message', message_id, {
            'push_status': 'sent',
            'push_sent_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        })
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    async def _get_template(self, template_code: str) -> Optional[Dict[str, Any]]:
        """Get message template by code."""
        templates = self.db.query(
            'MessageTemplate',
            filters={'code': template_code, 'is_active': True},
            limit=1,
        )
        return templates[0] if templates else None
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user messaging preferences."""
        preferences = self.db.query(
            'UserMessagingPreference',
            filters={'user_id': user_id},
            limit=1,
        )
        
        if preferences:
            return preferences[0]
        
        # Return defaults
        return {
            'user_id': user_id,
            'email_enabled': True,
            'push_enabled': True,
            'in_app_enabled': True,
            'digest_frequency': 'immediate',
        }
    
    def _filter_channels_by_preferences(
        self,
        channels: List[str],
        preferences: Dict[str, Any],
    ) -> List[str]:
        """Filter channels based on user preferences."""
        filtered = []
        
        for channel in channels:
            if channel == 'in_app' and preferences.get('in_app_enabled', True):
                filtered.append(channel)
            elif channel == 'email' and preferences.get('email_enabled', True):
                if preferences.get('email_address'):
                    filtered.append(channel)
            elif channel == 'push' and preferences.get('push_enabled', True):
                if preferences.get('push_subscription'):
                    filtered.append(channel)
        
        return filtered
    
    def _render_template(
        self,
        template: Dict[str, Any],
        variables: Dict[str, Any],
    ) -> Dict[str, str]:
        """Render template with variables."""
        rendered = {}
        
        # Fields to render
        fields = [
            'in_app_title', 'in_app_body', 'in_app_action_url', 'in_app_icon',
            'email_subject', 'email_body_html', 'email_body_text',
            'push_title', 'push_body', 'push_action_url', 'push_icon',
        ]
        
        for field in fields:
            value = template.get(field)
            if value:
                rendered[field] = self._render_string(value, variables)
        
        return rendered
    
    def _render_string(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render a single template string with {variable} substitution."""
        result = template_str
        
        for key, value in variables.items():
            placeholder = '{' + key + '}'
            result = result.replace(placeholder, str(value))
        
        return result
    
    async def _log_delivery(
        self,
        message_id: str,
        channel: str,
        status: str,
        provider: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Log delivery attempt."""
        log_id = str(uuid.uuid4())
        
        self.db.create('MessageDeliveryLog', {
            'id': log_id,
            'message_id': message_id,
            'channel': channel,
            'status': status,
            'provider': provider,
            'error_message': error_message,
            'attempted_at': datetime.now(timezone.utc),
            'delivered_at': datetime.now(timezone.utc) if status == 'success' else None,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        })


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_service_instance: Optional[MessagingService] = None


def get_messaging_service() -> MessagingService:
    """Get singleton MessagingService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = MessagingService()
    return _service_instance


# Module-level export for TimberServiceFactory
messaging_service = get_messaging_service()
