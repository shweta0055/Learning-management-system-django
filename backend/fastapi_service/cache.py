"""
Redis caching utilities for FastAPI service.
"""
import json
import hashlib
import functools
from typing import Optional, Any, Callable
import redis.asyncio as aioredis
from decouple import config

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
DEFAULT_TTL = 300  # 5 minutes


async def get_redis_client() -> aioredis.Redis:
    return aioredis.from_url(REDIS_URL, decode_responses=True)


async def cache_get(key: str) -> Optional[Any]:
    try:
        r = await get_redis_client()
        val = await r.get(key)
        await r.close()
        return json.loads(val) if val else None
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    try:
        r = await get_redis_client()
        await r.setex(key, ttl, json.dumps(value, default=str))
        await r.close()
    except Exception:
        pass


async def cache_delete(key: str) -> None:
    try:
        r = await get_redis_client()
        await r.delete(key)
        await r.close()
    except Exception:
        pass


async def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching a pattern, e.g. 'recommendations:*'"""
    try:
        r = await get_redis_client()
        keys = await r.keys(pattern)
        if keys:
            await r.delete(*keys)
        await r.close()
    except Exception:
        pass


def make_cache_key(*parts) -> str:
    """Create a deterministic cache key from parts."""
    raw = ":".join(str(p) for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()


def cached(ttl: int = DEFAULT_TTL, prefix: str = "lms"):
    """
    Async decorator for caching FastAPI route results.
    Usage:
        @router.get("/trending")
        @cached(ttl=60, prefix="trending")
        async def trending_courses(...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from function name + kwargs
            key_parts = [prefix, func.__name__] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = make_cache_key(*key_parts)

            cached_val = await cache_get(cache_key)
            if cached_val is not None:
                return cached_val

            result = await func(*args, **kwargs)
            await cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
