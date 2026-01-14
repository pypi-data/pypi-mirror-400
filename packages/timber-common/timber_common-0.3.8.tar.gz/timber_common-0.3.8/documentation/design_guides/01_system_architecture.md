# System Architecture

A comprehensive overview of Timber's architecture, design principles, and how components work together to provide a powerful, flexible foundation for the OakQuant ecosystem.

---

## Executive Summary

Timber is a **configuration-driven persistence and services library** that enables applications to define data models, services, and features through YAML files rather than writing boilerplate code. It provides a complete foundation for building research and analysis applications with built-in support for encryption, caching, vector search, GDPR compliance, and financial data fetching.

**Key Innovation:** Applications declare **what** they need (models, features, relationships) in YAML, and Timber handles **how** to implement it.

---

## Design Philosophy

### 1. Configuration Over Code

Traditional approach requires writing Python classes for every model:

```python
# Traditional: 50+ lines per model
class StockResearchSession(Base):
    __tablename__ = 'stock_research_sessions'
    id = Column(String(36), primary_key=True, default=uuid4)
    user_id = Column(String(36), ForeignKey('users.id'))
    symbol = Column(String(10), nullable=False)
    # ... 20+ more column definitions
    # ... relationship definitions
    # ... index definitions
    # ... method definitions
```

Timber approach uses declarative YAML:

```yaml
# Timber: Declarative, readable, maintainable
models:
  - name: StockResearchSession
    table_name: stock_research_sessions
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
      - name: symbol
        type: String(10)
        nullable: false
    encryption:
      enabled: true
      fields: [proprietary_analysis]
    caching:
      enabled: true
      ttl_seconds: 3600
```

**Benefits:**
- **Less Code:** 70% reduction in boilerplate
- **Easier Maintenance:** Change schema without touching Python
- **Version Control:** YAML diffs are human-readable
- **Application Agnostic:** Multiple apps share the same library
- **Feature Enablement:** Turn on encryption, caching, GDPR with one line

### 2. Modular Service Architecture

Instead of one monolithic ORM layer, Timber provides **specialized services**:

```
┌─────────────────────────────────────────────┐
│          Application Layer                   │
│   (Canopy, Grove, Future Apps)              │
└─────────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────┐
│          Timber Services Layer              │
├─────────────┬──────────────┬────────────────┤
│  Session    │  Research    │  Notification  │
│  Service    │  Service     │  Service       │
├─────────────┼──────────────┼────────────────┤
│  Tracker    │  Stock Data  │  Vector Search │
│  Service    │  Service     │  Service       │
└─────────────┴──────────────┴────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────┐
│     Dynamic Model Factory                   │
│   (Generates SQLAlchemy models from YAML)   │
└─────────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────┐
│     Database Layer (PostgreSQL)             │
└─────────────────────────────────────────────┘
```

Each service has a **single responsibility** and can be used independently or combined.

### 3. Extensibility Through Metadata

YAML model definitions include metadata that enables automatic feature provisioning:

```yaml
models:
  - name: UserData
    # Standard columns...
    
    # Metadata enables features automatically
    encryption:
      enabled: true
      fields: [ssn, bank_account]
    
    vector_search:
      enabled: true
      content_field: content
      embedding_model: BAAI/bge-small-en-v1.5
    
    gdpr:
      enabled: true
      user_id_field: user_id
      export_fields: [data, preferences]
    
    caching:
      enabled: true
      ttl_seconds: 3600
```

The system reads this metadata and automatically:
- Encrypts specified fields before storage
- Generates embeddings and enables semantic search
- Implements GDPR export/delete functionality
- Configures caching behavior

---

## High-Level Architecture

### Component Overview

