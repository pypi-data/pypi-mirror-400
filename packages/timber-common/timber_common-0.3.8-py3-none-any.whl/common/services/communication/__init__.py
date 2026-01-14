# common/services/communication/__init__.py
"""
Communication Services

Multi-channel messaging and notification delivery services.

Services:
- MessagingService: Multi-channel message delivery (in-app, email, push, sms)
- EmailService: Direct email sending with provider abstraction
- SMSService: Direct SMS sending with provider abstraction

Usage:
    # Messaging service (high-level, template-based)
    from common.services.communication import messaging_service
    
    await messaging_service.send_message(
        user_id="user-123",
        template_code="welcome_email",
        variables={'name': 'John'},
    )
    
    # Email service (low-level, direct sending)
    from common.services.communication import email_service
    
    await email_service.send(
        to="user@example.com",
        subject="Hello",
        html="<h1>Welcome!</h1>",
    )
    
    # SMS service (low-level, direct sending)
    from common.services.communication import sms_service
    
    await sms_service.send(
        to="+1234567890",
        body="Your verification code is 123456",
    )
    
    # Using factory functions
    from common.services.communication import (
        get_messaging_service,
        get_email_service,
        get_sms_service,
    )
"""

# Messaging Service (multi-channel delivery)
from .messaging_service import (
    MessagingService,
    get_messaging_service,
    messaging_service,
)

# Email Service (direct email sending)
from .email_service import (
    EmailService,
    EmailProvider,
    EmailMessage,
    EmailResult,
    EmailAddress,
    EmailAttachment,
    EmailStatus,
    SendGridProvider,
    SESProvider,
    SMTPProvider,
    ConsoleProvider,
    get_email_service,
    email_service,
)

# SMS Service (direct SMS sending)
from .sms_service import (
    SMSService,
    SMSProvider,
    SMSMessage,
    SMSResult,
    SMSStatus,
    SMSType,
    PhoneNumber,
    TwilioProvider,
    SNSProvider as SMSSNSProvider,  # Renamed to avoid confusion with email SES
    VonageProvider,
    ConsoleSMSProvider,
    get_sms_service,
    sms_service,
)

__all__ = [
    # Messaging Service
    'MessagingService',
    'get_messaging_service',
    'messaging_service',
    
    # Email Service
    'EmailService',
    'EmailProvider',
    'EmailMessage',
    'EmailResult',
    'EmailAddress',
    'EmailAttachment',
    'EmailStatus',
    'SendGridProvider',
    'SESProvider',
    'SMTPProvider',
    'ConsoleProvider',
    'get_email_service',
    'email_service',
    
    # SMS Service
    'SMSService',
    'SMSProvider',
    'SMSMessage',
    'SMSResult',
    'SMSStatus',
    'SMSType',
    'PhoneNumber',
    'TwilioProvider',
    'SMSSNSProvider',
    'VonageProvider',
    'ConsoleSMSProvider',
    'get_sms_service',
    'sms_service',
]