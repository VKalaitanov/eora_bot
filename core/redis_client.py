import aioredis
from typing import Optional
from core.config import REDIS_URL
from core.logger import setup_logger

logger = setup_logger("redis_client")

redis: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    """
    Возвращает объект Redis. Если нет подключения, создаёт его.

    Returns:
        aioredis.Redis: Асинхронное подключение к Redis.
    """
    global redis
    if redis is None:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        logger.info("Подключение к Redis установлено")
    return redis
