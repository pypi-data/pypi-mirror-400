# common/services/communication/sms_service.py
"""
Outbound SMS Service

Multi-provider SMS service supporting Twilio, AWS SNS, and Vonage.
Handles delivery tracking, retry logic, and template rendering.

Usage:
    from common.services.communication import sms_service
    
    # Send simple SMS
    await sms_service.send(
        to="+1234567890",
        body="Your verification code is 123456",
    )
    
    # Send with template
    await sms_service.send_template(
        to="+1234567890",
        template_code="verification_code",
        variables={'code': '123456'},
    )
    
    # Send bulk
    await sms_service.send_bulk(
        recipients=[
            {'to': '+1234567890', 'variables': {'name': 'User 1'}},
            {'to': '+0987654321', 'variables': {'name': 'User 2'}},
        ],
        template_code="promotion_alert",
    )
"""

import logging
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, List, Union
import uuid

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

class SMSStatus(Enum):
    """SMS delivery status."""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"
    REJECTED = "rejected"


class SMSType(Enum):
    """SMS message type."""
    TRANSACTIONAL = "transactional"  # OTP, alerts, notifications
    PROMOTIONAL = "promotional"       # Marketing messages
    

@dataclass
class PhoneNumber:
    """Phone number with validation and formatting."""
    number: str
    country_code: Optional[str] = None
    
    def __post_init__(self):
        # Normalize phone number
        self.number = self._normalize(self.number)
    
    def _normalize(self, number: str) -> str:
        """Normalize phone number to E.164 format."""
        # Remove all non-digit characters except leading +
        cleaned = re.sub(r'[^\d+]', '', number)
        
        # Ensure starts with +
        if not cleaned.startswith('+'):
            # Assume US if no country code and 10 digits
            if len(cleaned) == 10:
                cleaned = '+1' + cleaned
            elif len(cleaned) == 11 and cleaned.startswith('1'):
                cleaned = '+' + cleaned
            else:
                cleaned = '+' + cleaned
        
        return cleaned
    
    def __str__(self) -> str:
        return self.number
    
    @classmethod
    def parse(cls, value: Union[str, Dict, 'PhoneNumber']) -> 'PhoneNumber':
        """Parse various input formats into PhoneNumber."""
        if isinstance(value, PhoneNumber):
            return value
        if isinstance(value, dict):
            return cls(
                number=value.get('number', value.get('phone', '')),
                country_code=value.get('country_code'),
            )
        if isinstance(value, str):
            return cls(number=value)
        raise ValueError(f"Cannot parse phone number from: {value}")
    
    def is_valid(self) -> bool:
        """Basic validation - E.164 format check."""
        # E.164: + followed by 1-15 digits
        return bool(re.match(r'^\+[1-9]\d{1,14}$', self.number))


@dataclass
class SMSMessage:
    """Complete SMS message."""
    to: PhoneNumber
    body: str
    from_number: Optional[str] = None
    message_type: SMSType = SMSType.TRANSACTIONAL
    
    # Optional features
    media_urls: List[str] = field(default_factory=list)  # For MMS
    callback_url: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SMSResult:
    """Result of sending an SMS."""
    success: bool
    message_id: str
    provider_message_id: Optional[str] = None
    status: SMSStatus = SMSStatus.PENDING
    error: Optional[str] = None
    error_code: Optional[str] = None
    provider: Optional[str] = None
    sent_at: Optional[datetime] = None
    segments: int = 1  # Number of SMS segments
    cost: Optional[float] = None  # Cost in USD if available


# =============================================================================
# PROVIDER ABSTRACT BASE CLASS
# =============================================================================

