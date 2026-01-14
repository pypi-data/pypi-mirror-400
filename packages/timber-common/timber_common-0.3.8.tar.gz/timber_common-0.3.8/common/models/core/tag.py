# timber/common/models/core/tag.py
"""
Tag Model

Shared tagging system for categorizing content across the application.
Can be used for goals, notifications, research sessions, etc.
"""

from sqlalchemy import Column, Integer, String
from ..base import Base
from ..mixins import TimestampMixin


class Tag(Base, TimestampMixin):
    """
    Tag model for categorizing and organizing content.
    
    Tags are shared across the application and can be associated
    with multiple entity types through many-to-many relationships.
    """
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)  # Optional grouping
    color = Column(String(20), nullable=True)  # UI color code
    description = Column(String(255), nullable=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)
    
    def increment_usage(self):
        """Increment the usage count for this tag."""
        self.usage_count += 1
    
    def decrement_usage(self):
        """Decrement the usage count for this tag."""
        if self.usage_count > 0:
            self.usage_count -= 1
    
    def to_dict(self) -> dict:
        """Serialize tag to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'color': self.color,
            'description': self.description,
            'usage_count': self.usage_count
        }
    
    def __repr__(self) -> str:
        return f"<Tag '{self.name}'>"