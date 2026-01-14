# Service Architecture Best Practices

**Best practices for designing and implementing modular, maintainable services in Timber**

---

## Table of Contents

1. [Overview](#overview)
2. [Service Design Principles](#service-design-principles)
3. [Modular Service Architecture](#modular-service-architecture)
4. [Service Patterns](#service-patterns)
5. [Dependency Management](#dependency-management)
6. [Testing Services](#testing-services)
7. [Performance Considerations](#performance-considerations)
8. [Common Patterns](#common-patterns)
9. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Overview

Timber uses a modular service architecture where functionality is split into focused, single-responsibility services. This makes the codebase easier to understand, test, and maintain.

### Benefits of Modular Services

✅ **Single Responsibility**: Each service has one clear purpose  
✅ **Easy to Test**: Services can be tested in isolation  
✅ **Maintainable**: Changes are localized to specific services  
✅ **Reusable**: Services can be used across different parts of the application  
✅ **Scalable**: Services can be optimized or replaced independently  
✅ **Team-Friendly**: Multiple developers can work on different services

### Core Service Categories

```python
/common/services/
├── persistence/           # Data persistence operations
│   ├── session.py        # Session management
│   ├── research.py       # Research data
│   ├── notification.py   # Notifications
│   └── tracker.py        # Activity tracking
│
├── vector/               # Vector operations
│   ├── search.py         # Semantic search
│   ├── ingestion.py      # Data ingestion
│   └── embeddings.py     # Embedding generation
│
├── gdpr/                 # GDPR compliance
│   ├── deletion.py       # Data deletion
│   ├── export.py         # Data export
│   └── anonymization.py  # Data anonymization
│
├── encryption/           # Data security
│   └── field_encryption.py
│
└── data_fetcher.py       # External API integration
```

---

## Service Design Principles

### 1. Single Responsibility Principle

Each service should have ONE reason to change.

**✅ GOOD - Focused Services**:
```python
# session_service.py - Only manages sessions
class SessionPersistenceService:
    """Handles session CRUD operations only."""
    
    def create_session(self, session_type, user_id, **kwargs):
        """Create a new session."""
        pass
    
    def get_session(self, session_id, session_type):
        """Retrieve a session."""
        pass
    
    def update_session(self, session_id, **updates):
        """Update session fields."""
        pass
    
    def delete_session(self, session_id, session_type):
        """Delete a session."""
        pass

# research_service.py - Only manages research data
class ResearchPersistenceService:
    """Handles research data operations only."""
    
    def save_research(self, session_id, content, research_type):
        """Save research data."""
        pass
    
    def get_research(self, session_id):
        """Retrieve research data."""
        pass
```

**❌ BAD - God Service**:
```python
# persistence_service.py - Too many responsibilities
class PersistenceService:
    """Handles everything - sessions, research, notifications, tracking..."""
    
    def create_session(self, ...):
        pass
    
    def save_research(self, ...):
        pass
    
    def create_notification(self, ...):
        pass
    
    def track_event(self, ...):
        pass
    
    def cache_data(self, ...):
        pass
    
    # ... 50 more methods
```

### 2. Dependency Inversion

Services should depend on abstractions, not concretions.

**✅ GOOD - Depends on Interfaces**:
```python
from abc import ABC, abstractmethod

# Define interface
class CacheInterface(ABC):
    @abstractmethod
    def get(self, key):
        pass
    
    @abstractmethod
    def set(self, key, value, ttl=None):
        pass

# Service depends on interface
class SessionService:
    def __init__(self, cache: CacheInterface):
        self.cache = cache  # Any cache implementation works
    
    def get_cached_session(self, session_id):
        return self.cache.get(f"session:{session_id}")

# Easy to swap implementations
from caches import RedisCache, MemoryCache

# Use Redis in production
service = SessionService(cache=RedisCache())

# Use memory cache in tests
test_service = SessionService(cache=MemoryCache())
```

**❌ BAD - Tight Coupling**:
```python
# Hard-coded dependency on Redis
import redis

class SessionService:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379)  # Can't change!
    
    def get_cached_session(self, session_id):
        return self.redis.get(f"session:{session_id}")
```

### 3. Interface Segregation

Clients shouldn't depend on methods they don't use.

**✅ GOOD - Focused Interfaces**:
```python
class SessionReader(ABC):
    """Interface for reading sessions."""
    @abstractmethod
    def get_session(self, session_id):
        pass

class SessionWriter(ABC):
    """Interface for writing sessions."""
    @abstractmethod
    def create_session(self, session_type, user_id):
        pass
    
    @abstractmethod
    def update_session(self, session_id, **updates):
        pass

# Clients only depend on what they need
class SessionReportGenerator:
    def __init__(self, reader: SessionReader):  # Only needs reading
        self.reader = reader
    
    def generate_report(self, session_id):
        session = self.reader.get_session(session_id)
        # Generate report...
```

**❌ BAD - Fat Interface**:
```python
class SessionService(ABC):
    """Everything in one interface - clients must implement all methods."""
    @abstractmethod
    def get_session(self, session_id):
        pass
    
    @abstractmethod
    def create_session(self, session_type, user_id):
        pass
    
    @abstractmethod
    def update_session(self, session_id, **updates):
        pass
    
    @abstractmethod
    def delete_session(self, session_id):
        pass
    
    @abstractmethod
    def list_sessions(self, user_id):
        pass
    
    # ... 20 more methods

# This client only needs get_session but must implement everything!
class SessionReportGenerator(SessionService):
    def generate_report(self, session_id):
        session = self.get_session(session_id)
        # ...
    
    # Must implement all these even though they're not used:
    def create_session(self, session_type, user_id):
        raise NotImplementedError("Don't need this!")
    
    # ... and so on
```

### 4. Open/Closed Principle

Services should be open for extension but closed for modification.

**✅ GOOD - Extensible Design**:
```python
class BaseDataFetcher(ABC):
    """Base class for data fetchers."""
    
    @abstractmethod
    def fetch(self, symbol, **params):
        pass

# Extend without modifying base
class YFinanceDataFetcher(BaseDataFetcher):
    def fetch(self, symbol, **params):
        # yfinance implementation
        pass

class AlphaVantageDataFetcher(BaseDataFetcher):
    def fetch(self, symbol, **params):
        # Alpha Vantage implementation
        pass

# Data fetcher service uses strategy pattern
class StockDataService:
    def __init__(self):
        self.fetchers = {
            'yfinance': YFinanceDataFetcher(),
            'alphavantage': AlphaVantageDataFetcher(),
        }
    
    def fetch_data(self, symbol, source='yfinance', **params):
        fetcher = self.fetchers[source]
        return fetcher.fetch(symbol, **params)
    
    # Easy to add new source without modifying service
    def register_fetcher(self, name, fetcher):
        self.fetchers[name] = fetcher
```

### 5. Liskov Substitution

Subtypes must be substitutable for their base types.

**✅ GOOD - Proper Substitution**:
```python
class CacheService(ABC):
    @abstractmethod
    def get(self, key):
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key, value, ttl=None):
        """Set value in cache."""
        pass

class RedisCache(CacheService):
    def get(self, key):
        # Returns None if not found (consistent with interface)
        return self.redis.get(key)
    
    def set(self, key, value, ttl=None):
        # Honors TTL parameter
        self.redis.setex(key, ttl or 3600, value)

class MemoryCache(CacheService):
    def get(self, key):
        # Returns None if not found (consistent with interface)
        return self.cache.get(key)
    
    def set(self, key, value, ttl=None):
        # Honors TTL parameter
        expiry = datetime.now() + timedelta(seconds=ttl or 3600)
        self.cache[key] = (value, expiry)

# Both can be used interchangeably
def get_user_data(user_id, cache: CacheService):
    return cache.get(f"user:{user_id}")

# Works with either implementation
get_user_data('123', RedisCache())
get_user_data('123', MemoryCache())
```

---

## Modular Service Architecture

### Service Layer Structure

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  (Views, Controllers, API Endpoints)    │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         Service Layer                   │
│  ┌─────────────────────────────────┐   │
│  │  Persistence Services           │   │
│  │  - SessionService               │   │
│  │  - ResearchService              │   │
│  │  - NotificationService          │   │
│  └─────────────────────────────────┘   │
│                                          │
│  ┌─────────────────────────────────┐   │
│  │  Business Logic Services        │   │
│  │  - AnalysisService              │   │
│  │  - RecommendationService        │   │
│  └─────────────────────────────────┘   │
│                                          │
│  ┌─────────────────────────────────┐   │
│  │  Infrastructure Services        │   │
│  │  - CacheService                 │   │
│  │  - EncryptionService            │   │
│  │  - VectorService                │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         Data Layer                      │
│  (Models, Database, External APIs)      │
└─────────────────────────────────────────┘
```

### Example: Modular Persistence Services

```python
# common/services/persistence/__init__.py
"""Modular persistence services for Timber."""

from .session import session_service, SessionPersistenceService
from .research import research_service, ResearchPersistenceService
from .notification import notification_service, NotificationPersistenceService
from .tracker import tracker_service, TrackerPersistenceService

__all__ = [
    'session_service',
    'SessionPersistenceService',
    'research_service',
    'ResearchPersistenceService',
    'notification_service',
    'NotificationPersistenceService',
    'tracker_service',
    'TrackerPersistenceService',
]

# Optional: Unified facade for convenience
class PersistenceManager:
    """
    Unified interface to all persistence services.
    
    Provides convenience methods that delegate to specialized services.
    """
    
    def __init__(self):
        self.session = session_service
        self.research = research_service
        self.notification = notification_service
        self.tracker = tracker_service
    
    # Convenience methods that delegate
    def save_research_with_tracking(self, session_id, content, user_id):
        """Save research and track the event."""
        # Use research service
        research_id = self.research.save_research(
            session_id=session_id,
            content=content
        )
        
        # Use tracker service
        self.tracker.track_event(
            user_id=user_id,
            event_type='research_saved',
            metadata={'research_id': research_id}
        )
        
        return research_id

persistence_manager = PersistenceManager()
```

---

## Service Patterns

### Pattern 1: Singleton Pattern

Use for services that should have only one instance.

```python
class SessionPersistenceService:
    """Singleton service for session persistence."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Initialize once
        self._cache = {}
        self._initialized = True
    
    def create_session(self, session_type, user_id, **kwargs):
        """Create a new session."""
        # Implementation...
        pass

# Global singleton instance
session_service = SessionPersistenceService()

# All imports get the same instance
from common.services.persistence import session_service  # Same instance everywhere
```

### Pattern 2: Factory Pattern

Use for creating objects based on configuration.

```python
class DataFetcherFactory:
    """Factory for creating appropriate data fetchers."""
    
    _fetchers = {}
    
    @classmethod
    def register_fetcher(cls, name, fetcher_class):
        """Register a data fetcher implementation."""
        cls._fetchers[name] = fetcher_class
    
    @classmethod
    def create_fetcher(cls, source):
        """Create a data fetcher for the given source."""
        if source not in cls._fetchers:
            raise ValueError(f"Unknown data source: {source}")
        
        fetcher_class = cls._fetchers[source]
        return fetcher_class()

# Register fetchers
DataFetcherFactory.register_fetcher('yfinance', YFinanceDataFetcher)
DataFetcherFactory.register_fetcher('alphavantage', AlphaVantageDataFetcher)
DataFetcherFactory.register_fetcher('polygon', PolygonDataFetcher)

# Use factory
fetcher = DataFetcherFactory.create_fetcher('yfinance')
data = fetcher.fetch('AAPL')
```

### Pattern 3: Strategy Pattern

Use for interchangeable algorithms.

```python
class CachingStrategy(ABC):
    """Base class for caching strategies."""
    
    @abstractmethod
    def should_cache(self, key, value):
        """Determine if value should be cached."""
        pass
    
    @abstractmethod
    def get_ttl(self, key, value):
        """Get TTL for cached value."""
        pass

class TimeBased CachingStrategy(CachingStrategy):
    """Cache everything with fixed TTL."""
    
    def should_cache(self, key, value):
        return True
    
    def get_ttl(self, key, value):
        return 3600  # 1 hour

class SizeBasedCachingStrategy(CachingStrategy):
    """Only cache small values."""
    
    def should_cache(self, key, value):
        size = len(str(value))
        return size < 10000  # Only cache < 10KB
    
    def get_ttl(self, key, value):
        return 1800  # 30 minutes

class CacheService:
    def __init__(self, strategy: CachingStrategy):
        self.strategy = strategy
        self.cache = {}
    
    def set(self, key, value):
        if self.strategy.should_cache(key, value):
            ttl = self.strategy.get_ttl(key, value)
            self.cache[key] = (value, time.time() + ttl)
    
    def get(self, key):
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                return value
        return None

# Use different strategies
time_cache = CacheService(TimeBasedCachingStrategy())
size_cache = CacheService(SizeBasedCachingStrategy())
```

### Pattern 4: Repository Pattern

Use for data access abstraction.

```python
class SessionRepository(ABC):
    """Abstract repository for session data."""
    
    @abstractmethod
    def save(self, session):
        pass
    
    @abstractmethod
    def find_by_id(self, session_id):
        pass
    
    @abstractmethod
    def find_by_user(self, user_id):
        pass
    
    @abstractmethod
    def delete(self, session_id):
        pass

class SQLAlchemySessionRepository(SessionRepository):
    """SQLAlchemy implementation of session repository."""
    
    def save(self, session):
        with db_manager.session_scope() as db_session:
            db_session.add(session)
            db_session.commit()
    
    def find_by_id(self, session_id):
        with db_manager.session_scope() as db_session:
            return db_session.query(Session).filter_by(id=session_id).first()
    
    def find_by_user(self, user_id):
        with db_manager.session_scope() as db_session:
            return db_session.query(Session).filter_by(user_id=user_id).all()
    
    def delete(self, session_id):
        with db_manager.session_scope() as db_session:
            session = db_session.query(Session).filter_by(id=session_id).first()
            if session:
                db_session.delete(session)
                db_session.commit()

# Service uses repository
class SessionService:
    def __init__(self, repository: SessionRepository):
        self.repository = repository
    
    def create_session(self, user_id, session_type):
        session = Session(user_id=user_id, session_type=session_type)
        self.repository.save(session)
        return session.id
```

### Pattern 5: Facade Pattern

Simplify complex subsystems.

```python
class ResearchWorkflowFacade:
    """
    Simplified interface for complex research workflow.
    
    Coordinates multiple services to execute research workflow.
    """
    
    def __init__(self):
        self.session_service = session_service
        self.research_service = research_service
        self.data_service = stock_data_service
        self.notification_service = notification_service
        self.tracker_service = tracker_service
    
    def execute_research_workflow(self, user_id, symbol):
        """Execute complete research workflow."""
        
        # 1. Create session
        session_id = self.session_service.create_session(
            session_type='stock_research',
            user_id=user_id,
            metadata={'symbol': symbol}
        )
        
        # 2. Fetch data
        data, error = self.data_service.fetch_historical_data(symbol, period='1y')
        if error:
            return None, error
        
        # 3. Save research
        research_id = self.research_service.save_research(
            session_id=session_id,
            content={'data': data.to_dict()},
            research_type='historical'
        )
        
        # 4. Track event
        self.tracker_service.track_event(
            user_id=user_id,
            event_type='research_completed',
            metadata={'session_id': session_id, 'symbol': symbol}
        )
        
        # 5. Send notification
        self.notification_service.create_notification(
            user_id=user_id,
            type='research_complete',
            message=f'Research completed for {symbol}'
        )
        
        return session_id, None

# Simple interface for complex workflow
facade = ResearchWorkflowFacade()
session_id, error = facade.execute_research_workflow('user-123', 'AAPL')
```

---

## Dependency Management

### Dependency Injection

**✅ GOOD - Constructor Injection**:
```python
class NotificationService:
    """Service with injected dependencies."""
    
    def __init__(self, 
                 db_manager,
                 email_service=None,
                 sms_service=None):
        self.db_manager = db_manager
        self.email_service = email_service
        self.sms_service = sms_service
    
    def send_notification(self, user_id, message):
        # Save to database
        notification = Notification(user_id=user_id, message=message)
        with self.db_manager.session_scope() as session:
            session.add(notification)
        
        # Send via email if available
        if self.email_service:
            self.email_service.send(user_id, message)

# Easy to test with mocks
mock_db = MockDBManager()
mock_email = MockEmailService()
service = NotificationService(mock_db, mock_email)
```

### Service Locator (Use Sparingly)

```python
class ServiceLocator:
    """Central registry for services."""
    
    _services = {}
    
    @classmethod
    def register(cls, name, service):
        """Register a service."""
        cls._services[name] = service
    
    @classmethod
    def get(cls, name):
        """Get a service."""
        if name not in cls._services:
            raise ValueError(f"Service not found: {name}")
        return cls._services[name]

# Register services at startup
ServiceLocator.register('session', session_service)
ServiceLocator.register('research', research_service)

# Use in services
class AnalysisService:
    def analyze(self, session_id):
        # Locate service when needed
        research_service = ServiceLocator.get('research')
        research = research_service.get_research(session_id)
        # Perform analysis...
```

---

## Testing Services

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch

class TestSessionService:
    """Unit tests for SessionService."""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager."""
        return Mock()
    
    @pytest.fixture
    def session_service(self, mock_db_manager):
        """Create service with mocked dependencies."""
        from common.services.persistence.session import SessionPersistenceService
        service = SessionPersistenceService()
        service.db_manager = mock_db_manager
        return service
    
    def test_create_session(self, session_service, mock_db_manager):
        """Test session creation."""
        # Arrange
        session_type = 'stock_research'
        user_id = 'user-123'
        
        # Act
        session_id = session_service.create_session(session_type, user_id)
        
        # Assert
        assert session_id is not None
        mock_db_manager.session_scope.assert_called_once()
    
    def test_get_session_not_found(self, session_service):
        """Test getting non-existent session."""
        # Act
        result = session_service.get_session('nonexistent', 'stock_research')
        
        # Assert
        assert result is None
```

### Integration Testing

```python
import pytest

class TestSessionServiceIntegration:
    """Integration tests for SessionService."""
    
    @pytest.fixture(scope='class')
    def setup_database(self):
        """Set up test database."""
        from common import initialize_timber
        initialize_timber(create_tables=True)
    
    def test_create_and_retrieve_session(self, setup_database):
        """Test creating and retrieving a session."""
        from common.services.persistence import session_service
        
        # Create session
        session_id = session_service.create_session(
            session_type='stock_research',
            user_id='test-user'
        )
        
        # Retrieve session
        session = session_service.get_session(session_id, 'stock_research')
        
        # Verify
        assert session is not None
        assert session.id == session_id
        assert session.user_id == 'test-user'
    
    def test_update_session(self, setup_database):
        """Test updating a session."""
        from common.services.persistence import session_service
        
        # Create
        session_id = session_service.create_session(
            session_type='stock_research',
            user_id='test-user',
            status='active'
        )
        
        # Update
        success = session_service.update_session(
            session_id,
            status='completed'
        )
        
        # Verify
        assert success is True
        session = session_service.get_session(session_id, 'stock_research')
        assert session.status == 'completed'
```

---

## Performance Considerations

### 1. Lazy Loading

```python
class StockDataService:
    """Service with lazy-loaded dependencies."""
    
    def __init__(self):
        self._yfinance_client = None
        self._alphavantage_client = None
    
    @property
    def yfinance_client(self):
        """Lazy-load yfinance client."""
        if self._yfinance_client is None:
            import yfinance as yf
            self._yfinance_client = yf
        return self._yfinance_client
    
    @property
    def alphavantage_client(self):
        """Lazy-load Alpha Vantage client."""
        if self._alphavantage_client is None:
            from alpha_vantage.timeseries import TimeSeries
            self._alphavantage_client = TimeSeries(key=config.ALPHA_VANTAGE_API_KEY)
        return self._alphavantage_client
    
    def fetch_data(self, symbol, source='yfinance'):
        # Only load the client actually needed
        if source == 'yfinance':
            return self.yfinance_client.download(symbol)
        else:
            return self.alphavantage_client.get_daily(symbol)
```

### 2. Connection Pooling

```python
from sqlalchemy.pool import QueuePool

class DatabaseService:
    """Service with connection pooling."""
    
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections
            pool_recycle=3600    # Recycle after 1 hour
        )
```

### 3. Caching

```python
from functools import lru_cache

class CompanyDataService:
    """Service with caching."""
    
    @lru_cache(maxsize=1000)
    def get_company_info(self, symbol):
        """Get company info with caching."""
        # Expensive operation
        return self._fetch_company_info(symbol)
    
    def _fetch_company_info(self, symbol):
        """Actual fetch (uncached)."""
        # API call...
        pass
```

### 4. Batch Operations

```python
class NotificationService:
    """Service with batch processing."""
    
    def send_notifications_batch(self, notifications):
        """Send multiple notifications efficiently."""
        
        # Group by channel
        email_notifications = [n for n in notifications if n.channel == 'email']
        sms_notifications = [n for n in notifications if n.channel == 'sms']
        
        # Send in batches
        if email_notifications:
            self.email_service.send_batch(email_notifications)
        
        if sms_notifications:
            self.sms_service.send_batch(sms_notifications)
```

---

## Common Patterns

### Pattern: Service with Caching

```python
class CachedSessionService:
    """Session service with integrated caching."""
    
    def __init__(self, cache_service):
        self.cache_service = cache_service
        self.repository = SessionRepository()
    
    def get_session(self, session_id):
        """Get session with caching."""
        # Try cache first
        cache_key = f"session:{session_id}"
        cached = self.cache_service.get(cache_key)
        
        if cached:
            return cached
        
        # Cache miss - fetch from database
        session = self.repository.find_by_id(session_id)
        
        if session:
            # Cache for future requests
            self.cache_service.set(cache_key, session, ttl=3600)
        
        return session
    
    def update_session(self, session_id, **updates):
        """Update session and invalidate cache."""
        # Update database
        success = self.repository.update(session_id, **updates)
        
        if success:
            # Invalidate cache
            cache_key = f"session:{session_id}"
            self.cache_service.delete(cache_key)
        
        return success
```

### Pattern: Service with Retry Logic

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    """Retry decorator for service methods."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

class StockDataService:
    """Service with retry logic."""
    
    @retry(max_attempts=3, delay=2)
    def fetch_stock_data(self, symbol):
        """Fetch stock data with automatic retry."""
        # API call that might fail
        return self._api_call(symbol)
```

### Pattern: Service with Circuit Breaker

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    """Circuit breaker for external services."""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker."""
        if self.state == 'OPEN':
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.failures >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise

class ExternalAPIService:
    """Service with circuit breaker."""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
    
    def fetch_data(self, symbol):
        """Fetch data with circuit breaker protection."""
        return self.circuit_breaker.call(self._fetch_data, symbol)
    
    def _fetch_data(self, symbol):
        # Actual API call
        pass
```

---

## Anti-Patterns to Avoid

### 1. God Service

**❌ Avoid**:
```python
class MegaService:
    """One service that does everything."""
    def create_user(self, ...): pass
    def authenticate_user(self, ...): pass
    def send_email(self, ...): pass
    def fetch_stock_data(self, ...): pass
    def generate_report(self, ...): pass
    # ... 100 more methods
```

**✅ Instead**:
```python
# Split into focused services
class UserService: pass
class AuthService: pass
class EmailService: pass
class StockDataService: pass
class ReportService: pass
```

### 2. Service Chain

**❌ Avoid**:
```python
# Service A calls Service B calls Service C calls Service D...
class ServiceA:
    def __init__(self):
        self.service_b = ServiceB()
    
    def do_something(self):
        return self.service_b.do_something()

class ServiceB:
    def __init__(self):
        self.service_c = ServiceC()
    
    def do_something(self):
        return self.service_c.do_something()
# ... and so on
```

**✅ Instead**:
```python
# Use facade or coordinator
class WorkflowCoordinator:
    def __init__(self, service_a, service_b, service_c):
        self.service_a = service_a
        self.service_b = service_b
        self.service_c = service_c
    
    def execute_workflow(self):
        result_a = self.service_a.step_one()
        result_b = self.service_b.step_two(result_a)
        result_c = self.service_c.step_three(result_b)
        return result_c
```

### 3. Anemic Services

**❌ Avoid**:
```python
class SessionService:
    """Service with no logic - just CRUD."""
    def create(self, data): pass
    def read(self, id): pass
    def update(self, id, data): pass
    def delete(self, id): pass
    # No business logic!
```

**✅ Instead**:
```python
class SessionService:
    """Service with business logic."""
    def create_research_session(self, user_id, symbol):
        # Business logic
        if not self.user_can_research(user_id):
            raise PermissionError()
        
        # Create session
        session = Session(user_id=user_id, symbol=symbol)
        
        # Initialize workflow
        self.initialize_research_workflow(session)
        
        return session
    
    def user_can_research(self, user_id):
        # Business rule
        return True
    
    def initialize_research_workflow(self, session):
        # Business logic
        pass
```

---

## Summary

### Key Takeaways

1. **Single Responsibility**: Each service has one clear purpose
2. **Modular Design**: Split services by domain/responsibility
3. **Dependency Injection**: Inject dependencies for testability
4. **Singleton When Needed**: Use for services requiring single instance
5. **Test Thoroughly**: Unit test with mocks, integration test with real DB
6. **Performance Matters**: Use caching, pooling, lazy loading
7. **Handle Failures**: Implement retry logic and circuit breakers

### Service Design Checklist

- [ ] Service has single, clear responsibility
- [ ] Dependencies are injected, not hard-coded
- [ ] Service is testable in isolation
- [ ] Error handling is implemented
- [ ] Performance considerations addressed
- [ ] Documentation and examples provided
- [ ] Unit tests written
- [ ] Integration tests written

### Next Steps

1. Review existing services for refactoring opportunities
2. Break down god services into focused modules
3. Add dependency injection where missing
4. Implement caching for expensive operations
5. Add circuit breakers for external services
6. Write comprehensive tests
7. Document service interfaces and usage

---

**For more information:**
- [Caching Strategies](04_caching_strategies.md)
- [Error Handling](05_error_handling.md)
- [Performance Optimization](06_performance_optimization.md)
- [System Architecture](../design_guides/01_system_architecture.md)

---

**Last Updated**: October 19, 2024  
**Version**: 0.2.0