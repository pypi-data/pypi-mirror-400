# Performance Optimization Best Practices

**Comprehensive guide to optimizing Timber performance**

## Table of Contents
1. [Overview](#overview)
2. [Database Optimization](#database-optimization)
3. [Query Optimization](#query-optimization)
4. [Caching Strategies](#caching-strategies)
5. [Batch Processing](#batch-processing)
6. [Connection Pooling](#connection-pooling)
7. [Profiling and Monitoring](#profiling-and-monitoring)

## Overview

Performance optimization is critical for production applications. This guide covers best practices for optimizing Timber-based applications.

### Performance Goals
- Database queries < 50ms
- API responses < 200ms
- Memory usage < 1GB per process
- Handle 1000+ requests/second

## Database Optimization

### 1. Proper Indexing

```yaml
# Model configuration with indexes
models:
  - name: StockResearchSession
    table_name: stock_research_sessions
    
    columns:
      - name: user_id
        type: String(36)
        index: true  # Single column index
      
      - name: symbol
        type: String(10)
        index: true
      
      - name: created_at
        type: DateTime
        index: true
    
    indexes:
      # Composite index for common queries
      - columns: [user_id, created_at]
        name: idx_user_created
      
      - columns: [symbol, status]
        name: idx_symbol_status
```

### 2. Use Exists Instead of Count

**✅ GOOD**:
```python
# Check if records exist
exists = session.query(Model).filter_by(user_id=user_id).limit(1).scalar() is not None
```

**❌ BAD**:
```python
# Count all records (slow!)
count = session.query(Model).filter_by(user_id=user_id).count()
exists = count > 0
```

### 3. Eager Loading for Relationships

```python
# Avoid N+1 queries with eager loading
from sqlalchemy.orm import joinedload

sessions = session.query(StockResearch)\
    .options(joinedload(StockResearch.user))\
    .options(joinedload(StockResearch.notifications))\
    .filter_by(user_id=user_id)\
    .all()
```

## Query Optimization

### 1. Select Only Needed Columns

```python
# Load only specific columns
results = session.query(
    Model.id,
    Model.name,
    Model.created_at
).filter_by(user_id=user_id).all()
```

### 2. Use Bulk Operations

```python
# Bulk insert
session.bulk_insert_mappings(Model, [
    {'id': '1', 'name': 'A'},
    {'id': '2', 'name': 'B'},
    {'id': '3', 'name': 'C'},
])

# Bulk update
session.bulk_update_mappings(Model, [
    {'id': '1', 'status': 'completed'},
    {'id': '2', 'status': 'completed'},
])
```

### 3. Pagination

```python
def get_paginated_sessions(user_id, page=1, per_page=50):
    """Get paginated sessions."""
    query = session.query(StockResearch).filter_by(user_id=user_id)
    
    total = query.count()
    sessions = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'sessions': sessions,
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page
    }
```

## Caching Strategies

### 1. Query Result Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_company_info(symbol):
    """Cache company info."""
    with db_manager.session_scope() as session:
        return session.query(Company).filter_by(symbol=symbol).first()
```

### 2. Multi-Level Caching

```python
class CachedDataService:
    def get_data(self, key):
        # L1: Memory
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # L2: Redis
        value = self.redis.get(key)
        if value:
            self.memory_cache[key] = value
            return value
        
        # L3: Database
        value = self.db.query(key)
        if value:
            self.redis.setex(key, 3600, value)
            self.memory_cache[key] = value
        
        return value
```

## Batch Processing

### 1. Process in Chunks

```python
def process_large_dataset(symbols, chunk_size=100):
    """Process large dataset in chunks."""
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i + chunk_size]
        process_chunk(chunk)
        time.sleep(0.1)  # Rate limiting
```

### 2. Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def fetch_multiple_symbols(symbols):
    """Fetch data for multiple symbols in parallel."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_data, symbols))
    return results
```

## Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,         # Number of connections to keep
    max_overflow=20,      # Max extra connections
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=3600,    # Recycle connections after 1 hour
)
```

## Profiling and Monitoring

### 1. Query Profiling

```python
import time
import logging

logger = logging.getLogger(__name__)

def profile_query(func):
    """Decorator to profile query performance."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        if duration > 0.1:  # Log slow queries (>100ms)
            logger.warning(f"Slow query: {func.__name__} took {duration:.3f}s")
        
        return result
    return wrapper
```

### 2. Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record_metric(self, operation, duration):
        self.metrics[operation].append(duration)
    
    def get_stats(self, operation):
        if operation not in self.metrics:
            return None
        
        durations = self.metrics[operation]
        return {
            'count': len(durations),
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
            'p95': sorted(durations)[int(len(durations) * 0.95)]
        }
```

## Summary

### Key Takeaways
1. **Index Wisely**: Create indexes for frequently queried columns
2. **Cache Effectively**: Use multi-level caching
3. **Batch Operations**: Process data in batches
4. **Pool Connections**: Use connection pooling
5. **Monitor Performance**: Track and profile queries
6. **Optimize Queries**: Select only needed data

### Performance Checklist
- [ ] Proper indexes on all filtered columns
- [ ] Connection pooling configured
- [ ] Caching implemented for expensive operations
- [ ] Batch processing for large datasets
- [ ] Query profiling enabled
- [ ] Performance monitoring in place

---
**Last Updated**: October 19, 2024  
**Version**: 0.2.0