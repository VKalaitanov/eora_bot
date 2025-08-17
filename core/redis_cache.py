import asyncio
import json
import logging
import aioredis
from typing import List, Dict
from .parser import parse_all_cases
from info.parse_urls import CASE_LINKS

REDIS_URL = "redis://redis:6379"
CACHE_KEY = "cases"
CACHE_TTL = 3 * 60 * 60

redis = None

async def init_redis():
    global redis
    if redis is None:
        redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

async def get_cases() -> List[Dict[str, str]]:
    await init_redis()
    data = await redis.get(CACHE_KEY)
    if data:
        logging.info("Загружаем кейсы из Redis")
        return json.loads(data)

    logging.info("Кейсы не найдены в Redis. Парсим заново...")
    cases = await parse_all_cases(CASE_LINKS)
    await redis.set(CACHE_KEY, json.dumps(cases, ensure_ascii=False), ex=CACHE_TTL)
    return cases

async def background_parse():
    await init_redis()
    while True:
        try:
            logging.info("Обновление кейсов в Redis...")
            cases = await parse_all_cases(CASE_LINKS)
            await redis.set(CACHE_KEY, json.dumps(cases, ensure_ascii=False), ex=CACHE_TTL)
            logging.info(f"Обновлено {len(cases)} кейсов")
        except Exception as e:
            logging.error(f"Ошибка при фоновой загрузке кейсов: {e}")
        await asyncio.sleep(CACHE_TTL)
