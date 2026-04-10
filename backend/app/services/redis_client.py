import json

import redis
from redis.exceptions import RedisError

from app.core.config import get_settings


settings = get_settings()
redis_pool = redis.ConnectionPool.from_url(
    settings.redis_url,
    decode_responses=True,
    max_connections=settings.redis_max_connections,
)
redis_client = redis.Redis(connection_pool=redis_pool)


def get_cached_report(audio_hash: str) -> dict | None:
    try:
        value = redis_client.get(f"audio:{audio_hash}")
        return json.loads(value) if value else None
    except RedisError:
        return None


def set_cached_report(audio_hash: str, payload: dict, ttl_seconds: int = 86400) -> None:
    try:
        redis_client.setex(f"audio:{audio_hash}", ttl_seconds, json.dumps(payload, default=str))
    except RedisError:
        return


def check_rate_limit(*, key: str, limit: int, window_seconds: int) -> bool:
    try:
        current = redis_client.incr(key)
        if current == 1:
            redis_client.expire(key, window_seconds)
        return current <= limit
    except RedisError:
        # Fail open if Redis is unhealthy so auth/reporting does not fully stop.
        return True
