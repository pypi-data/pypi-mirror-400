# timber/common/services/encryption/field_encryption.py
"""
Field-Level Encryption Service

Provides transparent encryption/decryption of model fields using Fernet (symmetric encryption).
Integrates with SQLAlchemy events for automatic encryption on write and decryption on read.
"""

from typing import Dict, Optional, Any
from cryptography.fernet import Fernet, InvalidToken
import base64
import json
import logging
import os

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Service for encrypting/decrypting model fields.
    
    Uses Fernet symmetric encryption with key rotation support.
    Keys can be per-user or system-wide depending on configuration.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EncryptionService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Key storage
        self._keys: Dict[str, Fernet] = {}
        self._default_key_id = "default"
        
        # Initialize default key from environment
        self._initialize_default_key()
        
        self._initialized = True
        logger.info("Encryption Service initialized")
    
    def _initialize_default_key(self):
        """Initialize the default encryption key from environment."""
        default_key = os.getenv('ENCRYPTION_KEY')
        
        if not default_key:
            logger.warning(
                "No ENCRYPTION_KEY found in environment. "
                "Generating a new key. This should only happen in development!"
            )
            default_key = Fernet.generate_key().decode()
            logger.warning(f"Generated key: {default_key}")
        
        # Ensure key is bytes
        if isinstance(default_key, str):
            default_key = default_key.encode()
        
        self._keys[self._default_key_id] = Fernet(default_key)
    
    def register_key(self, key_id: str, key: bytes):
        """
        Register an encryption key.
        
        Args:
            key_id: Identifier for the key (e.g., "user_data_key", "user_123")
            key: Fernet encryption key (32 url-safe base64-encoded bytes)
        """
        try:
            self._keys[key_id] = Fernet(key)
            logger.info(f"Registered encryption key: {key_id}")
        except Exception as e:
            logger.error(f"Failed to register key {key_id}: {e}")
            raise
    
    def encrypt(self, data: Any, key_id: Optional[str] = None) -> str:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt (will be JSON-serialized if not string)
            key_id: Key identifier (uses default if not specified)
        
        Returns:
            Base64-encoded encrypted data
        """
        if data is None:
            return None
        
        key_id = key_id or self._default_key_id
        
        if key_id not in self._keys:
            raise ValueError(f"Unknown key identifier: {key_id}")
        
        # Convert to string if needed
        if not isinstance(data, str):
            data = json.dumps(data)
        
        # Encrypt
        fernet = self._keys[key_id]
        encrypted = fernet.encrypt(data.encode())
        
        # Return base64-encoded string for database storage
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str, key_id: Optional[str] = None) -> Any:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            key_id: Key identifier (uses default if not specified)
        
        Returns:
            Decrypted data (will attempt JSON deserialization)
        """
        if encrypted_data is None:
            return None
        
        key_id = key_id or self._default_key_id
        
        if key_id not in self._keys:
            raise ValueError(f"Unknown key identifier: {key_id}")
        
        try:
            # Decrypt
            fernet = self._keys[key_id]
            
            # Ensure bytes
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode()
            
            decrypted = fernet.decrypt(encrypted_data).decode()
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return decrypted
        
        except InvalidToken:
            logger.error("Failed to decrypt data - invalid token")
            raise
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def rotate_key(self, old_key_id: str, new_key_id: str, new_key: bytes):
        """
        Rotate encryption keys.
        
        Note: This only registers the new key. You'll need to re-encrypt
        existing data separately using `re_encrypt_field`.
        
        Args:
            old_key_id: Current key identifier
            new_key_id: New key identifier
            new_key: New encryption key
        """
        if old_key_id not in self._keys:
            raise ValueError(f"Old key not found: {old_key_id}")
        
        self.register_key(new_key_id, new_key)
        logger.info(f"Key rotation: {old_key_id} -> {new_key_id}")
    
    def re_encrypt_field(self, encrypted_data: str, old_key_id: str, new_key_id: str) -> str:
        """
        Re-encrypt data with a new key (for key rotation).
        
        Args:
            encrypted_data: Currently encrypted data
            old_key_id: Current key identifier
            new_key_id: New key identifier
        
        Returns:
            Data encrypted with new key
        """
        decrypted = self.decrypt(encrypted_data, old_key_id)
        return self.encrypt(decrypted, new_key_id)
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new Fernet encryption key."""
        return Fernet.generate_key()
    
    def has_key(self, key_id: str) -> bool:
        """Check if a key is registered."""
        return key_id in self._keys


# Singleton instance
encryption_service = EncryptionService()


# ============================================================
# SQLAlchemy Integration
# ============================================================

from sqlalchemy import event
from sqlalchemy.orm import Session


def setup_encryption_events(base_class):
    """
    Set up SQLAlchemy events for automatic encryption/decryption.
    
    Should be called once during application initialization with your Base class.
    
    Args:
        base_class: SQLAlchemy declarative base class
    """
    
    @event.listens_for(base_class, 'before_insert', propagate=True)
    @event.listens_for(base_class, 'before_update', propagate=True)
    def encrypt_fields(mapper, connection, target):
        """Encrypt fields before database write."""
        # Check if model has encrypted fields
        if not hasattr(target, 'get_encrypted_fields'):
            return
        
        encrypted_fields = target.get_encrypted_fields()
        if not encrypted_fields:
            return
        
        # Get encryption key identifier
        if hasattr(target, '_config') and 'encryption' in target._config:
            key_id = target._config['encryption'].get('key_identifier')
        else:
            key_id = None
        
        # Encrypt each field
        for field_name in encrypted_fields:
            if not hasattr(target, field_name):
                continue
            
            value = getattr(target, field_name)
            
            if value is not None:
                # Check if already encrypted (has encryption marker)
                if isinstance(value, str) and value.startswith('gAAAAA'):
                    # Already encrypted (Fernet tokens start with gAAAAA)
                    continue
                
                try:
                    encrypted_value = encryption_service.encrypt(value, key_id)
                    setattr(target, field_name, encrypted_value)
                except Exception as e:
                    logger.error(f"Failed to encrypt {field_name}: {e}")
    
    @event.listens_for(base_class, 'load', propagate=True)
    def decrypt_fields(target, context):
        """Decrypt fields after database read."""
        # Check if model has encrypted fields
        if not hasattr(target, 'get_encrypted_fields'):
            return
        
        encrypted_fields = target.get_encrypted_fields()
        if not encrypted_fields:
            return
        
        # Get encryption key identifier
        if hasattr(target, '_config') and 'encryption' in target._config:
            key_id = target._config['encryption'].get('key_identifier')
        else:
            key_id = None
        
        # Decrypt each field
        for field_name in encrypted_fields:
            if not hasattr(target, field_name):
                continue
            
            encrypted_value = getattr(target, field_name)
            
            if encrypted_value is not None:
                try:
                    decrypted_value = encryption_service.decrypt(encrypted_value, key_id)
                    setattr(target, field_name, decrypted_value)
                except Exception as e:
                    logger.error(f"Failed to decrypt {field_name}: {e}")
                    # Leave encrypted value in place rather than failing


# ============================================================
# Per-User Key Management
# ============================================================

class UserKeyManager:
    """
    Manages per-user encryption keys.
    
    For maximum security, each user can have their own encryption key.
    Keys are derived from a master key + user_id.
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize user key manager.
        
        Args:
            master_key: Master key for deriving user keys (from environment if not provided)
        """
        if master_key is None:
            master_key = os.getenv('MASTER_ENCRYPTION_KEY')
            if master_key:
                master_key = master_key.encode()
        
        self.master_key = master_key
    
    def get_user_key_id(self, user_id: str) -> str:
        """Get key identifier for a user."""
        return f"user_{user_id}"
    
    def register_user_key(self, user_id: str):
        """
        Register encryption key for a user.
        
        Derives key from master key + user_id for consistent key generation.
        """
        if not self.master_key:
            logger.warning("No master key available for per-user keys")
            return
        
        key_id = self.get_user_key_id(user_id)
        
        # Derive user key from master key + user_id
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=user_id.encode(),
            iterations=100000,
        )
        
        user_key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        
        encryption_service.register_key(key_id, user_key)
        logger.info(f"Registered encryption key for user {user_id}")


# Singleton instance
user_key_manager = UserKeyManager()