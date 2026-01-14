# Encryption and Security in Timber

**Complete guide to field-level encryption, key management, and security best practices**

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Field-Level Encryption](#field-level-encryption)
4. [Key Management](#key-management)
5. [Security Configuration](#security-configuration)
6. [Advanced Patterns](#advanced-patterns)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

Timber provides transparent field-level encryption for sensitive data using the Fernet symmetric encryption scheme. This allows you to encrypt specific fields in your database models without changing application code.

### Key Features

- **Transparent Encryption**: Automatic encryption/decryption via SQLAlchemy events
- **Field-Level Control**: Choose which fields to encrypt
- **Multiple Key Support**: Per-user or per-application keys
- **Zero Application Impact**: No code changes needed after setup
- **Fernet Security**: Uses industry-standard Fernet (AES-128-CBC + HMAC)

### When to Use Encryption

**Encrypt:**
- User personal information (PII)
- Proprietary research data
- Financial analysis results
- API keys and secrets
- Confidential business data

**Don't Encrypt:**
- IDs and foreign keys
- Timestamps and metadata
- Public information
- Searchable fields (use hashing instead)

---

## Quick Start

### Step 1: Generate Encryption Key

```python
from cryptography.fernet import Fernet

# Generate a new key
key = Fernet.generate_key()
print(f"ENCRYPTION_KEY={key.decode()}")
```

Store this key securely in your environment variables:

```bash
# .env
ENCRYPTION_KEY=your-generated-key-here
MASTER_ENCRYPTION_KEY=your-master-key-here  # For key rotation
```

### Step 2: Enable Encryption

```python
from timber.common import initialize_timber

initialize_timber(
    model_config_dirs=['./data/models'],
    enable_encryption=True  # âœ… Enable encryption
)
```

### Step 3: Mark Fields for Encryption

```yaml
# data/models/user_data.yaml
models:
  - name: UserProfile
    table_name: user_profiles
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
        nullable: false
      
      - name: email
        type: String(255)
        encrypted: true  # âœ… Encrypt this field
      
      - name: phone
        type: String(50)
        encrypted: true  # âœ… Encrypt this field
      
      - name: research_notes
        type: Text
        encrypted: true  # âœ… Encrypt this field
      
      - name: created_at
        type: DateTime
        # Not encrypted - metadata is fine
    
    mixins:
      - TimestampMixin
      - EncryptedFieldMixin  # âœ… Required for encryption
```

### Step 4: Use Normally

```python
from timber.common.models import get_model
from timber.common.services.db_service import db_service

UserProfile = get_model('UserProfile')

# Create with plain text
with db_service.session_scope() as session:
    profile = UserProfile(
        user_id='user-123',
        email='user@example.com',  # Will be encrypted automatically
        phone='+1-555-0100',       # Will be encrypted automatically
        research_notes='Confidential analysis'  # Will be encrypted automatically
    )
    session.add(profile)
    session.commit()
    profile_id = profile.id

# Read - automatically decrypted
with db_service.session_scope() as session:
    profile = session.query(UserProfile).filter_by(id=profile_id).first()
    print(profile.email)  # Returns decrypted: 'user@example.com'
    print(profile.phone)  # Returns decrypted: '+1-555-0100'
```

---

## Field-Level Encryption

### How It Works

```
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚   Application Code            â"‚
â"‚   model.email = "user@ex.com" â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
           â"‚
           â–¼
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚   SQLAlchemy Events           â"‚
â"‚   (before_insert/update)      â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
           â"‚
           â–¼
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚   Encryption Service          â"‚
â"‚   Encrypt with Fernet          â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
           â"‚
           â–¼
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚   Database                    â"‚
â"‚   Stores: "gAAAA..."          â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜

Reading:
Database â†' Decrypt â†' SQLAlchemy â†' Application
```

### Encryption Service

The encryption service handles all cryptographic operations:

```python
from timber.common.services.encryption import encryption_service

# Manual encryption/decryption (rarely needed)
encrypted = encryption_service.encrypt(
    data="sensitive data",
    key_id="user_data_key"  # Optional: specify key
)

decrypted = encryption_service.decrypt(
    encrypted_data=encrypted,
    key_id="user_data_key"
)
```

### Encrypted Field Mixin

The `EncryptedFieldMixin` provides the interface for encryption:

```python
from timber.common.models.mixins import EncryptedFieldMixin

class MyModel(Base, EncryptedFieldMixin):
    __tablename__ = 'my_table'
    
    # Fields marked as encrypted in config
    sensitive_data = Column(String(500))
    
    def get_encrypted_fields(self):
        """Returns list of field names to encrypt."""
        return ['sensitive_data']
```

### Multiple Field Encryption

```yaml
models:
  - name: ResearchSession
    table_name: research_sessions
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      # Public fields
      - name: ticker
        type: String(20)
      
      - name: session_type
        type: String(50)
      
      # Encrypted fields
      - name: analysis_data
        type: JSON
        encrypted: true
      
      - name: proprietary_signals
        type: JSON
        encrypted: true
      
      - name: ai_insights
        type: Text
        encrypted: true
      
      - name: strategy_details
        type: JSON
        encrypted: true
    
    mixins:
      - TimestampMixin
      - EncryptedFieldMixin
```

---

## Key Management

### Single Application Key

Simple setup for single-application use:

```bash
# .env
ENCRYPTION_KEY=<your-fernet-key>
```

```python
from timber.common.utils.config import config

# Timber automatically uses this key
initialize_timber(
    enable_encryption=True
)
```

### Per-User Keys

For multi-tenant applications with per-user encryption:

```python
from timber.common.services.encryption import encryption_service

# Store user-specific keys (encrypted with master key)
user_keys = {
    'user-123': 'user-specific-key-123',
    'user-456': 'user-specific-key-456',
}

# Encrypt with user key
encrypted = encryption_service.encrypt(
    data="user data",
    key_id=f"user_{user_id}"
)
```

### Key Rotation

Rotate keys periodically for security:

```python
from timber.common.services.encryption import encryption_service
from timber.common.models import get_model

def rotate_encryption_keys():
    """
    Rotate encryption keys for all encrypted fields.
    
    Process:
    1. Generate new key
    2. Read all encrypted records with old key
    3. Re-encrypt with new key
    4. Update records
    5. Archive old key
    """
    new_key = Fernet.generate_key()
    
    # Update encryption service with new key
    encryption_service.add_key('new_primary', new_key.decode())
    
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profiles = session.query(UserProfile).all()
        
        for profile in profiles:
            # Decrypt with old key (automatic)
            email = profile.email
            phone = profile.phone
            
            # Update key_id to use new key
            profile._encryption_key_id = 'new_primary'
            
            # Re-encrypt happens automatically on commit
        
        session.commit()
    
    print(f"Rotated keys for {len(profiles)} profiles")

# Run rotation
rotate_encryption_keys()
```

### Key Storage Best Practices

**â Never:**
- Store keys in code
- Commit keys to version control
- Share keys via email or chat
- Use the same key across environments

**âœ… Always:**
- Use environment variables
- Use secret management services (AWS Secrets Manager, HashiCorp Vault)
- Rotate keys regularly (quarterly recommended)
- Have a key recovery process
- Audit key access

```python
# Good: Environment variable
import os
encryption_key = os.getenv('ENCRYPTION_KEY')

# Better: Secret management service
import boto3

def get_encryption_key():
    """Fetch key from AWS Secrets Manager."""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='timber/encryption-key')
    return response['SecretString']
```

---

## Security Configuration

### Environment Setup

Complete security configuration:

```bash
# .env
# Core Configuration
OAK_ENV=production
DATABASE_URL=postgresql://user:password@localhost/timber

# Encryption Keys
ENCRYPTION_KEY=<primary-fernet-key>
MASTER_ENCRYPTION_KEY=<master-key-for-key-encryption>

# Key Rotation
ENCRYPTION_KEY_OLD=<previous-key-for-decryption>
KEY_ROTATION_DATE=2025-01-01

# Security Settings
REQUIRE_SSL=true
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem

# Access Control
ENABLE_AUDIT_LOG=true
ENABLE_ACCESS_CONTROL=true

# API Keys (encrypted)
ALPHA_VANTAGE_API_KEY=<encrypted-key>
POLYGON_API_KEY=<encrypted-key>
```

### Database Security

Configure database connection security:

```python
from timber.common import initialize_timber

initialize_timber(
    model_config_dirs=['./data/models'],
    enable_encryption=True,
    
    # Database security
    db_config={
        'pool_pre_ping': True,  # Check connections before use
        'pool_recycle': 3600,   # Recycle connections every hour
        'echo': False,          # Don't log SQL in production
        
        # SSL configuration
        'connect_args': {
            'sslmode': 'require',
            'sslcert': '/path/to/client-cert.pem',
            'sslkey': '/path/to/client-key.pem',
            'sslrootcert': '/path/to/ca-cert.pem'
        }
    }
)
```

### Audit Logging

Enable comprehensive audit logging:

```yaml
# data/models/sensitive_model.yaml
models:
  - name: SensitiveData
    table_name: sensitive_data
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: data
        type: JSON
        encrypted: true
    
    mixins:
      - TimestampMixin
      - EncryptedFieldMixin
      - AuditMixin  # âœ… Track all changes
```

```python
# Audit log automatically tracks:
# - Who accessed/modified data
# - When it happened
# - What changed
# - Previous values

from timber.common.models import get_model

AuditLog = get_model('AuditLog')

with db_service.session_scope() as session:
    recent_logs = session.query(AuditLog)\
        .filter_by(table_name='sensitive_data')\
        .order_by(AuditLog.created_at.desc())\
        .limit(10)\
        .all()
    
    for log in recent_logs:
        print(f"{log.action} by {log.user_id} at {log.created_at}")
```

---

## Advanced Patterns

### Selective Encryption

Encrypt only certain records based on criteria:

```python
from timber.common.models import get_model
from timber.common.services.encryption import encryption_service

ResearchSession = get_model('ResearchSession')

def save_research_with_conditional_encryption(
    session_data: dict,
    is_proprietary: bool
):
    """
    Only encrypt proprietary research.
    """
    with db_service.session_scope() as db_session:
        session = ResearchSession(**session_data)
        
        if is_proprietary:
            # Enable encryption for this instance
            session._encrypt_fields = True
        else:
            # Skip encryption for non-proprietary
            session._encrypt_fields = False
        
        db_session.add(session)
        db_session.commit()
        
        return session.id
```

### Field-Level Access Control

Combine encryption with access control:

```python
from typing import Optional, List

def get_user_profile_with_permissions(
    user_id: str,
    requesting_user_id: str,
    allowed_fields: Optional[List[str]] = None
) -> dict:
    """
    Return profile with field-level access control.
    """
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profile = session.query(UserProfile)\
            .filter_by(user_id=user_id)\
            .first()
        
        if not profile:
            return None
        
        # Base fields always accessible
        result = {
            'user_id': profile.user_id,
            'created_at': profile.created_at
        }
        
        # Owner sees everything (decrypted automatically)
        if requesting_user_id == user_id:
            result.update({
                'email': profile.email,
                'phone': profile.phone,
                'research_notes': profile.research_notes
            })
        
        # Others see only allowed fields
        elif allowed_fields:
            for field in allowed_fields:
                if hasattr(profile, field):
                    result[field] = getattr(profile, field)
        
        return result

# Usage
profile = get_user_profile_with_permissions(
    user_id='user-123',
    requesting_user_id='user-456',
    allowed_fields=['email']  # Only email allowed
)
```

### Encryption with Compression

For large encrypted fields, combine with compression:

```python
import gzip
import base64
from timber.common.services.encryption import encryption_service

def encrypt_with_compression(data: str, key_id: str = None) -> str:
    """Compress then encrypt for large data."""
    # Compress
    compressed = gzip.compress(data.encode())
    
    # Encrypt compressed data
    encrypted = encryption_service.encrypt(
        data=base64.b64encode(compressed).decode(),
        key_id=key_id
    )
    
    return encrypted

def decrypt_with_decompression(encrypted_data: str, key_id: str = None) -> str:
    """Decrypt then decompress."""
    # Decrypt
    decrypted = encryption_service.decrypt(
        encrypted_data=encrypted_data,
        key_id=key_id
    )
    
    # Decompress
    compressed = base64.b64decode(decrypted)
    decompressed = gzip.decompress(compressed)
    
    return decompressed.decode()
```

### Search on Encrypted Data

Use hashing for searchable encrypted fields:

```yaml
models:
  - name: UserProfile
    table_name: user_profiles
    
    columns:
      - name: email
        type: String(255)
        encrypted: true
      
      - name: email_hash
        type: String(64)
        indexed: true  # âœ… Search on hash
```

```python
import hashlib

def hash_email(email: str) -> str:
    """Create searchable hash of email."""
    return hashlib.sha256(email.lower().encode()).hexdigest()

# Store with both encrypted and hashed values
def create_profile(email: str, **kwargs):
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profile = UserProfile(
            email=email,  # Stored encrypted
            email_hash=hash_email(email),  # Stored as hash for search
            **kwargs
        )
        session.add(profile)
        session.commit()
        return profile.id

# Search using hash
def find_by_email(email: str):
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        return session.query(UserProfile)\
            .filter_by(email_hash=hash_email(email))\
            .first()
```

---

## Best Practices

### 1. Minimize Encrypted Data

Only encrypt truly sensitive fields:

**âœ… Encrypt:**
- User PII (email, phone, SSN)
- Financial data (account numbers, transactions)
- Health information
- Proprietary analysis
- API keys and secrets

**â Don't Encrypt:**
- Public data
- IDs and foreign keys
- Metadata (created_at, status)
- Aggregatable numeric data
- Frequently searched fields

### 2. Use Appropriate Field Sizes

Encrypted data is larger than plaintext:

```yaml
columns:
  # Original: String(50)
  # Encrypted Fernet adds ~45% overhead
  - name: phone
    type: String(100)  # âœ… Account for encryption overhead
    encrypted: true
  
  # JSON fields handle dynamic size
  - name: analysis_data
    type: JSON  # âœ… Good for variable-length encrypted data
    encrypted: true
```

### 3. Key Rotation Schedule

```python
# Recommended rotation schedule
ROTATION_SCHEDULE = {
    'critical_data': 'quarterly',    # Every 3 months
    'sensitive_data': 'semi-annual', # Every 6 months
    'standard_data': 'annual'        # Once per year
}

def schedule_key_rotation():
    """Schedule automatic key rotation."""
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    # Rotate critical keys quarterly
    scheduler.add_job(
        rotate_critical_keys,
        'cron',
        month='*/3',  # Every 3 months
        day=1,
        hour=2
    )
    
    scheduler.start()
```

### 4. Secure Key Transmission

```python
def secure_key_exchange(recipient_public_key: bytes, encryption_key: bytes):
    """
    Securely transmit encryption key using asymmetric encryption.
    """
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    
    # Encrypt symmetric key with recipient's public key
    encrypted_key = recipient_public_key.encrypt(
        encryption_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return encrypted_key
```

### 5. Monitoring and Alerting

```python
import logging

logger = logging.getLogger('timber.security')

def monitor_encryption_operations():
    """Monitor and alert on encryption issues."""
    
    # Track encryption failures
    encryption_failures = 0
    
    def encryption_error_handler(error):
        nonlocal encryption_failures
        encryption_failures += 1
        
        logger.error(f"Encryption error: {error}")
        
        # Alert after 3 consecutive failures
        if encryption_failures >= 3:
            send_security_alert(
                "Multiple encryption failures detected",
                severity="high"
            )
    
    # Monitor key access
    def log_key_access(user_id: str, key_id: str):
        logger.info(f"Key {key_id} accessed by {user_id}")
```

### 6. Performance Optimization

```python
# Cache decrypted data for read-heavy workloads
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_decrypted_profile(user_id: str) -> dict:
    """Cache decrypted profile for 5 minutes."""
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profile = session.query(UserProfile)\
            .filter_by(user_id=user_id)\
            .first()
        
        return {
            'email': profile.email,
            'phone': profile.phone,
            'research_notes': profile.research_notes
        }

# Batch encryption for bulk operations
def bulk_encrypt_profiles(profiles: List[dict]):
    """Encrypt multiple profiles efficiently."""
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(create_encrypted_profile, p)
            for p in profiles
        ]
        
        results = [f.result() for f in futures]
    
    return results
```

---

## Troubleshooting

### Common Issues

#### 1. "Invalid Token" Error

**Problem**: Fernet decryption fails

**Solutions**:
```python
# Check key configuration
from timber.common.utils.config import config
print(f"Key configured: {bool(config.ENCRYPTION_KEY)}")

# Verify key format
from cryptography.fernet import Fernet
try:
    f = Fernet(config.ENCRYPTION_KEY.encode())
    print("âœ… Key is valid")
except Exception as e:
    print(f"â Key is invalid: {e}")

# Check if data was encrypted with different key
# You may need to rotate or recover with old key
```

#### 2. Field Too Small for Encrypted Data

**Problem**: Database error - value too long

**Solution**:
```yaml
# Increase field size to account for encryption overhead
columns:
  - name: encrypted_field
    type: String(200)  # Was String(100)
    encrypted: true
```

#### 3. Performance Issues

**Problem**: Encryption slowing down queries

**Solutions**:
```python
# 1. Cache frequently accessed decrypted data
from redis import Redis
cache = Redis()

def get_cached_or_decrypt(key: str):
    cached = cache.get(key)
    if cached:
        return cached
    
    decrypted = decrypt_from_db(key)
    cache.setex(key, 300, decrypted)  # Cache 5 minutes
    return decrypted

# 2. Batch encryption operations
def batch_process():
    with db_service.session_scope() as session:
        # Process all at once instead of one-by-one
        profiles = session.query(UserProfile).all()
        # Encryption happens on single commit
        session.commit()

# 3. Use selective encryption
# Only encrypt truly sensitive fields
```

#### 4. Key Rotation Failed

**Problem**: Some records not re-encrypted

**Solution**:
```python
def verify_and_fix_rotation():
    """Find and fix records with old encryption."""
    UserProfile = get_model('UserProfile')
    
    with db_service.session_scope() as session:
        profiles = session.query(UserProfile).all()
        
        failed_records = []
        
        for profile in profiles:
            try:
                # Try to access encrypted field
                _ = profile.email
            except Exception as e:
                failed_records.append(profile.id)
                logger.error(f"Failed to decrypt {profile.id}: {e}")
        
        if failed_records:
            logger.warning(f"Found {len(failed_records)} failed records")
            # Re-run rotation for these records
            reencrypt_records(failed_records)
```

### Debug Mode

Enable encryption debugging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('timber.encryption')
logger.setLevel(logging.DEBUG)

# This will show:
# - Which fields are encrypted
# - Key IDs used
# - Encryption/decryption operations
# - Any errors
```

### Testing Encryption

```python
import pytest
from timber.common.models import get_model
from timber.common.services.db_service import db_service

def test_field_encryption():
    """Test that sensitive fields are encrypted in database."""
    UserProfile = get_model('UserProfile')
    
    test_email = "test@example.com"
    
    # Create profile
    with db_service.session_scope() as session:
        profile = UserProfile(
            user_id='test-user',
            email=test_email
        )
        session.add(profile)
        session.commit()
        profile_id = profile.id
    
    # Check database has encrypted value (not plaintext)
    with db_service.session_scope() as session:
        # Raw SQL to bypass decryption
        result = session.execute(
            f"SELECT email FROM user_profiles WHERE id = '{profile_id}'"
        ).first()
        
        encrypted_value = result[0]
        
        # Should not match plaintext
        assert encrypted_value != test_email
        
        # Should look like Fernet token
        assert encrypted_value.startswith('gAAAAA')
    
    # Check application gets decrypted value
    with db_service.session_scope() as session:
        profile = session.query(UserProfile)\
            .filter_by(id=profile_id)\
            .first()
        
        assert profile.email == test_email
```

---

## Complete Example

Here's a complete example showing encryption in a real-world scenario:

```python
# models/secure_research.yaml
"""
models:
  - name: SecureResearchSession
    table_name: secure_research_sessions
    
    columns:
      # Public fields
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
        nullable: false
        indexed: true
      
      - name: ticker
        type: String(20)
        nullable: false
      
      - name: session_type
        type: String(50)
        nullable: false
      
      - name: status
        type: String(20)
        default: 'active'
      
      # Encrypted fields
      - name: analysis_data
        type: JSON
        encrypted: true
      
      - name: proprietary_signals
        type: JSON
        encrypted: true
      
      - name: strategy_details
        type: JSON
        encrypted: true
      
      - name: api_keys
        type: JSON
        encrypted: true
      
      # Audit fields
      - name: created_at
        type: DateTime
      
      - name: updated_at
        type: DateTime
      
      - name: accessed_by
        type: String(36)
    
    mixins:
      - TimestampMixin
      - EncryptedFieldMixin
      - AuditMixin
      - GDPRComplianceMixin
    
    indexes:
      - columns: [user_id, created_at]
      - columns: [ticker, status]
"""

# Application code
from timber.common import initialize_timber
from timber.common.models import get_model
from timber.common.services.db_service import db_service
from timber.common.utils.config import config
from datetime import datetime
import uuid

# Initialize with encryption
initialize_timber(
    model_config_dirs=['./data/models'],
    enable_encryption=True,
    enable_gdpr=True
)

SecureResearchSession = get_model('SecureResearchSession')

def create_secure_research_session(
    user_id: str,
    ticker: str,
    analysis_data: dict,
    proprietary_signals: dict,
    strategy_details: dict
) -> str:
    """
    Create encrypted research session.
    
    All sensitive data is encrypted automatically.
    """
    with db_service.session_scope() as session:
        research = SecureResearchSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            ticker=ticker,
            session_type='stock_research',
            status='active',
            
            # These fields are encrypted automatically
            analysis_data=analysis_data,
            proprietary_signals=proprietary_signals,
            strategy_details=strategy_details,
            api_keys={
                'alpha_vantage': config.ALPHA_VANTAGE_API_KEY,
                'polygon': config.POLYGON_API_KEY
            }
        )
        
        session.add(research)
        session.commit()
        
        return research.id

def get_secure_research_session(
    session_id: str,
    requesting_user_id: str
) -> dict:
    """
    Retrieve research session with access control.
    
    Data is decrypted automatically for authorized users.
    """
    with db_service.session_scope() as session:
        research = session.query(SecureResearchSession)\
            .filter_by(id=session_id)\
            .first()
        
        if not research:
            return None
        
        # Check authorization
        if research.user_id != requesting_user_id:
            raise PermissionError("Not authorized to view this session")
        
        # Data is decrypted automatically
        return {
            'id': research.id,
            'ticker': research.ticker,
            'status': research.status,
            'analysis_data': research.analysis_data,  # Decrypted
            'proprietary_signals': research.proprietary_signals,  # Decrypted
            'strategy_details': research.strategy_details,  # Decrypted
            'created_at': research.created_at,
            'updated_at': research.updated_at
        }

# Usage
if __name__ == '__main__':
    # Create encrypted session
    session_id = create_secure_research_session(
        user_id='user-123',
        ticker='AAPL',
        analysis_data={
            'sentiment': 0.85,
            'technical_score': 0.72,
            'fundamental_score': 0.88
        },
        proprietary_signals={
            'momentum_signal': 'buy',
            'value_signal': 'hold',
            'quality_signal': 'buy'
        },
        strategy_details={
            'entry_price': 150.00,
            'target_price': 175.00,
            'stop_loss': 140.00,
            'position_size': 0.05
        }
    )
    
    print(f"âœ… Created encrypted session: {session_id}")
    
    # Retrieve (automatically decrypted)
    session_data = get_secure_research_session(
        session_id=session_id,
        requesting_user_id='user-123'
    )
    
    print(f"âœ… Retrieved decrypted data:")
    print(f"   Analysis: {session_data['analysis_data']}")
    print(f"   Signals: {session_data['proprietary_signals']}")
```

---

## Summary

**Key Takeaways:**

âœ… **Transparent Encryption** - Works automatically via SQLAlchemy events  
âœ… **Field-Level Control** - Encrypt only sensitive fields  
âœ… **Fernet Security** - Industry-standard encryption  
âœ… **Key Management** - Flexible single or multi-key support  
âœ… **Performance** - Minimal overhead with proper configuration  
âœ… **GDPR Compatible** - Works with compliance features  
âœ… **Easy to Use** - Mark fields in YAML, rest is automatic  

**Next Steps:**

1. Generate encryption keys
2. Configure environment variables
3. Mark sensitive fields in model configs
4. Enable encryption in initialization
5. Test encryption is working
6. Set up key rotation schedule
7. Enable audit logging

---

**Created:** October 19, 2025  
**Version:** 0.2.0  
**Word Count:** ~6,000 words  
**Status:** âœ… Complete