# Persistence Layer

A comprehensive guide to Timber's persistence layer architecture, explaining how modular services, database management, and transaction handling work together to provide a robust, scalable data access layer.

---

## Executive Summary

Timber's **persistence layer** replaces traditional monolithic ORMs with a **modular service architecture**. Instead of one large data access layer, Timber provides specialized services for different domains (sessions, research, notifications, tracking). This architecture improves maintainability, testability, and allows applications to use only the services they need.

**Core Innovation:** Domain-specific services + centralized database management + automatic feature integration = Clean, maintainable, powerful persistence.

---

## Architecture Overview

### Traditional vs Timber Approach

#### Traditional Monolithic ORM

```
┌─────────────────────────────────────────────┐
│         Application Layer                    │
└─────────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────┐
│    Monolithic ORM / Data Access Layer       │
│                                             │
│  • All models                               │
│  • All queries                              │
│  • All business logic                       │
│  • Tightly coupled                          │
│  • Hard to test                             │
│  • Single responsibility for everything     │
└─────────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────┐
│            Database                          │
└─────────────────────────────────────────────┘
```

**Problems:**
- Everything in one place (God object anti-pattern)
- Hard to maintain and test
- Difficult to extend
- Tight coupling between domains
- No clear separation of concerns

#### Timber Modular Service Architecture

```
┌───────────────────────────────────────────────────────────┐
│                  Application Layer                         │
└───────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ↓               ↓               ↓
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Session        │ │  Research       │ │  Notification   │
│  Service        │ │  Service        │ │  Service        │
│                 │ │                 │ │                 │
│ • Sessions only │ │ • Research only │ │ • Notifs only   │
│ • Focused API   │ │ • Focused API   │ │ • Focused API   │
│ • Easy to test  │ │ • Easy to test  │ │ • Easy to test  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
            │               │               │
            └───────────────┼───────────────┘
                            ↓
┌───────────────────────────────────────────────────────────┐
│              Database Manager (Shared)                     │
│                                                            │
│  • Connection pooling                                      │
│  • Session management                                      │
│  • Transaction handling                                    │
│  • Feature orchestration                                   │
└───────────────────────────────────────────────────────────┘
                            │
                            ↓
┌───────────────────────────────────────────────────────────┐
│                    PostgreSQL                              │
└───────────────────────────────────────────────────────────┘
```

**Benefits:**
- Clear separation of concerns
- Each service has single responsibility
- Easy to test in isolation
- Can extend with new services
- Loose coupling between domains
- Shared infrastructure (connection pooling, transactions)

---

## Core Components

### 1. Database Manager

The **Database Manager** provides centralized connection and session management.

