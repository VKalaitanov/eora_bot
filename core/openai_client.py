import asyncio
import logging
import os
from typing import List

import openai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL")

openai.api_key = API_KEY
openai.api_base = API_BASE_URL


def sync_call(prompt: str):
    """
    Базовый вызов модели.
    Принимает готовый промт и возвращает ответ от LLM.
    """
    response = openai.ChatCompletion.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты чат-бот компании EORA. "
                    "Отвечай строго по делу, без воды, коротко и понятно. "
                    "Используй только предоставленные материалы. "
                    "Вставляй ссылки в ответ в формате Markdown."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=600
    )
    return response


# --- Функция для пользователя ---
async def ask_openai(question: str, cases: List[dict]) -> str:
    """
    Принимает вопрос от пользователя и список кейсов.
    Формирует промт и возвращает чёткий ответ со ссылками в тексте.
    """

    # Формируем контекст: список кейсов с номерами и ссылками
    context = "Вот список кейсов:\n"
    for idx, case in enumerate(cases, 1):
        context += f"[{idx}] {case['title']} — {case['url']}\n"

    # Инструкция для LLM
    prompt = (
        f"{context}\n"
        f"Вопрос: {question}\n\n"
        "Ответь кратко и по делу.\n"
        "Используй **ровно те заголовки (title), которые приведены выше**, "
        "и ссылки из списка.\n"
        "Формат ответа строго такой:\n"
        "1) title [Магнит](https://example.com)\n "
        "2) title [KazanExpress](https://example.com).\n"
        "и так далее (3-4 примера).\n"
        "Не придумывай новые заголовки, используй только из списка."
    )

    try:
        response = await asyncio.to_thread(sync_call, prompt)
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logging.error(f"Ошибка LLM: {e}")
        return "Извините, сейчас я не могу получить ответ от модели."