```
┌───────────────────────────────────────────────────────────┐
│                    Application Layer                       │
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Canopy   │  │  Grove   │  │ Future   │               │
│  │ (Trading)│  │ (Research)│  │  Apps    │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└───────────────────────────────────────────────────────────┘
                         │
                         ↓ initialize_timber()
┌───────────────────────────────────────────────────────────┐
│                 Timber Core Library                        │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │         Model Factory & Registry                    │  │
│  │  • YAML Parser                                      │  │
│  │  • Dynamic SQLAlchemy Model Generator              │  │
│  │  • Model Registry (get_model())                    │  │
│  │  • Relationship Builder                            │  │
│  └────────────────────────────────────────────────────┘  │
│                         │                                  │
│  ┌─────────────────────┴────────────────────────────┐   │
│  │                                                    │   │
│  ┌──────────────────┐    ┌───────────────────────┐  │   │
│  │ Persistence      │    │ Data Services         │  │   │
│  │ Services         │    │                       │  │   │
│  │                  │    │ • Stock Data Service  │  │   │
│  │ • Session Svc    │    │ • Alpha Vantage       │  │   │
│  │ • Research Svc   │    │ • Yahoo Finance       │  │   │
│  │ • Notification   │    │ • Polygon.io          │  │   │
│  │ • Tracker Svc    │    │ • SEC Edgar           │  │   │
│  └──────────────────┘    └───────────────────────┘  │   │
│                                                       │   │
│  ┌──────────────────────────────────────────────────┴─┐ │
│  │           Cross-Cutting Services                    │ │
│  │                                                     │ │
│  │  ┌───────────┐  ┌──────────┐  ┌──────────────┐   │ │
│  │  │Encryption │  │ Caching  │  │Vector Search │   │ │
│  │  │Service    │  │Service   │  │Service       │   │ │
│  │  └───────────┘  └──────────┘  └──────────────┘   │ │
│  │                                                     │ │
│  │  ┌────────────┐  ┌──────────────────────────┐    │ │
│  │  │   GDPR     │  │    Database Manager      │    │ │
│  │  │  Service   │  │  (Connection, Sessions)  │    │ │
│  │  └────────────┘  └──────────────────────────┘    │ │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                      │
│                                                            │
│  ┌──────────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  PostgreSQL  │  │  Redis   │  │  Qdrant/Weaviate │   │
│  │  (Primary)   │  │ (Cache)  │  │ (Vector Store)   │   │
│  └──────────────┘  └──────────┘  └──────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

### Data Flow Example

**Scenario:** User creates a research session for AAPL stock

```
1. Application → Timber
   ────────────────────────────────────────────
   canopy.create_research_session(
       user_id='user-123',
       symbol='AAPL'
   )

2. Timber Session Service
   ────────────────────────────────────────────
   session_service.create_session(
       user_id='user-123',
       session_type='research',
       metadata={'symbol': 'AAPL'}
   )
   
3. Model Factory
   ────────────────────────────────────────────
   • Retrieves StockResearchSession model
   • Checks metadata for features:
     - Encryption: enabled ✓
     - Caching: enabled ✓
     - GDPR: enabled ✓

4. Feature Services (Automatic)
   ────────────────────────────────────────────
   a) Encryption Service
      • Identifies encrypted fields
      • Encrypts sensitive data
   
   b) Cache Service
      • Checks cache for existing data
      • Configures cache TTL
   
   c) Database Manager
      • Creates session
      • Inserts encrypted record
      • Commits transaction

5. Response to Application
   ────────────────────────────────────────────
   Returns: session_id = 'abc-123'
   
   Application continues with:
   - Fetch stock data
   - Perform analysis
   - Save research results
