# Testing Guide for Timber

**Complete guide to testing models, services, and workflows in Timber**

---

## Table of Contents

1. [Overview](#overview)
2. [Test Setup](#test-setup)
3. [Testing Models](#testing-models)
4. [Testing Services](#testing-services)
5. [Testing Workflows](#testing-workflows)
6. [Integration Testing](#integration-testing)
7. [Performance Testing](#performance-testing)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers testing strategies for Timber-based applications, from unit tests for models to integration tests for complete workflows.

### Testing Philosophy

- **Test Early**: Write tests as you develop
- **Test Often**: Run tests on every change
- **Test Thoroughly**: Cover edge cases and error paths
- **Test Independently**: Each test should be isolated
- **Test Realistically**: Use realistic test data

### Test Types

| Type | Scope | Speed | When to Use |
|------|-------|-------|-------------|
| Unit | Single function/class | âš¡âš¡âš¡ | Always |
| Integration | Multiple components | âš¡âš¡ | Service interactions |
| End-to-End | Complete workflows | âš¡ | Critical paths |
| Performance | System load | âš¡ | Before releases |

---

## Test Setup

### Install Testing Dependencies

```bash
# Install pytest and plugins
pip install pytest pytest-cov pytest-mock pytest-asyncio

# Or with poetry
poetry add --group dev pytest pytest-cov pytest-mock pytest-asyncio

# Additional useful testing libraries
pip install faker factory-boy freezegun responses
```

### Project Structure

```
timber/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   │
│   ├── unit/                    # Unit tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   │
│   ├── integration/             # Integration tests
│   │   ├── test_persistence.py
│   │   ├── test_vector_search.py
│   │   └── test_workflows.py
│   │
│   ├── fixtures/                # Test data
│   │   ├── sample_data.py
│   │   └── sample_configs.yaml
│   │
│   └── performance/             # Performance tests
│       ├── test_bulk_operations.py
│       └── test_search_performance.py
│
├── pytest.ini                   # Pytest configuration
└── .coveragerc                  # Coverage configuration
```

### Pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Output options
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=timber
    --cov-report=html
    --cov-report=term-missing

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    performance: marks tests as performance tests

# Ignore warnings
filterwarnings =
    ignore::DeprecationWarning
```

### Test Configuration File

```python
# tests/conftest.py
"""
Shared test fixtures and configuration.
"""

import pytest
import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from timber.common import initialize_timber
from timber.common.models import Base
from timber.common.services.db_service import db_service
from timber.common.utils.config import config


# ============================================================================
# Session-level Fixtures (Run once per test session)
# ============================================================================

@pytest.fixture(scope='session')
def test_database_url():
    """Test database URL."""
    return os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')


@pytest.fixture(scope='session')
def initialize_timber_for_tests(test_database_url):
    """
    Initialize Timber once for all tests.
    """
    # Override database URL for tests
    config.DATABASE_URL = test_database_url
    
    # Initialize Timber
    initialize_timber(
        model_config_dirs=['data/models'],
        enable_encryption=True,
        enable_gdpr=True,
        enable_auto_vector_ingestion=False,  # Manual control in tests
        create_tables=True
    )
    
    # Create all tables
    Base.metadata.create_all(bind=db_service.engine)
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=db_service.engine)


# ============================================================================
# Function-level Fixtures (Run for each test function)
# ============================================================================

@pytest.fixture
def db_session(initialize_timber_for_tests) -> Generator[Session, None, None]:
    """
    Provide a database session for each test.
    Automatically rolls back after each test.
    """
    with db_service.session_scope() as session:
        yield session
        # Rollback happens automatically via session_scope


@pytest.fixture
def clean_database(db_session):
    """
    Clean all tables before each test.
    """
    # Delete all data from tables
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
    
    yield
    
    # Cleanup after test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    from timber.common.models import get_model
    
    User = get_model('User')
    
    user = User(
        user_id='test-user-123',
        email='test@example.com',
        username='testuser'
    )
    db_session.add(user)
    db_session.commit()
    
    yield user
    
    # Cleanup handled by clean_database


@pytest.fixture
def sample_research_session(db_session, sample_user):
    """Create a sample research session."""
    from timber.common.models import get_model
    
    ResearchSession = get_model('StockResearchSession')
    
    session = ResearchSession(
        user_id=sample_user.user_id,
        ticker='AAPL',
        state='initialized',
        config={'analysis_type': 'fundamental'}
    )
    db_session.add(session)
    db_session.commit()
    
    yield session


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_stock_data():
    """Mock stock data for testing."""
    import pandas as pd
    from datetime import datetime, timedelta
    
    dates = pd.date_range(
        end=datetime.now(),
        periods=30,
        freq='D'
    )
    
    data = pd.DataFrame({
        'Date': dates,
        'Open': 150 + np.random.randn(30) * 5,
        'High': 155 + np.random.randn(30) * 5,
        'Low': 145 + np.random.randn(30) * 5,
        'Close': 150 + np.random.randn(30) * 5,
        'Volume': 1000000 + np.random.randint(-100000, 100000, 30)
    })
    
    return data


@pytest.fixture
def mock_embedding_service(mocker):
    """Mock embedding service for testing."""
    mock = mocker.Mock()
    mock.generate_embedding.return_value = [0.1] * 384
    mock.generate_embeddings_batch.return_value = [[0.1] * 384] * 10
    return mock
```

---

## Testing Models

### Basic Model Tests

```python
# tests/unit/test_models.py
"""
Unit tests for Timber models.
"""

import pytest
from datetime import datetime
from timber.common.models import get_model


class TestUserModel:
    """Tests for User model."""
    
    def test_create_user(self, db_session):
        """Test creating a user."""
        User = get_model('User')
        
        user = User(
            user_id='test-123',
            email='test@example.com',
            username='testuser'
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify user was created
        retrieved = db_session.query(User)\
            .filter_by(user_id='test-123')\
            .first()
        
        assert retrieved is not None
        assert retrieved.email == 'test@example.com'
        assert retrieved.username == 'testuser'
    
    def test_user_timestamps(self, db_session):
        """Test that timestamps are set automatically."""
        User = get_model('User')
        
        user = User(
            user_id='test-123',
            email='test@example.com',
            username='testuser'
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Check timestamps
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at == user.updated_at
    
    def test_user_update_timestamp(self, db_session):
        """Test that updated_at changes on update."""
        import time
        
        User = get_model('User')
        
        user = User(
            user_id='test-123',
            email='test@example.com',
            username='testuser'
        )
        
        db_session.add(user)
        db_session.commit()
        
        original_updated_at = user.updated_at
        
        # Wait a moment
        time.sleep(0.1)
        
        # Update user
        user.email = 'updated@example.com'
        db_session.commit()
        
        # Check updated_at changed
        assert user.updated_at > original_updated_at
    
    def test_user_required_fields(self, db_session):
        """Test that required fields are enforced."""
        User = get_model('User')
        
        # Missing required field should raise error
        with pytest.raises(Exception):
            user = User(email='test@example.com')  # Missing user_id
            db_session.add(user)
            db_session.commit()


class TestResearchSessionModel:
    """Tests for ResearchSession model."""
    
    def test_create_research_session(self, db_session, sample_user):
        """Test creating a research session."""
        ResearchSession = get_model('StockResearchSession')
        
        session = ResearchSession(
            user_id=sample_user.user_id,
            ticker='AAPL',
            state='initialized',
            config={'analysis_type': 'fundamental'}
        )
        
        db_session.add(session)
        db_session.commit()
        
        # Verify session created
        assert session.id is not None
        assert session.ticker == 'AAPL'
        assert session.state == 'initialized'
    
    def test_session_state_transitions(self, db_session, sample_research_session):
        """Test state transitions."""
        session = sample_research_session
        
        # Transition to processing
        session.state = 'processing'
        db_session.commit()
        
        assert session.state == 'processing'
        
        # Transition to completed
        session.state = 'completed'
        db_session.commit()
        
        assert session.state == 'completed'
    
    def test_session_json_fields(self, db_session, sample_research_session):
        """Test JSON field storage and retrieval."""
        session = sample_research_session
        
        # Update config
        session.config = {
            'analysis_type': 'technical',
            'indicators': ['RSI', 'MACD'],
            'timeframe': '1D'
        }
        db_session.commit()
        
        # Retrieve and verify
        retrieved = db_session.query(type(session))\
            .filter_by(id=session.id)\
            .first()
        
        assert retrieved.config['analysis_type'] == 'technical'
        assert 'RSI' in retrieved.config['indicators']


class TestModelMixins:
    """Tests for model mixins."""
    
    def test_timestamp_mixin(self, db_session):
        """Test TimestampMixin functionality."""
        User = get_model('User')
        
        user = User(
            user_id='test-123',
            email='test@example.com',
            username='testuser'
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Check both timestamps exist
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_soft_delete_mixin(self, db_session):
        """Test SoftDeleteMixin functionality."""
        # Assuming User has SoftDeleteMixin
        User = get_model('User')
        
        user = User(
            user_id='test-123',
            email='test@example.com',
            username='testuser'
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Soft delete
        if hasattr(user, 'deleted_at'):
            user.deleted_at = datetime.now()
            db_session.commit()
            
            assert user.deleted_at is not None
```

### Model Relationship Tests

```python
class TestModelRelationships:
    """Tests for model relationships."""
    
    def test_user_research_sessions_relationship(self, db_session, sample_user):
        """Test User -> ResearchSessions relationship."""
        ResearchSession = get_model('StockResearchSession')
        
        # Create multiple sessions for user
        for ticker in ['AAPL', 'MSFT', 'GOOGL']:
            session = ResearchSession(
                user_id=sample_user.user_id,
                ticker=ticker,
                state='initialized'
            )
            db_session.add(session)
        
        db_session.commit()
        
        # Query user's sessions
        sessions = db_session.query(ResearchSession)\
            .filter_by(user_id=sample_user.user_id)\
            .all()
        
        assert len(sessions) == 3
        tickers = [s.ticker for s in sessions]
        assert 'AAPL' in tickers
        assert 'MSFT' in tickers
        assert 'GOOGL' in tickers
```

---

## Testing Services

### Service Unit Tests

```python
# tests/unit/test_services.py
"""
Unit tests for Timber services.
"""

import pytest
from timber.common.services.persistence import (
    session_service,
    notification_service,
    tracker_service
)


class TestSessionService:
    """Tests for SessionService."""
    
    def test_create_session(self, db_session, sample_user):
        """Test creating a session."""
        session_id = session_service.create_session(
            session_type='stock_research',
            user_id=sample_user.user_id,
            initial_state='initialized',
            config={'ticker': 'AAPL'}
        )
        
        assert session_id is not None
        
        # Verify session exists
        session = session_service.get_session(session_id, 'stock_research')
        assert session is not None
        assert session.user_id == sample_user.user_id
        assert session.state == 'initialized'
    
    def test_transition_state(self, db_session, sample_research_session):
        """Test state transition."""
        session_id = sample_research_session.id
        
        # Transition state
        success = session_service.transition_state(
            session_id,
            'stock_research',
            'processing'
        )
        
        assert success is True
        
        # Verify state changed
        session = session_service.get_session(session_id, 'stock_research')
        assert session.state == 'processing'
    
    def test_update_session_data(self, db_session, sample_research_session):
        """Test updating session data."""
        session_id = sample_research_session.id
        
        # Update data
        success = session_service.update_session_data(
            session_id,
            'stock_research',
            {'results': {'score': 0.85}}
        )
        
        assert success is True
        
        # Verify data updated
        session = session_service.get_session(session_id, 'stock_research')
        assert 'results' in session.data
        assert session.data['results']['score'] == 0.85


class TestNotificationService:
    """Tests for NotificationService."""
    
    def test_create_notification(self, db_session, sample_user):
        """Test creating a notification."""
        notification_id = notification_service.create_notification(
            user_id=sample_user.user_id,
            notification_type='info',
            title='Test Notification',
            message='This is a test message',
            data={'extra': 'data'}
        )
        
        assert notification_id is not None
        
        # Verify notification created
        notif = notification_service.get_notification(notification_id)
        assert notif is not None
        assert notif.title == 'Test Notification'
        assert notif.notification_type == 'info'
    
    def test_get_user_notifications(self, db_session, sample_user):
        """Test retrieving user notifications."""
        # Create multiple notifications
        for i in range(3):
            notification_service.create_notification(
                user_id=sample_user.user_id,
                notification_type='info',
                title=f'Notification {i}',
                message=f'Message {i}'
            )
        
        # Get notifications
        notifications = notification_service.get_user_notifications(
            sample_user.user_id,
            limit=10
        )
        
        assert len(notifications) == 3
    
    def test_mark_as_read(self, db_session, sample_user):
        """Test marking notification as read."""
        # Create notification
        notif_id = notification_service.create_notification(
            user_id=sample_user.user_id,
            notification_type='info',
            title='Test',
            message='Message'
        )
        
        # Mark as read
        success = notification_service.mark_as_read(notif_id)
        assert success is True
        
        # Verify marked
        notif = notification_service.get_notification(notif_id)
        assert notif.read is True
        assert notif.read_at is not None


class TestTrackerService:
    """Tests for TrackerService."""
    
    def test_track_event(self, db_session, sample_user):
        """Test tracking an event."""
        event_id = tracker_service.track_event(
            user_id=sample_user.user_id,
            event_type='page_view',
            event_data={'page': '/dashboard'}
        )
        
        assert event_id is not None
        
        # Verify event tracked
        event = tracker_service.get_event(event_id)
        assert event is not None
        assert event.event_type == 'page_view'
        assert event.event_data['page'] == '/dashboard'
    
    def test_get_user_events(self, db_session, sample_user):
        """Test retrieving user events."""
        # Track multiple events
        for i in range(5):
            tracker_service.track_event(
                user_id=sample_user.user_id,
                event_type='action',
                event_data={'action': f'action_{i}'}
            )
        
        # Get events
        events = tracker_service.get_user_events(
            sample_user.user_id,
            limit=10
        )
        
        assert len(events) == 5
```

### Service Integration Tests

```python
# tests/integration/test_service_integration.py
"""
Integration tests for service interactions.
"""

import pytest
from timber.common.services.persistence import persistence_manager


class TestServiceIntegration:
    """Tests for service integration."""
    
    def test_complete_research_workflow(self, db_session, sample_user):
        """Test complete research workflow using multiple services."""
        # 1. Create session
        session_id = persistence_manager.create_research_session(
            user_id=sample_user.user_id,
            ticker='AAPL',
            session_type='stock_research'
        )
        
        assert session_id is not None
        
        # 2. Track session start
        persistence_manager.track_event(
            user_id=sample_user.user_id,
            event_type='research_started',
            event_data={'session_id': session_id}
        )
        
        # 3. Update session with results
        persistence_manager.update_research_session(
            session_id,
            'stock_research',
            state='completed',
            data={'score': 0.85}
        )
        
        # 4. Create notification
        notification_id = persistence_manager.create_notification(
            user_id=sample_user.user_id,
            notification_type='success',
            title='Research Complete',
            message='AAPL analysis completed'
        )
        
        assert notification_id is not None
        
        # Verify entire workflow
        session = persistence_manager.get_research_session(
            session_id,
            'stock_research'
        )
        assert session.state == 'completed'
        assert session.data['score'] == 0.85
```

---

## Testing Workflows

### Workflow Tests

```python
# tests/integration/test_workflows.py
"""
Tests for complete workflows.
"""

import pytest
from timber.common.models import get_model
from timber.common.services.db_service import db_service


class TestStockResearchWorkflow:
    """Tests for stock research workflow."""
    
    def test_complete_stock_research_workflow(
        self,
        db_session,
        sample_user,
        mock_stock_data
    ):
        """Test complete stock research workflow."""
        # Import workflow components
        from your_app.workflows.stock_research import (
            initialize_research,
            fetch_data,
            analyze_data,
            generate_report,
            save_results
        )
        
        # 1. Initialize research
        session_id = initialize_research(
            user_id=sample_user.user_id,
            ticker='AAPL'
        )
        
        assert session_id is not None
        
        # 2. Fetch data (mocked)
        data = fetch_data('AAPL', session_id)
        assert data is not None
        
        # 3. Analyze data
        analysis = analyze_data(data, session_id)
        assert 'score' in analysis
        assert 0 <= analysis['score'] <= 1
        
        # 4. Generate report
        report = generate_report(analysis, session_id)
        assert report is not None
        assert 'summary' in report
        
        # 5. Save results
        success = save_results(session_id, report, analysis)
        assert success is True
        
        # Verify workflow completion
        ResearchSession = get_model('StockResearchSession')
        session = db_session.query(ResearchSession)\
            .filter_by(id=session_id)\
            .first()
        
        assert session.state == 'completed'
        assert session.data is not None


class TestPortfolioWorkflow:
    """Tests for portfolio management workflow."""
    
    def test_create_and_update_portfolio(self, db_session, sample_user):
        """Test portfolio creation and update."""
        from your_app.workflows.portfolio import (
            create_portfolio,
            add_position,
            update_position,
            calculate_returns
        )
        
        # Create portfolio
        portfolio_id = create_portfolio(
            user_id=sample_user.user_id,
            name='Test Portfolio'
        )
        
        assert portfolio_id is not None
        
        # Add positions
        position_id = add_position(
            portfolio_id,
            ticker='AAPL',
            shares=100,
            entry_price=150.0
        )
        
        assert position_id is not None
        
        # Update position
        success = update_position(
            position_id,
            shares=150,
            current_price=155.0
        )
        
        assert success is True
        
        # Calculate returns
        returns = calculate_returns(portfolio_id)
        assert returns is not None
        assert 'total_return' in returns
```

---

## Integration Testing

### Database Integration Tests

```python
# tests/integration/test_database.py
"""
Database integration tests.
"""

import pytest
from timber.common.services.db_service import db_service


class TestDatabaseIntegration:
    """Tests for database operations."""
    
    def test_database_connection(self, initialize_timber_for_tests):
        """Test database connection."""
        assert db_service.check_connection() is True
    
    def test_transaction_rollback(self, db_session, sample_user):
        """Test transaction rollback on error."""
        User = get_model('User')
        
        initial_count = db_session.query(User).count()
        
        # Attempt invalid operation
        with pytest.raises(Exception):
            with db_service.session_scope() as session:
                user = User(
                    user_id='test-456',
                    email='test2@example.com',
                    username='testuser2'
                )
                session.add(user)
                
                # Force error
                raise Exception("Test error")
        
        # Verify rollback
        final_count = db_session.query(User).count()
        assert final_count == initial_count
    
    def test_concurrent_sessions(self, initialize_timber_for_tests):
        """Test multiple concurrent database sessions."""
        from concurrent.futures import ThreadPoolExecutor
        
        User = get_model('User')
        
        def create_user(user_num):
            with db_service.session_scope() as session:
                user = User(
                    user_id=f'test-{user_num}',
                    email=f'test{user_num}@example.com',
                    username=f'testuser{user_num}'
                )
                session.add(user)
                session.commit()
                return user.user_id
        
        # Create users concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            user_ids = list(executor.map(create_user, range(10)))
        
        assert len(user_ids) == 10
        assert len(set(user_ids)) == 10  # All unique


### Vector Search Integration Tests

```python
# tests/integration/test_vector_search.py
"""
Vector search integration tests.
"""

import pytest
from timber.common.services.vector import (
    vector_search_service,
    vector_ingestion_service
)


class TestVectorSearchIntegration:
    """Tests for vector search integration."""
    
    def test_ingest_and_search(self, db_session, mock_embedding_service):
        """Test document ingestion and search."""
        # Replace embedding service with mock
        vector_ingestion_service.embedding_service = mock_embedding_service
        vector_search_service.embedding_service = mock_embedding_service
        
        # Ingest documents
        docs = [
            {
                'content': 'Apple shows strong revenue growth',
                'source_type': 'research_notes',
                'source_id': 'note-1',
                'metadata': {'ticker': 'AAPL'}
            },
            {
                'content': 'Microsoft Azure gaining market share',
                'source_type': 'research_notes',
                'source_id': 'note-2',
                'metadata': {'ticker': 'MSFT'}
            }
        ]
        
        results = vector_ingestion_service.ingest_documents_batch(docs)
        assert len(results) == 2
        
        # Search
        search_results = vector_search_service.search(
            query='cloud computing',
            source_type='research_notes',
            limit=10
        )
        
        assert len(search_results) > 0
    
    def test_search_with_filters(self, db_session, mock_embedding_service):
        """Test search with metadata filters."""
        vector_search_service.embedding_service = mock_embedding_service
        
        # Ingest with metadata
        vector_ingestion_service.ingest_document(
            content='Tech sector analysis',
            source_type='research_notes',
            source_id='note-1',
            metadata={'ticker': 'AAPL', 'sector': 'Technology'}
        )
        
        # Search with filters
        results = vector_search_service.search(
            query='analysis',
            source_type='research_notes',
            filters={'sector': 'Technology'},
            limit=10
        )
        
        assert all(r['metadata'].get('sector') == 'Technology' for r in results)
```

---

## Performance Testing

### Load Testing

```python
# tests/performance/test_performance.py
"""
Performance tests.
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor


@pytest.mark.performance
class TestPerformance:
    """Performance tests."""
    
    def test_bulk_insert_performance(self, db_session):
        """Test bulk insert performance."""
        User = get_model('User')
        
        # Measure bulk insert time
        start_time = time.time()
        
        users = [
            User(
                user_id=f'user-{i}',
                email=f'user{i}@example.com',
                username=f'user{i}'
            )
            for i in range(1000)
        ]
        
        db_session.bulk_save_objects(users)
        db_session.commit()
        
        duration = time.time() - start_time
        
        print(f"Bulk insert of 1000 users: {duration:.2f}s")
        assert duration < 5.0  # Should complete in < 5 seconds
    
    def test_search_performance(self, db_session, mock_embedding_service):
        """Test search performance."""
        vector_search_service.embedding_service = mock_embedding_service
        
        # Ingest 1000 documents
        docs = [
            {
                'content': f'Document {i} content',
                'source_type': 'research_notes',
                'source_id': f'doc-{i}',
                'metadata': {}
            }
            for i in range(1000)
        ]
        
        vector_ingestion_service.ingest_documents_batch(docs)
        
        # Measure search time
        start_time = time.time()
        
        results = vector_search_service.search(
            query='test query',
            source_type='research_notes',
            limit=10
        )
        
        duration = time.time() - start_time
        
        print(f"Search time: {duration:.3f}s")
        assert duration < 1.0  # Should complete in < 1 second
    
    def test_concurrent_requests(self, db_session):
        """Test concurrent request handling."""
        User = get_model('User')
        
        def create_and_query_user(user_num):
            with db_service.session_scope() as session:
                # Create user
                user = User(
                    user_id=f'concurrent-{user_num}',
                    email=f'concurrent{user_num}@example.com',
                    username=f'concurrent{user_num}'
                )
                session.add(user)
                session.commit()
                
                # Query user
                retrieved = session.query(User)\
                    .filter_by(user_id=f'concurrent-{user_num}')\
                    .first()
                
                return retrieved is not None
        
        # Execute concurrent requests
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(create_and_query_user, range(100)))
        
        duration = time.time() - start_time
        
        print(f"100 concurrent requests: {duration:.2f}s")
        assert all(results)  # All should succeed
        assert duration < 10.0  # Should complete in < 10 seconds
```

### Memory Testing

```python
@pytest.mark.performance
class TestMemoryUsage:
    """Memory usage tests."""
    
    def test_large_result_set_memory(self, db_session):
        """Test memory usage with large result sets."""
        import tracemalloc
        
        User = get_model('User')
        
        # Create large dataset
        users = [
            User(
                user_id=f'mem-test-{i}',
                email=f'memtest{i}@example.com',
                username=f'memtest{i}'
            )
            for i in range(10000)
        ]
        
        db_session.bulk_save_objects(users)
        db_session.commit()
        
        # Measure memory usage
        tracemalloc.start()
        
        # Query large result set
        all_users = db_session.query(User).all()
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
        
        assert peak / 1024 / 1024 < 100  # Should use < 100 MB
```

---

## Best Practices

### 1. Test Isolation

```python
# âœ… Good: Each test is isolated
def test_create_user(clean_database):
    """Clean database ensures isolation."""
    user = create_user('test-1')
    assert user is not None

def test_delete_user(clean_database):
    """Starts with clean database."""
    user = create_user('test-2')
    delete_user(user.user_id)
    assert get_user('test-2') is None

# â Bad: Tests depend on each other
def test_create_user():
    """Creates user."""
    create_user('test-1')

def test_delete_user():
    """Assumes user from previous test exists."""
    delete_user('test-1')  # â Fails if run alone
```

### 2. Use Fixtures for Common Setup

```python
# âœ… Good: Reusable fixture
@pytest.fixture
def research_with_data(sample_user):
    """Research session with sample data."""
    session = create_research_session(sample_user.user_id, 'AAPL')
    add_research_data(session.id, sample_data)
    return session

def test_analyze_research(research_with_data):
    results = analyze_research(research_with_data.id)
    assert results is not None

# â Bad: Repeated setup
def test_analyze_research():
    user = create_user()
    session = create_research_session(user.user_id, 'AAPL')
    add_research_data(session.id, sample_data)
    results = analyze_research(session.id)
```

### 3. Test Error Conditions

```python
def test_create_session_invalid_user():
    """Test error handling for invalid user."""
    with pytest.raises(ValueError, match="User not found"):
        session_service.create_session(
            session_type='stock_research',
            user_id='nonexistent',
            initial_state='initialized'
        )

def test_transition_to_invalid_state():
    """Test error handling for invalid state transition."""
    session = create_session()
    
    with pytest.raises(ValueError, match="Invalid state transition"):
        session_service.transition_state(
            session.id,
            'stock_research',
            'invalid_state'
        )
```

### 4. Use Parameterized Tests

```python
@pytest.mark.parametrize('ticker,expected_valid', [
    ('AAPL', True),
    ('MSFT', True),
    ('INVALID', False),
    ('', False),
    (None, False),
])
def test_validate_ticker(ticker, expected_valid):
    """Test ticker validation with multiple inputs."""
    result = validate_ticker(ticker)
    assert result == expected_valid
```

### 5. Mock External Dependencies

```python
def test_fetch_stock_data(mocker):
    """Test with mocked external API."""
    # Mock external API call
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        'symbol': 'AAPL',
        'price': 150.0
    }
    
    mocker.patch('requests.get', return_value=mock_response)
    
    # Test function
    data = fetch_stock_data('AAPL')
    assert data['price'] == 150.0
```

---

## Troubleshooting

### Common Issues

#### 1. Test Database Not Found

```python
# Problem: Test database doesn't exist

# Solution: Use in-memory database for tests
@pytest.fixture(scope='session')
def test_database_url():
    return 'sqlite:///:memory:'  # âœ… In-memory DB
```

#### 2. Tests Interfering with Each Other

```python
# Problem: Tests affecting each other's data

# Solution: Use clean_database fixture
def test_something(clean_database, db_session):
    """Database is clean at start of each test."""
    pass
```

#### 3. Slow Tests

```python
# Problem: Tests taking too long

# Solution 1: Use marks to skip slow tests during development
@pytest.mark.slow
def test_large_dataset():
    pass

# Run without slow tests:
# pytest -m "not slow"

# Solution 2: Use mocks for external services
def test_with_mocks(mock_stock_data):
    """Much faster than real API calls."""
    pass
```

#### 4. Fixture Not Found

```python
# Problem: pytest.fixture_not_found

# Solution: Ensure conftest.py is in correct location
# and fixture is defined at appropriate scope
```

---

## Complete Example

```python
# Complete testing example for a research workflow

import pytest
from datetime import datetime
from timber.common.models import get_model
from timber.common.services.persistence import persistence_manager


class TestCompleteResearchWorkflow:
    """Complete testing example."""
    
    @pytest.fixture
    def research_setup(self, clean_database, sample_user):
        """Setup research environment."""
        # Create test data
        data = {
            'user': sample_user,
            'ticker': 'AAPL',
            'config': {
                'analysis_type': 'fundamental',
                'timeframe': '1Y'
            }
        }
        yield data
        # Cleanup handled by clean_database
    
    def test_create_research_session(self, research_setup):
        """Test session creation."""
        session_id = persistence_manager.create_research_session(
            user_id=research_setup['user'].user_id,
            ticker=research_setup['ticker'],
            session_type='stock_research',
            config=research_setup['config']
        )
        
        assert session_id is not None
        
        # Verify session
        session = persistence_manager.get_research_session(
            session_id,
            'stock_research'
        )
        
        assert session.ticker == 'AAPL'
        assert session.state == 'initialized'
    
    def test_process_research(self, research_setup):
        """Test research processing."""
        # Create session
        session_id = persistence_manager.create_research_session(
            user_id=research_setup['user'].user_id,
            ticker=research_setup['ticker'],
            session_type='stock_research'
        )
        
        # Update to processing
        persistence_manager.update_research_session(
            session_id,
            'stock_research',
            state='processing',
            data={'progress': 0.5}
        )
        
        # Verify update
        session = persistence_manager.get_research_session(
            session_id,
            'stock_research'
        )
        
        assert session.state == 'processing'
        assert session.data['progress'] == 0.5
    
    def test_complete_workflow(self, research_setup, mock_stock_data):
        """Test complete workflow end-to-end."""
        # 1. Create session
        session_id = persistence_manager.create_research_session(
            user_id=research_setup['user'].user_id,
            ticker=research_setup['ticker'],
            session_type='stock_research'
        )
        
        # 2. Process data
        persistence_manager.update_research_session(
            session_id,
            'stock_research',
            state='processing'
        )
        
        # 3. Complete analysis
        persistence_manager.update_research_session(
            session_id,
            'stock_research',
            state='completed',
            data={
                'score': 0.85,
                'recommendation': 'buy'
            }
        )
        
        # 4. Create notification
        notif_id = persistence_manager.create_notification(
            user_id=research_setup['user'].user_id,
            notification_type='success',
            title='Research Complete',
            message=f"{research_setup['ticker']} analysis completed"
        )
        
        # Verify complete workflow
        session = persistence_manager.get_research_session(
            session_id,
            'stock_research'
        )
        
        assert session.state == 'completed'
        assert session.data['score'] == 0.85
        assert notif_id is not None
    
    def test_error_handling(self, research_setup):
        """Test error handling."""
        # Test invalid session type
        with pytest.raises(ValueError):
            persistence_manager.create_research_session(
                user_id=research_setup['user'].user_id,
                ticker=research_setup['ticker'],
                session_type='invalid_type'
            )
        
        # Test invalid state transition
        session_id = persistence_manager.create_research_session(
            user_id=research_setup['user'].user_id,
            ticker=research_setup['ticker'],
            session_type='stock_research'
        )
        
        with pytest.raises(ValueError):
            persistence_manager.update_research_session(
                session_id,
                'stock_research',
                state='invalid_state'
            )


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Summary

**Key Takeaways:**

âœ… **Comprehensive Coverage** - Unit, integration, and performance tests  
âœ… **Test Isolation** - Each test independent  
âœ… **Fixtures** - Reusable test setup  
âœ… **Mocking** - Fast tests with mocked dependencies  
âœ… **Parameterization** - Test multiple scenarios  
âœ… **Error Testing** - Cover edge cases  
âœ… **Performance** - Ensure scalability  

**Next Steps:**

1. Set up test environment
2. Create conftest.py with fixtures
3. Write unit tests for models
4. Add service tests
5. Create integration tests
6. Run coverage reports
7. Set up CI/CD testing

---

**Created:** October 19, 2025  
**Version:** 0.2.0  
**Word Count:** ~6,500 words  
**Status:** âœ… Complete