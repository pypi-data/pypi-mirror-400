# Config-Driven Models

A comprehensive guide to Timber's configuration-driven model architecture, explaining how YAML definitions become SQLAlchemy models and how the factory pattern enables powerful, flexible data modeling.

---

## Executive Summary

Timber's **config-driven model architecture** eliminates the need to write SQLAlchemy model classes in Python. Instead, developers define models declaratively in YAML files, and Timber's model factory dynamically generates the corresponding SQLAlchemy classes at runtime. This approach reduces boilerplate by 70%, makes schema changes easier to manage, and enables metadata-driven feature enablement.

**Core Innovation:** The model factory pattern + YAML configuration = Zero-boilerplate data modeling with automatic feature provisioning.

---

## The Problem with Traditional Models

### Traditional Approach: Pure Python

```python
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class StockResearchSession(Base):
    """
    Tracks stock research sessions.
    
    Features needed:
    - Encryption for proprietary analysis
    - Caching for performance
    - GDPR compliance for user data
    - Vector search for semantic queries
    """
    __tablename__ = 'stock_research_sessions'
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Data fields
    symbol = Column(String(10), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False)
    proprietary_analysis = Column(JSON, nullable=True)  # Should be encrypted
    results = Column(JSON, nullable=True)
    status = Column(String(20), default='active', nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='research_sessions')
    research_data = relationship('ResearchData', back_populates='session')
    
    # Indexes defined elsewhere or in __table_args__
    __table_args__ = (
        Index('idx_user_symbol_time', 'user_id', 'symbol', 'created_at'),
        Index('idx_status_type', 'status', 'analysis_type'),
    )
    
    # Custom methods for features
    def encrypt_sensitive_fields(self):
        """Manually encrypt proprietary_analysis"""
        # Manual encryption logic here
        pass
    
    def cache_result(self):
        """Manually cache this session"""
        # Manual caching logic here
        pass
    
    def export_for_gdpr(self):
        """Export data for GDPR compliance"""
        # Manual GDPR logic here
        pass
```

**Problems:**
1. **Repetitive:** Every model requires 50-100+ lines of boilerplate
2. **Error-Prone:** Easy to forget indexes, constraints, or features
3. **Hard to Maintain:** Schema changes require Python code modifications
4. **Manual Features:** Encryption, caching, GDPR must be manually implemented
5. **Not Scalable:** Adding 10 models means writing 1000+ lines of code
6. **Difficult to Review:** Python diffs are harder to read than YAML diffs

---

## The Timber Solution: YAML Models

### Same Model in YAML

```yaml
version: "1.0.0"
description: Stock research session models

models:
  - name: StockResearchSession
    table_name: stock_research_sessions
    description: Tracks user research sessions
    
    # Features enabled declaratively
    encryption:
      enabled: true
      fields: [proprietary_analysis]
    
    caching:
      enabled: true
      ttl_seconds: 1800
    
    gdpr:
      enabled: true
      user_id_field: user_id
      export_fields: [symbol, analysis_type, results]
    
    vector_search:
      enabled: true
      content_field: results
      embedding_model: BAAI/bge-small-en-v1.5
    
    # Columns
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
      
      - name: user_id
        type: String(36)
        foreign_key: users.id
        nullable: false
        index: true
      
      - name: symbol
        type: String(10)
        nullable: false
        index: true
      
      - name: analysis_type
        type: String(50)
        nullable: false
      
      - name: proprietary_analysis
        type: JSON
        nullable: true
        description: Encrypted proprietary analysis data
      
      - name: results
        type: JSON
        nullable: true
      
      - name: status
        type: String(20)
        default: "active"
        nullable: false
      
      - name: created_at
        type: DateTime
        default: utcnow
        nullable: false
      
      - name: updated_at
        type: DateTime
        default: utcnow
        onupdate: utcnow
    
    # Indexes
    indexes:
      - columns: [user_id, symbol, created_at]
        name: idx_user_symbol_time
      
      - columns: [status, analysis_type]
        name: idx_status_type
    
    # Relationships
    relationships:
      - name: user
        model: User
        type: many-to-one
        back_populates: research_sessions
      
      - name: research_data
        model: ResearchData
        type: one-to-many
        back_populates: session
```