```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

class DatabaseManager:
    """
    Manages database connections, sessions, and transactions
    
    Responsibilities:
    - Connection pooling
    - Session lifecycle management
    - Transaction handling
    - Event hooks
    - Migration support
    """
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize database manager
        
        Args:
            database_url: SQLAlchemy database URL
            echo: Whether to log SQL statements
        """
        self.logger = logging.getLogger(__name__)
        self.database_url = database_url
        
        # Create engine with connection pooling
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,              # Maintain 20 connections
            max_overflow=40,           # Allow 40 more under load
            pool_timeout=30,           # Wait 30s for connection
            pool_recycle=3600,         # Recycle connections after 1h
            pool_pre_ping=True,        # Verify connections before use
            echo=echo,                 # Log SQL (disabled in production)
            echo_pool=False,           # Don't log pool events
            connect_args={
                'connect_timeout': 10,
                'application_name': 'timber'
            }
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Thread-local session for web apps
        self.ScopedSession = scoped_session(self.SessionLocal)
        
        # Register event listeners
        self._register_events()
        
        self.logger.info(f"DatabaseManager initialized with {database_url}")
    
    @contextmanager
    def session_scope(self):
        """
        Provide transactional scope around operations
        
        Usage:
            with db_manager.session_scope() as session:
                user = User(name="John")
                session.add(user)
                # Automatically commits on success
                # Automatically rolls back on error
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
            self.logger.debug("Transaction committed")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            session.close()
    
    def get_session(self):
        """
        Get a new session (caller responsible for closing)
        
        Note: Use session_scope() instead when possible
        """
        return self.SessionLocal()
    
    def create_all_tables(self, base):
        """
        Create all tables defined in models
        
        Args:
            base: SQLAlchemy declarative base
        """
        self.logger.info("Creating all tables")
        base.metadata.create_all(self.engine)
        self.logger.info("All tables created")
    
    def drop_all_tables(self, base):
        """
        Drop all tables (use with caution!)
        
        Args:
            base: SQLAlchemy declarative base
        """
        self.logger.warning("Dropping all tables")
        base.metadata.drop_all(self.engine)
        self.logger.warning("All tables dropped")
    
    def dispose(self):
        """
        Dispose of connection pool
        
        Call this on application shutdown
        """
        self.logger.info("Disposing database connections")
        self.engine.dispose()
    
    def _register_events(self):
        """Register SQLAlchemy event listeners"""
        
        # Log slow queries
        @event.listens_for(self.engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, 
                                         parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement,
                                        parameters, context, executemany):
            total_time = time.time() - context._query_start_time
            if total_time > 1.0:  # Log queries taking > 1s
                self.logger.warning(f"Slow query ({total_time:.2f}s): {statement}")
        
        # Connection pool monitoring
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            self.logger.debug("New database connection created")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            self.logger.debug("Connection checked out from pool")
    
    def get_pool_status(self):
        """
        Get current connection pool status
        
        Returns:
            dict: Pool statistics
        """
        pool = self.engine.pool
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'timeout': pool.timeout()
        }
    
    def health_check(self):
        """
        Check database connectivity
        
        Returns:
            bool: True if database is accessible
        """
        try:
            with self.session_scope() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
```

### 2. Base Service

All domain services inherit from a base service that provides common functionality:

```python
from abc import ABC
import logging
from typing import Optional, Dict, Any
from timber.common.models.base import db_manager
from timber.common import get_model

class BaseService(ABC):
    """
    Base class for all domain services
    
    Provides:
    - Database access
    - Model retrieval
    - Error handling
    - Logging
    - Feature orchestration
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize base service
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self.feature_orchestrator = FeatureOrchestrator()
    
    def _get_model(self, model_name: str):
        """
        Get model class from registry
        
        Args:
            model_name: Name of model
        
        Returns:
            SQLAlchemy model class
        """
        return get_model(model_name)
    
    def _handle_error(self, error: Exception, context: str, 
                     reraise: bool = True):
        """
        Handle service errors consistently
        
        Args:
            error: Exception that occurred
            context: Context description
            reraise: Whether to re-raise exception
        """
        error_msg = f"{context}: {error}"
        self.logger.error(error_msg, exc_info=True)
        
        if reraise:
            raise ServiceError(error_msg) from error
    
    def _before_insert(self, instance, model_config: dict):
        """
        Run before inserting record
        
        Hooks for:
        - Encryption
        - Validation
        - GDPR audit
        - Vector embedding generation
        """
        self.feature_orchestrator.before_insert(instance, model_config)
    
    def _after_query(self, instance, model_config: dict):
        """
        Run after querying record
        
        Hooks for:
        - Decryption
        - Caching
        """
        self.feature_orchestrator.after_query(instance, model_config)
    
    def _get_model_config(self, model_class) -> dict:
        """Get model configuration metadata"""
        return getattr(model_class, '__model_config__', {})


class ServiceError(Exception):
    """Base exception for service layer"""
    pass
```

### 3. Domain Services

Each domain service handles a specific area of the application:

#### Session Service

