import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramAPIError
from core.config import TELEGRAM_BOT_TOKEN, BACKGROUND_TASK_INTERVAL
from core.logger import setup_logger
from core.openai_client import ask_openai
from core.redis_cache import get_cases, background_parse
from core.search import simple_search

logger = setup_logger("bot")


async def send_welcome(message: types.Message) -> None:
    """
    Обработчик команды /start.

    Отправляет пользователю приветственное сообщение с инструкцией.
    Логирует возможные ошибки при отправке.
    """
    try:
        await message.answer(
            "Привет! Задай вопрос про проекты EORA, я постараюсь ответить с источниками."
        )
    except TelegramAPIError as e:
        logger.error("Ошибка при отправке приветственного сообщения: %s", e)


async def handle_question(message: types.Message) -> None:
    """
    Обработчик пользовательских сообщений.

    - Получает текст вопроса.
    - Загружает список кейсов из Redis (или парсит, если кэш пуст).
    - Выполняет простой поиск по кейсам.
    - Отправляет вопрос в LLM (OpenAI) для генерации ответа.
    - Возвращает пользователю готовый ответ с источниками.

    При ошибках уведомляет пользователя и пишет в лог.
    """
    question = message.text
    logger.info("Получен вопрос: %s", question)

    try:
        cases = await asyncio.wait_for(get_cases(), timeout=10)
    except Exception as e:
        logger.warning("Ошибка при получении кейсов: %s", e)
        await message.answer("Сервис временно недоступен, попробуйте позже.")
        return

    results = simple_search(question, cases)
    if not results:
        await message.answer("По вашему запросу ничего не найдено.")
        return

    try:
        answer = await asyncio.wait_for(
            ask_openai(question, [case for _, case in results]), timeout=20
        )
        await message.answer(answer, disable_web_page_preview=True, parse_mode="Markdown")
    except Exception as e:
        logger.exception("Ошибка при обработке вопроса: %s", e)
        await message.answer("Произошла ошибка при обработке запроса.")


async def start_background_tasks() -> None:
    """
    Запускает фоновые задачи.

    В текущей версии — регулярное обновление кейсов в Redis.
    """
    asyncio.create_task(background_parse())


async def main() -> None:
    """
    Основная точка входа для Telegram-бота.

    - Инициализирует бота и диспетчер.
    - Регистрирует хендлеры (/start и вопросы).
    - Запускает фоновые задачи.
    - Начинает polling.
    """
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(send_welcome, Command("start"))
    dp.message.register(handle_question)

    await start_background_tasks()
    logger.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical("Критическая ошибка при запуске бота: %s", e)
