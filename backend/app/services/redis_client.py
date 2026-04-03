import json

import redis

from app.core.config import get_settings


settings = get_settings()
redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def get_cached_report(audio_hash: str) -> dict | None:
    value = redis_client.get(f"audio:{audio_hash}")
    return json.loads(value) if value else None


def set_cached_report(audio_hash: str, payload: dict, ttl_seconds: int = 86400) -> None:
    redis_client.setex(f"audio:{audio_hash}", ttl_seconds, json.dumps(payload, default=str))
