# Caching Strategies Best Practices

**Complete guide to implementing effective multi-level caching in Timber**

---

## Table of Contents

1. [Overview](#overview)
2. [Cache Levels](#cache-levels)
3. [Caching Strategies](#caching-strategies)
4. [Implementation Patterns](#implementation-patterns)
5. [Cache Invalidation](#cache-invalidation)
6. [Performance Optimization](#performance-optimization)
7. [Monitoring](#monitoring)
8. [Common Patterns](#common-patterns)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Caching is critical for performance in data-intensive applications. Timber supports multiple caching strategies from simple in-memory caching to distributed Redis caching.

### Why Caching Matters

✅ **Reduced Latency**: Serve data from cache instead of database/API  
✅ **Lower Costs**: Reduce API calls to paid services  
✅ **Better Scalability**: Handle more requests with same resources  
✅ **Improved UX**: Faster response times for users  
✅ **Resilience**: Serve cached data when external services are down

### Cache Performance Impact

```
Database Query:     50-100ms
API Call:           200-1000ms
Memory Cache:       <1ms
Redis Cache:        1-5ms
File Cache:         5-10ms
```

---

## Cache Levels

### Level 1: Application Memory (L1)

**Fastest, smallest capacity, process-specific**

```python
from functools import lru_cache

class L1Cache:
    """In-memory LRU cache."""
    
    @lru_cache(maxsize=1000)
    def get_company_info(self, symbol):
        """Cache company info in memory."""
        return self._fetch_company_info(symbol)
    
    def _fetch_company_info(self, symbol):
        # Expensive operation
        return stock_data_service.fetch_company_info(symbol)

# Usage
cache = L1Cache()
info = cache.get_company_info('AAPL')  # Cached in memory
```

**Best for:**
- Frequently accessed data
- Small data objects
- Single-process applications
- Read-heavy workloads

### Level 2: Distributed Cache (L2)

**Fast, larger capacity, shared across processes**

```python
import redis
import json

class L2Cache:
    """Redis distributed cache."""
    
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    def get(self, key):
        """Get from Redis."""
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(self, key, value, ttl=3600):
        """Set in Redis with TTL."""
        self.redis.setex(key, ttl, json.dumps(value))
    
    def delete(self, key):
        """Delete from Redis."""
        self.redis.delete(key)

# Usage
cache = L2Cache()
cache.set('company:AAPL', {'name': 'Apple Inc'}, ttl=3600)
info = cache.get('company:AAPL')
```

**Best for:**
- Shared data across multiple processes
- Medium-sized objects
- Session data
- Distributed systems

### Level 3: File-Based Cache (L3)

**Slower, largest capacity, persistent**

```python
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

class L3Cache:
    """File-based persistent cache."""
    
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get(self, key):
        """Get from file cache."""
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        # Check if expired
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        expiry = datetime.fromisoformat(data['expiry'])
        if datetime.now() > expiry:
            cache_file.unlink()
            return None
        
        return data['value']
    
    def set(self, key, value, ttl=86400):
        """Set in file cache."""
        cache_file = self.cache_dir / f"{key}.json"
        
        data = {
            'value': value,
            'expiry': (datetime.now() + timedelta(seconds=ttl)).isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    
    def delete(self, key):
        """Delete from file cache."""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()

# Usage
cache = L3Cache()
cache.set('historical:AAPL', df.to_dict(), ttl=86400)
data = cache.get('historical:AAPL')
```

**Best for:**
- Large data objects
- Long-term caching
- Cold storage
- Backup/fallback cache

---

## Caching Strategies

### Strategy 1: Cache-Aside (Lazy Loading)

**Load data into cache on demand**

```python
class CacheAsideService:
    """Implement cache-aside pattern."""
    
    def __init__(self, cache, database):
        self.cache = cache
        self.database = database
    
    def get_data(self, key):
        """Get data with cache-aside."""
        # 1. Check cache first
        cached = self.cache.get(key)
        if cached:
            return cached
        
        # 2. Cache miss - fetch from database
        data = self.database.query(key)
        
        if data:
            # 3. Store in cache for next time
            self.cache.set(key, data, ttl=3600)
        
        return data
    
    def update_data(self, key, value):
        """Update data and invalidate cache."""
        # 1. Update database
        self.database.update(key, value)
        
        # 2. Invalidate cache
        self.cache.delete(key)

# Usage
service = CacheAsideService(redis_cache, database)
data = service.get_data('user:123')  # Cached after first fetch
```

### Strategy 2: Write-Through Cache

**Write to cache and database simultaneously**

```python
class WriteThroughService:
    """Implement write-through caching."""
    
    def __init__(self, cache, database):
        self.cache = cache
        self.database = database
    
    def save_data(self, key, value):
        """Save to both cache and database."""
        # 1. Write to database
        self.database.save(key, value)
        
        # 2. Write to cache
        self.cache.set(key, value, ttl=3600)
    
    def get_data(self, key):
        """Get from cache (always fresh)."""
        cached = self.cache.get(key)
        if cached:
            return cached
        
        # Fallback to database if cache miss
        data = self.database.query(key)
        if data:
            self.cache.set(key, data, ttl=3600)
        
        return data
```

### Strategy 3: Write-Behind Cache (Write-Back)

**Write to cache immediately, database asynchronously**

```python
import queue
import threading

class WriteBehindService:
    """Implement write-behind caching."""
    
    def __init__(self, cache, database):
        self.cache = cache
        self.database = database
        self.write_queue = queue.Queue()
        self._start_background_writer()
    
    def _start_background_writer(self):
        """Start background thread to write to database."""
        def writer():
            while True:
                key, value = self.write_queue.get()
                try:
                    self.database.save(key, value)
                except Exception as e:
                    logger.error(f"Failed to write {key}: {e}")
                self.write_queue.task_done()
        
        thread = threading.Thread(target=writer, daemon=True)
        thread.start()
    
    def save_data(self, key, value):
        """Save to cache immediately, database async."""
        # 1. Write to cache immediately
        self.cache.set(key, value, ttl=3600)
        
        # 2. Queue database write
        self.write_queue.put((key, value))
    
    def get_data(self, key):
        """Get from cache first."""
        return self.cache.get(key) or self.database.query(key)
```

### Strategy 4: Refresh-Ahead Cache

**Proactively refresh cache before expiration**

```python
import time
from datetime import datetime, timedelta

class RefreshAheadCache:
    """Implement refresh-ahead caching."""
    
    def __init__(self, cache, fetcher, refresh_threshold=0.8):
        self.cache = cache
        self.fetcher = fetcher
        self.refresh_threshold = refresh_threshold
        self._metadata = {}  # Track creation time and TTL
    
    def get(self, key, ttl=3600):
        """Get from cache with proactive refresh."""
        # Get cached value
        cached = self.cache.get(key)
        
        if cached:
            # Check if approaching expiration
            if self._should_refresh(key, ttl):
                # Refresh in background
                self._refresh_async(key, ttl)
            
            return cached
        
        # Cache miss - fetch and cache
        value = self.fetcher(key)
        if value:
            self._set_with_metadata(key, value, ttl)
        
        return value
    
    def _should_refresh(self, key, ttl):
        """Check if cache entry should be refreshed."""
        if key not in self._metadata:
            return False
        
        created_at, cache_ttl = self._metadata[key]
        age = (datetime.now() - created_at).total_seconds()
        
        # Refresh if past threshold (e.g., 80% of TTL)
        return age > (cache_ttl * self.refresh_threshold)
    
    def _set_with_metadata(self, key, value, ttl):
        """Set cache value with metadata."""
        self.cache.set(key, value, ttl=ttl)
        self._metadata[key] = (datetime.now(), ttl)
    
    def _refresh_async(self, key, ttl):
        """Refresh cache asynchronously."""
        def refresh():
            value = self.fetcher(key)
            if value:
                self._set_with_metadata(key, value, ttl)
        
        thread = threading.Thread(target=refresh, daemon=True)
        thread.start()
```

---

## Implementation Patterns

### Pattern 1: Multi-Level Cache

**Combine L1, L2, and L3 caches**

```python
class MultiLevelCache:
    """Three-level cache hierarchy."""
    
    def __init__(self):
        self.l1 = {}  # Memory
        self.l2 = redis.Redis()  # Redis
        self.l3 = FileCache('.cache')  # Disk
    
    def get(self, key):
        """Get from L1 → L2 → L3 → Source."""
        # Try L1 (fastest)
        if key in self.l1:
            return self.l1[key]
        
        # Try L2
        value = self.l2.get(key)
        if value:
            # Populate L1
            self.l1[key] = json.loads(value)
            return self.l1[key]
        
        # Try L3
        value = self.l3.get(key)
        if value:
            # Populate L2 and L1
            self.l2.setex(key, 3600, json.dumps(value))
            self.l1[key] = value
            return value
        
        return None
    
    def set(self, key, value, ttl=3600):
        """Set in all levels."""
        # L1
        self.l1[key] = value
        
        # L2
        self.l2.setex(key, ttl, json.dumps(value))
        
        # L3
        self.l3.set(key, value, ttl=ttl * 24)  # Longer TTL
    
    def delete(self, key):
        """Delete from all levels."""
        if key in self.l1:
            del self.l1[key]
        self.l2.delete(key)
        self.l3.delete(key)
```

### Pattern 2: Time-Based Invalidation

```python
class TimeBasedCache:
    """Cache with automatic time-based invalidation."""
    
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    def get(self, key):
        """Get with expiry check."""
        if key not in self.cache:
            return None
        
        # Check expiry
        if datetime.now() > self.expiry[key]:
            del self.cache[key]
            del self.expiry[key]
            return None
        
        return self.cache[key]
    
    def set(self, key, value, ttl=3600):
        """Set with expiry."""
        self.cache[key] = value
        self.expiry[key] = datetime.now() + timedelta(seconds=ttl)
    
    def cleanup_expired(self):
        """Remove all expired entries."""
        now = datetime.now()
        expired_keys = [
            k for k, exp in self.expiry.items()
            if now > exp
        ]
        
        for key in expired_keys:
            del self.cache[key]
            del self.expiry[key]
        
        return len(expired_keys)
```

### Pattern 3: Size-Based Eviction (LRU)

```python
from collections import OrderedDict

class LRUCache:
    """LRU cache with size limit."""
    
    def __init__(self, maxsize=1000):
        self.cache = OrderedDict()
        self.maxsize = maxsize
    
    def get(self, key):
        """Get and move to end (most recent)."""
        if key not in self.cache:
            return None
        
        # Move to end
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key, value):
        """Set and enforce size limit."""
        if key in self.cache:
            # Move to end
            self.cache.move_to_end(key)
        else:
            # Add new item
            self.cache[key] = value
            
            # Evict oldest if over limit
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)
```

### Pattern 4: Cache Stampede Prevention

```python
import threading
from collections import defaultdict

class StampedePreventionCache:
    """Prevent cache stampede with locking."""
    
    def __init__(self, cache, fetcher):
        self.cache = cache
        self.fetcher = fetcher
        self._locks = defaultdict(threading.Lock)
    
    def get(self, key, ttl=3600):
        """Get with stampede prevention."""
        # Try cache first
        cached = self.cache.get(key)
        if cached:
            return cached
        
        # Cache miss - use lock to prevent stampede
        with self._locks[key]:
            # Double-check cache (another thread might have filled it)
            cached = self.cache.get(key)
            if cached:
                return cached
            
            # Fetch and cache
            value = self.fetcher(key)
            if value:
                self.cache.set(key, value, ttl=ttl)
            
            return value
```

---

## Cache Invalidation

### Event-Based Invalidation

```python
class EventBasedCache:
    """Cache with event-driven invalidation."""
    
    def __init__(self, cache):
        self.cache = cache
        self.dependencies = defaultdict(set)  # key -> dependent keys
    
    def get(self, key):
        """Get from cache."""
        return self.cache.get(key)
    
    def set(self, key, value, depends_on=None, ttl=3600):
        """Set with dependencies."""
        self.cache.set(key, value, ttl=ttl)
        
        # Track dependencies
        if depends_on:
            for dep_key in depends_on:
                self.dependencies[dep_key].add(key)
    
    def invalidate(self, key):
        """Invalidate key and all dependents."""
        # Delete the key
        self.cache.delete(key)
        
        # Delete all dependent keys
        if key in self.dependencies:
            for dependent_key in self.dependencies[key]:
                self.cache.delete(dependent_key)
                self.invalidate(dependent_key)  # Recursive
            
            del self.dependencies[key]

# Usage
cache = EventBasedCache(redis_cache)

# Set with dependencies
cache.set('user:123', user_data, depends_on=['users'])
cache.set('user:123:profile', profile_data, depends_on=['user:123'])

# Invalidate user - cascades to profile
cache.invalidate('user:123')  # Also invalidates user:123:profile
```

### Tag-Based Invalidation

```python
class TagBasedCache:
    """Cache with tag-based invalidation."""
    
    def __init__(self, cache):
        self.cache = cache
        self.tags = defaultdict(set)  # tag -> set of keys
    
    def set(self, key, value, tags=None, ttl=3600):
        """Set with tags."""
        self.cache.set(key, value, ttl=ttl)
        
        # Track tags
        if tags:
            for tag in tags:
                self.tags[tag].add(key)
    
    def get(self, key):
        """Get from cache."""
        return self.cache.get(key)
    
    def invalidate_tag(self, tag):
        """Invalidate all keys with tag."""
        if tag in self.tags:
            for key in self.tags[tag]:
                self.cache.delete(key)
            del self.tags[tag]

# Usage
cache = TagBasedCache(redis_cache)

# Set with tags
cache.set('stock:AAPL', aapl_data, tags=['stocks', 'tech'])
cache.set('stock:GOOGL', googl_data, tags=['stocks', 'tech'])
cache.set('stock:JPM', jpm_data, tags=['stocks', 'finance'])

# Invalidate all tech stocks
cache.invalidate_tag('tech')  # Clears AAPL and GOOGL
```

---

## Performance Optimization

### 1. Batch Operations

```python
class BatchCacheService:
    """Cache service with batch operations."""
    
    def __init__(self, cache):
        self.cache = cache
    
    def get_many(self, keys):
        """Get multiple keys efficiently."""
        if hasattr(self.cache, 'mget'):
            # Redis mget
            values = self.cache.mget(keys)
            return dict(zip(keys, values))
        else:
            # Fallback to individual gets
            return {key: self.cache.get(key) for key in keys}
    
    def set_many(self, mapping, ttl=3600):
        """Set multiple key-value pairs."""
        if hasattr(self.cache, 'mset'):
            # Redis mset
            self.cache.mset(mapping)
            # Set TTL for each
            for key in mapping:
                self.cache.expire(key, ttl)
        else:
            # Fallback to individual sets
            for key, value in mapping.items():
                self.cache.set(key, value, ttl=ttl)
```

### 2. Compression

```python
import zlib
import json

class CompressedCache:
    """Cache with compression for large values."""
    
    def __init__(self, cache, compress_threshold=1024):
        self.cache = cache
        self.compress_threshold = compress_threshold
    
    def set(self, key, value, ttl=3600):
        """Set with compression."""
        serialized = json.dumps(value).encode()
        
        # Compress if over threshold
        if len(serialized) > self.compress_threshold:
            compressed = zlib.compress(serialized)
            self.cache.set(f"{key}:compressed", compressed, ttl=ttl)
        else:
            self.cache.set(key, serialized, ttl=ttl)
    
    def get(self, key):
        """Get and decompress if needed."""
        # Try compressed version first
        compressed = self.cache.get(f"{key}:compressed")
        if compressed:
            decompressed = zlib.decompress(compressed)
            return json.loads(decompressed)
        
        # Try uncompressed
        value = self.cache.get(key)
        if value:
            return json.loads(value)
        
        return None
```

### 3. Conditional Caching

```python
class ConditionalCache:
    """Cache only if conditions are met."""
    
    def __init__(self, cache):
        self.cache = cache
    
    def set(self, key, value, ttl=3600, conditions=None):
        """Set with conditions."""
        # Default conditions
        if conditions is None:
            conditions = {
                'max_size': 10000,  # bytes
                'min_value': True,  # non-empty
            }
        
        # Check conditions
        if conditions.get('max_size'):
            size = len(str(value))
            if size > conditions['max_size']:
                logger.warning(f"Value too large to cache: {size} bytes")
                return False
        
        if conditions.get('min_value'):
            if not value:
                logger.debug("Empty value, not caching")
                return False
        
        # Cache if all conditions met
        self.cache.set(key, value, ttl=ttl)
        return True
```

---

## Monitoring

### Cache Metrics

```python
class MonitoredCache:
    """Cache with metrics tracking."""
    
    def __init__(self, cache):
        self.cache = cache
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
    
    def get(self, key):
        """Get with hit/miss tracking."""
        value = self.cache.get(key)
        
        if value is not None:
            self.hits += 1
        else:
            self.misses += 1
        
        return value
    
    def set(self, key, value, ttl=3600):
        """Set with tracking."""
        self.cache.set(key, value, ttl=ttl)
        self.sets += 1
    
    def delete(self, key):
        """Delete with tracking."""
        self.cache.delete(key)
        self.deletes += 1
    
    def get_stats(self):
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'hit_rate': hit_rate,
            'total_requests': total
        }
    
    def reset_stats(self):
        """Reset statistics."""
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
```

---

## Common Patterns

### Pattern: Probabilistic Early Expiration

```python
import random

class ProbabilisticCache:
    """Cache with probabilistic early expiration to prevent stampede."""
    
    def __init__(self, cache, fetcher):
        self.cache = cache
        self.fetcher = fetcher
        self._metadata = {}
    
    def get(self, key, ttl=3600, beta=1.0):
        """Get with probabilistic early expiration."""
        cached = self.cache.get(key)
        
        if cached is None:
            # Cache miss - fetch and cache
            value = self.fetcher(key)
            self._set_with_metadata(key, value, ttl)
            return value
        
        # Check for probabilistic early expiration
        if self._should_recompute(key, ttl, beta):
            # Recompute in background
            self._recompute_async(key, ttl)
        
        return cached
    
    def _should_recompute(self, key, ttl, beta):
        """Determine if should recompute early."""
        if key not in self._metadata:
            return False
        
        created_at = self._metadata[key]
        age = (datetime.now() - created_at).total_seconds()
        
        # XFetch algorithm: probabilistic early expiration
        # P(recompute) increases as expiry approaches
        delta = ttl - age
        p = beta * random.random() * ttl
        
        return delta < p
    
    def _set_with_metadata(self, key, value, ttl):
        """Set with metadata."""
        self.cache.set(key, value, ttl=ttl)
        self._metadata[key] = datetime.now()
    
    def _recompute_async(self, key, ttl):
        """Recompute value asynchronously."""
        def recompute():
            value = self.fetcher(key)
            self._set_with_metadata(key, value, ttl)
        
        thread = threading.Thread(target=recompute, daemon=True)
        thread.start()
```

---

## Troubleshooting

### Issue: Low Hit Rate

**Symptoms**: Cache hit rate < 50%

**Diagnosis**:
```python
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")

if stats['hit_rate'] < 0.5:
    # Analyze access patterns
    # Check TTL settings
    # Verify cache is large enough
```

**Solutions**:
- Increase cache size
- Adjust TTL (longer for stable data)
- Implement prefetching
- Use appropriate cache level

### Issue: Memory Exhaustion

**Symptoms**: Out of memory errors, slow performance

**Solutions**:
```python
# 1. Implement size limits
cache = LRUCache(maxsize=10000)

# 2. Use compression
cache = CompressedCache(redis_cache)

# 3. Implement eviction policy
def evict_if_needed():
    if cache.size() > MAX_SIZE:
        cache.evict_lru()
```

### Issue: Stale Data

**Symptoms**: Users see outdated information

**Solutions**:
```python
# 1. Reduce TTL
cache.set(key, value, ttl=300)  # 5 minutes instead of 1 hour

# 2. Implement cache invalidation
def update_data(key, value):
    database.update(key, value)
    cache.delete(key)  # Invalidate

# 3. Use versioning
version = get_current_version()
cache.set(f"{key}:v{version}", value)
```

---

## Summary

### Key Takeaways

1. **Multi-Level**: Use L1 (memory) → L2 (Redis) → L3 (disk)
2. **Strategy**: Choose appropriate strategy (cache-aside, write-through, etc.)
3. **Invalidation**: Implement proper cache invalidation
4. **Monitoring**: Track hit rates and performance
5. **Optimization**: Use batching, compression, conditional caching

### Caching Checklist

- [ ] Appropriate cache level chosen
- [ ] TTL configured based on data volatility
- [ ] Cache invalidation strategy implemented
- [ ] Monitoring and metrics in place
- [ ] Cache stampede prevention considered
- [ ] Memory limits enforced
- [ ] Compression for large values
- [ ] Documentation of cache keys and TTLs

---

**For more information:**
- [Performance Optimization](06_performance_optimization.md)
- [Service Architecture](02_service_architecture.md)
- [Data Fetching Strategies](03_data_fetching_strategies.md)

---

**Last Updated**: October 19, 2024  
**Version**: 0.2.0