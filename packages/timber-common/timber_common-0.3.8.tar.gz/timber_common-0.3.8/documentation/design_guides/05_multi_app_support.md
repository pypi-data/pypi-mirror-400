# Multi-App Support

A comprehensive guide to building multiple applications on Timber's shared infrastructure, explaining how different applications can coexist, share resources, and maintain isolation while leveraging common services.

---

## Executive Summary

Timber is designed as a **shared library foundation** for the OakQuant ecosystem, enabling multiple applications (Canopy, Grove, and future apps) to leverage common infrastructure while maintaining clear data boundaries and application-specific features. This architecture reduces code duplication, ensures consistency, and accelerates new application development.

**Core Innovation:** Shared library + isolated data + application context = Multiple apps on one foundation.

---

## Vision: OakQuant Ecosystem

### The Ecosystem

```
┌─────────────────────────────────────────────────────────┐
│              OakQuant Ecosystem                          │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │  Canopy    │  │   Grove    │  │   Future Apps    │  │
│  │            │  │            │  │                  │  │
│  │ Trading    │  │ Research   │  │ • Portfolio      │  │
│  │ Platform   │  │ Platform   │  │ • Social         │  │
│  │            │  │            │  │ • Education      │  │
│  │ • Orders   │  │ • Analysis │  │ • News           │  │
│  │ • Alerts   │  │ • Reports  │  │ • Screener       │  │
│  │ • Charts   │  │ • Notes    │  │ • Backtesting    │  │
│  └────────────┘  └────────────┘  └──────────────────┘  │
│         │               │                │              │
│         └───────────────┴────────────────┘              │
│                         │                                │
│                         ↓                                │
│         ┌───────────────────────────────┐               │
│         │      Timber Library           │               │
│         │   (Shared Foundation)         │               │
│         │                               │               │
│         │ • Config-driven models        │               │
│         │ • Modular services            │               │
│         │ • Feature services            │               │
│         │ • Database management         │               │
│         │ • Vector search               │               │
│         │ • Encryption & GDPR           │               │
│         └───────────────────────────────┘               │
│                         │                                │
│                         ↓                                │
│         ┌───────────────────────────────┐               │
│         │   Shared Infrastructure       │               │
│         │                               │               │
│         │ • PostgreSQL (data)           │               │
│         │ • Redis (cache)               │               │
│         │ • Qdrant (vectors)            │               │
│         └───────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

### Applications

#### Canopy (Trading Platform)
- **Purpose:** Active trading and portfolio management
- **Features:** Order execution, alerts, real-time charts
- **User:** Active traders, day traders
- **Data:** Orders, positions, alerts, trading sessions

#### Grove (Research Platform)
- **Purpose:** Deep research and analysis
- **Features:** Company analysis, note-taking, research reports
- **User:** Long-term investors, researchers
- **Data:** Research sessions, analysis, notes, reports

#### Future Applications
- **Portfolio Manager:** Track multiple portfolios, performance
- **Social Trading:** Share ideas, follow traders
- **Education:** Learning modules, quizzes, certifications
- **News Aggregator:** Curated financial news
- **Stock Screener:** Advanced filtering and discovery
- **Backtesting:** Strategy testing with historical data

---

## Architecture Principles

### 1. Shared Library, Isolated Data

```
Application Layer:
┌──────────────────────────────────────────────────────┐
│ Each app has its own:                                │
│ • Flask/FastAPI application                          │
│ • UI/frontend                                        │
│ • Business logic                                     │
│ • API endpoints                                      │
└──────────────────────────────────────────────────────┘
                        │
                        ↓ imports Timber
┌──────────────────────────────────────────────────────┐
│ Timber Library (Shared):                             │
│ • Model factory                                      │
│ • Services layer                                     │
│ • Database manager                                   │
│ • Feature services                                   │
└──────────────────────────────────────────────────────┘
                        │
                        ↓
