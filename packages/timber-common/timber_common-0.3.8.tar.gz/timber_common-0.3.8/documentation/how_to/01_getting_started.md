# Getting Started with Timber

This guide will help you set up Timber and create your first model in under 10 minutes.

---

## Prerequisites

- Python 3.13.7 or higher
- PostgreSQL 12+ or SQLite 3.35+ (for development)
- Basic understanding of Python and SQL
- (Optional) Redis for caching

---

## Step 1: Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd timber-common

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
# Install in development mode
pip install -e .

# Or install required packages
pip install -r requirements.txt
```

---

## Step 2: Environment Configuration

Create a `.env` file in your project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Environment
OAK_ENV=development
APP_ENV=development

# Database - SQLite for development
DATABASE_URL=sqlite:///./timber_dev.db
DATABASE_ECHO=True

# For production, use PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/timber

# Encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your-generated-key-here

# Vector Search
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSION=384

# Caching
CACHE_ENABLED=True
CACHE_TTL_HOURS=24
REDIS_ENABLED=False

# Paths
DATA_DIR=./data
CACHE_DIR=./.cache
```

---

## Step 3: Create Directory Structure

```bash
# Create required directories
mkdir -p data/models
mkdir -p data/curated_companies
mkdir -p .cache
```

---

## Step 4: Your First Model

Create a model configuration file: `data/models/hello_world.yaml`

```yaml
version: "1.0.0"
description: My first Timber model

models:
  - name: HelloWorld
    table_name: hello_world
    description: A simple hello world model
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
        description: Unique identifier
      
      - name: message
        type: String(200)
        nullable: false
        description: Hello message
      
      - name: created_at
        type: DateTime
        default: utcnow
        nullable: false
        description: Creation timestamp
      
      - name: created_by
        type: String(100)
        nullable: true
        description: Creator name
```

---

## Step 5: Initialize Timber

Create a file `test_hello.py`:

```python
from timber.common import initialize_timber, get_model
from timber.common.models.base import db_manager

# Initialize Timber with your model configs
print("Initializing Timber...")
initialize_timber(
    model_config_dirs=['./data/models'],
    enable_encryption=False,  # Disable for this example
    enable_gdpr=False,
    create_tables=True,  # Automatically create tables
    validate_config=True
)

print("Timber initialized successfully!")

# Get the dynamically created model
HelloWorld = get_model('HelloWorld')

# Create an instance
with db_manager.session_scope() as session:
    hello = HelloWorld(
        message="Hello, Timber!",
        created_by="Your Name"
    )
    session.add(hello)
    session.commit()
    
    print(f"Created: {hello.message}")
    print(f"ID: {hello.id}")
    print(f"Timestamp: {hello.created_at}")

# Query all records
with db_manager.session_scope() as session:
    all_hellos = session.query(HelloWorld).all()
    print(f"\nTotal records: {len(all_hellos)}")
    
    for record in all_hellos:
        print(f"  - {record.message} (by {record.created_by})")
```

Run it:

```bash
python test_hello.py
```

Expected output:

```
Initializing Timber...
Timber initialized successfully!
Created: Hello, Timber!
ID: 550e8400-e29b-41d4-a716-446655440000
Timestamp: 2024-01-15 10:30:45.123456

Total records: 1
  - Hello, Timber! (by Your Name)
```

---

## Step 6: Verify Database

### For SQLite

```bash
# Open the database
sqlite3 timber_dev.db

# List tables
.tables

# View the data
SELECT * FROM hello_world;

# Exit
.quit
```

### For PostgreSQL

```bash
# Connect to database
psql -d timber

# List tables
\dt

# View the data
SELECT * FROM hello_world;

# Exit
\q
```

---

## Step 7: Explore More Features

### Stock Data Fetching

```python
from timber.common import stock_data_service

# Fetch historical data
df, error = stock_data_service.fetch_historical_data('AAPL', period='1mo')
if not error:
    print(df.head())
```

### Multiple Models

Create `data/models/advanced.yaml`:

```yaml
version: "1.0.0"

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
      - name: username
        type: String(100)
        unique: true
        nullable: false
  
  - name: UserActivity
    table_name: user_activities
    columns:
      - name: id
        type: String(36)
        primary_key: true
        default: uuid4
      - name: user_id
        type: String(36)
        foreign_key: users.id
        nullable: false
      - name: activity_type
        type: String(50)
        nullable: false
      - name: created_at
        type: DateTime
        default: utcnow
```

Use them:

```python
from timber.common import get_model
from timber.common.models.base import db_manager

User = get_model('User')
UserActivity = get_model('UserActivity')

with db_manager.session_scope() as session:
    # Create user
    user = User(email='user@example.com', username='trader1')
    session.add(user)
    session.flush()  # Get the ID
    
    # Create activity
    activity = UserActivity(
        user_id=user.id,
        activity_type='login'
    )
    session.add(activity)
    session.commit()
```

---

## Common Issues

### Issue: "No module named 'timber.common'"

**Solution**: Install in development mode
```bash
pip install -e .
```

### Issue: "Database connection failed"

**Solution**: Check your DATABASE_URL in `.env`
```bash
# For SQLite (development)
DATABASE_URL=sqlite:///./timber_dev.db

# For PostgreSQL (production)
DATABASE_URL=postgresql://user:password@localhost:5432/timber
```

### Issue: "No such table: hello_world"

**Solution**: Make sure `create_tables=True` in initialize_timber()

### Issue: "ENCRYPTION_KEY not set"

**Solution**: Generate a key
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Add to `.env`:
```bash
ENCRYPTION_KEY=<generated-key>
```

---

## Next Steps

1. **Create More Models**: See [Creating Models](02_creating_models.md)
2. **Use Services**: See [Using Services](03_using_services.md)
3. **Fetch Financial Data**: See [Financial Data](04_financial_data_fetching.md)
4. **Add Encryption**: See [Encryption Guide](05_encryption_and_security.md)
5. **Vector Search**: See [Vector Search](06_vector_search.md)

---

## Quick Reference

### Initialize Timber
```python
from timber.common import initialize_timber
initialize_timber(model_config_dirs=['./data/models'])
```

### Get a Model
```python
from timber.common import get_model
MyModel = get_model('MyModel')
```

### Database Session
```python
from timber.common.models.base import db_manager
with db_manager.session_scope() as session:
    # Your database operations
    pass
```

### Fetch Stock Data
```python
from timber.common import stock_data_service
df, error = stock_data_service.fetch_historical_data('AAPL', period='1y')
```

---

## Summary

You've learned how to:
- ✅ Install Timber
- ✅ Configure environment
- ✅ Create a YAML model
- ✅ Initialize Timber
- ✅ Create and query records
- ✅ Verify in database

**Congratulations!** You're ready to build with Timber. 🎉