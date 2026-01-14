# Creating Models with YAML

This guide explains how to define SQLAlchemy models using YAML configuration files instead of Python classes.

---

## Why YAML Models?

Traditional approach (Python):
```python
class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

Timber approach (YAML):
```yaml
models:
  - name: User
    table_name: users
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
      - name: email
        type: String(255)
        unique: true
        nullable: false
```

**Benefits:**
- No Python code needed
- Easy to read and modify
- Version control friendly
- Applications can add models without changing Timber
- Metadata enables automatic features (encryption, caching, GDPR)

---

## Basic Model Structure

```yaml
version: "1.0.0"
description: Optional description of this config file

models:
  - name: ModelName
    table_name: table_name
    description: What this model represents
    
    columns:
      - name: column_name
        type: SQLAlchemy_type
        # ... column options
    
    indexes:
      - columns: [col1, col2]
        unique: true
    
    relationships:
      - name: related_items
        model: RelatedModel
        type: one-to-many
```

---

## Column Types

### String Types
```yaml
- name: short_string
  type: String(50)

- name: long_text
  type: Text

- name: email
  type: String(255)
```

### Numeric Types
```yaml
- name: quantity
  type: Integer

- name: price
  type: Float

- name: precise_amount
  type: Numeric(10, 2)  # precision, scale

- name: is_active
  type: Boolean
```

### Date/Time Types
```yaml
- name: created_at
  type: DateTime
  default: utcnow

- name: birth_date
  type: Date

- name: event_time
  type: Time
```

### JSON Types
```yaml
- name: metadata
  type: JSON

- name: settings
  type: JSONB  # PostgreSQL only, better performance
```

### Special Types
```yaml
- name: uuid
  type: UUID  # Native UUID type

- name: array_field
  type: ARRAY(String)  # PostgreSQL only

- name: binary_data
  type: LargeBinary
```

---

## Column Options

### Primary Key
```yaml
- name: id
  type: String(36)
  primary_key: true
  default: uuid4
```

### Foreign Key
```yaml
- name: user_id
  type: String(36)
  foreign_key: users.id
  nullable: false
  index: true
```

### Constraints
```yaml
- name: email
  type: String(255)
  unique: true
  nullable: false
  index: true

- name: age
  type: Integer
  check: "age >= 18"
```

### Default Values
```yaml
# Function defaults
- name: id
  type: String(36)
  default: uuid4

- name: created_at
  type: DateTime
  default: utcnow

# Static defaults
- name: status
  type: String(20)
  default: "active"

- name: count
  type: Integer
  default: 0
```

---

## Relationships

### One-to-Many
```yaml
models:
  - name: User
    table_name: users
    columns:
      - name: id
        type: String(36)
        primary_key: true
    
    relationships:
      - name: posts
        model: Post
        type: one-to-many
        back_populates: user
  
  - name: Post
    table_name: posts
    columns:
      - name: id
        type: String(36)
        primary_key: true
      - name: user_id
        type: String(36)
        foreign_key: users.id
    
    relationships:
      - name: user
        model: User
        type: many-to-one
        back_populates: posts
```

### Many-to-Many
```yaml
models:
  - name: Student
    table_name: students
    columns:
      - name: id
        type: String(36)
        primary_key: true
    
    relationships:
      - name: courses
        model: Course
        type: many-to-many
        secondary: student_courses
  
  - name: Course
    table_name: courses
    columns:
      - name: id
        type: String(36)
        primary_key: true
    
    relationships:
      - name: students
        model: Student
        type: many-to-many
        secondary: student_courses
```

---

## Indexes

### Single Column Index
```yaml
columns:
  - name: email
    type: String(255)
    index: true
```

### Composite Index
```yaml
indexes:
  - columns: [user_id, created_at]
    name: idx_user_created

  - columns: [ticker, date]
    unique: true
```

---

## Advanced Features

### Encryption
```yaml
models:
  - name: SecureData
    table_name: secure_data
    
    encryption:
      enabled: true
      fields: [ssn, bank_account]
    
    columns:
      - name: ssn
        type: String(50)
      - name: bank_account
        type: String(100)
```

### GDPR Compliance
```yaml
models:
  - name: UserData
    table_name: user_data
    
    gdpr:
      enabled: true
      user_id_field: user_id
      export_fields: [data, preferences]
    
    columns:
      - name: user_id
        type: String(36)
```

### Caching
```yaml
models:
  - name: ExpensiveQuery
    table_name: expensive_queries
    
    caching:
      enabled: true
      ttl_seconds: 3600