┌──────────────────────────────────────────────────────┐
│ Shared Database:                                     │
│                                                      │
│ Tables:                                              │
│ • users (shared)                                     │
│ • sessions (all apps, typed by session_type)        │
│ • canopy_orders (Canopy only)                       │
│ • grove_research (Grove only)                       │
│ • notifications (shared)                             │
└──────────────────────────────────────────────────────┘
```

### 2. Application Context

Each application has a context that determines behavior:

```python
# Application identifies itself to Timber
from timber.common import initialize_timber

initialize_timber(
    app_name='canopy',  # Application identifier
    model_config_dirs=[
        './timber/data/models',      # Shared models
        './canopy/data/models'        # Canopy-specific models
    ],
    database_url=os.getenv('DATABASE_URL')
)
```

### 3. Data Isolation via Session Types

```python
# Canopy creates trading sessions
session_id = session_service.create_session(
    user_id='user-123',
    session_type='trading',  # Canopy's type
    metadata={'order_id': 'order-456'}
)

# Grove creates research sessions
session_id = session_service.create_session(
    user_id='user-123',
    session_type='research',  # Grove's type
    metadata={'symbol': 'AAPL'}
)

# Services filter by session_type automatically
canopy_sessions = session_service.get_user_sessions(
    user_id='user-123',
    session_type='trading'  # Only Canopy sessions
)
```

---

## Model Organization

### Shared Models

Models used by all applications:

```yaml
# timber/data/models/shared/user_models.yaml
version: "1.0.0"
description: Shared user models

models:
  - name: User
    table_name: users
    description: User account (shared across all apps)
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
      
      - name: email
        type: String(255)
        unique: true
        nullable: false
      
      - name: username
        type: String(100)
        unique: true
        nullable: false
      
      - name: created_at
        type: DateTime
        default: utcnow
    
    # Used by all apps
    relationships:
      - name: canopy_sessions
        model: TradingSession
        type: one-to-many
        back_populates: user
      
      - name: grove_sessions
        model: ResearchSession
        type: one-to-many
        back_populates: user
```

```yaml
# timber/data/models/shared/notification_models.yaml
version: "1.0.0"

models:
  - name: Notification
    table_name: notifications
    description: Notifications (shared across all apps)
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
        foreign_key: users.id
        index: true
      
      - name: app_name
        type: String(50)
        index: true
        description: Which app created this (canopy, grove, etc)
      
      - name: notification_type
        type: String(50)
        nullable: false
      
      - name: title
        type: String(255)
        nullable: false
      
      - name: message
        type: Text
      
      - name: is_read
        type: Boolean
        default: false
      
      - name: created_at
        type: DateTime
        default: utcnow
```

### Application-Specific Models

Each app defines its own models:

```yaml
# canopy/data/models/trading_models.yaml
version: "1.0.0"
description: Canopy trading models
depends: ["user_models.yaml"]

models:
  - name: TradingSession
    table_name: trading_sessions
    description: Canopy trading sessions
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
        foreign_key: users.id
        index: true
      
      - name: session_type
        type: String(50)
        default: "trading"
        index: true
      
      - name: strategy
        type: String(100)
        description: Trading strategy used
      
      - name: metadata
        type: JSON
  
  - name: Order
    table_name: orders
    description: Trading orders (Canopy only)
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
        foreign_key: users.id
      
      - name: session_id
        type: String(36)
        foreign_key: trading_sessions.id
      
      - name: symbol
        type: String(10)
        nullable: false
        index: true
      
      - name: order_type
        type: String(20)
        nullable: false
      
      - name: quantity
        type: Integer
      
      - name: price
        type: Numeric(10, 2)
      
      - name: status
        type: String(20)
        default: "pending"
```

```yaml
# grove/data/models/research_models.yaml
version: "1.0.0"
description: Grove research models
depends: ["user_models.yaml"]