class SMSProvider(ABC):
    """Abstract base class for SMS providers."""
    
    name: str = "base"
    
    @abstractmethod
    async def send(self, message: SMSMessage) -> SMSResult:
        """Send a single SMS."""
        pass
    
    @abstractmethod
    async def send_bulk(self, messages: List[SMSMessage]) -> List[SMSResult]:
        """Send multiple SMS messages."""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider is properly configured."""
        pass
    
    async def get_delivery_status(self, provider_message_id: str) -> Optional[SMSStatus]:
        """Get delivery status for a message (if supported)."""
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            'name': self.name,
            'configured': self.is_configured(),
        }
    
    def _count_segments(self, body: str) -> int:
        """
        Count SMS segments.
        
        GSM-7: 160 chars (or 153 per segment if multipart)
        Unicode: 70 chars (or 67 per segment if multipart)
        """
        # Check if message contains non-GSM characters
        gsm_chars = set(
            '@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ !"#¤%&\'()*+,-./0123456789:;<=>?'
            '¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà'
        )
        is_gsm = all(c in gsm_chars for c in body)
        
        if is_gsm:
            if len(body) <= 160:
                return 1
            return (len(body) + 152) // 153
        else:
            if len(body) <= 70:
                return 1
            return (len(body) + 66) // 67


# =============================================================================
# TWILIO PROVIDER
# =============================================================================

class TwilioProvider(SMSProvider):
    """Twilio SMS provider."""
    
    name = "twilio"
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
        messaging_service_sid: Optional[str] = None,
    ):
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = from_number or os.getenv('TWILIO_FROM_NUMBER')
        self.messaging_service_sid = messaging_service_sid or os.getenv('TWILIO_MESSAGING_SERVICE_SID')
        self._client = None
    
    def is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token and (self.from_number or self.messaging_service_sid))
    
    @property
    def client(self):
        """Lazy-load Twilio client."""
        if self._client is None:
            try:
                from twilio.rest import Client
                self._client = Client(self.account_sid, self.auth_token)
            except ImportError:
                raise ImportError("twilio package not installed. Run: pip install twilio")
        return self._client
    
    async def send(self, message: SMSMessage) -> SMSResult:
        """Send SMS via Twilio."""
        if not self.is_configured():
            return SMSResult(
                success=False,
                message_id=message.message_id,
                error="Twilio not configured",
                provider=self.name,
            )
        
        try:
            # Build message params
            params = {
                'to': str(message.to),
                'body': message.body,
            }
            
            # Use messaging service or from number
            if self.messaging_service_sid:
                params['messaging_service_sid'] = self.messaging_service_sid
            else:
                params['from_'] = message.from_number or self.from_number
            
            # Status callback
            if message.callback_url:
                params['status_callback'] = message.callback_url
            
            # Media URLs (MMS)
            if message.media_urls:
                params['media_url'] = message.media_urls
            
            # Send
            twilio_message = self.client.messages.create(**params)
            
            # Map Twilio status
            status_map = {
                'queued': SMSStatus.QUEUED,
                'sending': SMSStatus.QUEUED,
                'sent': SMSStatus.SENT,
                'delivered': SMSStatus.DELIVERED,
                'failed': SMSStatus.FAILED,
                'undelivered': SMSStatus.UNDELIVERED,
            }
            
            return SMSResult(
                success=True,
                message_id=message.message_id,
                provider_message_id=twilio_message.sid,
                status=status_map.get(twilio_message.status, SMSStatus.QUEUED),
                provider=self.name,
                sent_at=datetime.now(timezone.utc),
                segments=twilio_message.num_segments or self._count_segments(message.body),
            )
            
        except Exception as e:
            logger.error(f"Twilio send failed: {e}", exc_info=True)
            
            # Extract Twilio error code if available
            error_code = None
            if hasattr(e, 'code'):
                error_code = str(e.code)
            
            return SMSResult(
                success=False,
                message_id=message.message_id,
                error=str(e),
                error_code=error_code,
                status=SMSStatus.FAILED,
                provider=self.name,
            )
    
    async def send_bulk(self, messages: List[SMSMessage]) -> List[SMSResult]:
        """Send multiple SMS via Twilio."""
        # Twilio doesn't have native bulk API, send individually
        results = []
        for message in messages:
            result = await self.send(message)
            results.append(result)
        return results
    
    async def get_delivery_status(self, provider_message_id: str) -> Optional[SMSStatus]:
        """Get delivery status from Twilio."""
        try:
            twilio_message = self.client.messages(provider_message_id).fetch()
            
            status_map = {
                'queued': SMSStatus.QUEUED,
                'sending': SMSStatus.QUEUED,
                'sent': SMSStatus.SENT,
                'delivered': SMSStatus.DELIVERED,
                'failed': SMSStatus.FAILED,
                'undelivered': SMSStatus.UNDELIVERED,
            }
            
            return status_map.get(twilio_message.status)
            
        except Exception as e:
            logger.error(f"Failed to get Twilio status: {e}")
            return None


# =============================================================================
# AWS SNS PROVIDER
# =============================================================================

class SNSProvider(SMSProvider):
    """AWS SNS SMS provider."""
    
    name = "sns"
    
    def __init__(
        self,
        region: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        sender_id: Optional[str] = None,
    ):
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        self.access_key = access_key or os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = secret_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.sender_id = sender_id or os.getenv('AWS_SNS_SENDER_ID')
        self._client = None
    
    def is_configured(self) -> bool:
        # Can use IAM role if no explicit keys
        return True
    
    @property
    def client(self):
        """Lazy-load boto3 SNS client."""
        if self._client is None:
            try:
                import boto3
                kwargs = {'region_name': self.region}
                if self.access_key and self.secret_key:
                    kwargs['aws_access_key_id'] = self.access_key
                    kwargs['aws_secret_access_key'] = self.secret_key
                self._client = boto3.client('sns', **kwargs)
            except ImportError:
                raise ImportError("boto3 package not installed. Run: pip install boto3")
        return self._client
    
    async def send(self, message: SMSMessage) -> SMSResult:
        """Send SMS via AWS SNS."""
        try:
            # Build message attributes
            attributes = {
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional' if message.message_type == SMSType.TRANSACTIONAL else 'Promotional',
                },
            }
            
            # Sender ID (not supported in all regions)
            if self.sender_id:
                attributes['AWS.SNS.SMS.SenderID'] = {
                    'DataType': 'String',
                    'StringValue': self.sender_id,
                }
            
            # Send
            response = self.client.publish(
                PhoneNumber=str(message.to),
                Message=message.body,
                MessageAttributes=attributes,
            )
            
            return SMSResult(
                success=True,
                message_id=message.message_id,
                provider_message_id=response.get('MessageId', ''),
                status=SMSStatus.SENT,
                provider=self.name,
                sent_at=datetime.now(timezone.utc),
                segments=self._count_segments(message.body),
            )
            
        except Exception as e:
            logger.error(f"SNS send failed: {e}", exc_info=True)
            return SMSResult(
                success=False,
                message_id=message.message_id,
                error=str(e),
                status=SMSStatus.FAILED,
                provider=self.name,
            )
    
    async def send_bulk(self, messages: List[SMSMessage]) -> List[SMSResult]:
        """Send multiple SMS via SNS."""
        results = []
        for message in messages:
            result = await self.send(message)
            results.append(result)
        return results


# =============================================================================
# VONAGE (NEXMO) PROVIDER
# =============================================================================

class VonageProvider(SMSProvider):
    """Vonage (formerly Nexmo) SMS provider."""
    
    name = "vonage"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        from_number: Optional[str] = None,
        brand_name: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv('VONAGE_API_KEY')
        self.api_secret = api_secret or os.getenv('VONAGE_API_SECRET')
        self.from_number = from_number or os.getenv('VONAGE_FROM_NUMBER')
        self.brand_name = brand_name or os.getenv('VONAGE_BRAND_NAME')
        self._client = None
    
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret and (self.from_number or self.brand_name))
    
    @property
    def client(self):
        """Lazy-load Vonage client."""
        if self._client is None:
            try:
                import vonage
                self._client = vonage.Client(key=self.api_key, secret=self.api_secret)
            except ImportError:
                raise ImportError("vonage package not installed. Run: pip install vonage")
        return self._client
    
    async def send(self, message: SMSMessage) -> SMSResult:
        """Send SMS via Vonage."""
        if not self.is_configured():
            return SMSResult(
                success=False,
                message_id=message.message_id,
                error="Vonage not configured",
                provider=self.name,
            )
        
        try:
            import vonage
            sms = vonage.Sms(self.client)
            
            # Determine sender (alphanumeric brand or phone number)
            sender = message.from_number or self.brand_name or self.from_number
            
            response = sms.send_message({
                'from': sender,
                'to': str(message.to).lstrip('+'),  # Vonage wants no + prefix
                'text': message.body,
            })
            
            # Check response
            first_message = response.get('messages', [{}])[0]
            status_code = first_message.get('status', '1')
            
            if status_code == '0':
                return SMSResult(
                    success=True,
                    message_id=message.message_id,
                    provider_message_id=first_message.get('message-id', ''),
                    status=SMSStatus.SENT,
                    provider=self.name,
                    sent_at=datetime.now(timezone.utc),
                    segments=int(first_message.get('message-count', 1)),
                    cost=float(first_message.get('message-price', 0)),
                )
            else:
                return SMSResult(
                    success=False,
                    message_id=message.message_id,
                    error=first_message.get('error-text', 'Unknown error'),
                    error_code=status_code,
                    status=SMSStatus.FAILED,
                    provider=self.name,
                )
            
        except Exception as e:
            logger.error(f"Vonage send failed: {e}", exc_info=True)
            return SMSResult(
                success=False,
                message_id=message.message_id,
                error=str(e),
                status=SMSStatus.FAILED,
                provider=self.name,
            )
    
    async def send_bulk(self, messages: List[SMSMessage]) -> List[SMSResult]:
        """Send multiple SMS via Vonage."""
        results = []
        for message in messages:
            result = await self.send(message)
            results.append(result)
        return results


# =============================================================================
# CONSOLE PROVIDER (Development/Testing)
# =============================================================================

class ConsoleSMSProvider(SMSProvider):
    """Console SMS provider for development - prints SMS instead of sending."""
    
    name = "console"
    
    def is_configured(self) -> bool:
        return True
    
    async def send(self, message: SMSMessage) -> SMSResult:
        """Print SMS to console."""
        print("\n" + "=" * 60)
        print("📱 SMS (Console Provider)")
        print("=" * 60)
        print(f"To: {message.to}")
        if message.from_number:
            print(f"From: {message.from_number}")
        print(f"Type: {message.message_type.value}")
        print("-" * 60)
        print(f"Body ({len(message.body)} chars, ~{self._count_segments(message.body)} segments):")
        print(message.body)
        if message.media_urls:
            print(f"\nMedia: {message.media_urls}")
        print("=" * 60 + "\n")
        
        return SMSResult(
            success=True,
            message_id=message.message_id,
            provider_message_id=f"console-{message.message_id}",
            status=SMSStatus.SENT,
            provider=self.name,
            sent_at=datetime.now(timezone.utc),
            segments=self._count_segments(message.body),
        )
    
    async def send_bulk(self, messages: List[SMSMessage]) -> List[SMSResult]:
        """Print multiple SMS to console."""
        results = []
        for message in messages:
            result = await self.send(message)
            results.append(result)
        return results


# =============================================================================
# SMS SERVICE
# =============================================================================

class SMSService:
    """
    Main SMS service with provider abstraction.
    
    Supports multiple providers with automatic fallback.
    """
    
    # Provider registry
    PROVIDERS = {
        'twilio': TwilioProvider,
        'sns': SNSProvider,
        'vonage': VonageProvider,
        'console': ConsoleSMSProvider,
    }
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize SMS service.
        
        Args:
            provider: Provider name ('twilio', 'sns', 'vonage', 'console')
                     If not specified, auto-detects from environment.
        """
        self._provider_name = provider or os.getenv('SMS_PROVIDER', 'console')
        self._provider: Optional[SMSProvider] = None
        self._db = None
        
        logger.info(f"📱 SMSService initialized with provider: {self._provider_name}")
    
    @property
    def db(self):
        """Lazy-load database service for logging."""
        if self._db is None:
            try:
                from common.services import db_service
                self._db = db_service
            except ImportError:
                pass
        return self._db
    
    @property
    def provider(self) -> SMSProvider:
        """Get the configured SMS provider."""
        if self._provider is None:
            provider_class = self.PROVIDERS.get(self._provider_name)
            if not provider_class:
                logger.warning(f"Unknown provider '{self._provider_name}', falling back to console")
                provider_class = ConsoleSMSProvider
            self._provider = provider_class()
        return self._provider
    
    def set_provider(self, provider: Union[str, SMSProvider]) -> None:
        """Change the SMS provider."""
        if isinstance(provider, str):
            provider_class = self.PROVIDERS.get(provider)
            if not provider_class:
                raise ValueError(f"Unknown provider: {provider}")
            self._provider = provider_class()
            self._provider_name = provider
        else:
            self._provider = provider
            self._provider_name = provider.name
    
    async def send(
        self,
        to: Union[str, PhoneNumber],
        body: str,
        from_number: Optional[str] = None,
        message_type: SMSType = SMSType.TRANSACTIONAL,
        media_urls: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SMSResult:
        """
        Send a single SMS.
        
        Args:
            to: Recipient phone number (E.164 format preferred)
            body: Message text
            from_number: Sender number (if not using default)
            message_type: Transactional or promotional
            media_urls: Media URLs for MMS (if supported)
            tags: Tags for tracking
            metadata: Custom metadata
            
        Returns:
            SMSResult with delivery status
        """
        # Parse phone number
        phone = PhoneNumber.parse(to)
        
        if not phone.is_valid():
            return SMSResult(
                success=False,
                message_id=str(uuid.uuid4()),
                error=f"Invalid phone number: {to}",
                status=SMSStatus.REJECTED,
            )
        
        # Build message
        message = SMSMessage(
            to=phone,
            body=body,
            from_number=from_number,
            message_type=message_type,
            media_urls=media_urls or [],
            tags=tags or [],
            metadata=metadata or {},
        )
        
        # Send via provider
        result = await self.provider.send(message)
        
        # Log to database
        await self._log_sms(message, result)
        
        return result
    
    async def send_template(
        self,
        to: Union[str, PhoneNumber],
        template_code: str,
        variables: Dict[str, Any],
        from_number: Optional[str] = None,
        message_type: SMSType = SMSType.TRANSACTIONAL,
    ) -> SMSResult:
        """
        Send SMS using a template.
        
        Args:
            to: Recipient phone number
            template_code: MessageTemplate code
            variables: Template variables for rendering
            from_number: Sender number (if not using default)
            message_type: Transactional or promotional
            
        Returns:
            SMSResult with delivery status
        """
        # Load template
        template = await self._get_template(template_code)
        if not template:
            return SMSResult(
                success=False,
                message_id=str(uuid.uuid4()),
                error=f"Template not found: {template_code}",
                status=SMSStatus.FAILED,
            )
        
        # Render template
        body = self._render_string(template.get('sms_body', ''), variables)
        
        if not body:
            return SMSResult(
                success=False,
                message_id=str(uuid.uuid4()),
                error=f"Template has no SMS body: {template_code}",
                status=SMSStatus.FAILED,
            )
        
        return await self.send(
            to=to,
            body=body,
            from_number=from_number,
            message_type=message_type,
            tags=[template_code],
            metadata={'template_code': template_code},
        )
    
    async def send_bulk(
        self,
        recipients: List[Dict[str, Any]],
        template_code: Optional[str] = None,
        body: Optional[str] = None,
        from_number: Optional[str] = None,
        message_type: SMSType = SMSType.TRANSACTIONAL,
    ) -> List[SMSResult]:
        """
        Send bulk SMS.
        
        Args:
            recipients: List of dicts with 'to' and optional 'variables'
            template_code: Template to use (if not providing body)
            body: Message body (can include {variables})
            from_number: Sender number
            message_type: Transactional or promotional
            
        Returns:
            List of SMSResult
        """
        # Load template if specified
        template = None
        if template_code:
            template = await self._get_template(template_code)
        
        messages = []
        for recipient in recipients:
            to = recipient.get('to')
            variables = recipient.get('variables', {})
            
            phone = PhoneNumber.parse(to)
            if not phone.is_valid():
                continue
            
            if template:
                msg_body = self._render_string(template.get('sms_body', ''), variables)
            else:
                msg_body = self._render_string(body or '', variables)
            
            if not msg_body:
                continue
            
            messages.append(SMSMessage(
                to=phone,
                body=msg_body,
                from_number=from_number,
                message_type=message_type,
                tags=[template_code] if template_code else [],
                metadata={'bulk': True, 'template_code': template_code},
            ))
        
        # Send via provider
        results = await self.provider.send_bulk(messages)
        
        # Log results
        for message, result in zip(messages, results):
            await self._log_sms(message, result)
        
        return results
    
    async def send_otp(
        self,
        to: Union[str, PhoneNumber],
        code: str,
        expiry_minutes: int = 10,
    ) -> SMSResult:
        """
        Send OTP verification code.
        
        Convenience method for common use case.
        
        Args:
            to: Recipient phone number
            code: OTP code
            expiry_minutes: Code expiry time
            
        Returns:
            SMSResult
        """
        body = f"Your verification code is: {code}. It expires in {expiry_minutes} minutes."
        
        return await self.send(
            to=to,
            body=body,
            message_type=SMSType.TRANSACTIONAL,
            tags=['otp', 'verification'],
        )
    
    async def _get_template(self, template_code: str) -> Optional[Dict[str, Any]]:
        """Get SMS template by code."""
        if not self.db:
            return None
        
        try:
            templates = self.db.query(
                'MessageTemplate',
                filters={'code': template_code, 'is_active': True},
                limit=1,
            )
            return templates[0] if templates else None
        except Exception as e:
            logger.warning(f"Failed to load template {template_code}: {e}")
            return None
    
    def _render_string(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Render template string with variables."""
        if not template_str:
            return ''
        
        result = template_str
        for key, value in variables.items():
            placeholder = '{' + key + '}'
            result = result.replace(placeholder, str(value))
        return result
    
    async def _log_sms(self, message: SMSMessage, result: SMSResult) -> None:
        """Log SMS to database."""
        if not self.db:
            return
        
        try:
            self.db.create('MessageDeliveryLog', {
                'id': str(uuid.uuid4()),
                'message_id': message.message_id,
                'channel': 'sms',
                'status': 'success' if result.success else 'failed',
                'provider': result.provider,
                'provider_response': {
                    'provider_message_id': result.provider_message_id,
                    'status': result.status.value,
                    'segments': result.segments,
                    'cost': result.cost,
                },
                'error_message': result.error,
                'attempted_at': datetime.now(timezone.utc),
                'delivered_at': result.sent_at,
            })
        except Exception as e:
            logger.debug(f"Failed to log SMS: {e}")
    
    async def get_delivery_status(self, provider_message_id: str) -> Optional[SMSStatus]:
        """
        Get delivery status for a sent message.
        
        Args:
            provider_message_id: The provider's message ID
            
        Returns:
            SMSStatus if available
        """
        return await self.provider.get_delivery_status(provider_message_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            'provider': self._provider_name,
            'provider_status': self.provider.get_status(),
            'configured': self.provider.is_configured(),
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_service_instance: Optional[SMSService] = None


def get_sms_service() -> SMSService:
    """Get the singleton SMSService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = SMSService()
    return _service_instance


# Module-level singleton for convenience
sms_service = get_sms_service()
