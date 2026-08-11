import redis
from redis.exceptions import ConnectionError
from app.core.config import settings
import json

# Create a Redis connection pool
redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis() -> redis.Redis:
    """Returns a Redis client instance"""
    return redis.Redis(connection_pool=redis_pool)

_memory_cache = {}

def get_cache(key: str) -> dict | list | None:
    try:
        client = get_redis()
        data = client.get(key)
        if data:
            return json.loads(data)
    except ConnectionError:
        # Fallback to in-memory cache if Redis is not running
        if key in _memory_cache:
            import time
            entry = _memory_cache[key]
            if entry["expires_at"] > time.time():
                import copy
                return copy.deepcopy(entry["data"])
            else:
                del _memory_cache[key]
    return None

def set_cache(key: str, data: dict | list, expire: int = 3600) -> bool:
    try:
        client = get_redis()
        return client.set(key, json.dumps(data), ex=expire)
    except ConnectionError:
        # Fallback to in-memory cache if Redis is not running
        import time
        import copy
        _memory_cache[key] = {
            "data": copy.deepcopy(data),
            "expires_at": time.time() + expire
        }
        return True