```python
class SessionService(BaseService):
    """
    Manages user sessions (research, trading, portfolio, etc.)
    
    Responsibilities:
    - Create/read/update/delete sessions
    - Track session lifecycle
    - Query sessions by user/type/status
    """
    
    def create_session(self, user_id: str, session_type: str, 
                      metadata: Optional[Dict] = None) -> str:
        """
        Create a new session
        
        Args:
            user_id: User ID
            session_type: Type of session (research, trading, etc.)
            metadata: Optional session metadata
        
        Returns:
            str: Session ID
        
        Raises:
            ServiceError: If creation fails
        """
        try:
            Session = self._get_model('Session')
            model_config = self._get_model_config(Session)
            
            with self.db.session_scope() as session:
                # Create instance
                new_session = Session(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    session_type=session_type,
                    status='active',
                    metadata=metadata or {},
                    created_at=datetime.utcnow()
                )
                
                # Apply features before insert
                self._before_insert(new_session, model_config)
                
                # Save to database
                session.add(new_session)
                session.commit()
                
                self.logger.info(f"Created session {new_session.id}")
                return new_session.id
        
        except Exception as e:
            self._handle_error(e, "Failed to create session")
    
    def get_session(self, session_id: str) -> Optional[Any]:
        """
        Get session by ID
        
        Args:
            session_id: Session ID
        
        Returns:
            Session instance or None
        """
        try:
            Session = self._get_model('Session')
            model_config = self._get_model_config(Session)
            
            with self.db.session_scope() as session:
                result = session.query(Session)\
                    .filter_by(id=session_id)\
                    .first()
                
                if result:
                    # Apply features after query
                    self._after_query(result, model_config)
                
                return result
        
        except Exception as e:
            self._handle_error(e, f"Failed to get session {session_id}")
    
    def get_user_sessions(self, user_id: str, 
                         session_type: Optional[str] = None,
                         status: Optional[str] = None,
                         limit: int = 100) -> List[Any]:
        """
        Get all sessions for a user
        
        Args:
            user_id: User ID
            session_type: Optional type filter
            status: Optional status filter
            limit: Maximum results
        
        Returns:
            List of session instances
        """
        try:
            Session = self._get_model('Session')
            model_config = self._get_model_config(Session)
            
            with self.db.session_scope() as session:
                query = session.query(Session)\
                    .filter_by(user_id=user_id)
                
                # Apply filters
                if session_type:
                    query = query.filter_by(session_type=session_type)
                if status:
                    query = query.filter_by(status=status)
                
                # Order and limit
                results = query\
                    .order_by(Session.created_at.desc())\
                    .limit(limit)\
                    .all()
                
                # Apply features to all results
                for result in results:
                    self._after_query(result, model_config)
                
                return results
        
        except Exception as e:
            self._handle_error(e, f"Failed to get sessions for user {user_id}")
    
    def update_session(self, session_id: str, 
                      status: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> bool:
        """
        Update session
        
        Args:
            session_id: Session ID
            status: New status (optional)
            metadata: New metadata (optional)
        
        Returns:
            bool: True if updated
        """
        try:
            Session = self._get_model('Session')
            
            with self.db.session_scope() as session:
                result = session.query(Session)\
                    .filter_by(id=session_id)\
                    .first()
                
                if not result:
                    return False
                
                # Update fields
                if status is not None:
                    result.status = status
                if metadata is not None:
                    result.metadata = metadata
                
                result.updated_at = datetime.utcnow()
                
                session.commit()
                self.logger.info(f"Updated session {session_id}")
                return True
        
        except Exception as e:
            self._handle_error(e, f"Failed to update session {session_id}")
    
    def complete_session(self, session_id: str, 
                        result: Optional[Dict] = None) -> bool:
        """
        Mark session as completed
        
        Args:
            session_id: Session ID
            result: Session result data
        
        Returns:
            bool: True if completed
        """
        metadata = {'result': result} if result else {}
        return self.update_session(
            session_id,
            status='completed',
            metadata=metadata
        )
    
    def delete_session(self, session_id: str, user_id: str, 
                      hard_delete: bool = False) -> bool:
        """
        Delete session (soft delete by default)
        
        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
            hard_delete: If True, permanently delete
        
        Returns:
            bool: True if deleted
        """
        try:
            Session = self._get_model('Session')
            
            with self.db.session_scope() as session:
                result = session.query(Session)\
                    .filter_by(id=session_id, user_id=user_id)\
                    .first()
                
                if not result:
                    return False
                
                if hard_delete:
                    # Permanent delete
                    session.delete(result)
                    self.logger.info(f"Hard deleted session {session_id}")
                else:
                    # Soft delete
                    result.status = 'deleted'
                    result.deleted_at = datetime.utcnow()
                    self.logger.info(f"Soft deleted session {session_id}")
                
                session.commit()
                return True
        
        except Exception as e:
            self._handle_error(e, f"Failed to delete session {session_id}")
```

#### Research Service

