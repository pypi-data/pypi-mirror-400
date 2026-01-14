# timber/common/services/persistence/__init__.py
"""
Modular Persistence Service

Aggregates specialized persistence modules:
- Cache management
- Research data persistence  
- Session management
- Notification creation
- Tracker persistence
- Vector embedding ingestion

Each module focuses on a single responsibility for better
maintainability and testability.

Usage:
    # Import individual service singletons
    from common.services.persistence import session_service, notification_service
    
    # Import the unified manager
    from common.services.persistence import persistence_manager
    
    # Import convenience functions
    from common.services.persistence import handle_sector_analysis_persistence
"""

# ==========================================
# Base Classes and Service Implementations
# ==========================================

from .base import BasePersistenceService, gdpr_service
from .cache import CachePersistenceService
from .research import ResearchPersistenceService
from .session import SessionPersistenceService
from .notification import NotificationPersistenceService
from .tracker import TrackerPersistenceService

# ==========================================
# Manager and Singleton Instances
# ==========================================

from .manager import PersistenceManager
from .instances import (
    # Main manager
    persistence_manager,
    
    # Individual services
    session_service,
    notification_service,
    tracker_service,
    cache_service,
    research_service,
    
    # Convenience functions
    handle_sector_analysis_persistence,
    handle_index_analysis_persistence,
    handle_global_summary_persistence,
    create_simulation_notification,
    create_tracker_notification,
)


# ==========================================
# Public API
# ==========================================

__all__ = [
    # Base and service classes
    'BasePersistenceService',
    'CachePersistenceService',
    'ResearchPersistenceService',
    'SessionPersistenceService',
    'NotificationPersistenceService',
    'TrackerPersistenceService',
    
    # Manager class and singleton
    'PersistenceManager',
    'persistence_manager',
    
    # Individual service singletons (for direct import)
    'gdpr_service',
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