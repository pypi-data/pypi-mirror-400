# common/services/communication/email_service.py
"""
Outbound Email Service

Multi-provider email service supporting SendGrid, AWS SES, and SMTP.
Handles template rendering, delivery tracking, and retry logic.

Usage:
    from common.services.communication import email_service
    
    # Send simple email
    await email_service.send(
        to="user@example.com",
        subject="Welcome!",
        html="<h1>Hello</h1>",
    )
    
    # Send with template
    await email_service.send_template(
        to="user@example.com",
        template_code="welcome_email",
        variables={'name': 'John', 'action_url': 'https://...'},
    )
    
    # Send bulk
    await email_service.send_bulk(
        recipients=[
            {'to': 'user1@example.com', 'variables': {'name': 'User 1'}},
            {'to': 'user2@example.com', 'variables': {'name': 'User 2'}},
        ],
        template_code="newsletter",
    )
"""

import logging
import os
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

class EmailStatus(Enum):
    """Email delivery status."""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"
    SPAM = "spam"
    UNSUBSCRIBED = "unsubscribed"


@dataclass
class EmailAddress:
    """Email address with optional name."""
    email: str
    name: Optional[str] = None
    
    def __str__(self) -> str:
        if self.name:
            return f"{self.name} <{self.email}>"
        return self.email
    
    @classmethod
    def parse(cls, value: Union[str, Dict, 'EmailAddress']) -> 'EmailAddress':
        """Parse various input formats into EmailAddress."""
        if isinstance(value, EmailAddress):
            return value
        if isinstance(value, dict):
            return cls(email=value.get('email', ''), name=value.get('name'))
        if isinstance(value, str):
            # Handle "Name <email>" format
            if '<' in value and '>' in value:
                name = value[:value.index('<')].strip()
                email = value[value.index('<')+1:value.index('>')].strip()
                return cls(email=email, name=name if name else None)
            return cls(email=value)
        raise ValueError(f"Cannot parse email address from: {value}")


@dataclass
class EmailAttachment:
    """Email attachment."""
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"
    content_id: Optional[str] = None  # For inline images


@dataclass
class EmailMessage:
    """Complete email message."""
    to: List[EmailAddress]
    subject: str
    html: Optional[str] = None
    text: Optional[str] = None
    from_email: Optional[EmailAddress] = None
    reply_to: Optional[EmailAddress] = None
    cc: List[EmailAddress] = field(default_factory=list)
    bcc: List[EmailAddress] = field(default_factory=list)
    attachments: List[EmailAttachment] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Tracking
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EmailResult:
    """Result of sending an email."""
    success: bool
    message_id: str
    provider_message_id: Optional[str] = None
    status: EmailStatus = EmailStatus.PENDING
    error: Optional[str] = None
    provider: Optional[str] = None
    sent_at: Optional[datetime] = None


# =============================================================================
# PROVIDER ABSTRACT BASE CLASS
# =============================================================================