```

### Vector Search
```yaml
models:
  - name: Document
    table_name: documents
    
    vector_search:
      enabled: true
      content_field: content
      embedding_model: BAAI/bge-small-en-v1.5
    
    columns:
      - name: content
        type: Text
```

---

## Complete Example

```yaml
version: "1.0.0"
description: Stock research session models

models:
  - name: StockResearchSession
    table_name: stock_research_sessions
    description: Tracks user research sessions
    session_type: research
    
    # Enable features
    encryption:
      enabled: true
      fields: [proprietary_analysis]
    
    gdpr:
      enabled: true
      user_id_field: user_id
      export_fields: [symbol, analysis_type, results]
    
    caching:
      enabled: true
      ttl_seconds: 1800
    
    # Columns
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
        description: Session identifier
      
      - name: user_id
        type: String(36)
        foreign_key: users.id
        nullable: false
        index: true
        description: User who created the session
      
      - name: symbol
        type: String(10)
        nullable: false
        index: true
        description: Stock ticker symbol
      
      - name: analysis_type
        type: String(50)
        nullable: false
        description: Type of analysis (fundamental, technical, etc)
      
      - name: proprietary_analysis
        type: JSON
        nullable: true
        description: Encrypted proprietary analysis data
      
      - name: results
        type: JSON
        nullable: true
        description: Analysis results
      
      - name: status
        type: String(20)
        default: "active"
        nullable: false
        description: Session status
      
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

---

## File Organization

### Single File Per Domain
```
data/models/
├── user_models.yaml          # User, UserPreference, UserSession
├── research_models.yaml      # Research sessions and results
├── notification_models.yaml  # Notifications and alerts
└── tracking_models.yaml      # User activity tracking
```

### Dependencies Between Files
Use `depends` to control loading order:

```yaml
# file: user_models.yaml
version: "1.0.0"
# No dependencies, loads first

models:
  - name: User
    ...
```

```yaml
# file: research_models.yaml
version: "1.0.0"
depends: ["user_models.yaml"]  # Load User first

models:
  - name: ResearchSession
    columns:
      - name: user_id
        foreign_key: users.id  # User must exist first
```

---

## Best Practices

### 1. Use Descriptive Names
```yaml
# Good
- name: created_at
- name: user_email
- name: stock_ticker

# Avoid
- name: dt
- name: e
- name: s
```

### 2. Add Descriptions
```yaml
- name: risk_score
  type: Float
  description: Calculated risk score from 0.0 (low) to 1.0 (high)
```

### 3. Use Appropriate Types
```yaml
# For money
- name: price
  type: Numeric(10, 2)

# For IDs
- name: id
  type: String(36)  # UUID

# For short strings
- name: status
  type: String(20)

# For long text
- name: content
  type: Text
```

### 4. Add Indexes
```yaml
# For foreign keys
- name: user_id
  type: String(36)
  foreign_key: users.id
  index: true  # Always index FKs

# For common queries
indexes:
  - columns: [created_at]  # For time-based queries
  - columns: [status, type]  # For filtered queries
```

### 5. Use Constraints
```yaml
- name: email
  type: String(255)
  unique: true
  nullable: false

- name: age
  type: Integer
  check: "age >= 0"
```

---

## Testing Your Models

```python
from timber.common import initialize_timber, get_model
from timber.common.models.base import db_manager

# Initialize
initialize_timber(model_config_dirs=['./data/models'])

# Get model
MyModel = get_model('MyModel')

# Test creation
with db_manager.session_scope() as session:
    instance = MyModel(field1="value1", field2="value2")
    session.add(instance)
    session.commit()
    print(f"Created: {instance.id}")

# Test query
with db_manager.session_scope() as session:
    results = session.query(MyModel).filter_by(field1="value1").all()
    print(f"Found: {len(results)}")
```

---

## Common Patterns

### Audit Fields
```yaml
columns:
  - name: created_at
    type: DateTime
    default: utcnow
    nullable: false
  
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
```

### Soft Delete
```yaml
columns:
  - name: deleted_at
    type: DateTime
    nullable: true
  
  - name: deleted_by
    type: String(36)
    foreign_key: users.id
    nullable: true
  
  - name: is_deleted
    type: Boolean
    default: false
    index: true
```

### Versioning
```yaml
columns:
  - name: version
    type: Integer
    default: 1
    nullable: false
```

---

## Next Steps

- [Using Services](03_using_services.md)
- [Financial Data Fetching](04_financial_data_fetching.md)
- [Best Practices: Model Design](../best_practices/01_model_design_patterns.md)
- [Design Guide: Config-Driven Models](../design_guides/02_config_driven_models.md)