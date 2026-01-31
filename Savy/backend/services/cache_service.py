"""
Caching service with Redis support.
Automatically falls back to in-memory cache if Redis is unavailable.
"""
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import json
import structlog
from functools import wraps
from config import settings

logger = structlog.get_logger()

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis_not_installed", message="Install redis package for distributed caching")


class InMemoryCache:
    """
    Simple in-memory cache implementation.
    Thread-safe for single-process deployment.
    For multi-process/distributed: replace with Redis.
    """
    
    def __init__(self):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._stats = {"hits": 0, "misses": 0, "sets": 0}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key in self._cache:
            value, expiry = self._cache[key]
            
            # Check if expired
            if expiry and datetime.now() > expiry:
                del self._cache[key]
                self._stats["misses"] += 1
                logger.debug("cache_miss_expired", key=key)
                return None
            
            self._stats["hits"] += 1
            logger.debug("cache_hit", key=key)
            return value
        
        self._stats["misses"] += 1
        logger.debug("cache_miss", key=key)
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (default: 1 hour)
        """
        expiry = datetime.now() + timedelta(seconds=ttl_seconds) if ttl_seconds else None
        self._cache[key] = (value, expiry)
        self._stats["sets"] += 1
        logger.debug("cache_set", key=key, ttl=ttl_seconds)
    
    def delete(self, key: str):
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug("cache_delete", key=key)
    
    def clear(self):
        """Clear all cache."""
        self._cache.clear()
        logger.info("cache_cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size": len(self._cache)
        }


class RedisCache:
    """
    Redis-based cache implementation (distributed).
    """
    
    def __init__(self):
        if not REDIS_AVAILABLE:
            raise ImportError("redis package not installed")
        
        try:
            self.client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password if settings.redis_password else None,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info("redis_cache_connected", host=settings.redis_host, port=settings.redis_port)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            value = self.client.get(key)
            if value:
                logger.debug("cache_hit_redis", key=key)
                return json.loads(value)
            logger.debug("cache_miss_redis", key=key)
            return None
        except Exception as e:
            logger.error("redis_get_error", key=key, error=str(e))
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in Redis cache with TTL."""
        try:
            self.client.setex(
                name=key,
                time=ttl_seconds,
                value=json.dumps(value)
            )
            logger.debug("cache_set_redis", key=key, ttl=ttl_seconds)
        except Exception as e:
            logger.error("redis_set_error", key=key, error=str(e))
    
    def delete(self, key: str):
        """Delete key from Redis cache."""
        try:
            self.client.delete(key)
            logger.debug("cache_delete_redis", key=key)
        except Exception as e:
            logger.error("redis_delete_error", key=key, error=str(e))
    
    def clear(self):
        """Clear all cache (use with caution in production!)."""
        try:
            self.client.flushdb()
            logger.warning("redis_cache_flushed")
        except Exception as e:
            logger.error("redis_flush_error", error=str(e))
    
    def get_stats(self) -> dict:
        """Get Redis statistics."""
        try:
            info = self.client.info('stats')
            return {
                "type": "redis",
                "total_commands": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "hit_rate_percent": round(
                    info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0)) * 100,
                    2
                )
            }
        except Exception as e:
            logger.error("redis_stats_error", error=str(e))
            return {"error": str(e)}


# Global cache instance
_cache_instance = None

def get_cache():
    """Get global cache instance (Redis if available, else in-memory)."""
    global _cache_instance
    
    if _cache_instance is None:
        # Try Redis first
        if REDIS_AVAILABLE and settings.redis_host:
            try:
                _cache_instance = RedisCache()
                logger.info("cache_initialized", type="redis")
            except Exception as e:
                logger.warning("redis_unavailable_fallback_inmemory", error=str(e))
                _cache_instance = InMemoryCache()
                logger.info("cache_initialized", type="in_memory")
        else:
            _cache_instance = InMemoryCache()
            logger.info("cache_initialized", type="in_memory")
    
    return _cache_instance


