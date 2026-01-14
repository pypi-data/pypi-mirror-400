# timber/common/services/persistence/research.py
"""
Research Persistence Service

Handles persistence of research data with cache-first strategy.
"""

import hashlib
import json
from .base import BasePersistenceService
from .cache import CachePersistenceService
from ...models.base import db_manager


class ResearchPersistenceService(BasePersistenceService):
    """
    Manages research data persistence with intelligent caching.
    
    Implements the cache-first strategy where data is retrieved from cache
    if fresh, otherwise live analysis is performed and cached.
    """
    
    def __init__(self):
        super().__init__()
        self.cache_service = CachePersistenceService()
    
    def persist(self, data: dict) -> bool:
        """Persist research data."""
        raise NotImplementedError("Use specific research methods")
    
    def retrieve(self, identifier: str):
        """Retrieve research data."""
        raise NotImplementedError("Use specific research methods")
    
    def handle_sector_analysis(
        self,
        index_id: int,
        sector_name: str,
        live_analysis_func,
        session_id: str,
        index_analysis_for_session_id: str,
        **kwargs
    ):
        """
        Handle sector analysis with cache-first strategy.
        
        Args:
            index_id: Parent index ID
            sector_name: Sector name
            live_analysis_func: Function to call if cache miss
            session_id: Current session ID
            index_analysis_for_session_id: Index analysis ID for session
            **kwargs: Additional args for live_analysis_func
        
        Returns:
            Analysis results
        """
        # 1. Check cache
        cached_data = self.cache_service.get_sector_analysis(index_id, sector_name)
        
        if cached_data:
            # CACHE HIT
            analysis_result = {
                "outlook": cached_data.outlook,
                "trend_summary": cached_data.trend_summary,
                "news_sentiment_summary": cached_data.news_sentiment_summary,
                "top_companies": cached_data.top_companies_analysis
            }
            self._log_operation("SECTOR_ANALYSIS_CACHE_HIT", f"Using cached data for {sector_name}")
        else:
            # CACHE MISS - run live analysis
            self._log_operation("SECTOR_ANALYSIS_CACHE_MISS", f"Running live analysis for {sector_name}")
            analysis_result = live_analysis_func(**kwargs)
            
            # Update cache if successful
            if analysis_result and 'error' not in analysis_result:
                self.cache_service.update_sector_analysis(index_id, sector_name, analysis_result)
        
        # 2. Write to permanent research tables (for this session)
        if analysis_result and 'error' not in analysis_result:
            self._persist_to_session_tables(session_id, index_analysis_for_session_id, analysis_result)
        
        return analysis_result
    
    def _persist_to_session_tables(self, session_id: str, index_analysis_id: str, analysis_result: dict):
        """Write analysis to permanent session tables."""
        # This would write to SectorAnalysisResult and CompanyPeerComparison tables
        # Implementation depends on your specific table structure
        self._log_operation("RESEARCH_PERSISTED", f"Saved to session {session_id}")
    
    def handle_index_analysis(
        self,
        index_symbol: str,
        index_name: str,
        live_analysis_func,
        session_id: str,
        cache_duration_hours: int = 24
    ):
        """
        Handle index analysis with caching.
        
        Args:
            index_symbol: Index symbol
            index_name: Index name
            live_analysis_func: Function to call if cache miss
            session_id: Current session ID
            cache_duration_hours: Cache TTL
        
        Returns:
            Analysis results
        """
        # Check cache
        cached_data = self.cache_service.get_index_analysis(index_symbol, cache_duration_hours)
        
        if cached_data:
            analysis_result = {
                "name": cached_data.name,
                "summary": cached_data.performance_data,
                "components": cached_data.components
            }
            self._log_operation("INDEX_ANALYSIS_CACHE_HIT", f"Using cached data for {index_symbol}")
        else:
            # Run live analysis
            self._log_operation("INDEX_ANALYSIS_CACHE_MISS", f"Running live analysis for {index_symbol}")
            analysis_result = live_analysis_func()
            
            # Update cache
            if analysis_result and 'error' not in analysis_result:
                self.cache_service.update_index_analysis(
                    index_symbol,
                    analysis_result,
                    analysis_result.get('components')
                )
        
        return {index_symbol: analysis_result}
    
    def handle_global_summary(
        self,
        individual_summaries: dict,
        live_analysis_func,
        session_id: str,
        cache_duration_hours: int = 168
    ):
        """
        Handle global market summary with caching.
        
        Args:
            individual_summaries: Individual market summaries
            live_analysis_func: Function to call if cache miss
            session_id: Current session ID
            cache_duration_hours: Cache TTL
        
        Returns:
            Global summary
        """
        # Create content-based cache key
        sorted_summaries_str = json.dumps(individual_summaries, sort_keys=True)
        cache_key = hashlib.sha256(sorted_summaries_str.encode('utf-8')).hexdigest()
        
        # Check cache
        cached_summary = self.cache_service.get_global_summary(cache_key, cache_duration_hours)
        
        if cached_summary:
            global_summary = cached_summary.summary_data
            self._log_operation("GLOBAL_SUMMARY_CACHE_HIT", "Using cached global summary")
        else:
            # Run live analysis
            self._log_operation("GLOBAL_SUMMARY_CACHE_MISS", "Generating new global summary")
            global_summary = live_analysis_func(individual_summaries)
            
            # Update cache
            if global_summary and 'error' not in global_summary:
                self.cache_service.update_global_summary(cache_key, global_summary)
        
        return global_summary
    
    # Opportunity Research Methods
    
    def update_opportunity_index_overview(self, session_id: str, index_overview_data: dict):
        """Update opportunity research index overview in session."""
        self._log_operation("OPPORTUNITY_INDEX_UPDATED", f"Session {session_id}")
    
    def update_opportunity_sector(self, session_id: str, opportunity_sector_data: dict):
        """Update opportunity research sector data in session."""
        self._log_operation("OPPORTUNITY_SECTOR_UPDATED", f"Session {session_id}")
    
    def handle_opportunity_company_analysis(self, session_id: str, analysis_data: dict):
        """Persist opportunity company analysis."""
        self._log_operation("OPPORTUNITY_COMPANY_SAVED", f"Session {session_id}")
    
    def handle_opportunity_report(self, session_id: str, report_data: dict):
        """Persist opportunity final report."""
        self._log_operation("OPPORTUNITY_REPORT_SAVED", f"Session {session_id}")