class EmailProvider(ABC):
    """Abstract base class for email providers."""
    
    name: str = "base"
    
    @abstractmethod
    async def send(self, message: EmailMessage) -> EmailResult:
        """Send a single email."""
        pass
    
    @abstractmethod
    async def send_bulk(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple emails."""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider is properly configured."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            'name': self.name,
            'configured': self.is_configured(),
        }


# =============================================================================
# SENDGRID PROVIDER
# =============================================================================

class SendGridProvider(EmailProvider):
    """SendGrid email provider."""
    
    name = "sendgrid"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        self._client = None
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    @property
    def client(self):
        """Lazy-load SendGrid client."""
        if self._client is None:
            try:
                from sendgrid import SendGridAPIClient
                self._client = SendGridAPIClient(api_key=self.api_key)
            except ImportError:
                raise ImportError("sendgrid package not installed. Run: pip install sendgrid")
        return self._client
    
    async def send(self, message: EmailMessage) -> EmailResult:
        """Send email via SendGrid."""
        if not self.is_configured():
            return EmailResult(
                success=False,
                message_id=message.message_id,
                error="SendGrid API key not configured",
                provider=self.name,
            )
        
        try:
            from sendgrid.helpers.mail import (
                Mail, Email, To, Content, Attachment,
                FileContent, FileName, FileType, Disposition,
            )
            import base64
            
            # Build mail object
            mail = Mail()
            
            # From
            from_email = message.from_email or EmailAddress(
                email=os.getenv('EMAIL_FROM_ADDRESS', 'noreply@example.com'),
                name=os.getenv('EMAIL_FROM_NAME', 'OakQuant'),
            )
            mail.from_email = Email(from_email.email, from_email.name)
            
            # To
            for recipient in message.to:
                mail.add_to(To(recipient.email, recipient.name))
            
            # Subject
            mail.subject = message.subject
            
            # Content
            if message.text:
                mail.add_content(Content("text/plain", message.text))
            if message.html:
                mail.add_content(Content("text/html", message.html))
            
            # Reply-To
            if message.reply_to:
                mail.reply_to = Email(message.reply_to.email, message.reply_to.name)
            
            # CC/BCC
            for cc in message.cc:
                mail.add_cc(Email(cc.email, cc.name))
            for bcc in message.bcc:
                mail.add_bcc(Email(bcc.email, bcc.name))
            
            # Attachments
            for att in message.attachments:
                attachment = Attachment()
                attachment.file_content = FileContent(base64.b64encode(att.content).decode())
                attachment.file_name = FileName(att.filename)
                attachment.file_type = FileType(att.content_type)
                attachment.disposition = Disposition('attachment')
                if att.content_id:
                    attachment.content_id = att.content_id
                    attachment.disposition = Disposition('inline')
                mail.add_attachment(attachment)
            
            # Custom headers
            for key, value in message.headers.items():
                mail.add_header({key: value})
            
            # Tags (categories in SendGrid)
            for tag in message.tags[:10]:  # SendGrid limit
                mail.add_category(tag)
            
            # Custom args (metadata)
            if message.metadata:
                mail.custom_args = message.metadata
            
            # Send
            response = self.client.send(mail)
            
            # Extract message ID from response headers
            provider_msg_id = response.headers.get('X-Message-Id', '')
            
            return EmailResult(
                success=response.status_code in (200, 201, 202),
                message_id=message.message_id,
                provider_message_id=provider_msg_id,
                status=EmailStatus.QUEUED if response.status_code == 202 else EmailStatus.SENT,
                provider=self.name,
                sent_at=datetime.now(timezone.utc),
            )
            
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}", exc_info=True)
            return EmailResult(
                success=False,
                message_id=message.message_id,
                error=str(e),
                status=EmailStatus.FAILED,
                provider=self.name,
            )
    
    async def send_bulk(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple emails via SendGrid."""
        results = []
        for message in messages:
            result = await self.send(message)
            results.append(result)
        return results


# =============================================================================
# AWS SES PROVIDER
# =============================================================================

class SESProvider(EmailProvider):
    """AWS SES email provider."""
    
    name = "ses"
    
    def __init__(
        self,
        region: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        self.access_key = access_key or os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = secret_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self._client = None
    
    def is_configured(self) -> bool:
        # Can use IAM role if no explicit keys
        return True
    
    @property
    def client(self):
        """Lazy-load boto3 SES client."""
        if self._client is None:
            try:
                import boto3
                kwargs = {'region_name': self.region}
                if self.access_key and self.secret_key:
                    kwargs['aws_access_key_id'] = self.access_key
                    kwargs['aws_secret_access_key'] = self.secret_key
                self._client = boto3.client('ses', **kwargs)
            except ImportError:
                raise ImportError("boto3 package not installed. Run: pip install boto3")
        return self._client
    
    async def send(self, message: EmailMessage) -> EmailResult:
        """Send email via AWS SES."""
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Build MIME message for attachments support
            msg = MIMEMultipart('mixed')
            
            # From
            from_email = message.from_email or EmailAddress(
                email=os.getenv('EMAIL_FROM_ADDRESS', 'noreply@example.com'),
                name=os.getenv('EMAIL_FROM_NAME', 'OakQuant'),
            )
            msg['From'] = str(from_email)
            msg['To'] = ', '.join(str(r) for r in message.to)
            msg['Subject'] = message.subject
            
            if message.cc:
                msg['Cc'] = ', '.join(str(r) for r in message.cc)
            if message.reply_to:
                msg['Reply-To'] = str(message.reply_to)
            
            # Body
            body = MIMEMultipart('alternative')
            if message.text:
                body.attach(MIMEText(message.text, 'plain', 'utf-8'))
            if message.html:
                body.attach(MIMEText(message.html, 'html', 'utf-8'))
            msg.attach(body)
            
            # Attachments
            for att in message.attachments:
                part = MIMEBase(*att.content_type.split('/'))
                part.set_payload(att.content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{att.filename}"'
                )
                msg.attach(part)
            
            # Send via SES
            destinations = [r.email for r in message.to]
            if message.cc:
                destinations.extend(r.email for r in message.cc)
            if message.bcc:
                destinations.extend(r.email for r in message.bcc)
            
            response = self.client.send_raw_email(
                Source=str(from_email),
                Destinations=destinations,
                RawMessage={'Data': msg.as_string()},
            )
            
            return EmailResult(
                success=True,
                message_id=message.message_id,
                provider_message_id=response.get('MessageId', ''),
                status=EmailStatus.SENT,
                provider=self.name,
                sent_at=datetime.now(timezone.utc),
            )
            
        except Exception as e:
            logger.error(f"SES send failed: {e}", exc_info=True)
            return EmailResult(
                success=False,
                message_id=message.message_id,
                error=str(e),
                status=EmailStatus.FAILED,
                provider=self.name,
            )
    
    async def send_bulk(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple emails via SES."""
        results = []
        for message in messages:
            result = await self.send(message)
            results.append(result)
        return results


# =============================================================================
# SMTP PROVIDER
# =============================================================================

class SMTPProvider(EmailProvider):
    """Generic SMTP email provider."""
    
    name = "smtp"
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        use_ssl: bool = False,
    ):
        self.host = host or os.getenv('SMTP_HOST', 'localhost')
        self.port = port or int(os.getenv('SMTP_PORT', '587'))
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
        self.use_tls = use_tls
        self.use_ssl = use_ssl
    
    def is_configured(self) -> bool:
        return bool(self.host)
    
    async def send(self, message: EmailMessage) -> EmailResult:
        """Send email via SMTP."""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Build MIME message
            msg = MIMEMultipart('mixed')
            
            # From
            from_email = message.from_email or EmailAddress(
                email=os.getenv('EMAIL_FROM_ADDRESS', 'noreply@example.com'),
                name=os.getenv('EMAIL_FROM_NAME', 'OakQuant'),
            )
            msg['From'] = str(from_email)
            msg['To'] = ', '.join(str(r) for r in message.to)
            msg['Subject'] = message.subject
            msg['Message-ID'] = f"<{message.message_id}@oakquant.com>"
            
            if message.cc:
                msg['Cc'] = ', '.join(str(r) for r in message.cc)
            if message.reply_to:
                msg['Reply-To'] = str(message.reply_to)
            
            # Custom headers
            for key, value in message.headers.items():
                msg[key] = value
            
            # Body
            body = MIMEMultipart('alternative')
            if message.text:
                body.attach(MIMEText(message.text, 'plain', 'utf-8'))
            if message.html:
                body.attach(MIMEText(message.html, 'html', 'utf-8'))
            msg.attach(body)
            
            # Attachments
            for att in message.attachments:
                part = MIMEBase(*att.content_type.split('/'))
                part.set_payload(att.content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{att.filename}"'
                )
                if att.content_id:
                    part.add_header('Content-ID', f'<{att.content_id}>')
                msg.attach(part)
            
            # Connect and send
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port)
            else:
                server = smtplib.SMTP(self.host, self.port)
                if self.use_tls:
                    server.starttls()
            
            if self.username and self.password:
                server.login(self.username, self.password)
            
            # Get all recipients
            recipients = [r.email for r in message.to]
            recipients.extend(r.email for r in message.cc)
            recipients.extend(r.email for r in message.bcc)
            
            server.sendmail(from_email.email, recipients, msg.as_string())
            server.quit()
            
            return EmailResult(
                success=True,
                message_id=message.message_id,
                provider_message_id=message.message_id,
                status=EmailStatus.SENT,
                provider=self.name,
                sent_at=datetime.now(timezone.utc),
            )
            
        except Exception as e:
            logger.error(f"SMTP send failed: {e}", exc_info=True)
            return EmailResult(
                success=False,
                message_id=message.message_id,
                error=str(e),
                status=EmailStatus.FAILED,
                provider=self.name,
            )
    
    async def send_bulk(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Send multiple emails via SMTP."""
        results = []
        for message in messages:
            result = await self.send(message)
            results.append(result)
        return results


# =============================================================================
# CONSOLE PROVIDER (Development/Testing)
# =============================================================================

class ConsoleProvider(EmailProvider):
    """Console email provider for development - prints emails instead of sending."""
    
    name = "console"
    
    def is_configured(self) -> bool:
        return True
    
    async def send(self, message: EmailMessage) -> EmailResult:
        """Print email to console."""
        print("\n" + "=" * 60)
        print("📧 EMAIL (Console Provider)")
        print("=" * 60)
        print(f"To: {', '.join(str(r) for r in message.to)}")
        if message.cc:
            print(f"Cc: {', '.join(str(r) for r in message.cc)}")
        if message.from_email:
            print(f"From: {message.from_email}")
        print(f"Subject: {message.subject}")
        print("-" * 60)
        if message.text:
            print("TEXT:")
            print(message.text[:500])
            if len(message.text) > 500:
                print("... (truncated)")
        if message.html:
            print("\nHTML:")
            print(message.html[:500])
            if len(message.html) > 500:
                print("... (truncated)")
        print("=" * 60 + "\n")
        
        return EmailResult(
            success=True,
            message_id=message.message_id,
            provider_message_id=f"console-{message.message_id}",
            status=EmailStatus.SENT,
            provider=self.name,
            sent_at=datetime.now(timezone.utc),
        )
    
    async def send_bulk(self, messages: List[EmailMessage]) -> List[EmailResult]:
        """Print multiple emails to console."""
        results = []
        for message in messages:
            result = await self.send(message)
            results.append(result)
        return results


# =============================================================================
# EMAIL SERVICE
# =============================================================================

class EmailService:
    """
    Main email service with provider abstraction.
    
    Supports multiple providers with automatic fallback.
    """
    
    # Provider registry
    PROVIDERS = {
        'sendgrid': SendGridProvider,
        'ses': SESProvider,
        'smtp': SMTPProvider,
        'console': ConsoleProvider,
    }
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize email service.
        
        Args:
            provider: Provider name ('sendgrid', 'ses', 'smtp', 'console')
                     If not specified, auto-detects from environment.
        """
        self._provider_name = provider or os.getenv('EMAIL_PROVIDER', 'console')
        self._provider: Optional[EmailProvider] = None
        self._db = None
        
        logger.info(f"📧 EmailService initialized with provider: {self._provider_name}")
    
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
    def provider(self) -> EmailProvider:
        """Get the configured email provider."""
        if self._provider is None:
            provider_class = self.PROVIDERS.get(self._provider_name)
            if not provider_class:
                logger.warning(f"Unknown provider '{self._provider_name}', falling back to console")
                provider_class = ConsoleProvider
            self._provider = provider_class()
        return self._provider
    
    def set_provider(self, provider: Union[str, EmailProvider]) -> None:
        """Change the email provider."""
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
        to: Union[str, List[str], EmailAddress, List[EmailAddress]],
        subject: str,
        html: Optional[str] = None,
        text: Optional[str] = None,
        from_email: Optional[Union[str, EmailAddress]] = None,
        reply_to: Optional[Union[str, EmailAddress]] = None,
        cc: Optional[List[Union[str, EmailAddress]]] = None,
        bcc: Optional[List[Union[str, EmailAddress]]] = None,
        attachments: Optional[List[EmailAttachment]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmailResult:
        """
        Send a single email.
        
        Args:
            to: Recipient(s)
            subject: Email subject
            html: HTML body
            text: Plain text body
            from_email: Sender address
            reply_to: Reply-to address
            cc: CC recipients
            bcc: BCC recipients
            attachments: File attachments
            tags: Tags for tracking
            metadata: Custom metadata
            
        Returns:
            EmailResult with delivery status
        """
        # Normalize recipients
        if isinstance(to, (str, EmailAddress)):
            to = [to]
        recipients = [EmailAddress.parse(r) for r in to]
        
        # Build message
        message = EmailMessage(
            to=recipients,
            subject=subject,
            html=html,
            text=text,
            from_email=EmailAddress.parse(from_email) if from_email else None,
            reply_to=EmailAddress.parse(reply_to) if reply_to else None,
            cc=[EmailAddress.parse(r) for r in (cc or [])],
            bcc=[EmailAddress.parse(r) for r in (bcc or [])],
            attachments=attachments or [],
            tags=tags or [],
            metadata=metadata or {},
        )
        
        # Send via provider
        result = await self.provider.send(message)
        
        # Log to database
        await self._log_email(message, result)
        
        return result
    
    async def send_template(
        self,
        to: Union[str, List[str], EmailAddress, List[EmailAddress]],
        template_code: str,
        variables: Dict[str, Any],
        from_email: Optional[Union[str, EmailAddress]] = None,
        reply_to: Optional[Union[str, EmailAddress]] = None,
        cc: Optional[List[Union[str, EmailAddress]]] = None,
        bcc: Optional[List[Union[str, EmailAddress]]] = None,
        attachments: Optional[List[EmailAttachment]] = None,
    ) -> EmailResult:
        """
        Send email using a template.
        
        Args:
            to: Recipient(s)
            template_code: MessageTemplate code
            variables: Template variables for rendering
            from_email: Sender address
            reply_to: Reply-to address
            cc: CC recipients
            bcc: BCC recipients
            attachments: File attachments
            
        Returns:
            EmailResult with delivery status
        """
        # Load template
        template = await self._get_template(template_code)
        if not template:
            return EmailResult(
                success=False,
                message_id=str(uuid.uuid4()),
                error=f"Template not found: {template_code}",
                status=EmailStatus.FAILED,
            )
        
        # Render template
        subject = self._render_string(template.get('email_subject', ''), variables)
        html = self._render_string(template.get('email_body_html', ''), variables)
        text = self._render_string(template.get('email_body_text', ''), variables)
        
        return await self.send(
            to=to,
            subject=subject,
            html=html,
            text=text or None,
            from_email=from_email,
            reply_to=reply_to,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            tags=[template_code],
            metadata={'template_code': template_code},
        )
    
    async def send_bulk(
        self,
        recipients: List[Dict[str, Any]],
        template_code: Optional[str] = None,
        subject: Optional[str] = None,
        html: Optional[str] = None,
        text: Optional[str] = None,
        from_email: Optional[Union[str, EmailAddress]] = None,
    ) -> List[EmailResult]:
        """
        Send bulk emails.
        
        Args:
            recipients: List of dicts with 'to' and optional 'variables'
            template_code: Template to use (if not providing subject/html/text)
            subject: Subject (can include {variables})
            html: HTML body (can include {variables})
            text: Text body (can include {variables})
            from_email: Sender address
            
        Returns:
            List of EmailResult
        """
        # Load template if specified
        template = None
        if template_code:
            template = await self._get_template(template_code)
        
        messages = []
        for recipient in recipients:
            to = recipient.get('to')
            variables = recipient.get('variables', {})
            
            if template:
                msg_subject = self._render_string(template.get('email_subject', ''), variables)
                msg_html = self._render_string(template.get('email_body_html', ''), variables)
                msg_text = self._render_string(template.get('email_body_text', ''), variables)
            else:
                msg_subject = self._render_string(subject or '', variables)
                msg_html = self._render_string(html or '', variables)
                msg_text = self._render_string(text or '', variables) if text else None
            
            messages.append(EmailMessage(
                to=[EmailAddress.parse(to)],
                subject=msg_subject,
                html=msg_html,
                text=msg_text,
                from_email=EmailAddress.parse(from_email) if from_email else None,
                tags=[template_code] if template_code else [],
                metadata={'bulk': True, 'template_code': template_code},
            ))
        
        # Send via provider
        results = await self.provider.send_bulk(messages)
        
        # Log results
        for message, result in zip(messages, results):
            await self._log_email(message, result)
        
        return results
    
    async def _get_template(self, template_code: str) -> Optional[Dict[str, Any]]:
        """Get email template by code."""
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
    
    async def _log_email(self, message: EmailMessage, result: EmailResult) -> None:
        """Log email to database."""
        if not self.db:
            return
        
        try:
            self.db.create('MessageDeliveryLog', {
                'id': str(uuid.uuid4()),
                'message_id': message.message_id,
                'channel': 'email',
                'status': 'success' if result.success else 'failed',
                'provider': result.provider,
                'provider_response': {
                    'provider_message_id': result.provider_message_id,
                    'status': result.status.value,
                },
                'error_message': result.error,
                'attempted_at': datetime.now(timezone.utc),
                'delivered_at': result.sent_at,
            })
        except Exception as e:
            logger.debug(f"Failed to log email: {e}")
    
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

_service_instance: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get the singleton EmailService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = EmailService()
    return _service_instance


# Module-level singleton for convenience
email_service = get_email_service()
