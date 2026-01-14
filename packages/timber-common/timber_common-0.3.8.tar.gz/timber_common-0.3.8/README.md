# Timber

**Configuration-driven persistence library with automatic encryption, caching, vector search, and GDPR compliance**

[![PyPI version](https://badge.fury.io/py/timber-common.svg)](https://badge.fury.io/py/timber-common)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## What is Timber?

Timber is a **configuration-driven persistence library** that eliminates boilerplate code by defining SQLAlchemy models in YAML instead of Python. It automatically provides encryption, caching, vector search, and GDPR compliance based on simple configuration flags.

**Transform this Python boilerplate:**

```python
class StockResearchSession(Base):
    __tablename__ = 'stock_research_sessions'
    id = Column(String(36), primary_key=True, default=uuid4)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    symbol = Column(String(10), nullable=False)
    analysis = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    # ... 50+ more lines of boilerplate
```

**Into this YAML configuration:**

```yaml
models:
  - name: StockResearchSession
    table_name: stock_research_sessions
    
    # Enable features with one line
    encryption:
      enabled: true
      fields: [analysis]
    
    caching:
      enabled: true
      ttl_seconds: 3600
    
    vector_search:
      enabled: true
      content_field: analysis
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      - name: user_id
        type: String(36)
        foreign_key: users.id
      - name: symbol
        type: String(10)
      - name: analysis
        type: JSON
```

---

## Key Features

### 🎯 Configuration-Driven Models
- **Zero Python boilerplate** - Define models in YAML
- **Dynamic generation** - Models created at runtime
- **Full SQLAlchemy** - All SQLAlchemy features supported
- **Type-safe** - Validated configuration with clear errors

### 🔐 Automatic Encryption
- **Field-level encryption** - Specify fields to encrypt
- **Transparent** - Automatic encrypt/decrypt
- **Secure** - Uses Fernet (symmetric encryption)
- **No code changes** - Enable with one config line

### ⚡ Multi-Level Caching
- **Redis support** - Distributed caching
- **Local cache** - In-memory fallback
- **Automatic invalidation** - Cache cleared on updates
- **Configurable TTL** - Per-model cache duration

### 🔍 Vector Search
- **Semantic search** - Find by meaning, not keywords
- **Automatic embeddings** - Generated on insert
- **Multiple backends** - Qdrant, Weaviate, Pinecone
- **Hybrid search** - Combine vector + keyword

### ✅ GDPR Compliance
- **Data export** - User data export in JSON
- **Right to deletion** - Complete data removal
- **Audit trails** - Track data operations
- **Configurable** - Specify exportable fields

### 🏗️ Modular Services
- **Session Service** - User session management
- **Research Service** - Store analysis and research
- **Notification Service** - User notifications
- **Tracker Service** - Event tracking and analytics
- **Stock Data Service** - Financial data fetching

### 🌐 Multi-App Support
- **Shared infrastructure** - One library, many apps
- **Data isolation** - Clear boundaries between apps
- **Consistent patterns** - Same API across applications

---

## Quick Start

### Installation

```bash
pip install timber-common
```

### Basic Example

```python
from timber.common import initialize_timber, get_model
from timber.common.services.persistence import session_service

# 1. Initialize Timber with your model configs
initialize_timber(
    model_config_dirs=['./data/models'],
    database_url='postgresql://localhost:5432/mydb'
)

# 2. Use services immediately
session_id = session_service.create_session(
    user_id='user-123',
    session_type='research',
    metadata={'symbol': 'AAPL'}
)

# 3. Or access models directly
Session = get_model('Session')
session = session_service.get_session(session_id)
print(f"Created session for {session.metadata['symbol']}")
```

### Complete Workflow Example

```python
from timber.common import initialize_timber
from timber.common.services.persistence import (
    session_service,
    research_service,
    notification_service
)

# Initialize
initialize_timber(model_config_dirs=['./data/models'])

# Create research session
session_id = session_service.create_session(
    user_id='user-123',
    session_type='research',
    metadata={'symbol': 'AAPL'}
)

# Save research (automatically encrypted if configured)
research_id = research_service.save_research(
    session_id=session_id,
    content={
        'company': 'Apple Inc.',
        'analysis': 'Strong fundamentals...',
        'recommendation': 'Buy'
    },
    research_type='fundamental'
)

# Notify user (automatically stored)
notification_service.create_notification(
    user_id='user-123',
    notification_type='research_complete',
    title='Analysis Complete',
    message='Your AAPL analysis is ready'
)

print(f"✅ Research workflow complete!")
```

### Vector Search Example

```python
from timber.common.services.vector import vector_service

# Semantic search (finds by meaning, not just keywords)
results = vector_service.search(
    query="companies with strong AI capabilities",
    collection_name="research_documents",
    limit=10
)

for result in results:
    print(f"{result['payload']['title']}: {result['score']:.3f}")
```

---

## Documentation

### 📚 How-To Guides
- [Getting Started](documentation/how_to/01_getting_started.md) - Setup and first model
- [Creating Models](documentation/how_to/02_creating_models.md) - YAML model definitions
- [Using Services](documentation/how_to/03_using_services.md) - Persistence services

### 🏛️ Design Guides
- [System Architecture](documentation/design_guides/01_system_architecture.md) - Overall design
- [Config-Driven Models](documentation/design_guides/02_config_driven_models.md) - Model factory pattern
- [Persistence Layer](documentation/design_guides/03_persistence_layer.md) - Database architecture
- [Vector Integration](documentation/design_guides/04_vector_integration.md) - Semantic search
- [Multi-App Support](documentation/design_guides/05_multi_app_support.md) - Multiple applications

### 📖 Full Documentation Index
See [DOCUMENTATION_INDEX.md](documentation/DOCUMENTATION_INDEX.md) for complete documentation structure.

---

## Requirements

- **Python:** 3.13+
- **Database:** PostgreSQL 12+
- **Optional:** Redis (for distributed caching)
- **Optional:** Qdrant/Weaviate/Pinecone (for vector search)

---

## Installation Options

### Basic Installation

```bash
pip install timber-common
```

### With Vector Search (Qdrant)

```bash
pip install timber-common[qdrant]
```

### With All Optional Features

```bash
pip install timber-common[all]
```

### Development Installation

```bash
git clone https://github.com/pumulo/timber-common.git
cd timber-common
poetry install
```

---

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Vector Database (optional)
QDRANT_URL=http://localhost:6333

# Encryption
ENCRYPTION_KEY=your-fernet-key-here

# Feature Flags
ENABLE_ENCRYPTION=true
ENABLE_VECTOR_SEARCH=true
ENABLE_GDPR=true
CACHE_ENABLED=true
```

### Model Configuration

Create YAML files in `data/models/`:

```yaml
# data/models/user_models.yaml
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
      
      - name: created_at
        type: DateTime
        default: utcnow
```

---

## Use Cases

### Financial Applications
- Trading platforms
- Research tools
- Portfolio management
- Market analysis

### Content Platforms
- Document management
- Knowledge bases
- Content recommendation
- Semantic search

### Data Analytics
- User behavior tracking
- Event analytics
- Session management
- Activity monitoring

### Multi-Tenant Applications
- SaaS platforms
- Enterprise applications
- Multiple product lines
- Isolated data domains

---

## Architecture

```
┌─────────────────────────────────────────┐
│          Your Application               │
└─────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│         Timber Library                  │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ Model Factory│  │  Services Layer │ │
│  └──────────────┘  └─────────────────┘ │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │   Encryption │  │  Vector Search  │ │
│  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│      Infrastructure                     │
│  PostgreSQL │ Redis │ Qdrant           │
└─────────────────────────────────────────┘
```

---

## Examples

### E-Commerce Platform

```yaml
models:
  - name: Product
    table_name: products
    
    vector_search:
      enabled: true
      content_field: description
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      - name: name
        type: String(255)
      - name: description
        type: Text
      - name: price
        type: Numeric(10, 2)
```

### Healthcare Application

```yaml
models:
  - name: PatientRecord
    table_name: patient_records
    
    encryption:
      enabled: true
      fields: [ssn, medical_history]
    
    gdpr:
      enabled: true
      user_id_field: patient_id
      export_fields: [name, date_of_birth, medical_history]
    
    columns:
      - name: id
        type: String(36)
        primary_key: true
      - name: patient_id
        type: String(36)
        foreign_key: patients.id
      - name: ssn
        type: String(11)
      - name: medical_history
        type: JSON
```

---

## Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=common --cov=modules

# Run specific test
poetry run pytest tests/test_models.py::test_create_model
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/pumulo/timber-common.git
cd timber-common

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Type check
poetry run mypy common modules
```

---

## Performance

Timber is designed for production use with:

- **Connection pooling** - Efficient database connections
- **Query optimization** - Built-in best practices
- **Caching** - Multi-level cache strategy
- **Batch operations** - Efficient bulk processing

### Benchmarks

```
Operation               Time (ms)    Notes
─────────────────────────────────────────────
Simple INSERT           1-5          Single record
Batch INSERT (100)      10-20        Bulk insert
SELECT by ID            1-2          Indexed lookup
Vector search           5-15         Semantic search
Cached query            < 1          Redis/local cache
```

---

## Roadmap

### Version 0.2.0 (Q1 2025)
- [ ] MySQL and SQLite support
- [ ] GraphQL API generation
- [ ] CLI tools for model management
- [ ] Enhanced monitoring dashboard

### Version 0.3.0 (Q2 2025)
- [ ] Real-time data streaming
- [ ] Advanced analytics
- [ ] Built-in vector store (no external DB required)
- [ ] Docker and Kubernetes templates

### Future
- [ ] Multi-database transactions
- [ ] Distributed tracing
- [ ] Auto-scaling recommendations
- [ ] Visual model designer

---

## Support

### Get Help
- **Documentation:** [Full docs](documentation/)
- **Issues:** [GitHub Issues](https://github.com/pumulo/timber-common/issues)
- **Email:** pumulo@gmail.com

### Commercial Support
For enterprise support, training, or consulting:
- Email: pumulo@gmail.com

---

## License

Timber is released under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2025 Pumulo Sikaneta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

See [LICENSE](LICENSE) file for full license text.

---

## Author

**Pumulo Sikaneta**

- Email: pumulo@gmail.com
- GitHub: [@pumulo](https://github.com/pumulo)
- Website: [Your website]

---

## Acknowledgments

Built with:
- [SQLAlchemy](https://www.sqlalchemy.org/) - The Python SQL toolkit
- [PostgreSQL](https://www.postgresql.org/) - The world's most advanced open source database
- [FastEmbed](https://github.com/qdrant/fastembed) - Fast embedding generation
- [Poetry](https://python-poetry.org/) - Python dependency management

---

## Citation

If you use Timber in academic research, please cite:

```bibtex
@software{timber2025,
  author = {Sikaneta, Pumulo},
  title = {Timber: Configuration-Driven Persistence Library},
  year = {2025},
  url = {https://github.com/pumulo/timber-common},
  version = {0.1.0}
}
```

---

## Star History

If you find Timber useful, please star the repository! ⭐

---

**Made with ❤️ by Pumulo Sikaneta**

**Copyright © 2025 Pumulo Sikaneta. All rights reserved.**