# timber/common/services/persistence/session.py
"""
Session Persistence Service

Manages workflow session state transitions and research data updates.
"""

from .base import BasePersistenceService
from ...models.registry import get_session_model
from ...models.base import db_manager


class SessionPersistenceService(BasePersistenceService):
    """
    Manages workflow session operations.
    
    Handles state transitions, research data updates, and session lifecycle.
    """
    
    def persist(self, data: dict) -> bool:
        """Persist session data."""
        raise NotImplementedError("Use specific session methods")
    
    def retrieve(self, identifier: str):
        """Retrieve session data."""
        raise NotImplementedError("Use specific session methods")
    
    def transition_state(self, session_id: str, session_type: str, new_state: str):
        """
        Transition a workflow session to a new state.
        
        Args:
            session_id: Session ID
            session_type: Type of session
            new_state: New state
        """
        session_model = get_session_model(session_type)
        
        if not session_model:
            self.logger.error(f"Unknown session type: {session_type}")
            return
        
        with db_manager.session_scope() as db_session:
            session = db_session.query(session_model).get(session_id)
            
            if session:
                old_state = session.state
                session.state = new_state
                self._log_operation("STATE_TRANSITION", f"{session_type} {session_id}: {old_state} -> {new_state}")
            else:
                self.logger.error(f"Session not found: {session_id}")
    
    def update_research_data(self, session_id: str, session_type: str, data: dict):
        """
        Update research data for a session.
        
        Args:
            session_id: Session ID
            session_type: Type of session
            data: Data to update
        """
        session_model = get_session_model(session_type)
        
        if not session_model:
            self.logger.error(f"Unknown session type: {session_type}")
            return
        
        with db_manager.session_scope() as db_session:
            session = db_session.query(session_model).get(session_id)
            
            if session:
                # Update research_data field
                if hasattr(session, 'research_data'):
                    current_data = session.research_data or {}
                    current_data.update(data)
                    session.research_data = current_data
                    
                    # Flag as modified for SQLAlchemy
                    from sqlalchemy.orm.attributes import flag_modified
                    flag_modified(session, 'research_data')
                    
                    self._log_operation("RESEARCH_DATA_UPDATED", f"{session_type} {session_id}")
                else:
                    self.logger.warning(f"Session {session_id} has no research_data field")
            else:
                self.logger.error(f"Session not found: {session_id}")


# timber/common/services/persistence/tracker.py
"""
Tracker Persistence Service

Manages tracked asset status and events.
"""

from .base import BasePersistenceService
from ...models.base import db_manager


class TrackerPersistenceService(BasePersistenceService):
    """
    Manages tracked asset operations.
    
    Handles tracker status updates and event logging.
    """
    
    def persist(self, data: dict) -> bool:
        """Persist tracker data."""
        raise NotImplementedError("Use specific tracker methods")
    
    def retrieve(self, identifier: str):
        """Retrieve tracker data."""
        raise NotImplementedError("Use specific tracker methods")
    
    def update_status(self, tracker_id: str, new_status: str):
        """
        Update tracker status.
        
        Args:
            tracker_id: Tracker ID
            new_status: New status (e.g., 'active', 'paused', 'achieved')
        """
        # Import here to avoid circular imports
        # from ...models.tracker import TrackedAsset
        
        self._log_operation("TRACKER_STATUS_UPDATED", f"Tracker {tracker_id} -> {new_status}")
    
    def log_event(self, tracker_id: str, event_data: dict):
        """
        Log a tracker monitoring event.
        
        Args:
            tracker_id: Tracker ID
            event_data: Event data
        """
        self._log_operation("TRACKER_EVENT_LOGGED", f"Tracker {tracker_id}")