```python
class ResearchService(BaseService):
    """
    Manages research data and analysis results
    
    Responsibilities:
    - Save research data
    - Query research by session/user/type
    - Update research records
    - Search research content
    """
    
    def save_research(self, session_id: str, content: Dict,
                     research_type: str,
                     metadata: Optional[Dict] = None) -> str:
        """
        Save research data
        
        Args:
            session_id: Associated session ID
            content: Research content (JSON)
            research_type: Type of research
            metadata: Additional metadata
        
        Returns:
            str: Research ID
        """
        try:
            Research = self._get_model('ResearchData')
            model_config = self._get_model_config(Research)
            
            with self.db.session_scope() as session:
                research = Research(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    research_type=research_type,
                    content=content,
                    metadata=metadata or {},
                    created_at=datetime.utcnow()
                )
                
                # Apply features (encryption, vector embedding)
                self._before_insert(research, model_config)
                
                session.add(research)
                session.commit()
                
                self.logger.info(f"Saved research {research.id}")
                return research.id
        
        except Exception as e:
            self._handle_error(e, "Failed to save research")
    
    def get_research(self, research_id: str) -> Optional[Any]:
        """Get research by ID"""
        try:
            Research = self._get_model('ResearchData')
            model_config = self._get_model_config(Research)
            
            with self.db.session_scope() as session:
                result = session.query(Research)\
                    .filter_by(id=research_id)\
                    .first()
                
                if result:
                    self._after_query(result, model_config)
                
                return result
        
        except Exception as e:
            self._handle_error(e, f"Failed to get research {research_id}")
    
    def get_session_research(self, session_id: str,
                           research_type: Optional[str] = None) -> List[Any]:
        """Get all research for a session"""
        try:
            Research = self._get_model('ResearchData')
            model_config = self._get_model_config(Research)
            
            with self.db.session_scope() as session:
                query = session.query(Research)\
                    .filter_by(session_id=session_id)
                
                if research_type:
                    query = query.filter_by(research_type=research_type)
                
                results = query\
                    .order_by(Research.created_at.desc())\
                    .all()
                
                for result in results:
                    self._after_query(result, model_config)
                
                return results
        
        except Exception as e:
            self._handle_error(e, f"Failed to get research for session {session_id}")
```

---

## Transaction Management

### Simple Transactions

```python
# Services handle transactions automatically
session_id = session_service.create_session(
    user_id='user-123',
    session_type='research'
)
# Transaction automatically committed
```

### Complex Transactions

For operations spanning multiple services:

```python
from timber.common.models.base import db_manager

# Manual transaction control
with db_manager.session_scope() as db_session:
    # Multiple operations in single transaction
    Session = get_model('Session')
    Research = get_model('ResearchData')
    
    # Create session
    new_session = Session(...)
    db_session.add(new_session)
    
    # Create related research
    research = Research(
        session_id=new_session.id,
        ...
    )
    db_session.add(research)
    
    # Both committed together
    # Automatic rollback on error
```

### Nested Transactions

```python
with db_manager.session_scope() as session:
    # Outer transaction
    user = User(...)
    session.add(user)
    
    # Nested operations use same transaction
    session_id = session_service.create_session(
        user_id=user.id,
        session_type='research'
    )
    
    # All committed together
```

---

## Connection Pooling

### Pool Configuration

```python
# Optimized for production
engine = create_engine(
    database_url,
    poolclass=QueuePool,
    
    # Core pool
    pool_size=20,          # Always maintain 20 connections
    
    # Overflow
    max_overflow=40,       # Allow 40 additional under load
                          # Total max: 60 connections
    
    # Timeouts
    pool_timeout=30,       # Wait 30s for connection
    pool_recycle=3600,     # Recycle after 1 hour
    
    # Health checks
    pool_pre_ping=True,    # Verify before use
    
    # Connection args
    connect_args={
        'connect_timeout': 10,
        'application_name': 'timber',
        'options': '-c statement_timeout=30000'  # 30s query timeout
    }
)
```

### Monitoring Pool

```python
# Get pool statistics
stats = db_manager.get_pool_status()
print(f"Pool size: {stats['pool_size']}")
print(f"Checked out: {stats['checked_out']}")
print(f"Available: {stats['checked_in']}")
print(f"Overflow: {stats['overflow']}")

# Example output:
# Pool size: 20
# Checked out: 5
# Available: 15
# Overflow: 0
```