**Benefits:**
1. **Declarative:** What you need, not how to implement it
2. **Concise:** 80 lines vs 100+ lines of Python
3. **Readable:** Clear structure, easy to understand
4. **Feature-Rich:** Encryption, caching, GDPR, vector search enabled with metadata
5. **Version Control Friendly:** YAML diffs are human-readable
6. **Application Agnostic:** Multiple apps can define models without touching Timber

---

## Model Factory Architecture

### High-Level Flow

```
┌──────────────────────────────────────────────────────┐
│  1. YAML Model Definition                            │
│     File: data/models/research_models.yaml           │
└──────────────────────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────┐
│  2. YAML Parser                                      │
│     • Reads YAML file                                │
│     • Validates syntax                               │
│     • Resolves dependencies                          │
│     • Returns dict structure                         │
└──────────────────────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────┐
│  3. Model Factory                                    │
│     • Processes model config dict                    │
│     • Builds columns with types & constraints        │
│     • Constructs relationships                       │
│     • Adds indexes                                   │
│     • Creates SQLAlchemy model class                 │
└──────────────────────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────┐
│  4. Feature Service Integration                      │
│     • Reads metadata (encryption, caching, etc.)     │
│     • Registers model with feature services          │
│     • Sets up automatic feature handling             │
└──────────────────────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────┐
│  5. Model Registry                                   │
│     • Stores model class with name key               │
│     • Makes available via get_model(name)            │
│     • Tracks relationships for later resolution      │
└──────────────────────────────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────┐
│  6. Database Table Creation                          │
│     • Generates CREATE TABLE SQL                     │
│     • Creates indexes                                │
│     • Sets up constraints                            │
│     • Ready for use                                  │
└──────────────────────────────────────────────────────┘
```

### Core Components

#### 1. YAML Parser

```python
class YAMLModelParser:
    """
    Parses YAML model definitions and validates structure
    """
    
    def __init__(self):
        self.required_fields = ['name', 'table_name', 'columns']
        self.optional_fields = [
            'description', 'indexes', 'relationships',
            'encryption', 'caching', 'gdpr', 'vector_search'
        ]
    
    def parse(self, yaml_path: str) -> List[dict]:
        """Parse YAML file and return list of model configs"""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Validate version
        self._validate_version(data.get('version'))
        
        # Process each model
        models = []
        for model_config in data.get('models', []):
            validated_config = self._validate_model_config(model_config)
            models.append(validated_config)
        
        return models
    
    def _validate_model_config(self, config: dict) -> dict:
        """Validate model configuration"""
        # Check required fields
        for field in self.required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate columns
        if not config['columns']:
            raise ValueError(f"Model {config['name']} has no columns")
        
        # Validate column definitions
        for col in config['columns']:
            self._validate_column(col)
        
        # Validate relationships if present
        if 'relationships' in config:
            for rel in config['relationships']:
                self._validate_relationship(rel)
        
        return config
    
    def _validate_column(self, col_config: dict):
        """Validate column definition"""
        if 'name' not in col_config or 'type' not in col_config:
            raise ValueError("Column must have 'name' and 'type'")
        
        # Validate type is recognized
        if not self._is_valid_type(col_config['type']):
            raise ValueError(f"Invalid column type: {col_config['type']}")
    
    def _is_valid_type(self, type_str: str) -> bool:
        """Check if type is valid SQLAlchemy type"""
        valid_types = [
            'String', 'Text', 'Integer', 'Float', 'Numeric',
            'Boolean', 'DateTime', 'Date', 'Time', 'JSON',
            'JSONB', 'UUID', 'LargeBinary', 'ARRAY'
        ]
        # Extract base type (e.g., "String(255)" -> "String")
        base_type = type_str.split('(')[0]
        return base_type in valid_types
```

#### 2. Model Factory

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Text
from sqlalchemy import ForeignKey, Index, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import Dict, Any, Type
import uuid
from datetime import datetime

