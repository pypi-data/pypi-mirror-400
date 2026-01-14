# timber/common/services/inventory/cached_capabilities.py
"""
Cached Capabilities Service

Adds intelligent caching to the capabilities inventory service.
Provides multi-level caching:
- In-memory cache for instant access
- Redis cache for distributed systems
- File-based cache for persistence

This dramatically improves performance for repeated inventory queries.
"""

import json
import hashlib
import pickle
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging

from common.config import config, Config
from .available_capabilities import AvailableCapabilitiesService

logger = logging.getLogger(__name__)


class CachedCapabilitiesService(AvailableCapabilitiesService):
    """
    Capabilities service with intelligent multi-level caching.
    
    Caching Strategy:
    - Level 1 (Memory): Instant access, lost on restart
    - Level 2 (Redis): Distributed cache, shared across instances
    - Level 3 (File): Persistent cache, survives restarts
    
    Cache Keys:
    - Based on model directories and configuration
    - Invalidated when models change
    
    Usage:
        service = CachedCapabilitiesService(
            services={'session_service': session_service},
            enable_cache=True,
            cache_ttl_hours=24
        )
        
        # First call: slow (generates inventory)
        inventory = service.generate_full_inventory()
        
        # Second call: instant (from cache)
        inventory = service.generate_full_inventory()
    """
    
    def __init__(
        self,
        services: Optional[Dict[str, Any]] = None,
        enable_cache: bool = True,
        cache_ttl_hours: int = 24,
        cache_dir: Optional[Path] = None,
        enable_memory_cache: bool = True,
        enable_redis_cache: bool = None,
        enable_file_cache: bool = True
    ):
        """
        Initialize cached capabilities service.
        
        Args:
            services: Optional dictionary of services to inventory
            enable_cache: Enable caching (master switch)
            cache_ttl_hours: Cache time-to-live in hours
            cache_dir: Directory for file-based cache
            enable_memory_cache: Enable in-memory caching (Level 1)
            enable_redis_cache: Enable Redis caching (Level 2, auto-detects if None)
            enable_file_cache: Enable file-based caching (Level 3)
        """
        super().__init__(services=services)
        
        self.enable_cache = enable_cache
        self.cache_ttl_hours = cache_ttl_hours
        self.cache_ttl_seconds = cache_ttl_hours * 3600
        
        # Cache directory
        self.cache_dir = cache_dir or Path('.timber_cache')
        if enable_file_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache levels
        self.enable_memory_cache = enable_memory_cache
        self.enable_redis_cache = enable_redis_cache if enable_redis_cache is not None else config.REDIS_ENABLED
        self.enable_file_cache = enable_file_cache
        
        # Memory cache (Level 1)
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Redis cache (Level 2)
        self._redis_client = None
        if self.enable_redis_cache:
            self._init_redis()
        
        logger.info(f"CachedCapabilitiesService initialized:")
        logger.info(f"  Cache enabled: {enable_cache}")
        logger.info(f"  TTL: {cache_ttl_hours} hours")
        logger.info(f"  Memory cache: {enable_memory_cache}")
        logger.info(f"  Redis cache: {self.enable_redis_cache}")
        logger.info(f"  File cache: {enable_file_cache}")
    
    # ========================================================================
    # Cache Initialization
    # ========================================================================
    
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            import redis
            self._redis_client = redis.from_url(
                config.REDIS_URL,
                password=config.REDIS_PASSWORD,
                decode_responses=False  # We'll handle serialization
            )
            # Test connection
            self._redis_client.ping()
            logger.info("✓ Redis cache connected")
        except ImportError:
            logger.warning("✗ Redis package not installed, disabling Redis cache")
            self.enable_redis_cache = False
        except Exception as e:
            logger.warning(f"✗ Redis connection failed: {e}, disabling Redis cache")
            self.enable_redis_cache = False
    
    # ========================================================================
    # Cache Key Generation
    # ========================================================================
    
    def _generate_cache_key(self, operation: str, **kwargs) -> str:
        """
        Generate cache key based on operation and parameters.
        
        Args:
            operation: Operation name (e.g., 'full_inventory', 'model_info')
            **kwargs: Parameters that affect the result
        
        Returns:
            Cache key string
        """
        # Create stable key from parameters
        key_parts = [operation]
        
        # Add sorted kwargs
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (list, dict)):
                v = json.dumps(v, sort_keys=True)
            key_parts.append(f"{k}={v}")
        
        key_string = ":".join(key_parts)
        
        # Hash for consistent length
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        
        return f"timber:capabilities:{operation}:{key_hash}"
    
    # ========================================================================
    # Cache Operations
    # ========================================================================
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from cache (tries all levels).
        
        Args:
            cache_key: Cache key
        
        Returns:
            Cached value or None
        """
        if not self.enable_cache:
            return None
        
        # Level 1: Memory cache (fastest)
        if self.enable_memory_cache:
            cached = self._get_from_memory(cache_key)
            if cached:
                logger.debug(f"✓ Cache hit (memory): {cache_key}")
                return cached
        
        # Level 2: Redis cache (distributed)
        if self.enable_redis_cache:
            cached = self._get_from_redis(cache_key)
            if cached:
                logger.debug(f"✓ Cache hit (Redis): {cache_key}")
                # Populate memory cache
                if self.enable_memory_cache:
                    self._set_in_memory(cache_key, cached)
                return cached
        
        # Level 3: File cache (persistent)
        if self.enable_file_cache:
            cached = self._get_from_file(cache_key)
            if cached:
                logger.debug(f"✓ Cache hit (file): {cache_key}")
                # Populate upper levels
                if self.enable_redis_cache:
                    self._set_in_redis(cache_key, cached)
                if self.enable_memory_cache:
                    self._set_in_memory(cache_key, cached)
                return cached
        
        logger.debug(f"✗ Cache miss: {cache_key}")
        return None
    
    def _set_in_cache(self, cache_key: str, value: Dict[str, Any]):
        """
        Set value in all enabled cache levels.
        
        Args:
            cache_key: Cache key
            value: Value to cache
        """
        if not self.enable_cache:
            return
        
        if self.enable_memory_cache:
            self._set_in_memory(cache_key, value)
        
        if self.enable_redis_cache:
            self._set_in_redis(cache_key, value)
        
        if self.enable_file_cache:
            self._set_in_file(cache_key, value)
        
        logger.debug(f"✓ Cached: {cache_key}")
    
    def _invalidate_cache(self, cache_key: Optional[str] = None):
        """
        Invalidate cache (all levels).
        
        Args:
            cache_key: Specific key to invalidate, or None for all
        """
        if cache_key:
            logger.info(f"Invalidating cache key: {cache_key}")
            
            if self.enable_memory_cache:
                self._memory_cache.pop(cache_key, None)
            
            if self.enable_redis_cache and self._redis_client:
                try:
                    self._redis_client.delete(cache_key)
                except Exception as e:
                    logger.warning(f"Redis cache invalidation failed: {e}")
            
            if self.enable_file_cache:
                cache_file = self.cache_dir / f"{cache_key}.json"
                if cache_file.exists():
                    cache_file.unlink()
        else:
            logger.info("Invalidating all caches")
            self._memory_cache.clear()
            
            if self.enable_redis_cache and self._redis_client:
                try:
                    # Delete all keys matching pattern
                    pattern = "timber:capabilities:*"
                    for key in self._redis_client.scan_iter(match=pattern):
                        self._redis_client.delete(key)
                except Exception as e:
                    logger.warning(f"Redis cache invalidation failed: {e}")
            
            if self.enable_file_cache:
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
    
    # ========================================================================
    # Level 1: Memory Cache
    # ========================================================================
    
    def _get_from_memory(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get from memory cache."""
        cached = self._memory_cache.get(cache_key)
        if cached:
            # Check expiration
            if datetime.fromisoformat(cached['expires_at']) > datetime.utcnow():
                return cached['data']
            else:
                # Expired, remove
                self._memory_cache.pop(cache_key, None)
        return None
    
    def _set_in_memory(self, cache_key: str, value: Dict[str, Any]):
        """Set in memory cache."""
        self._memory_cache[cache_key] = {
            'data': value,
            'cached_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=self.cache_ttl_seconds)).isoformat()
        }
    
    # ========================================================================
    # Level 2: Redis Cache
    # ========================================================================
    
    def _get_from_redis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get from Redis cache."""
        if not self._redis_client:
            return None
        
        try:
            cached_bytes = self._redis_client.get(cache_key)
            if cached_bytes:
                return pickle.loads(cached_bytes)
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
        
        return None
    
    def _set_in_redis(self, cache_key: str, value: Dict[str, Any]):
        """Set in Redis cache."""
        if not self._redis_client:
            return
        
        try:
            cached_bytes = pickle.dumps(value)
            self._redis_client.setex(
                cache_key,
                self.cache_ttl_seconds,
                cached_bytes
            )
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
    
    # ========================================================================
    # Level 3: File Cache
    # ========================================================================
    
    def _get_from_file(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get from file cache."""
        # Sanitize key for filename
        safe_key = cache_key.replace(':', '_')
        cache_file = self.cache_dir / f"{safe_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Check expiration
            expires_at = datetime.fromisoformat(cached['expires_at'])
            if expires_at > datetime.utcnow():
                return cached['data']
            else:
                # Expired, remove
                cache_file.unlink()
        except Exception as e:
            logger.warning(f"File cache read failed: {e}")
        
        return None
    
    def _set_in_file(self, cache_key: str, value: Dict[str, Any]):
        """Set in file cache."""
        safe_key = cache_key.replace(':', '_')
        cache_file = self.cache_dir / f"{safe_key}.json"
        
        try:
            cached = {
                'data': value,
                'cached_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(seconds=self.cache_ttl_seconds)).isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cached, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"File cache write failed: {e}")
    
    # ========================================================================
    # Cached Methods
    # ========================================================================
    
    def generate_full_inventory(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate full inventory with caching.
        
        Args:
            use_cache: Whether to use cache
        
        Returns:
            Full inventory dictionary
        """
        if not use_cache:
            return super().generate_full_inventory()
        
        cache_key = self._generate_cache_key('full_inventory')
        
        # Try cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info("✓ Returning cached full inventory")
            return cached
        
        # Generate fresh inventory
        logger.info("Generating fresh inventory...")
        inventory = super().generate_full_inventory()
        
        # Cache it
        self._set_in_cache(cache_key, inventory)
        
        return inventory
    
    def get_model_info(self, model_name: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get model info with caching.
        
        Args:
            model_name: Name of the model
            use_cache: Whether to use cache
        
        Returns:
            Model information or None
        """
        if not use_cache:
            return super().get_model_info(model_name)
        
        cache_key = self._generate_cache_key('model_info', model_name=model_name)
        
        # Try cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # Get fresh data
        model_info = super().get_model_info(model_name)
        
        # Cache it
        if model_info:
            self._set_in_cache(cache_key, model_info)
        
        return model_info
    
    def list_all_models(self, use_cache: bool = True) -> List[str]:
        """
        List all models with caching.
        
        Args:
            use_cache: Whether to use cache
        
        Returns:
            List of model names
        """
        if not use_cache:
            return super().list_all_models()
        
        cache_key = self._generate_cache_key('list_models')
        
        # Try cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # Get fresh data
        models = super().list_all_models()
        
        # Cache it
        self._set_in_cache(cache_key, models)
        
        return models
    
    def get_capabilities_summary(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get capabilities summary with caching.
        
        Args:
            use_cache: Whether to use cache
        
        Returns:
            Summary dictionary
        """
        if not use_cache:
            return super().get_capabilities_summary()
        
        cache_key = self._generate_cache_key('summary')
        
        # Try cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # Get fresh data
        summary = super().get_capabilities_summary()
        
        # Cache it
        self._set_in_cache(cache_key, summary)
        
        return summary
    
    # ========================================================================
    # Cache Management
    # ========================================================================
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        stats = {
            'enabled': self.enable_cache,
            'ttl_hours': self.cache_ttl_hours,
            'levels': {
                'memory': {
                    'enabled': self.enable_memory_cache,
                    'entries': len(self._memory_cache) if self.enable_memory_cache else 0
                },
                'redis': {
                    'enabled': self.enable_redis_cache,
                    'connected': self._redis_client is not None
                },
                'file': {
                    'enabled': self.enable_file_cache,
                    'entries': len(list(self.cache_dir.glob("*.json"))) if self.enable_file_cache else 0
                }
            }
        }
        
        return stats
    
    def clear_cache(self):
        """Clear all caches."""
        logger.info("Clearing all caches...")
        self._invalidate_cache()
        logger.info("✓ All caches cleared")
    
    def warm_cache(self):
        """
        Warm up the cache by pre-generating common queries.
        
        This can be run during application startup to ensure
        fast responses for the first requests.
        """
        logger.info("Warming up cache...")
        
        # Generate full inventory
        self.generate_full_inventory(use_cache=False)
        logger.info("✓ Full inventory cached")
        
        # Cache all model info
        models = self.list_all_models(use_cache=False)
        for model_name in models:
            self.get_model_info(model_name, use_cache=False)
        logger.info(f"✓ {len(models)} models cached")
        
        # Cache summary
        self.get_capabilities_summary(use_cache=False)
        logger.info("✓ Summary cached")
        
        logger.info("✓ Cache warmed up")