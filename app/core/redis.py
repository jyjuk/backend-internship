from typing import Optional
import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()

redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    return redis_client


async def close_redis_client() -> None:
    global redis_client

    if redis_client:
        await redis_client.close()
        redis_client = None