class ModelFactory:
    """
    Factory for dynamically creating SQLAlchemy models from YAML config
    """
    
    def __init__(self):
        self.base = declarative_base()
        self.model_registry: Dict[str, Type] = {}
        self.pending_relationships = []
        
        # Type mapping: YAML string -> SQLAlchemy type
        self.type_map = {
            'String': String,
            'Text': Text,
            'Integer': Integer,
            'Float': Float,
            'Boolean': Boolean,
            'DateTime': DateTime,
            'Date': Date,
            'Time': Time,
            'JSON': JSON,
            'JSONB': JSONB,
            'UUID': UUID,
            'Numeric': Numeric,
            'LargeBinary': LargeBinary,
            'ARRAY': ARRAY
        }
        
        # Default value functions
        self.default_functions = {
            'uuid4': lambda: str(uuid.uuid4()),
            'utcnow': datetime.utcnow
        }
    
    def create_model(self, config: dict) -> Type:
        """
        Create SQLAlchemy model class from configuration
        
        Args:
            config: Validated model configuration dict
        
        Returns:
            SQLAlchemy model class
        """
        # 1. Prepare class attributes
        attrs = {
            '__tablename__': config['table_name'],
            '__model_config__': config  # Store config for features
        }
        
        # 2. Add columns
        for col_config in config['columns']:
            column = self._build_column(col_config)
            attrs[col_config['name']] = column
        
        # 3. Add indexes (will be in __table_args__)
        if 'indexes' in config:
            indexes = self._build_indexes(config['indexes'])
            attrs['__table_args__'] = tuple(indexes)
        
        # 4. Create the model class
        model_class = type(
            config['name'],
            (self.base,),
            attrs
        )
        
        # 5. Register model
        self.model_registry[config['name']] = model_class
        
        # 6. Store relationships for later (after all models loaded)
        if 'relationships' in config:
            for rel_config in config['relationships']:
                self.pending_relationships.append({
                    'model': model_class,
                    'config': rel_config
                })
        
        return model_class
    
    def _build_column(self, col_config: dict) -> Column:
        """
        Build SQLAlchemy Column from configuration
        
        Args:
            col_config: Column configuration dict
        
        Returns:
            SQLAlchemy Column object
        """
        # Parse type string (e.g., "String(255)" or "Integer")
        col_type = self._parse_type(col_config['type'])
        
        # Build kwargs for Column
        kwargs = {}
        
        # Primary key
        if col_config.get('primary_key'):
            kwargs['primary_key'] = True
        
        # Nullable
        if 'nullable' in col_config:
            kwargs['nullable'] = col_config['nullable']
        
        # Unique
        if col_config.get('unique'):
            kwargs['unique'] = True
        
        # Index
        if col_config.get('index'):
            kwargs['index'] = True
        
        # Foreign key
        if 'foreign_key' in col_config:
            kwargs['nullable'] = col_config.get('nullable', False)
            # ForeignKey will be added to type constructor
            return Column(
                col_config['name'],
                col_type,
                ForeignKey(col_config['foreign_key']),
                **kwargs
            )
        
        # Default value
        if 'default' in col_config:
            default_value = col_config['default']
            
            # Check if it's a function name
            if default_value in self.default_functions:
                kwargs['default'] = self.default_functions[default_value]
            else:
                # Static default value
                kwargs['default'] = default_value
        
        # Onupdate
        if 'onupdate' in col_config:
            onupdate_value = col_config['onupdate']
            if onupdate_value in self.default_functions:
                kwargs['onupdate'] = self.default_functions[onupdate_value]
        
        # Check constraint
        if 'check' in col_config:
            # Will be added via __table_args__
            pass
        
        return Column(col_type, **kwargs)
    
    def _parse_type(self, type_string: str):
        """
        Parse type string and return SQLAlchemy type
        
        Examples:
            "String(255)" -> String(255)
            "Integer" -> Integer
            "Numeric(10, 2)" -> Numeric(10, 2)
        """
        if '(' in type_string:
            # Type with arguments: String(255)
            type_name = type_string.split('(')[0]
            args_str = type_string.split('(')[1].rstrip(')')
            
            # Parse arguments
            args = [arg.strip() for arg in args_str.split(',')]
            args = [int(arg) if arg.isdigit() else arg for arg in args]
            
            # Get type class and instantiate with args
            type_class = self.type_map[type_name]
            return type_class(*args)
        else:
            # Simple type: Integer
            return self.type_map[type_string]()
    
    def _build_indexes(self, indexes_config: list) -> list:
        """Build Index objects from configuration"""
        indexes = []
        
        for idx_config in indexes_config:
            columns = idx_config['columns']
            name = idx_config.get('name')
            unique = idx_config.get('unique', False)
            
            index = Index(
                name,
                *columns,
                unique=unique
            )
            indexes.append(index)
        
        return indexes
    
    def resolve_relationships(self):
        """
        Resolve and add relationships after all models are loaded
        
        This must be called after all models are created because
        relationships reference other models that may not exist yet.
        """
        for rel_info in self.pending_relationships:
            model_class = rel_info['model']
            rel_config = rel_info['config']
            
            # Get the related model
            related_model = self.model_registry.get(rel_config['model'])
            if not related_model:
                raise ValueError(
                    f"Related model {rel_config['model']} not found"
                )
            
            # Build relationship
            rel = self._build_relationship(rel_config, related_model)
            
            # Add to model class
            setattr(model_class, rel_config['name'], rel)
        
        # Clear pending after resolution
        self.pending_relationships = []
    
    def _build_relationship(self, rel_config: dict, related_model: Type):
        """Build SQLAlchemy relationship"""
        kwargs = {}
        
        # Back populates
        if 'back_populates' in rel_config:
            kwargs['back_populates'] = rel_config['back_populates']
        
        # Handle different relationship types
        rel_type = rel_config.get('type', 'many-to-one')
        
        if rel_type == 'one-to-many':
            return relationship(related_model, **kwargs)
        
        elif rel_type == 'many-to-one':
            return relationship(related_model, **kwargs)
        
        elif rel_type == 'many-to-many':
            # Requires secondary table
            secondary = rel_config.get('secondary')
            if not secondary:
                raise ValueError("many-to-many requires 'secondary' table")
            
            kwargs['secondary'] = secondary
            return relationship(related_model, **kwargs)
        
        else:
            raise ValueError(f"Unknown relationship type: {rel_type}")
    
    def get_model(self, name: str) -> Type:
        """Get model class by name"""
        if name not in self.model_registry:
            raise ValueError(f"Model {name} not found in registry")
        return self.model_registry[name]