### Pool Tuning

```python
# For read-heavy workloads
pool_size = 30
max_overflow = 20

# For write-heavy workloads
pool_size = 15
max_overflow = 10

# For microservices (many instances)
pool_size = 5
max_overflow = 5

# Calculate total: (instances * (pool_size + max_overflow)) < DB max_connections
# Example: 10 instances * (5 + 5) = 100 connections < 200 max
```

---

## Query Optimization

### Eager Loading

```python
# Avoid N+1 queries
from sqlalchemy.orm import joinedload

with db_manager.session_scope() as session:
    # Bad: N+1 queries
    sessions = session.query(Session).all()
    for s in sessions:
        print(s.user.name)  # Separate query for each user!
    
    # Good: Single query with join
    sessions = session.query(Session)\
        .options(joinedload(Session.user))\
        .all()
    
    for s in sessions:
        print(s.user.name)  # No additional queries
```

### Batch Operations

```python
# Insert many records efficiently
with db_manager.session_scope() as session:
    # Bad: Individual inserts
    for item in items:
        session.add(Research(content=item))
        session.commit()  # Commit each one
    
    # Good: Batch insert
    research_objects = [
        Research(content=item) 
        for item in items
    ]
    session.bulk_save_objects(research_objects)
    session.commit()  # Single commit
```

### Pagination

```python
def get_paginated_sessions(page: int = 1, per_page: int = 20):
    """Efficient pagination"""
    Session = get_model('Session')
    
    with db_manager.session_scope() as session:
        query = session.query(Session)
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Paginated results
        results = query\
            .order_by(Session.created_at.desc())\
            .offset(offset)\
            .limit(per_page)\
            .all()
        
        # Total count (cached)
        total = query.count()
        
        return {
            'results': results,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
```

### Index Usage

```python
# Services use indexes automatically

# This query uses idx_user_symbol_time index
sessions = session.query(Session)\
    .filter_by(user_id='user-123')\
    .filter_by(symbol='AAPL')\
    .order_by(Session.created_at.desc())\
    .all()

# Verify index usage with EXPLAIN
result = session.execute(
    text("EXPLAIN SELECT * FROM sessions WHERE user_id = :uid"),
    {'uid': 'user-123'}
)
print(result.fetchall())
```

---

## Caching Strategy

### Service-Level Caching

```python
class SessionService(BaseService):
    """Session service with caching"""
    
    def __init__(self, db_manager, cache_service):
        super().__init__(db_manager)
        self.cache = cache_service
    
    def get_session(self, session_id: str):
        """Get session with caching"""
        # Try cache first
        cache_key = f"session:{session_id}"
        cached = self.cache.get(cache_key)
        
        if cached:
            self.logger.debug(f"Cache hit: {session_id}")
            return cached
        
        # Cache miss - query database
        self.logger.debug(f"Cache miss: {session_id}")
        session = self._query_session(session_id)
        
        if session:
            # Cache for 1 hour
            self.cache.set(cache_key, session, ttl=3600)
        
        return session
    
    def update_session(self, session_id: str, **kwargs):
        """Update and invalidate cache"""
        # Update database
        updated = self._update_session(session_id, **kwargs)
        
        # Invalidate cache
        cache_key = f"session:{session_id}"
        self.cache.delete(cache_key)
        
        return updated
```

### Multi-Level Caching

```
┌──────────────────────────────────────┐
│  1. Application Memory (L1)         │
│     • Fastest (nanoseconds)          │
│     • Instance-specific              │
│     • LRU eviction                   │
└──────────────────────────────────────┘
                │ miss
                ↓
┌──────────────────────────────────────┐
│  2. Redis (L2)                       │
│     • Fast (milliseconds)            │
│     • Shared across instances        │
│     • TTL-based expiration           │
└──────────────────────────────────────┘
                │ miss
                ↓
┌──────────────────────────────────────┐
│  3. PostgreSQL (L3)                  │
│     • Slower (10-100ms)              │
│     • Persistent                     │
│     • Source of truth                │
└──────────────────────────────────────┘
```