```

---

## Core Components

### 1. Model Factory

**Purpose:** Dynamically generate SQLAlchemy models from YAML configurations

**Key Features:**
- Parses YAML model definitions
- Creates SQLAlchemy model classes at runtime
- Handles relationships, indexes, constraints
- Registers models in global registry
- Validates configuration syntax

**Architecture:**

```python
class ModelFactory:
    """
    Factory for creating SQLAlchemy models from YAML config
    """
    
    def __init__(self):
        self.model_registry = {}  # name -> model class
        self.base = declarative_base()
    
    def load_from_yaml(self, yaml_path: str):
        """Parse YAML and create models"""
        config = self._parse_yaml(yaml_path)
        
        for model_config in config['models']:
            model_class = self._build_model(model_config)
            self._register_model(model_class)
    
    def _build_model(self, config: dict):
        """Build SQLAlchemy model from config"""
        # 1. Create class attributes dict
        attrs = {
            '__tablename__': config['table_name'],
            '__metadata__': config.get('metadata', {})
        }
        
        # 2. Add columns
        for col_config in config['columns']:
            attrs[col_config['name']] = self._build_column(col_config)
        
        # 3. Add relationships
        for rel_config in config.get('relationships', []):
            attrs[rel_config['name']] = self._build_relationship(rel_config)
        
        # 4. Create model class dynamically
        return type(config['name'], (self.base,), attrs)
```

**Why This Matters:**
- **Zero Python code** needed for new models
- **Consistent structure** across all models
- **Easy to extend** with new column types or features
- **Metadata-driven** feature enablement

### 2. Database Manager

**Purpose:** Manage database connections, sessions, and transactions

**Key Features:**
- Connection pooling
- Session lifecycle management
- Transaction handling
- Migration support
- Multi-database support

**Architecture:**

```python
class DatabaseManager:
    """
    Centralized database connection and session management
    """
    
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True  # Verify connections
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    @contextmanager
    def session_scope(self):
        """Provide transactional scope with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_all_tables(self):
        """Create all registered model tables"""
        Base.metadata.create_all(self.engine)
```

### 3. Service Layer

**Purpose:** Provide domain-specific business logic and data operations

**Service Pattern:**

Each service follows a consistent pattern:

```python
class BaseService:
    """Base class for all services"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _get_model(self, model_name: str):
        """Get model from registry"""
        return get_model(model_name)
    
    def _handle_error(self, error: Exception, context: str):
        """Centralized error handling"""
        self.logger.error(f"{context}: {error}")
        # Could integrate with monitoring here
        raise ServiceError(context) from error
```

**Service Specialization:**

```python
class SessionService(BaseService):
    """Manages user sessions (research, portfolio, etc.)"""
    
    def create_session(self, user_id: str, session_type: str, 
                      metadata: dict = None) -> str:
        """Create a new session"""
        Session = self._get_model('Session')
        
        with self.db.session_scope() as session:
            new_session = Session(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_type=session_type,
                metadata=metadata,
                status='active'
            )
            session.add(new_session)
            return new_session.id
```

### 4. Feature Services

**Purpose:** Provide cross-cutting functionality based on model metadata

#### Encryption Service

```python
class EncryptionService:
    """Handles field-level encryption"""
    
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)
    
    def encrypt_model_fields(self, model_instance, model_config: dict):
        """Encrypt fields marked in config"""
        encryption_config = model_config.get('encryption', {})
        
        if not encryption_config.get('enabled'):
            return
        
        for field in encryption_config.get('fields', []):
            value = getattr(model_instance, field)
            if value:
                encrypted = self.fernet.encrypt(value.encode())
                setattr(model_instance, field, encrypted.decode())