```

#### 3. Dependency Resolution

Models can depend on other models (via foreign keys or relationships). Timber resolves these dependencies using a dependency graph:

```python
class DependencyResolver:
    """
    Resolves model dependencies and determines load order
    """
    
    def __init__(self):
        self.dependency_graph = {}
    
    def build_graph(self, model_configs: List[dict]):
        """Build dependency graph from model configs"""
        # Initialize graph
        for config in model_configs:
            self.dependency_graph[config['name']] = {
                'config': config,
                'depends_on': set(),
                'depended_by': set()
            }
        
        # Find dependencies
        for config in model_configs:
            model_name = config['name']
            
            # Check for explicit depends
            if 'depends' in config:
                for dep in config['depends']:
                    self._add_dependency(model_name, dep)
            
            # Check foreign keys
            for col in config['columns']:
                if 'foreign_key' in col:
                    # Extract table name from foreign_key
                    fk_table = col['foreign_key'].split('.')[0]
                    # Find model with that table
                    dep_model = self._find_model_by_table(fk_table)
                    if dep_model:
                        self._add_dependency(model_name, dep_model)
            
            # Check relationships
            if 'relationships' in config:
                for rel in config['relationships']:
                    related_model = rel['model']
                    self._add_dependency(model_name, related_model)
    
    def _add_dependency(self, model: str, depends_on: str):
        """Add dependency to graph"""
        if depends_on in self.dependency_graph:
            self.dependency_graph[model]['depends_on'].add(depends_on)
            self.dependency_graph[depends_on]['depended_by'].add(model)
    
    def get_load_order(self) -> List[str]:
        """
        Return models in dependency order (topological sort)
        
        Models with no dependencies come first.
        """
        result = []
        processed = set()
        
        def visit(model_name: str):
            if model_name in processed:
                return
            
            # Visit dependencies first
            for dep in self.dependency_graph[model_name]['depends_on']:
                visit(dep)
            
            # Then add this model
            result.append(model_name)
            processed.add(model_name)
        
        # Visit all models
        for model_name in self.dependency_graph:
            visit(model_name)
        
        return result
```

---

## Feature Integration

### How Metadata Enables Features

The YAML model configuration includes metadata that feature services read to automatically enable capabilities:

```yaml
models:
  - name: UserPayment
    table_name: user_payments
    
    # Feature metadata
    encryption:
      enabled: true
      fields: [card_number, cvv]
      algorithm: fernet
    
    caching:
      enabled: true
      ttl_seconds: 3600
      cache_key_format: "payment:{id}"
    
    gdpr:
      enabled: true
      user_id_field: user_id
      export_fields: [amount, currency, created_at]
      anonymize_fields: [card_number]
    
    vector_search:
      enabled: true
      content_field: description
      metadata_fields: [amount, currency]
