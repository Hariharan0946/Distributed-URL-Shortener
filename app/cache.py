import json
from typing import Any

from redis.asyncio import Redis


class CacheClient:
    def __init__(self, redis_url: str | None, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._redis: Redis | None = Redis.from_url(redis_url, decode_responses=True) if redis_url else None

    @property
    def enabled(self) -> bool:
        return self._redis is not None

    async def get_url(self, short_code: str) -> dict[str, Any] | None:
        if not self._redis:
            return None
        cached = await self._redis.get(f"url:{short_code}")
        return json.loads(cached) if cached else None

    async def set_url(self, short_code: str, payload: dict[str, Any]) -> None:
        if not self._redis:
            return
        await self._redis.setex(f"url:{short_code}", self.ttl_seconds, json.dumps(payload))

    async def invalidate_url(self, short_code: str) -> None:
        if not self._redis:
            return
        await self._redis.delete(f"url:{short_code}")

