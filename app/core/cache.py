import json

import redis

from app.core.config import settings

_client = (
    redis.Redis.from_url(settings.redis_url, decode_responses=True)
    if settings.redis_url
    else None
)
VERSION_KEY = "products:version"


def products_version() -> str:
    if _client is None:
        return "0"
    try:
        return _client.get(VERSION_KEY) or "0"
    except redis.RedisError:
        return "0"


def bump_products_version() -> None:
    if _client is None:
        return
    try:
        _client.incr(VERSION_KEY)
    except redis.RedisError:
        pass


def cache_get(key: str):
    if _client is None:
        return None
    try:
        raw = _client.get(key)
    except redis.RedisError:
        return None
    return json.loads(raw) if raw else None


def cache_set(key: str, value, ttl: int = 60) -> None:
    if _client is None:
        return
    try:
        _client.setex(key, ttl, json.dumps(value))
    except redis.RedisError:
        pass
