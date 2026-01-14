# Model Design Patterns - Best Practices

Recommended patterns for designing robust, maintainable YAML models in Timber.

---

## Core Principles

### 1. Single Responsibility
Each model should represent one clear concept:

**Good:**
```yaml
# user_models.yaml
models:
  - name: User
    # User authentication and profile

  - name: UserPreference  
    # User settings and preferences

  - name: UserSession
    # Active user sessions
```

**Avoid:**
```yaml
# Don't mix unrelated concepts
models:
  - name: Everything
    columns:
      - name: user_email
      - name: stock_ticker
      - name: notification_text
      # Too many responsibilities!
```

### 2. Consistent Naming
Use clear, descriptive names following conventions:

**Naming Conventions:**
- Models: PascalCase (`UserPreference`, `StockResearchSession`)
- Tables: snake_case (`user_preferences`, `stock_research_sessions`)
- Columns: snake_case (`created_at`, `user_id`, `is_active`)
- Foreign keys: `<table>_id` (`user_id`, `session_id`)

### 3. Explicit Over Implicit
Be explicit about nullability, defaults, and constraints:

**Good:**
```yaml
- name: email
  type: String(255)
  unique: true
  nullable: false  # Explicit
  index: true

- name: status
  type: String(20)
  default: "active"  # Explicit default
  nullable: false
```

### 4. Appropriate Data Types
Choose the right type for each field:

```yaml
# Money - use Numeric for precision
- name: price
  type: Numeric(10, 2)

# IDs - use String(36) for UUIDs
- name: id
  type: String(36)
  default: uuid4

# Flags - use Boolean
- name: is_active
  type: Boolean
  default: true

# Timestamps - use DateTime
- name: created_at
  type: DateTime
  default: utcnow

# Flexible data - use JSON
- name: metadata
  type: JSON
```

---

## Common Patterns

### Pattern 1: Audit Trail
Track who did what and when:

```yaml
models:
  - name: AuditableEntity
    columns:
      - name: created_at
        type: DateTime
        default: utcnow
        nullable: false
      
      - name: created_by
        type: String(36)
        foreign_key: users.id
        nullable: false
      
      - name: updated_at
        type: DateTime
        default: utcnow
        onupdate: utcnow
      
      - name: updated_by
        type: String(36)
        foreign_key: users.id
        nullable: true
```

**Use when:** You need to track creation and modification history.

### Pattern 2: Soft Delete
Mark records as deleted instead of removing them:

```yaml
models:
  - name: SoftDeletable
    columns:
      - name: is_deleted
        type: Boolean
        default: false
        index: true
      
      - name: deleted_at
        type: DateTime
        nullable: true
      
      - name: deleted_by
        type: String(36)
        foreign_key: users.id
        nullable: true

    indexes:
      - columns: [is_deleted, created_at]
```

**Use when:** You need to preserve data for auditing or recovery.

**Query pattern:**
```python
# Only active records
active = session.query(MyModel).filter_by(is_deleted=False).all()
```

### Pattern 3: Versioning
Track version history:

```yaml
models:
  - name: Versioned
    columns:
      - name: version
        type: Integer
        default: 1
        nullable: false
      
      - name: previous_version_id
        type: String(36)
        nullable: true
      
      - name: is_current_version
        type: Boolean
        default: true
        index: true
```

**Use when:** You need to maintain version history of records.

### Pattern 4: State Machine
Model entities with defined states:

```yaml
models:
  - name: WorkflowEntity
    columns:
      - name: status
        type: String(20)
        default: "draft"
        nullable: false
        index: true
        # Valid states: draft, submitted, approved, rejected, published
      
      - name: status_changed_at
        type: DateTime
        default: utcnow
      
      - name: status_changed_by
        type: String(36)
        foreign_key: users.id

    indexes:
      - columns: [status, created_at]
```

**Use when:** Records go through defined lifecycle states.

### Pattern 5: Polymorphic Association
One relationship, multiple target types:

```yaml
models:
  - name: Comment
    table_name: comments
    columns:
      - name: commentable_type
        type: String(50)
        nullable: false
        index: true
      
      - name: commentable_id
        type: String(36)
        nullable: false
        index: true
      
      - name: content
        type: Text
    
    indexes:
      - columns: [commentable_type, commentable_id]
```

**Use when:** An entity can be associated with multiple types of parents.

**Python usage:**
```python
# Comment on a post
comment = Comment(
    commentable_type='Post',
    commentable_id=post.id,
    content='Great post!'
)

# Comment on a research session  
comment = Comment(
    commentable_type='ResearchSession',
    commentable_id=session.id,
    content='Interesting analysis'
)
```

### Pattern 6: Hierarchical Data (Self-Reference)
Parent-child relationships:

```yaml
models:
  - name: Category
    table_name: categories
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
      
      - name: parent_id
        type: String(36)
        foreign_key: categories.id
        nullable: true
        index: true
      
      - name: name
        type: String(100)
        nullable: false
      
      - name: level
        type: Integer
        default: 0
    
    relationships:
      - name: children
        model: Category
        type: one-to-many
        foreign_keys: [parent_id]
      
      - name: parent
        model: Category
        type: many-to-one
        remote_side: [id]
```

**Use when:** Modeling tree structures (categories, org charts, etc).

---

## Anti-Patterns to Avoid

### ❌ Don't: God Objects
Models that try to do everything:

