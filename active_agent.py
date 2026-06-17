#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Active subscriber growth agent"""

import os
import asyncio
import logging
import requests
from api_rotator import generate_with_rotation

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


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
    prompt = (
        "Напиши рекламный пост для Telegram.\n\n"
        "Курс по вайбкодингу, 30 дней, бесплатно.\n"
        "Чему научишься: Cursor, Claude, v0.dev\n\n"
        "Только текст поста. Без пояснений, без \"Вот пост:\", без кавычек.\n"
        "3-5 строк, эмодзи, ссылка t.me/CODEScodingbot"
    )

    try:
        content, provider = await generate_with_rotation(
            "Ты — маркетолог. Пиши готовые посты без пояснений.\n\n" + prompt, max_tokens=256
        )
        if content:
            logger.info(f"Promo post with {provider}")
            # Убираем лишние обёртки если есть
            content = content.strip().strip('"').strip("'")
            if content.startswith("Вот") or content.startswith("Пост:"):
                content = content.split("\n", 1)[-1].strip()
            return content
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
    prompt = (
        "Найди 5 свежих постов в Telegram-каналах о программировании и ИИ.\n"
        "Предложи полезные комментарии к каждому посту.\n"
        "Формат: номер поста + текст комментария\n"
        "Стиль: экспертный, полезный"
    )

    try:
        content, provider = await generate_with_rotation(
            "Ты — эксперт по вайбкодингу.\n\n" + prompt, max_tokens=512
        )
        if content:
            logger.info(f"Comments with {provider}")
            return content
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


async def find合作_opportunities():
    """Ищет каналы для сотрудничества"""
    prompt = (
        "Найди 10 Telegram-каналов с аудиторией 500-5000 подписчиков.\n"
        "Тематика: программирование, ИИ, стартапы\n\n"
        "Для каждого канала предложи:\n"
        "1. Название\n"
        "2. Почему подходит\n"
        "3. Как сотрудничать"
    )

    try:
        content, provider = await generate_with_rotation(
            "Ты — бизнес-аналитик.\n\n" + prompt, max_tokens=1024
        )
        if content:
            logger.info(f"Opportunities with {provider}")
            return content
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

    # 1. Генерируем пост (но НЕ публикуем автоматически)
    post = await generate_promo_post()
    if post:
        logger.info("✅ Post generated (not published)")

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