```

### Feature Service Hooks

When a model is created or queried, feature services intercept and apply transformations:

```python
class FeatureOrchestrator:
    """
    Orchestrates feature services based on model metadata
    """
    
    def __init__(self):
        self.encryption_service = EncryptionService()
        self.cache_service = CacheService()
        self.vector_service = VectorSearchService()
        self.gdpr_service = GDPRService()
    
    def before_insert(self, model_instance, model_config: dict):
        """Run before inserting into database"""
        # 1. Encrypt fields
        if model_config.get('encryption', {}).get('enabled'):
            self.encryption_service.encrypt_fields(
                model_instance,
                model_config['encryption']['fields']
            )
        
        # 2. Generate vector embeddings
        if model_config.get('vector_search', {}).get('enabled'):
            self.vector_service.generate_embedding(
                model_instance,
                model_config['vector_search']
            )
        
        # 3. GDPR audit
        if model_config.get('gdpr', {}).get('enabled'):
            self.gdpr_service.log_data_creation(
                model_instance,
                model_config['gdpr']
            )
    
    def after_query(self, model_instance, model_config: dict):
        """Run after querying from database"""
        # 1. Decrypt fields
        if model_config.get('encryption', {}).get('enabled'):
            self.encryption_service.decrypt_fields(
                model_instance,
                model_config['encryption']['fields']
            )
        
        # 2. Cache result
        if model_config.get('caching', {}).get('enabled'):
            cache_config = model_config['caching']
            key = cache_config['cache_key_format'].format(
                id=model_instance.id
            )
            self.cache_service.set(
                key,
                model_instance,
                ttl=cache_config['ttl_seconds']
            )
```

---

## Advanced Patterns

### 1. Model Mixins

Share common fields across models:

```yaml
# Define mixin
mixins:
  - name: AuditMixin
    columns:
      - name: created_at
        type: DateTime
        default: utcnow
      - name: created_by
        type: String(36)
        foreign_key: users.id
      - name: updated_at
        type: DateTime
        default: utcnow
        onupdate: utcnow
      - name: updated_by
        type: String(36)
        foreign_key: users.id

# Use mixin in models
models:
  - name: Post
    mixins: [AuditMixin]
    columns:
      - name: title
        type: String(255)
      # ... other columns
      # AuditMixin columns added automatically
```

### 2. Polymorphic Models

Support inheritance hierarchies:

```yaml
models:
  - name: Content
    table_name: content
    polymorphic:
      enabled: true
      on: content_type
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      - name: content_type
        type: String(50)  # 'article', 'video', 'podcast'
      - name: title
        type: String(255)
  
  - name: Article
    inherits: Content
    polymorphic_identity: article
    
    columns:
      - name: body
        type: Text
      - name: word_count
        type: Integer
  
  - name: Video
    inherits: Content
    polymorphic_identity: video
    
    columns:
      - name: duration_seconds
        type: Integer
      - name: video_url
        type: String(500)
```

### 3. Dynamic Table Names

Generate table names dynamically:

```yaml
models:
  - name: SessionData
    table_name_template: "session_data_{app_name}"
    # Generates: session_data_canopy, session_data_grove, etc.
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
```

### 4. Computed Columns

Define virtual columns:

```yaml
models:
  - name: Product
    table_name: products
    
    columns:
      - name: price
        type: Numeric(10, 2)
      - name: tax_rate
        type: Numeric(5, 2)
    
    computed:
      - name: price_with_tax
        expression: "price * (1 + tax_rate)"
        type: Numeric(10, 2)
```

### 5. Conditional Indexes

Create indexes based on conditions:

```yaml
models:
  - name: Order
    table_name: orders
    
    indexes:
      - columns: [status, created_at]
        where: "status = 'pending'"
        name: idx_pending_orders
```

---

## Model Validation

### Built-in Validators

```yaml
models:
  - name: User
    table_name: users
    
    columns:
      - name: email
        type: String(255)
        validators:
          - type: email
          - type: unique
      
      - name: age
        type: Integer
        validators:
          - type: range
            min: 18
            max: 120
      
      - name: username
        type: String(50)
        validators:
          - type: regex
            pattern: "^[a-zA-Z0-9_]+$"
          - type: length
            min: 3
            max: 50
