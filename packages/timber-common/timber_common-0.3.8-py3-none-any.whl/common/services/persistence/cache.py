# timber/common/services/persistence/cache.py
"""
Cache Persistence Service

Manages cache operations for research data with TTL-based freshness checks.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm.attributes import flag_modified

from common.services.persistence.base import BasePersistenceService

from common.models.registry import get_model 
from common.models.base import db_manager


class CachePersistenceService(BasePersistenceService):
    """
    Manages cache operations for market and stock data.
    
    Handles TTL-based cache freshness, retrieval, and updates.
    """
    
    def _get_model(self, model_name: str):
        """Helper to dynamically retrieve the model class."""
        model = get_model(model_name)
        if not model:
            self.logger.error(f"Cache model not found in registry: {model_name}")
            # Consider raising an error or returning None based on your needs
        return model
    
    def persist(self, data: dict) -> bool:
        """Persist cache data (implementation varies by cache type)."""
        raise NotImplementedError("Use specific cache methods instead")
    
    def retrieve(self, identifier: str) -> Optional[dict]:
        """Retrieve cache data (implementation varies by cache type)."""
        raise NotImplementedError("Use specific cache methods instead")
    
    # ===== Index Cache =====
    
    def get_or_create_index(self, index_name: str, index_symbol: str):
        """
        Get existing index or create a new one.
        
        Args:
            index_name: Human-readable index name
            index_symbol: Index ticker symbol
        
        Returns:
            CachedMarketIndex instance
        """
        CachedMarketIndex = self._get_model("CachedMarketIndex")
        with db_manager.session_scope() as session:
            index = session.query(CachedMarketIndex).filter_by(symbol=index_symbol).first()
            
            if not index:
                index = CachedMarketIndex(name=index_name, symbol=index_symbol)
                session.add(index)
                session.commit()
                self._log_operation("INDEX_CREATED", f"Created index {index_symbol}")
            
            return index
    
    def get_index_analysis(self, index_symbol: str, max_age_hours: int = 24):
        """
        Get cached index analysis if fresh.
        
        Args:
            index_symbol: Index ticker symbol
            max_age_hours: Maximum age in hours
        
        Returns:
            CachedMarketIndex if fresh, None otherwise
        """
        CachedMarketIndex = self._get_model('CachedMarketIndex')
        with db_manager.session_scope() as session:
            index = session.query(CachedMarketIndex).filter_by(symbol=index_symbol).first()
            
            if index and not index.is_stale(max_age_hours) and index.performance_data:
                self._log_operation("INDEX_CACHE_HIT", f"Fresh index data for {index_symbol}")
                return index
            
            self._log_operation("INDEX_CACHE_MISS", f"Stale or missing index data for {index_symbol}")
            return None
    
    def update_index_analysis(self, index_symbol: str, analysis_data: dict, components: list):
        """
        Update index analysis cache.
        
        Args:
            index_symbol: Index ticker symbol
            analysis_data: Analysis results
            components: List of index components
        """
        with db_manager.session_scope() as session:
            index = self.get_or_create_index(analysis_data.get('name', index_symbol), index_symbol)
            
            index.performance_data = analysis_data.get('summary')
            index.components = components
            index.last_updated = datetime.now(timezone.utc)
            
            session.merge(index)
            self._log_operation("INDEX_CACHE_UPDATED", f"Updated index {index_symbol}")
    
    # ===== Sector Cache =====
    
    def get_sector_analysis(
        self,
        index_id: int,
        sector_name: str,
        ttl_hours: int = 6
    ):
        """
        Get cached sector analysis if fresh.
        
        Args:
            index_id: Parent index ID
            sector_name: Sector name
            ttl_hours: Time-to-live in hours
        
        Returns:
            CachedSectorAnalysis if fresh, None otherwise
        """
        CachedSectorAnalysis = self._get_model('CachedSectorAnalysis')
        with db_manager.session_scope() as session:
            cached_result = session.query(CachedSectorAnalysis).filter_by(
                index_id=index_id,
                sector_name=sector_name
            ).order_by(CachedSectorAnalysis.last_updated.desc()).first()
            
            if cached_result and not cached_result.is_stale(ttl_hours):
                self._log_operation("SECTOR_CACHE_HIT", f"Fresh sector data: {sector_name}")
                return cached_result
            
            self._log_operation("SECTOR_CACHE_MISS", f"Stale or missing sector data: {sector_name}")
            return None
    
    def update_sector_analysis(self, index_id: int, sector_name: str, analysis_data: dict):
        """
        Update sector analysis cache.
        
        Args:
            index_id: Parent index ID
            sector_name: Sector name
            analysis_data: Analysis results
        """
        CachedSectorAnalysis = self._get_model('CachedSectorAnalysis')
        with db_manager.session_scope() as session:
            existing_entry = session.query(CachedSectorAnalysis).filter_by(
                index_id=index_id,
                sector_name=sector_name
            ).first()
            
            if existing_entry:
                existing_entry.outlook = analysis_data.get('outlook')
                existing_entry.trend_summary = analysis_data.get('trend_summary')
                existing_entry.news_sentiment_summary = analysis_data.get('news_sentiment_summary')
                existing_entry.top_companies_analysis = analysis_data.get('top_companies_analysis')
                existing_entry.last_updated = datetime.now(timezone.utc)
            else:
                cache_key = f"{index_id}-{sector_name.lower().replace(' ', '-')}"
                new_entry = CachedSectorAnalysis(
                    index_id=index_id,
                    sector_name=sector_name,
                    cache_key=cache_key,
                    outlook=analysis_data.get('outlook'),
                    trend_summary=analysis_data.get('trend_summary'),
                    news_sentiment_summary=analysis_data.get('news_sentiment_summary'),
                    top_companies_analysis=analysis_data.get('top_companies_analysis')
                )
                session.add(new_entry)
            
            self._log_operation("SECTOR_CACHE_UPDATED", f"Updated sector {sector_name}")
    
    # ===== Stock Cache =====
    
    def get_ticker_data(self, ticker_symbol: str, ttl_hours: int = 6):
        """
        Get cached ticker data if fresh.
        
        Args:
            ticker_symbol: Stock ticker
            ttl_hours: Time-to-live in hours
        
        Returns:
            CachedStockData if fresh, None otherwise
        """
        CachedStockData = self._get_model('CachedStockData')
        with db_manager.session_scope() as session:
            cached_result = session.query(CachedStockData).filter_by(ticker=ticker_symbol).first()
            
            if cached_result and not cached_result.is_stale(ttl_hours):
                self._log_operation("STOCK_CACHE_HIT", f"Fresh stock data: {ticker_symbol}")
                return cached_result
            
            self._log_operation("STOCK_CACHE_MISS", f"Stale or missing stock data: {ticker_symbol}")
            return None
    
    def update_ticker_data(self, ticker_symbol: str, research_data: dict):
        """
        Update ticker cache.
        
        Args:
            ticker_symbol: Stock ticker
            research_data: Research data
        """
        CachedStockData = self._get_model('CachedStockData')
        with db_manager.session_scope() as session:
            existing_entry = session.query(CachedStockData).filter_by(ticker=ticker_symbol).first()
            
            company_info = research_data.get('company_info', {})
            financial_data = research_data.get('financials', {})
            performance_data = research_data.get('performance', {})
            news_data = research_data.get('news', {})
            summary_data = research_data.get('summary', {})
            
            if existing_entry:
                existing_entry.company_name = company_info.get('longName')
                existing_entry.gics_sector = company_info.get('sector')
                existing_entry.financial_statements = financial_data
                existing_entry.performance_metrics = performance_data
                existing_entry.news_analysis = news_data
                existing_entry.worthiness_summary = summary_data
                existing_entry.last_updated = datetime.now(timezone.utc)
            else:
                new_entry = CachedStockData(
                    ticker=ticker_symbol,
                    company_name=company_info.get('longName'),
                    gics_sector=company_info.get('sector'),
                    financial_statements=financial_data,
                    performance_metrics=performance_data,
                    news_analysis=news_data,
                    worthiness_summary=summary_data
                )
                session.add(new_entry)
            
            self._log_operation("STOCK_CACHE_UPDATED", f"Updated stock {ticker_symbol}")
    
    # ===== Global Summary Cache =====
    
    def get_global_summary(self, cache_key: str, max_age_hours: int = 168):
        """
        Get cached global summary if fresh.
        
        Args:
            cache_key: Content-based cache key
            max_age_hours: Maximum age in hours
        
        Returns:
            CachedGlobalSummary if fresh, None otherwise
        """
        CachedGlobalSummary = self._get_model('CachedGlobalSummary')
        with db_manager.session_scope() as session:
            cached_summary = session.query(CachedGlobalSummary).filter_by(
                cache_key=cache_key
            ).first()
            
            if cached_summary and not cached_summary.is_stale(max_age_hours):
                self._log_operation("GLOBAL_CACHE_HIT", f"Fresh global summary")
                return cached_summary
            
            self._log_operation("GLOBAL_CACHE_MISS", f"Stale or missing global summary")
            return None
    
    def update_global_summary(self, cache_key: str, summary_data: dict):
        """
        Update global summary cache.
        
        Args:
            cache_key: Content-based cache key
            summary_data: Summary data
        """
        CachedGlobalSummary = self._get_model('CachedGlobalSummary')
        with db_manager.session_scope() as session:
            cached_summary = session.query(CachedGlobalSummary).filter_by(
                cache_key=cache_key
            ).first()
            
            if not cached_summary:
                cached_summary = CachedGlobalSummary(cache_key=cache_key)
                session.add(cached_summary)
            
            cached_summary.summary_data = summary_data
            cached_summary.last_updated = datetime.now(timezone.utc)
            
            self._log_operation("GLOBAL_CACHE_UPDATED", "Updated global summary")


# timber/common/services/persistence/notification.py
"""
Notification Persistence Service

