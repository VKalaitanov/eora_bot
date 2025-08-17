import logging
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List
import asyncio
from info.parse_urls import CASE_LINKS

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"}
    try:
        async with session.get(url, timeout=10, headers=headers) as resp:
            return await resp.text()
    except Exception as e:
        logging.error(f"Ошибка загрузки {url}: {e}")
        return ""

async def parse_case(session: aiohttp.ClientSession, url: str) -> dict:
    html = await fetch_html(session, url)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Без названия"

    content_div = soup.find("div", class_="case-content") or soup.find("article") or soup
    texts = []

    for tn in content_div.find_all("div", class_="tn-atom"):
        if tn.find_parent("header") or tn.find_parent("footer"):
            continue
        text = tn.get_text(separator=" ", strip=True)
        if text and text != title:
            texts.append(text)

    full_text = "\n".join(texts).strip()
    logging.info(f"Парсинг кейса: {title} ({url}) — {len(full_text)} символов текста")
    return {"title": title, "text": full_text, "url": url}

async def parse_all_cases(urls: List[str] = CASE_LINKS) -> List[Dict[str, str]]:
    async with aiohttp.ClientSession() as session:
        tasks = [parse_case(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return [case for case in results if case]
