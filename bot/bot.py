import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

from core.openai_client import ask_openai
from core.redis_cache import get_cases, background_parse
from core.search import simple_search

logging.basicConfig(level=logging.INFO)
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
print(TELEGRAM_BOT_TOKEN)


async def send_welcome(message: types.Message):
    await message.answer("Привет! Задай вопрос про проекты EORA, я постараюсь ответить с источниками.")

async def handle_question(message: types.Message):
    question = message.text
    # Берём актуальные кейсы из Redis
    cases = await get_cases()

    results = simple_search(question, cases)
    if not results:
        await message.answer("Извините, по вашему запросу ничего не найдено.")
        return

    # --- Получаем ответ от LLM (передаём все результаты без фильтрации) ---
    answer = await ask_openai(question, [case for _, case in results])
    print(answer)

    # --- Отправляем ответ пользователю ---
    await message.answer(answer, disable_web_page_preview=True, parse_mode="Markdown")


async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(send_welcome, Command("start"))
    dp.message.register(handle_question)  # больше не partial, актуальные кейсы берутся внутри

    # --- Фоновая задача: обновление кейсов каждые 3 часа ---
    import asyncio
    asyncio.create_task(background_parse())

    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
