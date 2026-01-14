# Changelog

All notable changes to Timber will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-19

### Added - Initial Release

#### Core Features
- **Config-Driven Models**: Define SQLAlchemy models using YAML configuration files
- **Dynamic Model Factory**: Automatically generate model classes from YAML at runtime
- **Model Registry**: Global model registry with `get_model()` accessor
- **Relationship Resolution**: Automatic relationship building with dependency management

#### Database Management
- **Connection Pooling**: Optimized PostgreSQL connection pooling with QueuePool
- **Session Management**: Context manager for automatic transaction handling
- **Transaction Support**: Automatic commit/rollback with `session_scope()`
- **Health Checks**: Database connectivity monitoring
- **Migration Support**: Schema evolution with Alembic integration

#### Service Layer
- **Session Service**: Manage user sessions across applications
- **Research Service**: Store and query research data and analysis
- **Notification Service**: User notification system with read tracking
- **Tracker Service**: Event tracking and user activity analytics
- **Stock Data Service**: Financial data fetching from multiple sources

#### Feature Services
- **Encryption Service**: Field-level encryption with Fernet
- **Cache Service**: Multi-level caching (Redis + local)
- **Vector Search Service**: Semantic search with embeddings
- **GDPR Service**: Data export and deletion for compliance

#### Vector Search Integration
- **Automatic Embedding Generation**: Using sentence-transformers
- **Vector Database Support**: Qdrant, Weaviate, Pinecone integration
- **Semantic Search**: Find similar documents by meaning
- **Hybrid Search**: Combine vector and keyword search
- **Batch Processing**: Efficient batch embedding generation

#### Data Sources
- **Yahoo Finance**: Historical and real-time stock data
- **Alpha Vantage**: Company fundamentals and financials
- **Polygon.io**: Market data and news
- **SEC Edgar**: Company filings and documents

#### Security & Compliance
- **Field-Level Encryption**: Automatic encryption of sensitive fields
- **GDPR Compliance**: Data export, deletion, and audit trails
- **Secure Configuration**: Environment variable management
- **Connection Security**: SSL/TLS support for database connections

#### Multi-Application Support
- **Application Context**: Separate contexts for different apps
- **Session Type Filtering**: Isolate data by application
- **Shared Infrastructure**: Common database, cache, and vector store
- **Independent Deployment**: Apps deploy separately

#### Documentation
- **How-To Guides**: Step-by-step instructions for common tasks
  - Getting Started
  - Creating Models
  - Using Services
- **Design Guides**: Architecture and design documentation
  - System Architecture
  - Config-Driven Models
  - Persistence Layer
  - Vector Integration
  - Multi-App Support
- **API Documentation**: Comprehensive API reference
- **Code Examples**: Working examples for all features

#### Developer Tools
- **Type Hints**: Full type annotation support
- **Testing Framework**: pytest integration with fixtures
- **Code Quality**: Black, isort, mypy configuration
- **Error Handling**: Consistent error types and handling patterns

### Technical Details

#### Supported Python Versions
- Python 3.13+

#### Supported Databases
- PostgreSQL 12+
- pgvector extension for vector support

#### Supported Vector Stores
- Qdrant (recommended)
- Weaviate
- Pinecone

#### Embedding Models
- BAAI/bge-small-en-v1.5 (default)
- sentence-transformers/all-MiniLM-L6-v2
- Custom models supported

### Dependencies
- SQLAlchemy 2.0.36+
- PostgreSQL driver (psycopg2-binary)
- Redis 6.4.0+
- Pydantic 2.11.9+
- FastEmbed 0.7.3+
- Cryptography 46.0.2+
- See pyproject.toml for complete dependency list

### Known Limitations
- Requires PostgreSQL (other databases not yet supported)
- Python 3.13+ only
- Vector search requires external vector database

### Breaking Changes
- None (initial release)

### Migration Guide
- None (initial release)

---

## [Unreleased]

### Planned Features
- MySQL and SQLite support
- Built-in vector store option (no external database required)
- GraphQL API generation
- Real-time data streaming
- Advanced analytics dashboard
- CLI tools for model management
- Docker deployment templates
- Kubernetes manifests

---

## Version History

- **0.1.0** (2025-10-19) - Initial public release

---

## Copyright

Copyright (c) 2025 Pumulo Sikaneta. All rights reserved.

This software is released under the MIT License.
See LICENSE file for details.

## Author

**Pumulo Sikaneta**
- Email: pumulo@gmail.com
- GitHub: [@pumulo](https://github.com/pumulo)

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## Support

For bugs, feature requests, or questions:
- GitHub Issues: https://github.com/pumulo/timber-common/issues
- Email: pumulo@gmail.com