models:
  - name: ResearchSession
    table_name: research_sessions
    description: Grove research sessions
    
    vector_search:
      enabled: true
      content_field: notes
      embedding_model: BAAI/bge-small-en-v1.5
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
        foreign_key: users.id
        index: true
      
      - name: session_type
        type: String(50)
        default: "research"
        index: true
      
      - name: symbol
        type: String(10)
        index: true
      
      - name: notes
        type: Text
        description: Research notes
      
      - name: analysis
        type: JSON
  
  - name: ResearchReport
    table_name: research_reports
    description: Published research reports (Grove only)
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      
      - name: user_id
        type: String(36)
        foreign_key: users.id
      
      - name: session_id
        type: String(36)
        foreign_key: research_sessions.id
      
      - name: title
        type: String(255)
      
      - name: content
        type: Text
      
      - name: is_published
        type: Boolean
        default: false
```

---

## Service Usage Patterns

### Shared Service Instance

All apps use the same service instances:

```python
# canopy/app.py
from timber.common import initialize_timber
from timber.common.services.persistence import (
    session_service,
    notification_service,
    tracker_service
)

# Initialize Timber for Canopy
initialize_timber(
    app_name='canopy',
    model_config_dirs=[
        './timber/data/models/shared',
        './canopy/data/models'
    ]
)

# Use shared services with Canopy context
def create_trading_session(user_id: str, strategy: str):
    """Create Canopy trading session"""
    session_id = session_service.create_session(
        user_id=user_id,
        session_type='trading',  # Canopy's type
        metadata={
            'strategy': strategy,
            'app': 'canopy'
        }
    )
    
    # Track event
    tracker_service.track_event(
        user_id=user_id,
        event_type='trading_session_created',
        event_data={'session_id': session_id}
    )
    
    return session_id
```

```python
# grove/app.py
from timber.common import initialize_timber
from timber.common.services.persistence import (
    session_service,
    notification_service,
    tracker_service
)

# Initialize Timber for Grove
initialize_timber(
    app_name='grove',
    model_config_dirs=[
        './timber/data/models/shared',
        './grove/data/models'
    ]
)

# Use shared services with Grove context
def create_research_session(user_id: str, symbol: str):
    """Create Grove research session"""
    session_id = session_service.create_session(
        user_id=user_id,
        session_type='research',  # Grove's type
        metadata={
            'symbol': symbol,
            'app': 'grove'
        }
    )
    
    # Track event
    tracker_service.track_event(
        user_id=user_id,
        event_type='research_session_created',
        event_data={'session_id': session_id, 'symbol': symbol}
    )
    
    return session_id
```

### App-Specific Services

Apps can extend with custom services:

```python
# canopy/services/order_service.py
from timber.common.services.base import BaseService
from timber.common import get_model

