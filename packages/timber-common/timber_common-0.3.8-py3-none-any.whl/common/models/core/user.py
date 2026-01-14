# timber/common/models/core/user.py
"""
User Model

Core user model with multi-role support and relationships to all user-specific data.
Integrates with Flask-Login and includes GDPR compliance.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, JSON, Boolean
from werkzeug.security import generate_password_hash, check_password_hash

from ..base import Base
from ..mixins import TimestampMixin, GDPRComplianceMixin


class User(Base, TimestampMixin, GDPRComplianceMixin):
    """
    User model with support for multiple roles and OAuth.
    
    Serves as the central user identity across the OakQuant system.
    All user-specific data should reference this model via user_id.
    """
    __tablename__ = 'users'
    
    # Core User Fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth-only users and service accounts
    name = Column(String(255), nullable=True)
    profile_picture = Column(String(512), nullable=True)
    
    # Service Account Support
    is_service_account = Column(Boolean, nullable=False, default=False, index=True)
    # Service accounts are system users (e.g., "service:acorn") that don't authenticate
    # They have no password and are used for automated processes
    
    # Role Management
    # Stored as JSON array: ["user", "admin", "analyst"]
    roles = Column(JSON, nullable=False, default=lambda: ["user"])
    
    # Subscription & Features
    subscription_tier = Column(String(50), nullable=False, default='free')
    # Options: 'free', 'basic', 'premium', 'enterprise'
    
    # Authentication & Session
    last_login_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    
    # Feature Flags / User-Specific Settings
    acorn_corner_suggestion = Column(JSON, nullable=True)
    user_settings = Column(JSON, nullable=True, default=lambda: {})
    
    # === Flask-Login Integration ===
    
    @property
    def is_authenticated(self) -> bool:
        """Required by Flask-Login."""
        return True
    
    @property
    def is_anonymous(self) -> bool:
        """Required by Flask-Login."""
        return False
    
    def get_id(self) -> str:
        """Required by Flask-Login."""
        return self.id
    
    # === Password Management ===
    
    def set_password(self, password: str):
        """
        Hash and store a password.
        
        Args:
            password: Plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Check if provided password matches the hash.
        
        Args:
            password: Plain text password to check
        
        Returns:
            True if password matches, False otherwise
        """
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    # === Role Management ===
    
    def get_roles(self) -> List[str]:
        """
        Get list of user's roles.
        
        Returns:
            List of role names
        """
        if isinstance(self.roles, list):
            return self.roles
        elif isinstance(self.roles, str):
            import json
            try:
                return json.loads(self.roles)
            except json.JSONDecodeError:
                return ["user"]
        return ["user"]
    
    def has_role(self, role_name: str) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            role_name: Name of the role to check
        
        Returns:
            True if user has the role, False otherwise
        """
        return role_name in self.get_roles()
    
    def add_role(self, role_name: str):
        """
        Add a role to the user.
        
        Args:
            role_name: Name of the role to add
        """
        current_roles = self.get_roles()
        if role_name not in current_roles:
            current_roles.append(role_name)
            self.roles = current_roles
    
    def remove_role(self, role_name: str):
        """
        Remove a role from the user.
        
        Args:
            role_name: Name of the role to remove
        """
        current_roles = self.get_roles()
        if role_name in current_roles:
            current_roles.remove(role_name)
            self.roles = current_roles
    
    def is_admin(self) -> bool:
        """Check if user is an administrator."""
        return self.has_role('admin') or self.has_role('application:admin')
    
    def is_analyst(self) -> bool:
        """Check if user is an analyst."""
        return self.has_role('analyst')
    
    # === Subscription Management ===
    
    @property
    def is_premium(self) -> bool:
        """Check if user has a premium subscription."""
        return self.subscription_tier in ['premium', 'enterprise']
    
    @property
    def is_free(self) -> bool:
        """Check if user is on free tier."""
        return self.subscription_tier == 'free'
    
    def upgrade_subscription(self, new_tier: str):
        """
        Upgrade user's subscription tier.
        
        Args:
            new_tier: New subscription tier
        """
        valid_tiers = ['free', 'basic', 'premium', 'enterprise']
        if new_tier not in valid_tiers:
            raise ValueError(f"Invalid tier: {new_tier}")
        self.subscription_tier = new_tier
    
    # === Session Management ===
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login_at = datetime.now(timezone.utc)
    
    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False
    
    def activate(self):
        """Activate the user account."""
        self.is_active = True
    
    def verify_email(self):
        """Mark user's email as verified."""
        self.is_verified = True
    
    # === Settings Management ===
    
    def get_setting(self, key: str, default=None):
        """
        Get a user setting.
        
        Args:
            key: Setting key
            default: Default value if setting not found
        
        Returns:
            Setting value or default
        """
        if self.user_settings is None:
            return default
        return self.user_settings.get(key, default)
    
    def set_setting(self, key: str, value):
        """
        Set a user setting.
        
        Args:
            key: Setting key
            value: Setting value
        """
        if self.user_settings is None:
            self.user_settings = {}
        
        # Create a new dict to trigger SQLAlchemy's change detection
        settings = dict(self.user_settings)
        settings[key] = value
        self.user_settings = settings
    
    def remove_setting(self, key: str):
        """
        Remove a user setting.
        
        Args:
            key: Setting key to remove
        """
        if self.user_settings and key in self.user_settings:
            settings = dict(self.user_settings)
            del settings[key]
            self.user_settings = settings
    
    # === GDPR Implementation ===
    
    def export_data(self) -> dict:
        """
        Export user data for GDPR compliance.
        
        Returns:
            Dictionary with user data
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'roles': self.get_roles(),
            'subscription_tier': self.subscription_tier,
            'is_verified': self.is_verified,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_settings': self.user_settings
        }
    
    # === Serialization ===
    
    def to_dict(self, include_sensitive=False) -> dict:
        """
        Convert user to dictionary.
        
        Args:
            include_sensitive: If True, include sensitive fields
        
        Returns:
            User data as dictionary
        """
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'profile_picture': self.profile_picture,
            'roles': self.get_roles(),
            'subscription_tier': self.subscription_tier,
            'is_premium': self.is_premium,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'is_service_account': self.is_service_account,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
                'user_settings': self.user_settings
            })
        
        return data
    
    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User {self.email}>"