Creates and manages user notifications.
"""

from .base import BasePersistenceService
from ...models.base import db_manager


class NotificationPersistenceService(BasePersistenceService):
    """
    Creates and manages user notifications.
    
    Handles notification creation for various events across the application.
    """
    
    def persist(self, data: dict) -> bool:
        """Persist notification data."""
        raise NotImplementedError("Use specific notification methods")
    
    def retrieve(self, identifier: str):
        """Retrieve notification data."""
        raise NotImplementedError("Use specific notification methods")
    
    def create_simulation_notification(
        self,
        user_id: str,
        results: dict,
        years_to_simulate: int,
        original_prompt: str = None
    ):
        """
        Create portfolio simulation notification.
        
        Args:
            user_id: User ID
            results: Simulation results
            years_to_simulate: Number of years simulated
            original_prompt: Original user prompt
        """
        if not user_id:
            self.logger.warning("No user_id provided for notification")
            return
        
        # Import here to avoid circular imports
        from ...models.core.user import User  # Assuming you have Notification model
        
        # Build notification content
        content = "<p><strong>Your portfolio simulation has been completed.</strong></p>"
        
        if original_prompt:
            content += (
                "<div class='notification-context'>"
                "<p><strong>Your Request:</strong></p>"
                f"<blockquote>{original_prompt}</blockquote>"
                "</div>"
            )
        
        content += (
            "<div class='notification-context'>"
            "<p><strong>Your Results:</strong></p>"
            f"<blockquote><p>Your {years_to_simulate}-year portfolio simulation is complete! </p>"
            f"<p>The projected median value is <strong>${results['median_final_value']:,.2f}</strong>.</p> "
            f"<p>The likely range is between ${results['percentile_25']:,.2f} and ${results['percentile_75']:,.2f}.</p></blockquote>"
            "</div>"
        )
        
        # This would create the notification - adapt to your Notification model
        self._log_operation("NOTIFICATION_CREATED", f"Simulation notification for user {user_id}")
    
    def create_tracker_notification(
        self,
        user_id: str,
        content: str,
        goal_id: int,
        stock_symbol: str
    ):
        """
        Create tracker event notification.
        
        Args:
            user_id: User ID
            content: Notification content
            goal_id: Associated goal ID
            stock_symbol: Stock symbol
        """
        if not user_id:
            self.logger.warning("No user_id provided for notification")
            return
        
        self._log_operation("NOTIFICATION_CREATED", f"Tracker notification for user {user_id}")
    
    def create_research_complete_notification(
        self,
        user_id: str,
        session_id: str,
        session_type: str,
        summary: str
    ):
        """
        Create research completion notification.
        
        Args:
            user_id: User ID
            session_id: Research session ID
            session_type: Type of research
            summary: Summary text
        """
        if not user_id:
            self.logger.warning("No user_id provided for notification")
            return
        
        self._log_operation("NOTIFICATION_CREATED", f"Research complete notification for user {user_id}")