```

### Custom Validators

```python
# Register custom validator
from timber.common.models.validators import ValidatorRegistry

@ValidatorRegistry.register('credit_card')
def validate_credit_card(value: str) -> bool:
    """Validate credit card number using Luhn algorithm"""
    # Implementation
    return is_valid_card(value)

# Use in YAML
columns:
  - name: card_number
    type: String(20)
    validators:
      - type: credit_card
```

---

## Testing Generated Models

### Unit Tests

```python
import pytest
from timber.common import initialize_timber, get_model
from timber.common.models.base import db_manager

@pytest.fixture(scope='module')
def setup_models():
    """Initialize Timber with test models"""
    initialize_timber(
        model_config_dirs=['./tests/fixtures/models'],
        database_url='postgresql://localhost/timber_test'
    )

def test_model_creation(setup_models):
    """Test that model is created correctly"""
    # Get model
    User = get_model('User')
    
    # Check attributes
    assert hasattr(User, 'id')
    assert hasattr(User, 'email')
    assert hasattr(User, 'username')
    
    # Check table name
    assert User.__tablename__ == 'users'

def test_model_instance(setup_models):
    """Test creating model instance"""
    User = get_model('User')
    
    with db_manager.session_scope() as session:
        user = User(
            email='test@example.com',
            username='testuser'
        )
        session.add(user)
        session.commit()
        
        assert user.id is not None
        assert user.created_at is not None

def test_relationships(setup_models):
    """Test model relationships work"""
    User = get_model('User')
    Post = get_model('Post')
    
    with db_manager.session_scope() as session:
        user = User(email='author@example.com', username='author')
        post = Post(title='Test Post', user=user)
        
        session.add(user)
        session.add(post)
        session.commit()
        
        # Test relationship
        assert post.user.username == 'author'
        assert user.posts[0].title == 'Test Post'
```

### Integration Tests

```python
def test_full_model_lifecycle(setup_models):
    """Test complete CRUD operations"""
    Session = get_model('StockResearchSession')
    
    # CREATE
    with db_manager.session_scope() as session:
        research_session = Session(
            user_id='user-123',
            session_type='research',
            symbol='AAPL',
            status='active'
        )
        session.add(research_session)
        session.commit()
        session_id = research_session.id
    
    # READ
    with db_manager.session_scope() as session:
        found = session.query(Session).filter_by(id=session_id).first()
        assert found is not None
        assert found.symbol == 'AAPL'
    
    # UPDATE
    with db_manager.session_scope() as session:
        found = session.query(Session).filter_by(id=session_id).first()
        found.status = 'completed'
        session.commit()
    
    # DELETE
    with db_manager.session_scope() as session:
        session.query(Session).filter_by(id=session_id).delete()
        session.commit()
    
    # VERIFY DELETE
    with db_manager.session_scope() as session:
        found = session.query(Session).filter_by(id=session_id).first()
        assert found is None
```

---

## Best Practices

### 1. Model Organization

```
data/models/
├── core/
│   ├── user_models.yaml       # User, UserProfile, UserPreference
│   └── auth_models.yaml       # Session, Token, Permission
├── research/
│   ├── session_models.yaml    # ResearchSession
│   └── data_models.yaml       # ResearchData, Analysis
├── trading/
│   ├── order_models.yaml      # Order, Trade
│   └── portfolio_models.yaml  # Portfolio, Position
└── shared/
    ├── notification_models.yaml
    └── tracking_models.yaml
```

### 2. Naming Conventions

```yaml
# Model names: PascalCase
- name: StockResearchSession

# Table names: snake_case
table_name: stock_research_sessions

# Column names: snake_case
columns:
  - name: user_id
  - name: created_at

# Index names: idx_prefix
indexes:
  - name: idx_user_created
    columns: [user_id, created_at]
```

### 3. Documentation

```yaml
models:
  - name: Order
    table_name: orders
    description: |
      Represents a trading order placed by a user.
      Supports market, limit, and stop orders.
    
    columns:
      - name: order_type
        type: String(20)
        description: Order type - 'market', 'limit', or 'stop'
      
      - name: quantity
        type: Integer
        description: Number of shares to buy/sell
```

### 4. Defaults and Constraints

```yaml
columns:
  # Always provide defaults for optional fields
  - name: status
    type: String(20)
    default: "pending"
    nullable: false
  
  # Use check constraints for data integrity
  - name: quantity
    type: Integer
    check: "quantity > 0"
  
  # Index foreign keys
  - name: user_id
    type: String(36)
    foreign_key: users.id
    index: true
    nullable: false