```

#### Cache Service

```python
class CacheService:
    """Manages caching based on model configuration"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.local_cache = {}  # Fallback
    
    def get_or_fetch(self, key: str, fetch_func: callable, 
                     ttl: int = None):
        """Get from cache or execute fetch function"""
        # Try cache first
        if self.redis:
            cached = self.redis.get(key)
            if cached:
                return json.loads(cached)
        
        # Fetch and cache
        result = fetch_func()
        if self.redis and ttl:
            self.redis.setex(key, ttl, json.dumps(result))
        
        return result
```

#### Vector Search Service

```python
class VectorSearchService:
    """Provides semantic search capabilities"""
    
    def __init__(self, vector_store_client):
        self.vector_store = vector_store_client
        self.embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    
    def ingest_document(self, model_instance, model_config: dict):
        """Auto-ingest content for vector search"""
        vector_config = model_config.get('vector_search', {})
        
        if not vector_config.get('enabled'):
            return
        
        content_field = vector_config['content_field']
        content = getattr(model_instance, content_field)
        
        # Generate embedding
        embedding = self.embedding_model.encode(content)
        
        # Store in vector database
        self.vector_store.upsert(
            collection=model_config['table_name'],
            id=model_instance.id,
            vector=embedding.tolist(),
            payload={'content': content}
        )
```

---

## Initialization Flow

When an application starts and calls `initialize_timber()`:

```
┌──────────────────────────────────────────────────┐
│  1. Application Startup                          │
│     from timber.common import initialize_timber  │
│     initialize_timber(                           │
│         model_config_dirs=['./data/models']      │
│     )                                            │
└──────────────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────┐
│  2. Configuration Loading                        │
│     • Read .env file                             │
│     • Parse database URLs                        │
│     • Load encryption keys                       │
│     • Configure feature flags                    │
└──────────────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────┐
│  3. Database Manager Initialization              │
│     • Create engine with connection pool         │
│     • Configure session factory                  │
│     • Test database connectivity                 │
└──────────────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────┐
│  4. Model Discovery & Loading                    │
│     • Scan model_config_dirs for YAML files      │
│     • Parse each YAML file                       │
│     • Resolve dependencies (depends field)       │
│     • Build dependency graph                     │
└──────────────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────┐
│  5. Model Factory Processing                     │
│     For each model config:                       │
│     • Generate SQLAlchemy model class            │
│     • Create columns with types & constraints    │
│     • Build relationships                        │
│     • Add indexes                                │
│     • Register in model registry                 │
└──────────────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────┐
│  6. Feature Service Initialization               │
│     • Initialize encryption service              │
│     • Connect to Redis (if enabled)              │
│     • Connect to vector store (if enabled)       │
│     • Set up GDPR compliance tools               │
└──────────────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────┐
│  7. Domain Service Initialization                │
│     • Create SessionService instance             │
│     • Create ResearchService instance            │
│     • Create NotificationService instance        │
│     • Create TrackerService instance             │
│     • Create StockDataService instance           │
└──────────────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────┐
│  8. Table Creation (if needed)                   │
│     • Check existing tables                      │
│     • Create missing tables                      │
│     • Run migrations (if configured)             │
└──────────────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────┐
│  9. Ready for Use                                │
│     • All services available                     │
│     • Models registered and queryable            │
│     • Features enabled based on config           │
└──────────────────────────────────────────────────┘
```

---

## Request Flow Example

**Complete flow for creating and querying a research session:**

```
USER ACTION: Create research session for AAPL
──────────────────────────────────────────────────

1. Application Layer (Canopy)
   ┌────────────────────────────────────────┐
   │ research_session = create_research(    │
   │     user_id='user-123',                │
   │     symbol='AAPL'                      │
   │ )                                      │
   └────────────────────────────────────────┘
                  │
                  ↓
2. Session Service
   ┌────────────────────────────────────────┐
   │ session_id = session_service.create(   │
   │     user_id='user-123',                │
   │     session_type='research',           │
   │     metadata={'symbol': 'AAPL'}        │
   │ )                                      │
   └────────────────────────────────────────┘
                  │
                  ↓
3. Model Registry
   ┌────────────────────────────────────────┐
   │ Session = get_model('Session')         │
   │ # Returns dynamically created class    │
   └────────────────────────────────────────┘
                  │
                  ↓
4. Feature Interception
   ┌────────────────────────────────────────┐
   │ Check model metadata:                  │
   │  • encryption.enabled = True           │
   │  • caching.enabled = True              │
   │  • gdpr.enabled = True                 │
   └────────────────────────────────────────┘
            │             │
            ↓             ↓
   ┌─────────────┐  ┌─────────────┐
   │ Encryption  │  │   Cache     │
   │  Service    │  │  Service    │
   │             │  │             │
   │ Encrypt     │  │ Generate    │
   │ sensitive   │  │ cache key   │
   │ fields      │  │             │
   └─────────────┘  └─────────────┘
                  │
                  ↓
5. Database Manager
   ┌────────────────────────────────────────┐
   │ with db.session_scope() as sess:       │
   │     new_session = Session(...)         │
   │     sess.add(new_session)              │
   │     sess.commit()                      │
   └────────────────────────────────────────┘
                  │
                  ↓
6. PostgreSQL
   ┌────────────────────────────────────────┐
   │ INSERT INTO sessions                   │
   │ VALUES (                               │
   │   'abc-123',                           │
   │   'user-123',                          │
   │   'research',                          │
   │   '{"symbol": "AAPL"}',                │
   │   'active',                            │
   │   '2024-10-19 ...'                     │
   │ )                                      │
   └────────────────────────────────────────┘
                  │
                  ↓
7. Post-Processing
   ┌────────────────────────────────────────┐
   │ • Cache the new session                │
   │ • Log GDPR audit trail                 │
   │ • Return session_id to application     │
   └────────────────────────────────────────┘
                  │
                  ↓
8. Application Layer
   ┌────────────────────────────────────────┐
   │ # Continue with research workflow      │
   │ fetch_stock_data(session_id, 'AAPL')   │
   │ perform_analysis(...)                  │
   │ save_results(...)                      │
   └────────────────────────────────────────┘
```

---

## Multi-Application Support

Timber is designed to support multiple applications in the OakQuant ecosystem:

```
┌─────────────────────────────────────────────────────┐
│              OakQuant Ecosystem                      │
│                                                      │
│  ┌───────────┐  ┌───────────┐  ┌────────────────┐ │
│  │  Canopy   │  │   Grove   │  │   Future Apps  │ │
│  │           │  │           │  │                │ │
│  │ Trading   │  │ Research  │  │  • Portfolio   │ │
│  │ Dashboard │  │ Platform  │  │  • Social      │ │
│  │           │  │           │  │  • Education   │ │
│  └───────────┘  └───────────┘  └────────────────┘ │
│         │              │                │           │
│         └──────────────┴────────────────┘           │
│                        │                             │
│                        ↓                             │
│         ┌──────────────────────────┐                │
│         │    Timber Library        │                │
│         │  (Shared Foundation)     │                │
│         └──────────────────────────┘                │
│                        │                             │
│                        ↓                             │
│         ┌──────────────────────────┐                │
│         │  Shared PostgreSQL DB    │                │
│         └──────────────────────────┘                │
└─────────────────────────────────────────────────────┘
```

**How It Works:**

1. **Shared Library:** All apps import Timber
2. **App-Specific Models:** Each app defines its own YAML models
3. **Shared Models:** Common models (User, Session) in Timber
4. **Isolated Data:** Apps use session_type to separate data
5. **Common Services:** All apps use same service layer

**Example:**

```yaml
# canopy/data/models/trading_models.yaml
models:
  - name: TradeOrder
    table_name: trade_orders
    session_type: trading  # Canopy-specific
    # ...

# grove/data/models/research_models.yaml
models:
  - name: ResearchReport
    table_name: research_reports
    session_type: research  # Grove-specific
    # ...
```

Both apps can use the same Timber services:

```python
# In Canopy
from timber.common.services.persistence import session_service

canopy_session = session_service.create_session(
    user_id='user-123',
    session_type='trading',  # Canopy's type
    metadata={'order_id': 'order-456'}
)

# In Grove
grove_session = session_service.create_session(
    user_id='user-123',
    session_type='research',  # Grove's type
    metadata={'symbol': 'AAPL'}
)
```

---

## Extensibility Points

Timber is designed to be extended without modifying core code:

### 1. Custom Column Types

```python
# Register custom type
from timber.common.models.factory import ModelFactory

factory = ModelFactory()
factory.register_type('MoneyAmount', Numeric(12, 2))

# Use in YAML
columns:
  - name: price
    type: MoneyAmount  # Custom type
```

### 2. Custom Services

```python
# Create your own service
from timber.common.services.base import BaseService

class PortfolioService(BaseService):
    def calculate_returns(self, portfolio_id: str):
        # Your logic here
        pass

# Use alongside Timber services
from timber.common.services.persistence import session_service
portfolio_service = PortfolioService(db_manager)
```

### 3. Model Hooks

```python
# Add lifecycle hooks to models
class AuditMixin:
    def before_insert(self):
        self.created_at = datetime.utcnow()
    
    def before_update(self):
        self.updated_at = datetime.utcnow()

# Apply via metadata
models:
  - name: AuditedModel
    mixins: [AuditMixin]
```

### 4. Custom Feature Services

```python
# Add your own feature service
class ComplianceService:
    def check_regulatory_compliance(self, model_instance):
        # Your compliance logic
        pass

# Register in model config
models:
  - name: Trade
    compliance:
      enabled: true
      rules: [finra, sec]
```

---

## Performance Considerations

### Connection Pooling

```python
# Optimized connection pool configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Connections to maintain
    max_overflow=40,        # Additional connections under load
    pool_recycle=3600,      # Recycle connections hourly
    pool_pre_ping=True,     # Verify connection health
    echo=False              # Disable SQL logging in prod
)
```

### Query Optimization

```python
# Services use efficient queries
class SessionService:
    def get_user_sessions(self, user_id: str, limit: int = 10):
        """Optimized query with eager loading"""
        Session = self._get_model('Session')
        
        with self.db.session_scope() as session:
            return session.query(Session)\
                .filter_by(user_id=user_id)\
                .options(joinedload(Session.research_data))\  # Eager load
                .order_by(Session.created_at.desc())\
                .limit(limit)\
                .all()
```

### Caching Strategy

```python
# Multi-level caching
1. Redis (distributed)    → Fast, shared across instances
2. Local memory           → Faster, instance-specific
3. Database               → Fallback

# Automatic cache invalidation on updates
def update_session(session_id: str, **kwargs):
    # Update database
    session = self._update_db(session_id, **kwargs)
    
    # Invalidate cache
    cache_service.delete(f"session:{session_id}")
    
    return session
```

---

## Security Architecture

### 1. Encryption at Rest

```python
# Field-level encryption for sensitive data
models:
  - name: UserPayment
    encryption:
      enabled: true
      fields: [card_number, cvv, ssn]

# Encrypted before storage, decrypted on retrieval
```

### 2. Connection Security

```python
# Use SSL for database connections
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"
```

### 3. Secrets Management

```python
# Never hardcode secrets
# Use environment variables
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
API_KEYS = os.getenv('API_KEYS')
```

### 4. GDPR Compliance

```python
# Automatic GDPR support
models:
  - name: UserData
    gdpr:
      enabled: true
      user_id_field: user_id
      export_fields: [email, name, preferences]

# Use GDPR service
from timber.common.services.gdpr import gdpr_service

# Export user data
gdpr_service.export_user_data('user-123')

# Delete user data
gdpr_service.delete_user_data('user-123')
```

---

## Error Handling Strategy

### Consistent Error Pattern

```python
# All services follow same error handling pattern

def create_session(self, user_id: str, ...):
    try:
        # Business logic
        session = self._create(...)
        return session.id
    
    except ValidationError as e:
        # Log and re-raise with context
        self.logger.error(f"Validation failed: {e}")
        raise ServiceError(f"Invalid session data: {e}")
    
    except DatabaseError as e:
        # Log and re-raise with context
        self.logger.error(f"Database error: {e}")
        raise ServiceError(f"Failed to create session: {e}")
    
    except Exception as e:
        # Catch-all for unexpected errors
        self.logger.exception("Unexpected error")
        raise ServiceError(f"Unexpected error: {e}")
```

### Error Types

```python
class ServiceError(Exception):
    """Base exception for service layer"""
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
```

---

## Testing Architecture

### Unit Tests

```python
# Test services in isolation
def test_session_service():
    # Mock database
    mock_db = MagicMock()
    
    # Create service with mock
    service = SessionService(mock_db)
    
    # Test behavior
    session_id = service.create_session(
        user_id='test-user',
        session_type='test'
    )
    
    assert session_id is not None
    mock_db.session_scope.assert_called_once()
```

### Integration Tests

```python
# Test with real database
@pytest.fixture(scope='module')
def test_db():
    # Create test database
    test_db_url = 'postgresql://localhost/timber_test'
    initialize_timber(
        database_url=test_db_url,
        model_config_dirs=['./tests/models']
    )
    yield
    # Cleanup

def test_full_workflow(test_db):
    # Test complete workflow
    session_id = session_service.create_session(...)
    research_id = research_service.save_research(...)
    notification_id = notification_service.create_notification(...)
    
    # Verify data consistency
    session = session_service.get_session(session_id)
    assert session.metadata['research_id'] == research_id
```

---

## Monitoring & Observability

### Logging Strategy

```python
# Structured logging throughout
import logging
import json

logger = logging.getLogger(__name__)

def log_event(event_type: str, data: dict):
    logger.info(json.dumps({
        'event': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        **data
    }))

# Usage in services
log_event('session_created', {
    'session_id': session_id,
    'user_id': user_id,
    'session_type': session_type
})
```

### Metrics

```python
# Track key metrics
class ServiceMetrics:
    def __init__(self):
        self.request_count = Counter('requests_total')
        self.request_duration = Histogram('request_duration_seconds')
        self.error_count = Counter('errors_total')
    
    def record_request(self, service: str, method: str, duration: float):
        self.request_count.labels(service=service, method=method).inc()
        self.request_duration.labels(service=service, method=method).observe(duration)
```

---

## Migration Strategy

### Schema Evolution

```python
# Use Alembic for migrations
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add new column
    op.add_column('sessions', 
        sa.Column('priority', sa.String(20), nullable=True)
    )
    
    # Update YAML config
    """
    models:
      - name: Session
        columns:
          - name: priority
            type: String(20)
            nullable: true
    """
```

### Backward Compatibility

```python
# Support old and new field names
class Session:
    @property
    def session_type(self):
        # New field name
        return self._session_type
    
    @property
    def type(self):
        # Old field name (deprecated)
        warnings.warn("Use session_type instead", DeprecationWarning)
        return self._session_type
```

---

## Summary

Timber provides a **powerful, flexible foundation** for the OakQuant ecosystem through:

1. **Configuration-Driven Models:** Define data models in YAML instead of Python
2. **Modular Services:** Specialized services for different domains
3. **Automatic Features:** Encryption, caching, vector search, GDPR from metadata
4. **Multi-App Support:** Shared library, isolated data, consistent interface
5. **Extensibility:** Add custom types, services, and features without core changes
6. **Production Ready:** Connection pooling, error handling, monitoring, security

**Key Benefits:**
- 70% less boilerplate code
- Consistent patterns across applications
- Easy to add new applications to ecosystem
- Features enabled declaratively
- Scales horizontally with minimal configuration

---

## Next Steps

- **[Config-Driven Models](02_config_driven_models.md)** - Deep dive into YAML model definitions
- **[Persistence Layer](03_persistence_layer.md)** - Understanding the database architecture
- **[Vector Integration](04_vector_integration.md)** - Semantic search capabilities
- **[Multi-App Support](05_multi_app_support.md)** - Building multiple applications on Timber

---

**Last Updated:** October 19, 2024  
**Version:** 0.2.0  
**Authors:** Timber Architecture Team