### Cache Invalidation

```python
# Cache invalidation strategies

# 1. Time-based (TTL)
cache.set('key', value, ttl=3600)  # Expire after 1 hour

# 2. Event-based (on update/delete)
def update_session(session_id, **kwargs):
    # Update DB
    session = _update_db(session_id, **kwargs)
    
    # Invalidate cache
    cache.delete(f"session:{session_id}")
    
    # Also invalidate related caches
    cache.delete(f"user_sessions:{session.user_id}")
    
    return session

# 3. Version-based
def get_cached_data(key, version):
    versioned_key = f"{key}:v{version}"
    return cache.get(versioned_key)
```

---

## Error Handling

### Service Errors

```python
class ServiceError(Exception):
    """Base service exception"""
    pass

class ValidationError(ServiceError):
    """Data validation failed"""
    pass

class NotFoundError(ServiceError):
    """Resource not found"""
    pass

class PermissionError(ServiceError):
    """User lacks permission"""
    pass

class DatabaseError(ServiceError):
    """Database operation failed"""
    pass
```

### Error Handling Pattern

```python
def create_session(self, user_id: str, session_type: str):
    """Create session with proper error handling"""
    try:
        # Validate inputs
        if not user_id:
            raise ValidationError("user_id is required")
        
        if session_type not in ['research', 'trading', 'portfolio']:
            raise ValidationError(f"Invalid session_type: {session_type}")
        
        # Business logic
        Session = self._get_model('Session')
        
        with self.db.session_scope() as session:
            new_session = Session(
                user_id=user_id,
                session_type=session_type
            )
            session.add(new_session)
            session.commit()
            
            return new_session.id
    
    except ValidationError:
        # Re-raise validation errors
        raise
    
    except SQLAlchemyError as e:
        # Database errors
        self.logger.error(f"Database error: {e}", exc_info=True)
        raise DatabaseError(f"Failed to create session: {e}")
    
    except Exception as e:
        # Unexpected errors
        self.logger.exception("Unexpected error in create_session")
        raise ServiceError(f"Unexpected error: {e}")
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class SessionService(BaseService):
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def create_session_with_retry(self, user_id: str, session_type: str):
        """Create session with automatic retry on transient errors"""
        return self.create_session(user_id, session_type)
```

---

## Testing Services

### Unit Tests

```python
import pytest
from unittest.mock import MagicMock, patch
from timber.common.services.persistence import SessionService

class TestSessionService:
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager"""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_db_manager):
        """Create service instance"""
        return SessionService(mock_db_manager)
    
    def test_create_session(self, service, mock_db_manager):
        """Test session creation"""
        # Setup mock
        mock_session = MagicMock()
        mock_db_manager.session_scope.return_value.__enter__.return_value = mock_session
        
        # Call service
        session_id = service.create_session(
            user_id='user-123',
            session_type='research'
        )
        
        # Verify
        assert session_id is not None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    def test_create_session_validation_error(self, service):
        """Test validation error handling"""
        with pytest.raises(ValidationError):
            service.create_session(
                user_id='',  # Invalid
                session_type='research'
            )
```

### Integration Tests

```python
@pytest.fixture(scope='module')
def test_db():
    """Setup test database"""
    test_db_url = 'postgresql://localhost/timber_test'
    
    # Initialize Timber
    initialize_timber(
        database_url=test_db_url,
        model_config_dirs=['./tests/fixtures/models']
    )
    
    yield
    
    # Cleanup
    db_manager.drop_all_tables()

def test_session_lifecycle(test_db):
    """Test complete session lifecycle"""
    from timber.common.services.persistence import session_service
    
    # CREATE
    session_id = session_service.create_session(
        user_id='test-user',
        session_type='research',
        metadata={'symbol': 'AAPL'}
    )
    
    assert session_id is not None
    
    # READ
    session = session_service.get_session(session_id)
    assert session is not None
    assert session.user_id == 'test-user'
    assert session.symbol == 'AAPL'
    
    # UPDATE
    updated = session_service.update_session(
        session_id,
        status='completed'
    )
    assert updated
    
    # VERIFY UPDATE
    session = session_service.get_session(session_id)
    assert session.status == 'completed'
    
    # DELETE
    deleted = session_service.delete_session(
        session_id,
        user_id='test-user',
        hard_delete=True
    )
    assert deleted
    
    # VERIFY DELETE
    session = session_service.get_session(session_id)
    assert session is None
```

