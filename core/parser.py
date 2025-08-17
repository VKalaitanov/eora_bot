import asyncio
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from info.parse_urls import CASE_LINKS
from core.logger import setup_logger

logger = setup_logger("parser")

# Настройки парсинга
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"}
TIMEOUT = 10  # секунд


async def fetch_html(session: aiohttp.ClientSession, url: str, timeout: int = TIMEOUT) -> str:
    """
    Загружает HTML страницы по URL с использованием aiohttp.

    Args:
        session (aiohttp.ClientSession): Сессия aiohttp.
        url (str): URL страницы.
        timeout (int): Таймаут запроса в секундах.

    Returns:
        str: HTML страницы или пустая строка при ошибке.
    """
    try:
        async with session.get(url, headers=HEADERS, timeout=timeout) as resp:
            resp.raise_for_status()
            return await resp.text()
    except Exception as e:
        logger.error("Ошибка загрузки %s: %s", url, e)
        return ""


async def parse_case(session: aiohttp.ClientSession, url: str) -> Optional[Dict[str, str]]:
    """
    Парсит один кейс по URL: извлекает заголовок и текст контента.

    Args:
        session (aiohttp.ClientSession): Сессия aiohttp.
        url (str): URL кейса.

    Returns:
        Optional[Dict[str, str]]: Словарь с ключами 'title', 'text', 'url', либо None при ошибке.
    """
    html = await fetch_html(session, url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Без названия"

    # Основной контент кейса
    content_div = soup.find("div", class_="case-content") or soup.find("article") or soup
    texts: List[str] = []

    for tn in content_div.find_all("div", class_="tn-atom"):
        if tn.find_parent("header") or tn.find_parent("footer"):
            continue
        text = tn.get_text(separator=" ", strip=True)
        if text and text != title:
            texts.append(text)

    full_text = "\n".join(texts).strip()
    logger.info("Парсинг кейса: %s (%s) — %d символов текста", title, url, len(full_text))
    return {"title": title, "text": full_text, "url": url}


async def parse_all_cases(urls: List[str] = CASE_LINKS) -> List[Dict[str, str]]:
    """
    Парсит список кейсов асинхронно.

    Args:
        urls (List[str], optional): Список URL кейсов. Defaults to CASE_LINKS.

    Returns:
        List[Dict[str, str]]: Список словарей с кейсами.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [parse_case(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    parsed_cases: List[Dict[str, str]] = []
    for result in results:
        if isinstance(result, dict):
            parsed_cases.append(result)
        elif isinstance(result, Exception):
            logger.error("Ошибка при парсинге кейса: %s", result)

    return parsed_cases
