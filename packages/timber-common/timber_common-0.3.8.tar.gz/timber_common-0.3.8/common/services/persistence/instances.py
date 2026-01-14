# timber/common/services/persistence/instances.py
"""
Singleton Instances and Convenience Functions

This module provides:
1. Singleton instances of all persistence services
2. Convenience wrapper functions for backward compatibility

Import these when you need direct access to individual services.
"""

from .manager import PersistenceManager
from .cache import CachePersistenceService
from .research import ResearchPersistenceService
from .session import SessionPersistenceService
from .notification import NotificationPersistenceService
from .tracker import TrackerPersistenceService


# ==========================================
# Singleton Instances
# ==========================================

# Main persistence manager (aggregates all services)
persistence_manager = PersistenceManager()

# Individual service singletons for direct import
# These are independent instances that can be used directly
# Each service class implements singleton pattern internally
session_service = SessionPersistenceService()
notification_service = NotificationPersistenceService()
tracker_service = TrackerPersistenceService()
cache_service = CachePersistenceService()
research_service = ResearchPersistenceService()


# ==========================================
# Convenience Functions (Backward Compatibility)
# ==========================================
# These wrapper functions maintain backward compatibility
# with existing code that uses functional interfaces

def handle_sector_analysis_persistence(*args, **kwargs):
    """
    Convenience wrapper for sector analysis persistence.
    
    Delegates to persistence_manager.handle_sector_analysis_persistence()
    """
    return persistence_manager.handle_sector_analysis_persistence(*args, **kwargs)


def handle_index_analysis_persistence(*args, **kwargs):
    """
    Convenience wrapper for index analysis persistence.
    
    Delegates to persistence_manager.handle_index_analysis_persistence()
    """
    return persistence_manager.handle_index_analysis_persistence(*args, **kwargs)


def handle_global_summary_persistence(*args, **kwargs):
    """
    Convenience wrapper for global summary persistence.
    
    Delegates to persistence_manager.handle_global_summary_persistence()
    """
    return persistence_manager.handle_global_summary_persistence(*args, **kwargs)


def create_simulation_notification(*args, **kwargs):
    """
    Convenience wrapper for creating simulation notifications.
    
    Delegates to persistence_manager.create_simulation_notification()
    """
    return persistence_manager.create_simulation_notification(*args, **kwargs)


def create_tracker_notification(*args, **kwargs):
    """
    Convenience wrapper for creating tracker notifications.
    
    Delegates to persistence_manager.create_tracker_notification()
    """
    return persistence_manager.create_tracker_notification(*args, **kwargs)


# ==========================================
# Public API
# ==========================================

__all__ = [
    # Manager singleton
    'persistence_manager',
    
    # Individual service singletons
    'session_service',
    'notification_service',
    'tracker_service',
    'cache_service',
    'research_service',
    
    # Convenience functions
    'handle_sector_analysis_persistence',
    'handle_index_analysis_persistence',
    'handle_global_summary_persistence',
    'create_simulation_notification',
    'create_tracker_notification',
]