```yaml
# BAD: Too many responsibilities
models:
  - name: Everything
    columns:
      - name: user_email
      - name: user_password
      - name: stock_ticker
      - name: stock_price
      - name: notification_text
      # ... 50 more columns
```

**Fix:** Split into separate, focused models.

### ❌ Don't: Ambiguous Nullability
Not specifying nullable:

```yaml
# BAD: Is email required or optional?
- name: email
  type: String(255)
  # nullable: ???
```

**Fix:** Always be explicit:
```yaml
- name: email
  type: String(255)
  nullable: false  # Required
```

### ❌ Don't: Missing Indexes
Forgetting indexes on frequently queried fields:

```yaml
# BAD: user_id will be slow to query
- name: user_id
  type: String(36)
  foreign_key: users.id
```

**Fix:** Add indexes:
```yaml
- name: user_id
  type: String(36)
  foreign_key: users.id
  index: true  # Much faster!
```

### ❌ Don't: Wrong Data Types
Using inappropriate types:

```yaml
# BAD: Money stored as Float (precision loss!)
- name: price
  type: Float

# BAD: Boolean as String
- name: is_active
  type: String(5)  # "true", "false"?
```

**Fix:** Use appropriate types:
```yaml
- name: price
  type: Numeric(10, 2)

- name: is_active
  type: Boolean
```

### ❌ Don't: Ignoring Relationships
Not defining relationships between related models:

```yaml
# BAD: Just a foreign key, no relationship
models:
  - name: Post
    columns:
      - name: user_id
        foreign_key: users.id
```

**Fix:** Define the relationship:
```yaml
models:
  - name: Post
    columns:
      - name: user_id
        foreign_key: users.id
    
    relationships:
      - name: user
        model: User
        type: many-to-one
```

---

## Model Organization

### File Structure
Organize models by domain:

```
data/models/
├── 00_base_models.yaml          # Core: User, Company
├── 01_authentication.yaml       # Auth: OAuth, Session
├── 02_research.yaml             # Research: Session, Data
├── 03_notifications.yaml        # Notifications: Notification, Alert
├── 04_tracking.yaml             # Tracking: Activity, Event
└── 05_reporting.yaml            # Reporting: Report, Schedule
```

**Why numbered?** Ensures load order (authentication before research).

### Dependencies
Use `depends` for cross-file references:

```yaml
# 02_research.yaml
version: "1.0.0"
depends: ["00_base_models.yaml"]  # Need User first

models:
  - name: ResearchSession
    columns:
      - name: user_id
        foreign_key: users.id
```

---

## Performance Considerations

### Index Strategy
Index fields used in:
- WHERE clauses
- JOIN conditions
- ORDER BY clauses
- Foreign keys (always!)

```yaml
# High-traffic query: Find user's recent sessions
# Query: WHERE user_id = ? AND created_at > ? ORDER BY created_at DESC

indexes:
  - columns: [user_id, created_at]
    name: idx_user_recent_sessions
```

### Composite Indexes
Order matters - most selective first:

```yaml
# Query: WHERE status = 'active' AND user_id = ?
# user_id is more selective than status

indexes:
  - columns: [user_id, status]  # Good
  # NOT: [status, user_id]      # Less effective
```

### Avoid Over-Indexing
Too many indexes slow down writes:

```yaml
# DON'T index everything
columns:
  - name: rarely_queried_field
    type: String(100)
    # index: true  # Skip if not needed
```

---

## Security Best Practices

### Sensitive Data
Mark sensitive fields for encryption:

```yaml
models:
  - name: SecureData
    encryption:
      enabled: true
      fields: [ssn, credit_card, secret_key]
    
    columns:
      - name: ssn
        type: String(50)
      - name: credit_card
        type: String(100)
```

### GDPR Compliance
Enable for models with user data:

```yaml
models:
  - name: UserActivity
    gdpr:
      enabled: true
      user_id_field: user_id
      export_fields: [activity_type, timestamp, metadata]
    
    columns:
      - name: user_id
        type: String(36)
```

---

## Testing Your Models

```python
import pytest
from timber.common import initialize_timber, get_model
from timber.common.models.base import db_manager

def test_user_model():
    # Arrange
    User = get_model('User')
    
    with db_manager.session_scope() as session:
        # Act
        user = User(
            email='test@example.com',
            username='testuser'
        )
        session.add(user)
        session.commit()
        
        # Assert
        assert user.id is not None
        assert user.created_at is not None
        
        # Verify constraints
        found = session.query(User).filter_by(email='test@example.com').first()
        assert found.username == 'testuser'
```

---

## Summary Checklist

When designing a model, ensure:

- [ ] Single, clear responsibility
- [ ] Consistent naming (PascalCase models, snake_case columns)
- [ ] Explicit nullability on all columns
- [ ] Appropriate data types
- [ ] Indexes on foreign keys and query fields
- [ ] Relationships defined (not just FKs)
- [ ] Audit fields if needed (created_at, updated_at)
- [ ] Soft delete if needed
- [ ] Encryption for sensitive fields
- [ ] GDPR compliance if handling user data
- [ ] Composite indexes for common queries
- [ ] Constraints (unique, check) where appropriate
- [ ] Descriptions on complex fields

---

## Next Steps

- [Service Architecture](02_service_architecture.md)
- [Creating Models Guide](../how_to/02_creating_models.md)
- [Design Guide: Config-Driven Models](../design_guides/02_config_driven_models.md)