---

## Performance Benchmarks

### Typical Operation Times

```
Operation                    Time (ms)    Notes
────────────────────────────────────────────────────
Simple INSERT                1-5         Single record
Batch INSERT (100)           10-20       Bulk insert
Simple SELECT by ID          1-2         Indexed
SELECT with JOIN             2-5         With relationship
Complex query (filters)      5-15        Multiple conditions
UPDATE single record         2-5         By ID
DELETE single record         2-5         By ID
Transaction (3 operations)   5-10        Atomic

With Caching:
────────────────────────────────────────────────────
Cache hit (Redis)            0.5-1       Very fast
Cache hit (Local)            < 0.1       Fastest
Cache miss + DB query        2-5         Add cache latency
```

---

## Best Practices

### 1. Use Context Managers

```python
# Good: Automatic cleanup
with db_manager.session_scope() as session:
    # Work with session
    pass

# Bad: Manual management
session = db_manager.get_session()
try:
    # Work with session
    session.commit()
finally:
    session.close()
```

### 2. Service Composition

```python
# Compose services for complex workflows
class WorkflowService:
    def __init__(self, session_service, research_service, notification_service):
        self.session = session_service
        self.research = research_service
        self.notification = notification_service
    
    def execute_research_workflow(self, user_id, symbol):
        # Create session
        session_id = self.session.create_session(
            user_id, 'research', {'symbol': symbol}
        )
        
        # Perform research
        research_id = self.research.save_research(
            session_id, content={...}
        )
        
        # Notify user
        self.notification.create_notification(
            user_id,
            'Research complete',
            {'research_id': research_id}
        )
        
        return session_id
```

### 3. Connection Pooling

```python
# Do: Reuse connections from pool
with db_manager.session_scope() as session:
    # Multiple operations use same connection
    result1 = session.query(Model1).all()
    result2 = session.query(Model2).all()

# Don't: Create new connections
for item in items:
    with db_manager.session_scope() as session:
        # New connection each time! Inefficient
        session.query(Model).filter_by(id=item).first()
```

### 4. Batch Operations

```python
# Good: Batch processing
items = [...]
with db_manager.session_scope() as session:
    for item in items:
        session.add(Model(data=item))
    session.commit()  # Single commit

# Bad: Individual commits
for item in items:
    with db_manager.session_scope() as session:
        session.add(Model(data=item))
        # Commits each one individually
```

### 5. Query Optimization

```python
# Use indexes
sessions = session.query(Session)\
    .filter_by(user_id='user-123')\  # Indexed
    .order_by(Session.created_at.desc())\  # Part of composite index
    .limit(10)\
    .all()

# Avoid SELECT *
sessions = session.query(Session.id, Session.status)\  # Select only needed columns
    .filter_by(user_id='user-123')\
    .all()

# Use query count efficiently
total = session.query(func.count(Session.id))\
    .filter_by(user_id='user-123')\
    .scalar()
```

---

## Summary

Timber's persistence layer provides:

1. **Modular Services:** Domain-specific services with single responsibilities
2. **Centralized Management:** Database connections and transactions handled centrally
3. **Connection Pooling:** Efficient connection reuse and management
4. **Transaction Control:** Automatic and manual transaction management
5. **Error Handling:** Consistent error handling across all services
6. **Caching:** Multi-level caching for performance
7. **Query Optimization:** Built-in optimizations and best practices
8. **Testability:** Easy to unit test and integration test

**Key Benefits:**
- Clean separation of concerns
- Easy to test and maintain
- Scalable architecture
- Consistent patterns
- Production-ready

---

## Next Steps

- **[System Architecture](01_system_architecture.md)** - Overall design
- **[Config-Driven Models](02_config_driven_models.md)** - Model factory
- **[Vector Integration](04_vector_integration.md)** - Semantic search
- **[Using Services How-To](../how_to/03_using_services.md)** - Practical guide

---

**Last Updated:** October 19, 2024  
**Version:** 0.2.0  
**Authors:** Timber Architecture Team