# ============================================================================
# CACHE DECORATORS
# ============================================================================

def cached(ttl_seconds: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: Cache TTL in seconds
        key_prefix: Prefix for cache key
        
    Usage:
        @cached(ttl_seconds=300, key_prefix="user_categories")
        def get_user_categories(user_id: str):
            return fetch_from_db(user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [key_prefix or func.__name__]
            
            # Add args to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    cache_key_parts.append(str(arg))
            
            # Add kwargs to key
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (str, int, float, bool)):
                    cache_key_parts.append(f"{k}:{v}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cache = get_cache()
            cached_value = cache.get(cache_key)
            
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


# ============================================================================
# CACHE HELPERS
# ============================================================================

def cache_user_categories(user_id: str, categories: list, ttl: int = 3600):
    """Cache user categories."""
    cache = get_cache()
    cache.set(f"user_categories:{user_id}", categories, ttl)


def get_cached_user_categories(user_id: str) -> Optional[list]:
    """Get cached user categories."""
    cache = get_cache()
    return cache.get(f"user_categories:{user_id}")


def invalidate_user_categories(user_id: str):
    """Invalidate user categories cache."""
    cache = get_cache()
    cache.delete(f"user_categories:{user_id}")


def cache_user_settings(user_id: str, settings: dict, ttl: int = 1800):
    """Cache user settings (30 min TTL)."""
    cache = get_cache()
    cache.set(f"user_settings:{user_id}", settings, ttl)


def get_cached_user_settings(user_id: str) -> Optional[dict]:
    """Get cached user settings."""
    cache = get_cache()
    return cache.get(f"user_settings:{user_id}")


def invalidate_user_settings(user_id: str):
    """Invalidate user settings cache."""
    cache = get_cache()
    cache.delete(f"user_settings:{user_id}")


# ============================================================================
# REDIS ADAPTER (for production)
# ============================================================================

class RedisCache:
    """
    Redis-based cache implementation.
    Drop-in replacement for InMemoryCache.
    
    Usage:
        # In config.py, add: redis_url: str = "redis://localhost:6379/0"
        # In this file, replace global cache:
        # _cache_instance = RedisCache(settings.redis_url)
    """
    
    def __init__(self, redis_url: str):
        try:
            import redis
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self._stats = {"hits": 0, "misses": 0, "sets": 0}
            logger.info("redis_cache_initialized", url=redis_url)
        except ImportError:
            logger.error("redis_not_installed", message="Install with: pip install redis")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        try:
            value = self.redis.get(key)
            if value:
                self._stats["hits"] += 1
                # Deserialize JSON
                return json.loads(value)
            self._stats["misses"] += 1
            return None
        except Exception as e:
            logger.error("redis_get_failed", key=key, error=str(e))
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in Redis with TTL."""
        try:
            # Serialize to JSON
            serialized = json.dumps(value, default=str)
            self.redis.setex(key, ttl_seconds, serialized)
            self._stats["sets"] += 1
        except Exception as e:
            logger.error("redis_set_failed", key=key, error=str(e))
    
    def delete(self, key: str):
        """Delete key from Redis."""
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error("redis_delete_failed", key=key, error=str(e))
    
    def clear(self):
        """Clear all Redis cache (use with caution!)."""
        try:
            self.redis.flushdb()
            logger.info("redis_cache_cleared")
        except Exception as e:
            logger.error("redis_clear_failed", error=str(e))
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        try:
            info = self.redis.info("stats")
            return {
                **self._stats,
                "total_requests": total_requests,
                "hit_rate_percent": round(hit_rate, 2),
                "redis_keyspace_hits": info.get("keyspace_hits", 0),
                "redis_keyspace_misses": info.get("keyspace_misses", 0),
            }
        except:
            return {
                **self._stats,
                "total_requests": total_requests,
                "hit_rate_percent": round(hit_rate, 2),
            }
