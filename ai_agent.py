#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AI Agent for autonomous channel posting"""

import os
import random
import asyncio
import logging
from api_rotator import generate_with_rotation
from course_data import COURSE_DAYS, WEEK_NAMES

logger = logging.getLogger(__name__)


CHANNEL_TOPICS = [
    {
        "type": "course_day",
        "prompt": "Создай короткий промо-пост для Telegram-канала о {day_title}. "
                  "Добавь интригу и мотивацию. Длина: 100-150 слов. "
                  "Используй эмодзи. Только русский язык.",
    },
    {
        "type": "tips",
        "prompt": "Напиши пост с 3-5 лайфхаками по вайбкодингу. "
                  "Тема: {theme}. Формат: список с эмодзи. Длина: 100-150 слов.",
    },
    {
        "type": "real_project",
        "prompt": "Расскажи о реальном проекте созданном с помощью ИИ. "
                  "Опиши: что создали, сколько времени заняло, результат. "
                  "Длина: 100-150 слов. Эмодзи.",
    },
    {
        "type": "motivation",
        "prompt": "Напиши мотивирующий пост для начинающих вайбкодеров. "
                  "Расскажи почему это круто и что можно создать. "
                  "Длина: 80-120 слов. Эмодзи.",
    },
    {
        "type": "tool_review",
        "prompt": "Обзор инструмента для вайбкодинга: {tool}. "
                  "Расскажи что умеет, плюсы, минусы. "
                  "Длина: 100-150 слов. Эмодзи.",
    },
]

TOOLS = ["Cursor", "Claude", "v0.dev", "Replit", "Bolt.new", "Lovable", "Supabase"]

THEMES = [
    "промпт-инжиниринг и написание промптов",
    "создание лендингов и сайтов",
    "Telegram-боты и автоматизация",
    "SaaS-проекты и монетизация",
    "работа с базами данных",
    "деплой и запуск проектов",
]

SYSTEM_PROMPT = """Ты — автор Telegram-канала о вайбкодинге @codesergo.
Пиши живые, интересные посты на русском языке.
Используй эмодзи активно (3-5 в каждом посте).
Структурируй текст короткими абзацами.
Никогда не используй Markdown-разметку (*, _, #, и т.д).
Пиши обычным текстом."""


async def generate_channel_post(topic_type=None, **kwargs):
    if topic_type is None:
        topic_type = random.choice(CHANNEL_TOPICS)

    template = topic_type["prompt"]
    theme = random.choice(THEMES) if "theme" in template else ""
    tool = random.choice(TOOLS) if "tool" in template else ""
    day_num = random.randint(1, 30)
    day_title = COURSE_DAYS[day_num]["title"]

    user_prompt = template.format(
        theme=theme,
        tool=tool,
        day_title=day_title,
    )

    for attempt in range(3):
        try:
            prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
            content, provider = await generate_with_rotation(prompt, max_tokens=512)
            if content:
                logger.info(f"Channel post generated with {provider}")
                return content
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2 ** attempt)

    return None


async def generate_course_post(day_num):
    day = COURSE_DAYS.get(day_num)
    if not day:
        return None

    week = (day_num - 1) // 7 + 1
    prompt = (
        f"Создай привлекательный пост для Telegram-канала о Дне {day_num} курса вайбкодинга.\n"
        f"Тема: {day['title']}\n"
        f"Неделя {week}: {WEEK_NAMES[week]}\n\n"
        f"Вступление: {day['intro']}\n\n"
        f"Совет: {day.get('tip', '')}\n\n"
        "Формат: цепляющий заголовок, 3-4 абзаца, эмодзи, призыв к действию. "
        "Длина: 100-150 слов. Только русский."
    )

    for attempt in range(3):
        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
            content, provider = await generate_with_rotation(full_prompt, max_tokens=512)
            if content:
                logger.info(f"Course post generated with {provider}")
                return content
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2 ** attempt)

    return None


async def post_to_channel(bot, text, image_path=None):
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as photo:
                await bot.send_photo(
                    chat_id=os.getenv("CHANNEL_ID"),
                    photo=photo,
                    caption=text,
                )
        else:
            await bot.send_message(
                chat_id=os.getenv("CHANNEL_ID"),
                text=text,
            )
        logger.info("✅ Post published to channel")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to publish: {e}")
        return False


async def autonomous_post(bot):
    logger.info("🤖 AI Agent: starting autonomous post...")

    post_type = random.choice(["course_promo", "tips", "project", "motivation"])

    if post_type == "course_promo":
        day_num = random.randint(1, 30)
        text = await generate_course_post(day_num)
        img_path = os.path.join("images", f"day_{day_num}.png")
    elif post_type == "tips":
        text = await generate_channel_post(CHANNEL_TOPICS[1])
        img_path = None
    elif post_type == "project":
        text = await generate_channel_post(CHANNEL_TOPICS[2])
        img_path = None
    else:
        text = await generate_channel_post(CHANNEL_TOPICS[3])
        img_path = None

    if text:
        await post_to_channel(bot, text, img_path)
    else:
        logger.warning("⚠️ Failed to generate post")


async def scheduled_autonomous_job(bot):
    logger.info("🤖 Running autonomous agent job...")
    await autonomous_post(bot)
