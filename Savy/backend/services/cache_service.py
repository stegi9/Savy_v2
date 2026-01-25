"""
Redis Cache Service for Savy.
Provides caching for API responses and rate limiting to reduce latency under load.
"""
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import structlog

logger = structlog.get_logger()

# Redis client (lazy initialization)
_redis_client = None


def get_redis():
    """Get Redis client instance (lazy loading for optional dependency)."""
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        import redis
        from config import settings
        
        redis_url = getattr(settings, 'redis_url', None)
        if not redis_url:
            logger.info("redis_not_configured", message="Redis URL not set, caching disabled")
            return None
        
        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        # Test connection
        _redis_client.ping()
        logger.info("redis_connected", url=redis_url.split("@")[-1])  # Log without password
        return _redis_client
        
    except ImportError:
        logger.warning("redis_not_installed", message="Install redis: pip install redis")
        return None
    except Exception as e:
        logger.warning("redis_connection_failed", error=str(e))
        return None


def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


async def cached(
    prefix: str,
    ttl_seconds: int = 300,  # 5 minutes default
    skip_if: Callable = None
):
    """
    Decorator to cache async function results in Redis.
    
    Usage:
        @cached("affiliate_search", ttl_seconds=600)
        async def search_offers(query: str) -> dict:
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis = get_redis()
            
            # Skip caching if Redis not available or skip condition met
            if redis is None:
                return await func(*args, **kwargs)
            
            if skip_if and skip_if(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Generate cache key
            key = f"savy:{prefix}:{cache_key(*args, **kwargs)}"
            
            try:
                # Try to get from cache
                cached_value = redis.get(key)
                if cached_value:
                    logger.debug("cache_hit", key=key[:50])
                    return json.loads(cached_value)
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                
                # Cache the result
                redis.setex(key, ttl_seconds, json.dumps(result, default=str))
                logger.debug("cache_set", key=key[:50], ttl=ttl_seconds)
                
                return result
                
            except Exception as e:
                logger.warning("cache_error", error=str(e))
                # On cache error, just execute the function
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class RateLimiter:
    """
    Simple Redis-based rate limiter.
    Prevents API abuse and protects LLM endpoints.
    """
    
    def __init__(self, key_prefix: str, max_requests: int, window_seconds: int):
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def is_allowed(self, identifier: str) -> tuple[bool, int]:
        """
        Check if request is allowed for given identifier.
        
        Returns:
            (is_allowed, remaining_requests)
        """
        redis = get_redis()
        
        if redis is None:
            # No Redis = no rate limiting
            return True, self.max_requests
        
        key = f"savy:ratelimit:{self.key_prefix}:{identifier}"
        
        try:
            # Use Redis pipeline for atomic operations
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.ttl(key)
            results = pipe.execute()
            
            current_count = results[0]
            ttl = results[1]
            
            # Set expiry on first request
            if ttl == -1:
                redis.expire(key, self.window_seconds)
            
            remaining = max(0, self.max_requests - current_count)
            is_allowed = current_count <= self.max_requests
            
            if not is_allowed:
                logger.warning("rate_limit_exceeded", identifier=identifier, key=self.key_prefix)
            
            return is_allowed, remaining
            
        except Exception as e:
            logger.warning("rate_limit_error", error=str(e))
            return True, self.max_requests


# Pre-configured rate limiters
chat_rate_limiter = RateLimiter("chat", max_requests=20, window_seconds=60)
affiliate_rate_limiter = RateLimiter("affiliate", max_requests=30, window_seconds=60)
