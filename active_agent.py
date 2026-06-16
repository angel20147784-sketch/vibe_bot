#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Active subscriber growth agent"""

import os
import asyncio
import logging
import requests
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
        )
    return _client


PROMO_TEXTS = [
    "🎓 Бесплатный курс по вайбкодингу!\n\nНаучись создавать приложения с помощью ИИ за 30 дней.\n\n👉 t.me/CODEScodingbot",
    "⚡ Хочешь создавать сайты без опыта?\n\nВайбкодинг — твоё будущее!\n\nНачни бесплатно 👇\nt.me/CODEScodingbot",
    "🚀 Cursor + Claude = твоё приложение за час\n\nБесплатный курс:\nt.me/CODEScodingbot",
    "💡 ИИ пишет код за тебя!\n\nНаучись создавать проекты:\nt.me/CODEScodingbot",
    "📦 Telegram-боты, сайты, SaaS — всё за 30 дней\n\nКурс бесплатно 👇\nt.me/CODEScodingbot",
]

TARGET_CHANNELS = [
    "@tproger",
    "@habr",
    "@vc",
    "@python_course",
    "@webdev",
    "@javascript",
    "@freelance",
    "@startup",
    "@it_kursy",
    "@codesergo",
]


async def generate_promo_post():
    client = get_client()

    prompt = (
        "Создай короткий рекламный пост для Telegram-канала о бесплатном курсе вайбкодинга.\n\n"
        "Курс: 30 дней, бесплатно\n"
        "Чему научишься: Cursor, Claude, v0.dev, создание сайтов, ботов, SaaS\n\n"
        "Формат: 3-5 строк, эмодзи, ссылка t.me/CODEScodingbot\n"
        "Стиль: живой, мотивирующий"
    )

    try:
        response = await client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[
                {"role": "system", "content": "Ты — маркетолог. Пиши короткие рекламные посты."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=256,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


async def post_to_channel(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": CHANNEL_ID, "text": text}
        )
        return r.json().get("ok")
    except Exception as e:
        logger.error(f"Error posting: {e}")
        return False


async def comment_on_posts():
    """Комментирует посты в других каналах (через search)"""
    client = get_client()

    prompt = (
        "Найди 5 свежих постов в Telegram-каналах о программировании и ИИ.\n"
        "Предложи полезные комментарии к каждому посту.\n"
        "Формат: номер поста + текст комментария\n"
        "Стиль: экспертный, полезный"
    )

    try:
        response = await client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[
                {"role": "system", "content": "Ты — эксперт по вайбкодингу."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=512,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


async def find合作_opportunities():
    """Ищет каналы для сотрудничества"""
    client = get_client()

    prompt = (
        "Найди 10 Telegram-каналов с аудиторией 500-5000 подписчиков.\n"
        "Тематика: программирование, ИИ, стартапы\n\n"
        "Для каждого канала предложи:\n"
        "1. Название\n"
        "2. Почему подходит\n"
        "3. Как сотрудничать"
    )

    try:
        response = await client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[
                {"role": "system", "content": "Ты — бизнес-аналитик."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


async def daily_growth_task():
    """Ежедневная задача роста"""
    logger.info("🚀 Running daily growth task...")

    # 1. Генерируем и публикуем пост
    post = await generate_promo_post()
    if post:
        await post_to_channel(post)
        logger.info("✅ Posted to channel")

    # 2. Ищем возможности для сотрудничества
    opportunities = await find合作_opportunities()
    if opportunities:
        logger.info(f"✅ Found opportunities:\n{opportunities[:200]}...")

    # 3. Генерируем комментарии
    comments = await comment_on_posts()
    if comments:
        logger.info(f"✅ Generated comments:\n{comments[:200]}...")

    return {
        "post": post,
        "opportunities": opportunities,
        "comments": comments,
    }


if __name__ == "__main__":
    asyncio.run(daily_growth_task())