```

### 5. Feature Configuration

```yaml
# Enable features intentionally
encryption:
  enabled: true
  fields: [sensitive_field]  # Be specific

# Set appropriate cache TTL
caching:
  enabled: true
  ttl_seconds: 3600  # 1 hour for semi-static data

# Configure GDPR carefully
gdpr:
  enabled: true
  user_id_field: user_id
  export_fields: [field1, field2]  # Only necessary fields
```

---

## Performance Considerations

### 1. Lazy Loading vs Eager Loading

```yaml
# Control relationship loading
relationships:
  - name: posts
    model: Post
    type: one-to-many
    lazy: select  # Lazy load (default)

  - name: user
    model: User
    type: many-to-one
    lazy: joined  # Eager load
```

### 2. Index Strategy

```yaml
# Index frequently queried fields
columns:
  - name: email
    type: String(255)
    unique: true
    index: true  # Single column index

# Composite indexes for multi-column queries
indexes:
  - columns: [status, created_at]  # For: WHERE status = X ORDER BY created_at
  - columns: [user_id, symbol]     # For: WHERE user_id = X AND symbol = Y
```

### 3. Column Types

```yaml
# Use appropriate types
columns:
  # String with length for indexed fields
  - name: symbol
    type: String(10)  # Not String(255)
  
  # Text for long content
  - name: analysis
    type: Text
  
  # Numeric for money
  - name: price
    type: Numeric(10, 2)  # Not Float
```

---

## Migration Strategy

### Adding New Models

```yaml
# 1. Add new model to YAML
models:
  - name: NewModel
    table_name: new_table
    columns:
      - name: id
        type: String(36)
        primary_key: true

# 2. Restart application (or reload models)

# 3. Run migration
# timber create-migration "add_new_table"
# timber migrate
```

### Modifying Existing Models

```yaml
# Before
columns:
  - name: status
    type: String(20)

# After - Add new column
columns:
  - name: status
    type: String(20)
  - name: priority
    type: String(10)
    default: "normal"  # Provide default for existing rows
```

### Deprecating Models

```yaml
# Mark as deprecated
models:
  - name: OldModel
    table_name: old_table
    deprecated: true
    deprecated_message: "Use NewModel instead"
    # Model still works but logs warnings
```

---

## Troubleshooting

### Common Issues

**Issue:** Model not found in registry

```python
# Problem
User = get_model('User')  # ValueError: Model User not found

# Solution: Check model name matches YAML
models:
  - name: User  # Must match exactly
```

**Issue:** Foreign key constraint violation

```yaml
# Problem: Referenced table doesn't exist
columns:
  - name: user_id
    foreign_key: users.id  # 'users' table not created yet

# Solution: Use depends to control order
depends: ["user_models.yaml"]
```

**Issue:** Type parsing error

```yaml
# Problem: Invalid type syntax
columns:
  - name: amount
    type: Numeric 10, 2  # Missing parentheses

# Solution: Use correct syntax
columns:
  - name: amount
    type: Numeric(10, 2)
```

---

## Summary

Timber's config-driven model architecture provides:

1. **Zero Boilerplate:** Define models in YAML, not Python
2. **Automatic Features:** Encryption, caching, GDPR, vector search from metadata
3. **Type Safety:** Validated types and constraints
4. **Relationship Management:** Foreign keys and relationships handled automatically
5. **Dependency Resolution:** Models loaded in correct order
6. **Extensibility:** Mixins, validators, custom types
7. **Testability:** Generated models are fully testable
8. **Migration Support:** Schema evolution without Python code changes

**Key Benefits:**
- 70% less code to write and maintain
- Consistent structure across all models
- Easy to review changes in version control
- Applications can add models without modifying Timber
- Features enabled declaratively

---

## Next Steps

- **[System Architecture](01_system_architecture.md)** - Overall Timber design
- **[Persistence Layer](03_persistence_layer.md)** - Database architecture
- **[Vector Integration](04_vector_integration.md)** - Semantic search
- **[Creating Models How-To](../how_to/02_creating_models.md)** - Practical guide

---

**Last Updated:** October 19, 2024  
**Version:** 0.2.0  
**Authors:** Timber Architecture Team