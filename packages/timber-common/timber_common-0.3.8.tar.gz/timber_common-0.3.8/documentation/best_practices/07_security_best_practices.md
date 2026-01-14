# Security Best Practices

**Comprehensive security guidelines for Timber applications**

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Authorization](#authorization)
4. [Data Protection](#data-protection)
5. [API Security](#api-security)
6. [Audit Logging](#audit-logging)
7. [Vulnerability Management](#vulnerability-management)

## Overview

Security is paramount in financial applications. This guide covers best practices for securing Timber-based applications.

### Security Principles
- **Defense in Depth**: Multiple layers of security
- **Least Privilege**: Minimal necessary permissions
- **Zero Trust**: Never trust, always verify
- **Fail Secure**: Default to secure state
- **Security by Design**: Built-in from the start

## Authentication

### 1. Strong Password Requirements

```python
import re
from passlib.hash import bcrypt

def validate_password(password):
    """Validate password strength."""
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain number"
    
    if not re.search(r'[!@#$%^&*]', password):
        return False, "Password must contain special character"
    
    return True, None

def hash_password(password):
    """Securely hash password."""
    return bcrypt.hash(password)

def verify_password(password, hashed):
    """Verify password against hash."""
    return bcrypt.verify(password, hashed)
```

### 2. Multi-Factor Authentication

```python
import pyotp

class MFAService:
    """Multi-factor authentication service."""
    
    @staticmethod
    def generate_secret():
        """Generate MFA secret."""
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(secret, email):
        """Get TOTP provisioning URI."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(email, issuer_name="Timber")
    
    @staticmethod
    def verify_totp(secret, token):
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
```

### 3. Session Management

```python
from datetime import datetime, timedelta
import secrets

class SessionManager:
    """Secure session management."""
    
    def create_session(self, user_id):
        """Create secure session."""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        session = Session(
            id=session_id,
            user_id=user_id,
            expires_at=expires_at,
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session_id
    
    def validate_session(self, session_id):
        """Validate and renew session."""
        session = Session.query.get(session_id)
        
        if not session:
            return None
        
        if datetime.utcnow() > session.expires_at:
            db.session.delete(session)
            db.session.commit()
            return None
        
        # Extend session
        session.expires_at = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        
        return session
```

## Authorization

### 1. Role-Based Access Control (RBAC)

```python
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"

class Permission(Enum):
    READ_RESEARCH = "read_research"
    WRITE_RESEARCH = "write_research"
    DELETE_RESEARCH = "delete_research"
    MANAGE_USERS = "manage_users"

ROLE_PERMISSIONS = {
    Role.ADMIN: [Permission.READ_RESEARCH, Permission.WRITE_RESEARCH, 
                 Permission.DELETE_RESEARCH, Permission.MANAGE_USERS],
    Role.ANALYST: [Permission.READ_RESEARCH, Permission.WRITE_RESEARCH],
    Role.USER: [Permission.READ_RESEARCH]
}

def has_permission(user, permission):
    """Check if user has permission."""
    return permission in ROLE_PERMISSIONS.get(user.role, [])

def require_permission(permission):
    """Decorator to require permission."""
    def decorator(func):
        def wrapper(user, *args, **kwargs):
            if not has_permission(user, permission):
                raise PermissionError(f"Permission denied: {permission.value}")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_permission(Permission.DELETE_RESEARCH)
def delete_research(user, research_id):
    # Only users with DELETE_RESEARCH permission can call this
    pass
```

### 2. Resource-Level Authorization

```python
def can_access_research(user, research):
    """Check if user can access research."""
    # Owner can always access
    if research.user_id == user.id:
        return True
    
    # Admins can access everything
    if user.role == Role.ADMIN:
        return True
    
    # Shared research
    if research.shared_with and user.id in research.shared_with:
        return True
    
    return False
```

## Data Protection

### 1. Field-Level Encryption

```python
from timber.common.services.encryption import encryption_service

# Encrypt sensitive data
encrypted_ssn = encryption_service.encrypt(user.ssn)

# Store only encrypted value
user.ssn_encrypted = encrypted_ssn
user.ssn = None  # Don't store plaintext!
```

### 2. PII Protection

```python
import re

def redact_pii(text):
    """Redact PII from text."""
    # Redact SSN
    text = re.sub(r'\d{3}-\d{2}-\d{4}', 'XXX-XX-XXXX', text)
    
    # Redact credit card
    text = re.sub(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}', 
                 'XXXX-XXXX-XXXX-XXXX', text)
    
    # Redact email
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL]', text)
    
    return text
```

### 3. Data Sanitization

```python
import bleach

def sanitize_input(text):
    """Sanitize user input."""
    # Remove HTML tags
    text = bleach.clean(text, tags=[], strip=True)
    
    # Remove SQL injection attempts
    dangerous_patterns = ['--', ';', 'DROP', 'DELETE', 'UPDATE']
    for pattern in dangerous_patterns:
        if pattern.lower() in text.lower():
            raise ValueError("Invalid input detected")
    
    return text.strip()
```

## API Security

### 1. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["1000 per hour", "100 per minute"]
)

@app.route('/api/research')
@limiter.limit("10 per minute")
def get_research():
    # Rate limited endpoint
    pass
```

### 2. API Key Management

```python
import secrets

def generate_api_key():
    """Generate secure API key."""
    return f"sk_{secrets.token_urlsafe(32)}"

def validate_api_key(api_key):
    """Validate API key."""
    key = APIKey.query.filter_by(key=api_key, active=True).first()
    
    if not key:
        return None
    
    if key.expires_at and datetime.utcnow() > key.expires_at:
        return None
    
    # Update last used
    key.last_used_at = datetime.utcnow()
    db.session.commit()
    
    return key
```

### 3. CORS Configuration

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["X-Total-Count"],
        "max_age": 3600
    }
})
```

## Audit Logging

### 1. Security Event Logging

```python
class SecurityLogger:
    """Log security events."""
    
    @staticmethod
    def log_login(user_id, success, ip_address):
        """Log login attempt."""
        event = SecurityEvent(
            event_type='login',
            user_id=user_id,
            success=success,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.session.add(event)
        db.session.commit()
    
    @staticmethod
    def log_data_access(user_id, resource_type, resource_id):
        """Log data access."""
        event = SecurityEvent(
            event_type='data_access',
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(event)
        db.session.commit()
```

### 2. Anomaly Detection

```python
class AnomalyDetector:
    """Detect suspicious activity."""
    
    def detect_suspicious_login(self, user_id, ip_address):
        """Detect suspicious login."""
        # Get recent logins
        recent = SecurityEvent.query.filter_by(
            user_id=user_id,
            event_type='login'
        ).order_by(SecurityEvent.timestamp.desc()).limit(10).all()
        
        # Check for unusual IP
        known_ips = {event.ip_address for event in recent}
        if ip_address not in known_ips and len(known_ips) > 0:
            self.alert(f"Login from new IP: {ip_address} for user {user_id}")
        
        # Check for rapid attempts
        last_hour = [e for e in recent 
                    if (datetime.utcnow() - e.timestamp).seconds < 3600]
        if len(last_hour) > 10:
            self.alert(f"Excessive login attempts for user {user_id}")
```

## Vulnerability Management

### 1. Dependency Scanning

```bash
# Check for known vulnerabilities
pip install safety
safety check

# Keep dependencies updated
pip install pip-audit
pip-audit
```

### 2. Security Headers

```python
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

## Summary

### Security Checklist
- [ ] Strong authentication implemented
- [ ] MFA enabled for sensitive operations
- [ ] Role-based access control (RBAC)
- [ ] Field-level encryption for PII
- [ ] API rate limiting configured
- [ ] Security event logging enabled
- [ ] Regular dependency updates
- [ ] Security headers configured
- [ ] Input validation and sanitization
- [ ] Regular security audits scheduled

---
**Last Updated**: October 19, 2024  
**Version**: 0.2.0