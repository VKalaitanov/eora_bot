import asyncio
import json
from typing import List, Dict
from core.redis_client import get_redis
from core.logger import setup_logger
from .parser import parse_all_cases
from info.parse_urls import CASE_LINKS
from core.config import CACHE_TTL

logger = setup_logger("redis_cache")
CACHE_KEY = "cases"

async def get_cases() -> List[Dict[str, str]]:
    """
    Получение списка кейсов из Redis или парсинг при отсутствии данных.

    Returns:
        List[Dict[str, str]]: Список кейсов.
    """
    redis = await get_redis()
    data = await redis.get(CACHE_KEY)
    if data:
        logger.info("Загружаем кейсы из Redis")
        return json.loads(data)

    logger.info("Кейсы не найдены в Redis. Парсим заново...")
    try:
        cases = await parse_all_cases(CASE_LINKS)
        await redis.set(CACHE_KEY, json.dumps(cases, ensure_ascii=False), ex=CACHE_TTL)
        logger.info(f"Спарсено и сохранено {len(cases)} кейсов")
        return cases
    except Exception as e:
        logger.exception("Ошибка при парсинге кейсов: %s", e)
        return []

async def background_parse() -> None:
    """
    Фоновое обновление кейсов каждые CACHE_TTL секунд.
    """
    redis = await get_redis()
    while True:
        try:
            logger.info("Фоновое обновление кейсов в Redis...")
            cases = await parse_all_cases(CASE_LINKS)
            await redis.set(CACHE_KEY, json.dumps(cases, ensure_ascii=False), ex=CACHE_TTL)
            logger.info(f"Фоновое обновление завершено: {len(cases)} кейсов")
        except Exception as e:
            logger.exception("Ошибка при фоновой загрузке кейсов: %s", e)
        await asyncio.sleep(CACHE_TTL)
