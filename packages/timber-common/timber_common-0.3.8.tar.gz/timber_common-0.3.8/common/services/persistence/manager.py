# timber/common/services/persistence/manager.py
"""
Persistence Manager

Unified interface to all persistence services.
Delegates operations to specialized service modules.
"""

from .cache import CachePersistenceService
from .research import ResearchPersistenceService
from .session import SessionPersistenceService
from .notification import NotificationPersistenceService
from .tracker import TrackerPersistenceService

import logging

logger = logging.getLogger(__name__)


class PersistenceManager:
    """
    Unified interface to all persistence services.
    
    Provides a single entry point for all data persistence operations
    while delegating to specialized services.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PersistenceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Initialize all specialized services
        self.cache = CachePersistenceService()
        self.research = ResearchPersistenceService()
        self.session = SessionPersistenceService()
        self.notification = NotificationPersistenceService()
        self.tracker = TrackerPersistenceService()
        
        self._initialized = True
        logger.info("Persistence Manager initialized with all services")
    
    # ==========================================
    # Cache Operations
    # ==========================================
    
    def get_cached_sector_analysis(self, index_id: int, sector_name: str, ttl_hours: int = 6):
        """Retrieve cached sector analysis."""
        return self.cache.get_sector_analysis(index_id, sector_name, ttl_hours)
    
    def update_sector_analysis_cache(self, index_id: int, sector_name: str, analysis_data: dict):
        """Update sector analysis cache."""
        return self.cache.update_sector_analysis(index_id, sector_name, analysis_data)
    
    def get_cached_ticker_data(self, ticker_symbol: str, ttl_hours: int = 6):
        """Retrieve cached ticker data."""
        return self.cache.get_ticker_data(ticker_symbol, ttl_hours)
    
    def update_ticker_cache(self, ticker_symbol: str, research_data: dict):
        """Update ticker cache."""
        return self.cache.update_ticker_data(ticker_symbol, research_data)
    
    def get_cached_index_analysis(self, index_symbol: str, max_age_hours: int = 24):
        """Retrieve cached index analysis."""
        return self.cache.get_index_analysis(index_symbol, max_age_hours)
    
    def update_index_analysis_cache(self, index_symbol: str, analysis_data: dict, components: list):
        """Update index analysis cache."""
        return self.cache.update_index_analysis(index_symbol, analysis_data, components)
    
    def get_cached_global_summary(self, cache_key: str, max_age_hours: int = 168):
        """Retrieve cached global summary."""
        return self.cache.get_global_summary(cache_key, max_age_hours)
    
    def update_global_summary_cache(self, cache_key: str, summary_data: dict):
        """Update global summary cache."""
        return self.cache.update_global_summary(cache_key, summary_data)
    
    # ==========================================
    # Research Persistence Operations
    # ==========================================
    
    def handle_sector_analysis_persistence(
        self,
        index_id: int,
        sector_name: str,
        live_analysis_func,
        session_id: str,
        index_analysis_for_session_id: str,
        **kwargs
    ):
        """Handle sector analysis with caching and persistence."""
        return self.research.handle_sector_analysis(
            index_id, sector_name, live_analysis_func,
            session_id, index_analysis_for_session_id, **kwargs
        )
    
    def handle_index_analysis_persistence(
        self,
        index_symbol: str,
        index_name: str,
        live_analysis_func,
        session_id: str,
        cache_duration_hours: int = 24
    ):
        """Handle index analysis with caching and persistence."""
        return self.research.handle_index_analysis(
            index_symbol, index_name, live_analysis_func,
            session_id, cache_duration_hours
        )
    
    def handle_global_summary_persistence(
        self,
        individual_summaries: dict,
        live_analysis_func,
        session_id: str,
        cache_duration_hours: int = 168
    ):
        """Handle global summary with caching and persistence."""
        return self.research.handle_global_summary(
            individual_summaries, live_analysis_func,
            session_id, cache_duration_hours
        )
    
    # ==========================================
    # Opportunity Research Operations
    # ==========================================
    
    def update_opportunity_index_overview(self, session_id: str, index_overview_data: dict):
        """Update opportunity research index overview."""
        return self.research.update_opportunity_index_overview(session_id, index_overview_data)
    
    def update_opportunity_sector(self, session_id: str, opportunity_sector_data: dict):
        """Update opportunity research sector data."""
        return self.research.update_opportunity_sector(session_id, opportunity_sector_data)
    
    def handle_opportunity_company_analysis(self, session_id: str, analysis_data: dict):
        """Persist opportunity company analysis."""
        return self.research.handle_opportunity_company_analysis(session_id, analysis_data)
    
    def handle_opportunity_report(self, session_id: str, report_data: dict):
        """Persist opportunity final report."""
        return self.research.handle_opportunity_report(session_id, report_data)
    
    # ==========================================
    # Session Management Operations
    # ==========================================
    
    def get_or_create_index(self, index_name: str, index_symbol: str):
        """Get or create a cached market index."""
        return self.cache.get_or_create_index(index_name, index_symbol)
    
    def transition_workflow_state(self, session_id: str, session_type: str, new_state: str):
        """Transition a workflow session to a new state."""
        return self.session.transition_state(session_id, session_type, new_state)
    
    def update_session_research_data(self, session_id: str, session_type: str, data: dict):
        """Update research data for a session."""
        return self.session.update_research_data(session_id, session_type, data)
    
    # ==========================================
    # Notification Operations
    # ==========================================
    
    def create_simulation_notification(
        self,
        user_id: str,
        results: dict,
        years_to_simulate: int,
        original_prompt: str = None
    ):
        """Create a portfolio simulation notification."""
        return self.notification.create_simulation_notification(
            user_id, results, years_to_simulate, original_prompt
        )
    
    def create_tracker_notification(
        self,
        user_id: str,
        content: str,
        goal_id: int,
        stock_symbol: str
    ):
        """Create a tracker event notification."""
        return self.notification.create_tracker_notification(
            user_id, content, goal_id, stock_symbol
        )
    
    def create_research_complete_notification(
        self,
        user_id: str,
        session_id: str,
        session_type: str,
        summary: str
    ):
        """Create a research completion notification."""
        return self.notification.create_research_complete_notification(
            user_id, session_id, session_type, summary
        )
    
    # ==========================================
    # Tracker Operations
    # ==========================================
    
    def update_tracker_status(self, tracker_id: str, new_status: str):
        """Update tracker status."""
        return self.tracker.update_status(tracker_id, new_status)
    
    def log_tracker_event(self, tracker_id: str, event_data: dict):
        """Log a tracker monitoring event."""
        return self.tracker.log_event(tracker_id, event_data)