class OrderService(BaseService):
    """Canopy-specific order management service"""
    
    def create_order(self, user_id: str, symbol: str, 
                    order_type: str, quantity: int, price: float):
        """Create trading order"""
        Order = self._get_model('Order')
        
        with self.db.session_scope() as session:
            order = Order(
                id=str(uuid.uuid4()),
                user_id=user_id,
                symbol=symbol,
                order_type=order_type,
                quantity=quantity,
                price=price,
                status='pending'
            )
            
            session.add(order)
            session.commit()
            
            return order.id
    
    def get_user_orders(self, user_id: str, status: str = None):
        """Get orders for user"""
        Order = self._get_model('Order')
        
        with self.db.session_scope() as session:
            query = session.query(Order).filter_by(user_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            
            return query.order_by(Order.created_at.desc()).all()

# Create instance
from timber.common.models.base import db_manager
order_service = OrderService(db_manager)
```

```python
# grove/services/report_service.py
from timber.common.services.base import BaseService
from timber.common import get_model

class ReportService(BaseService):
    """Grove-specific research report service"""
    
    def create_report(self, user_id: str, session_id: str,
                     title: str, content: str):
        """Create research report"""
        Report = self._get_model('ResearchReport')
        
        with self.db.session_scope() as session:
            report = Report(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                title=title,
                content=content,
                is_published=False
            )
            
            session.add(report)
            session.commit()
            
            return report.id
    
    def publish_report(self, report_id: str, user_id: str):
        """Publish research report"""
        Report = self._get_model('ResearchReport')
        
        with self.db.session_scope() as session:
            report = session.query(Report)\
                .filter_by(id=report_id, user_id=user_id)\
                .first()
            
            if report:
                report.is_published = True
                report.published_at = datetime.utcnow()
                session.commit()
                return True
            
            return False

# Create instance
from timber.common.models.base import db_manager
report_service = ReportService(db_manager)
```

---

## Data Isolation Strategies

### 1. Session Type Filtering

```python
# Each app filters by its session_type
class SessionService(BaseService):
    
    def get_app_sessions(self, user_id: str, app_name: str):
        """Get sessions for specific app"""
        Session = self._get_model('Session')
        
        # Map app to session types
        type_map = {
            'canopy': ['trading', 'paper_trading'],
            'grove': ['research', 'analysis'],
            'portfolio': ['portfolio_review', 'rebalance']
        }
        
        session_types = type_map.get(app_name, [])
        
        with self.db.session_scope() as session:
            return session.query(Session)\
                .filter(Session.user_id == user_id)\
                .filter(Session.session_type.in_(session_types))\
                .all()
```

### 2. Application Metadata

```python
# Add app context to all records
def create_with_app_context(model_class, app_name: str, **kwargs):
    """Create record with app metadata"""
    if not hasattr(kwargs, 'metadata'):
        kwargs['metadata'] = {}
    
    kwargs['metadata']['app'] = app_name
    kwargs['metadata']['created_by_app'] = app_name
    
    return model_class(**kwargs)

# Usage
order = create_with_app_context(
    Order,
    app_name='canopy',
    user_id='user-123',
    symbol='AAPL'
)
```

### 3. Separate Tables

```python
# Apps can have completely separate tables
# Canopy:
#   - orders
#   - trading_sessions
#   - alerts

# Grove:
#   - research_reports
#   - research_sessions
#   - notes

# No overlap, clear separation
```

### 4. Row-Level Security (PostgreSQL)

```sql
-- Enable row-level security
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Create policy for Canopy
CREATE POLICY canopy_sessions_policy ON sessions
    FOR ALL
    USING (session_type IN ('trading', 'paper_trading'));

-- Create policy for Grove
CREATE POLICY grove_sessions_policy ON sessions
    FOR ALL
    USING (session_type IN ('research', 'analysis'));

-- Application sets role before queries
SET ROLE canopy_app;
-- Now can only see Canopy sessions
```

---

## Cross-App Features

### Shared Notifications

```python
# Canopy creates notification
notification_service.create_notification(
    user_id='user-123',
    notification_type='order_filled',
    title='Order Filled',
    message='Your AAPL order has been filled',
    data={'app': 'canopy', 'order_id': 'order-456'}
)

# Grove creates notification
notification_service.create_notification(
    user_id='user-123',
    notification_type='research_complete',
    title='Research Complete',
    message='Your AAPL analysis is ready',
    data={'app': 'grove', 'report_id': 'report-789'}
)

# User sees all notifications from all apps
notifications = notification_service.get_user_notifications(
    user_id='user-123',
    unread_only=True
)

# Each notification includes 'app' context
for notif in notifications:
    app = notif.data.get('app')
    print(f"[{app}] {notif.title}: {notif.message}")
```

### Cross-App Analytics

```python
# Track user activity across all apps
def get_user_activity_summary(user_id: str):
    """Get activity across all apps"""
    
    # Get sessions from all apps
    all_sessions = session_service.get_user_sessions(user_id)
    
    # Group by app/type
    summary = {
        'canopy': {
            'trading': len([s for s in all_sessions if s.session_type == 'trading']),
            'paper_trading': len([s for s in all_sessions if s.session_type == 'paper_trading'])
        },
        'grove': {
            'research': len([s for s in all_sessions if s.session_type == 'research']),
            'analysis': len([s for s in all_sessions if s.session_type == 'analysis'])
        },
        'total': len(all_sessions)
    }
    
    return summary
```

### Unified Search

```python
# Search across all apps
from timber.common.services.vector import vector_service

def unified_search(user_id: str, query: str):
    """Search across all app data"""
    results = []
    
    # Search Canopy orders
    canopy_results = vector_service.search(
        query=query,
        collection_name='orders',
        filter_dict={'user_id': user_id},
        limit=10
    )
    results.extend([{**r, 'app': 'canopy'} for r in canopy_results])
    
    # Search Grove research
    grove_results = vector_service.search(
        query=query,
        collection_name='research_reports',
        filter_dict={'user_id': user_id},
        limit=10
    )
    results.extend([{**r, 'app': 'grove'} for r in grove_results])
    
    # Sort by relevance
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results[:20]
```

---

## Configuration Management

### Environment Variables

```bash
# .env file (shared by all apps)

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/oakquant

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector Database
QDRANT_URL=http://localhost:6333

# Feature Flags
ENABLE_ENCRYPTION=true
ENABLE_VECTOR_SEARCH=true
ENABLE_GDPR=true

# App-specific
CANOPY_API_KEY=canopy-key-123
GROVE_API_KEY=grove-key-456
```

### Application Configuration

```python
# canopy/config.py
import os
from timber.common.utils.config import TimberConfig

class CanopyConfig(TimberConfig):
    """Canopy-specific configuration"""
    
    # App identity
    APP_NAME = 'canopy'
    APP_VERSION = '1.0.0'
    
    # Model directories
    MODEL_DIRS = [
        './timber/data/models/shared',
        './canopy/data/models'
    ]
    
    # Canopy-specific settings
    ENABLE_PAPER_TRADING = os.getenv('ENABLE_PAPER_TRADING', 'true').lower() == 'true'
    ENABLE_REAL_TRADING = os.getenv('ENABLE_REAL_TRADING', 'false').lower() == 'true'
    ORDER_CONFIRMATION_REQUIRED = True
    
    # Brokerage APIs
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

# grove/config.py
class GroveConfig(TimberConfig):
    """Grove-specific configuration"""
    
    # App identity
    APP_NAME = 'grove'
    APP_VERSION = '1.0.0'
    
    # Model directories
    MODEL_DIRS = [
        './timber/data/models/shared',
        './grove/data/models'
    ]
    
    # Grove-specific settings
    ENABLE_PUBLIC_REPORTS = os.getenv('ENABLE_PUBLIC_REPORTS', 'true').lower() == 'true'
    ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'
    MAX_REPORT_LENGTH = 50000
    
    # AI APIs
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

---

## Deployment Architecture

### Single Database, Multiple Apps

```
┌─────────────────────────────────────────────────────┐
│               Load Balancer                          │
└─────────────────────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         ↓                     ↓
┌─────────────────┐   ┌─────────────────┐
│  Canopy App     │   │  Grove App      │
│  (3 instances)  │   │  (2 instances)  │
│                 │   │                 │
│  • Flask/FastAPI│   │  • Flask/FastAPI│
│  • Imports      │   │  • Imports      │
│    Timber       │   │    Timber       │
└─────────────────┘   └─────────────────┘
         │                     │
         └──────────┬──────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────────┐
│           Shared Infrastructure                      │
│                                                      │
│  ┌───────────────┐  ┌──────────┐  ┌──────────────┐│
│  │  PostgreSQL   │  │  Redis   │  │   Qdrant     ││
│  │  (Primary)    │  │ (Cache)  │  │  (Vectors)   ││
│  └───────────────┘  └──────────┘  └──────────────┘│
└─────────────────────────────────────────────────────┘
```

### Scaling Considerations

```python
# Connection pool sizing
# Each instance needs connections
# Total = (canopy_instances + grove_instances) * pool_size

# Example:
canopy_instances = 3
grove_instances = 2
pool_size_per_instance = 10
max_overflow_per_instance = 5

total_max_connections = (
    (canopy_instances + grove_instances) * 
    (pool_size_per_instance + max_overflow_per_instance)
)

# total_max_connections = (3 + 2) * (10 + 5) = 75
# Ensure PostgreSQL max_connections > 75 (e.g., 100)
```

---

## Testing Multi-App Setup

### Integration Testing

```python
import pytest
from timber.common import initialize_timber

@pytest.fixture(scope='module')
def canopy_setup():
    """Setup Timber for Canopy"""
    initialize_timber(
        app_name='canopy',
        model_config_dirs=[
            './tests/fixtures/models/shared',
            './tests/fixtures/models/canopy'
        ],
        database_url='postgresql://localhost/timber_test'
    )

@pytest.fixture(scope='module')
def grove_setup():
    """Setup Timber for Grove"""
    initialize_timber(
        app_name='grove',
        model_config_dirs=[
            './tests/fixtures/models/shared',
            './tests/fixtures/models/grove'
        ],
        database_url='postgresql://localhost/timber_test'
    )

def test_canopy_sessions(canopy_setup):
    """Test Canopy session creation"""
    from timber.common.services.persistence import session_service
    
    session_id = session_service.create_session(
        user_id='test-user',
        session_type='trading',
        metadata={'app': 'canopy'}
    )
    
    assert session_id is not None

def test_grove_sessions(grove_setup):
    """Test Grove session creation"""
    from timber.common.services.persistence import session_service
    
    session_id = session_service.create_session(
        user_id='test-user',
        session_type='research',
        metadata={'app': 'grove'}
    )
    
    assert session_id is not None

def test_data_isolation(canopy_setup, grove_setup):
    """Test that apps can't see each other's sessions"""
    from timber.common.services.persistence import session_service
    
    # Canopy creates session
    canopy_session = session_service.create_session(
        user_id='test-user',
        session_type='trading'
    )
    
    # Grove creates session
    grove_session = session_service.create_session(
        user_id='test-user',
        session_type='research'
    )
    
    # Get Canopy sessions
    canopy_sessions = session_service.get_user_sessions(
        user_id='test-user',
        session_type='trading'
    )
    
    # Should only see Canopy session
    assert len(canopy_sessions) == 1
    assert canopy_sessions[0].id == canopy_session
    
    # Get Grove sessions
    grove_sessions = session_service.get_user_sessions(
        user_id='test-user',
        session_type='research'
    )
    
    # Should only see Grove session
    assert len(grove_sessions) == 1
    assert grove_sessions[0].id == grove_session
```

---

## Adding a New Application

### Step-by-Step Guide

#### 1. Create Application Structure

```bash
# Create new app directory
mkdir -p myapp/data/models
mkdir -p myapp/services
mkdir -p myapp/api

# Create files
touch myapp/__init__.py
touch myapp/app.py
touch myapp/config.py
touch myapp/data/models/myapp_models.yaml
```

#### 2. Define Models

```yaml
# myapp/data/models/myapp_models.yaml
version: "1.0.0"
description: MyApp models
depends: ["user_models.yaml"]

models:
  - name: MyAppSession
    table_name: myapp_sessions
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
      
      - name: user_id
        type: String(36)
        foreign_key: users.id
        index: true
      
      - name: session_type
        type: String(50)
        default: "myapp"
        index: true
      
      - name: data
        type: JSON
      
      - name: created_at
        type: DateTime
        default: utcnow
```

#### 3. Configure Application

```python
# myapp/config.py
from timber.common.utils.config import TimberConfig

class MyAppConfig(TimberConfig):
    APP_NAME = 'myapp'
    APP_VERSION = '1.0.0'
    
    MODEL_DIRS = [
        './timber/data/models/shared',
        './myapp/data/models'
    ]
    
    # MyApp-specific settings
    MYAPP_FEATURE_ENABLED = True
```

#### 4. Initialize Timber

```python
# myapp/app.py
from flask import Flask
from timber.common import initialize_timber
from myapp.config import MyAppConfig

app = Flask(__name__)

# Initialize Timber
initialize_timber(
    app_name=MyAppConfig.APP_NAME,
    model_config_dirs=MyAppConfig.MODEL_DIRS,
    database_url=MyAppConfig.DATABASE_URL
)

# Import services
from timber.common.services.persistence import (
    session_service,
    notification_service
)

@app.route('/create-session', methods=['POST'])
def create_session():
    user_id = request.json['user_id']
    
    session_id = session_service.create_session(
        user_id=user_id,
        session_type='myapp',
        metadata={'app': 'myapp'}
    )
    
    return {'session_id': session_id}
```

#### 5. Create Custom Services

```python
# myapp/services/myapp_service.py
from timber.common.services.base import BaseService
from timber.common import get_model

class MyAppService(BaseService):
    """MyApp-specific service"""
    
    def do_myapp_thing(self, user_id: str):
        """MyApp business logic"""
        MyAppSession = self._get_model('MyAppSession')
        
        with self.db.session_scope() as session:
            # Your logic here
            pass
```

#### 6. Run Database Migrations

```bash
# Create migration for new tables
timber create-migration "add_myapp_tables"

# Apply migration
timber migrate
```

#### 7. Deploy

```bash
# Add to deployment configuration
# Update load balancer
# Configure monitoring
```

---

## Best Practices

### 1. Use Session Types

```python
# Good: Use session_type to separate data
session_service.create_session(
    user_id='user-123',
    session_type='myapp_feature',  # Clear identifier
    metadata={'app': 'myapp'}
)

# Query only your sessions
sessions = session_service.get_user_sessions(
    user_id='user-123',
    session_type='myapp_feature'
)
```

### 2. Namespace Tables

```yaml
# Good: Clear table naming
models:
  - name: MyAppData
    table_name: myapp_data  # Prefixed with app name

  - name: MyAppReport
    table_name: myapp_reports

# Avoid: Generic names
  - name: Data
    table_name: data  # Conflicts with other apps
```

### 3. Include App Context

```python
# Always include app identifier
metadata = {
    'app': 'myapp',
    'version': '1.0.0',
    'feature': 'reporting'
}

session_service.create_session(
    user_id='user-123',
    session_type='myapp',
    metadata=metadata
)
```

### 4. Share Carefully

```python
# Good: Share via services
from timber.common.services.persistence import notification_service

notification_service.create_notification(
    user_id='user-123',
    notification_type='myapp_alert',
    title='MyApp Alert',
    data={'app': 'myapp', 'alert_id': 'alert-123'}
)

# Avoid: Direct database access to other app's tables
# Don't query canopy_orders from grove
```

### 5. Respect Boundaries

```python
# Good: Each app manages its own data
class MyAppService:
    def get_myapp_data(self, user_id: str):
        # Query MyApp tables only
        pass

# Avoid: Cross-app data access
class MyAppService:
    def get_canopy_orders(self, user_id: str):
        # Don't access other app's data directly
        # Use shared services or APIs instead
        pass
```

---

## Summary

Timber's multi-app support provides:

1. **Shared Foundation:** All apps use same library and infrastructure
2. **Data Isolation:** Clear boundaries via session types and table naming
3. **Consistent Services:** Same service interfaces across apps
4. **Easy Scaling:** Add new apps without modifying Timber
5. **Cross-App Features:** Shared notifications, analytics, search
6. **Independent Deployment:** Each app deploys independently
7. **Resource Efficiency:** Shared database, cache, vector store

**Key Benefits:**
- Rapid new application development
- Consistent patterns across ecosystem
- Reduced code duplication
- Shared infrastructure costs
- Unified user experience

---

## Next Steps

- **[System Architecture](01_system_architecture.md)** - Overall Timber design
- **[Config-Driven Models](02_config_driven_models.md)** - Model definitions
- **[Persistence Layer](03_persistence_layer.md)** - Database services
- **[Vector Integration](04_vector_integration.md)** - Semantic search

---

**Last Updated:** October 19, 2024  
**Version:** 0.2.0  
**Authors:** Timber Architecture Team