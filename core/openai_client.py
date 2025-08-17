import asyncio
import openai
from typing import List, Dict
from core.config import API_KEY, API_BASE_URL, MODEL_NAME, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS, CACHE_TTL
from core.logger import setup_logger
from core.redis_client import get_redis

logger = setup_logger("openai_client")

openai.api_key = API_KEY
openai.api_base = API_BASE_URL

def sync_call(prompt: str) -> openai.openai_object.OpenAIObject:
    """
    Синхронный вызов модели OpenAI.

    Args:
        prompt (str): Текст запроса к модели.

    Returns:
        openai.openai_object.OpenAIObject: Ответ модели.
    """
    return openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": (
                "Ты чат-бот компании EORA. "
                "Отвечай строго по делу, без воды, коротко и понятно. "
                "Используй только предоставленные материалы. "
                "Вставляй ссылки в ответ в формате Markdown."
            )},
            {"role": "user", "content": prompt}
        ],
        temperature=OPENAI_TEMPERATURE,
        max_tokens=OPENAI_MAX_TOKENS
    )

async def ask_openai(question: str, cases: List[Dict[str, str]], timeout: int = 20) -> str:
    """
    Асинхронное получение ответа от LLM с кэшированием в Redis.

    Args:
        question (str): Вопрос пользователя.
        cases (List[Dict[str, str]]): Список кейсов для контекста.
        timeout (int, optional): Таймаут запроса к модели. Defaults to 20.

    Returns:
        str: Ответ модели.
    """
    if not cases:
        logger.warning("Список кейсов пустой")
        return "Нет доступных кейсов для ответа."

    redis = await get_redis()
    cache_key = f"llm_response:{question.strip()}"
    cached = await redis.get(cache_key)
    if cached:
        logger.info("Ответ получен из кэша Redis")
        return cached

    context_lines = [f"[{idx}] {case['title']} — {case['url']}" for idx, case in enumerate(cases, 1)]
    context = "Вот список кейсов:\n" + "\n".join(context_lines)
    prompt = (
        f"{context}\n"
        f"Вопрос: {question}\n\n"
        "Ответь кратко и по делу, выбрав 3–4 самых подходящих кейса.\n"
        "- Используй формулировку в стиле: '1) Мы создали <title> для <компании>'\n"
        "- Всегда вставляй ссылку рядом с названием компании в формате Markdown.\n"
        "- Не используй 'мы можем', 'мы также можем'.\n"
        "- Не делай общий список всех кейсов, только релевантные.\n"
        "- Не повторяй одну и ту же компанию.\n\n"
        "Формат ответа:\n"
        "1) <краткое описание> для <компания> [ссылка]\n"
        "2) <краткое описание> для <компания> [ссылка]\n"
        "..."
    )

    try:
        response = await asyncio.wait_for(asyncio.to_thread(sync_call, prompt), timeout=timeout)
        content: str = response.choices[0].message["content"].strip()
        await redis.set(cache_key, content, ex=CACHE_TTL)
        logger.info("Ответ сохранён в Redis")
        return content
    except asyncio.TimeoutError:
        logger.warning("Таймаут при запросе к модели LLM")
        return "Извините, модель не ответила вовремя, попробуйте позже."
    except Exception as e:
        logger.exception("Ошибка при вызове LLM: %s", e)
        return "Извините, сейчас я не могу получить ответ от модели."
