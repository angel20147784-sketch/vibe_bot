#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AI Tutor - guides users after subscription"""

import os
import logging
from openai import AsyncOpenAI
from course_data import COURSE_DAYS, WEEK_NAMES

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

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


TUTOR_SYSTEM = """Ты — ИИ-наставник Telegram-канала по вайбкодингу @codesergo.

Твоя роль:
- Помогать пользователям разобраться в курсе
- Отвечать на вопросы по каждому дню
- Объяснять сложные темы простым языком
- Мотивировать и поддерживать

Стиль:
- Простой и понятный язык
- Используй эмодзи (2-3 на ответ)
- Короткие абзацы (2-3 предложения)
- Без Markdown-разметки

Формат ответа:
- Отвечай на русском языке
- Будь дружелюбным и supportive
- Давай конкретные советы
- Если вопрос по теме дня — опирайся на контент курса

Темы курса:
- День 1-7: Знакомство с вайбкодингом (Cursor, Claude, v0.dev)
- День 8-14: Инструменты и техники (промпт-инжиниринг, API, БД)
- День 15-21: Реальные проекты (авторизация, деплой, монетизация)
- День 22-28: Продвинутые техники (оптимизация, безопасность, тесты)
- День 29-30: Итоги и планы"""


ONBOARDING_MESSAGES = {
    "welcome": (
        "🎉 Добро пожаловать в курс!\n\n"
        "Теперь тебе доступны все 30 дней.\n\n"
        "Как начать:\n"
        "1. Отправь /day чтобы получить текущий урок\n"
        "2. Читай и выполняй шаги\n"
        "3. Отправь /next когда готов к следующему\n\n"
        "Могу помочь с любым вопросом — просто напиши!"
    ),
    "day_1": (
        "📚 Начнём с Дня 1!\n\n"
        "Сегодня ты узнаешь что такое вайбкодинг.\n\n"
        "Задачи дня:\n"
        "1. Скачай Cursor (cursor.com)\n"
        "2. Создай аккаунт\n"
        "3. Создай первую страницу\n\n"
        "Отправь /day чтобы получить урок с подробностями."
    ),
    "need_help": (
        "💡 Нужна помощь?\n\n"
        "Просто напиши свой вопрос — я отвечу!\n\n"
        "Могу помочь с:\n"
        "• Установкой инструментов\n"
        "• Написанием промптов\n"
        "• Исправлением ошибок\n"
        "• Объяснением тем курса"
    ),
}


def get_onboarding_text(user_day):
    if user_day == 1:
        return ONBOARDING_MESSAGES["day_1"]
    return ONBOARDING_MESSAGES["welcome"]


async def ask_tutor(question, current_day=1):
    client = get_client()

    day_info = COURSE_DAYS.get(current_day, {})
    week = (current_day - 1) // 7 + 1
    week_name = WEEK_NAMES.get(week, "")

    context = (
        f"Пользователь сейчас на дне {current_day} из 30.\n"
        f"Неделя {week}: {week_name}\n"
        f"Тема дня: {day_info.get('title', 'Неизвестно')}\n"
        f"Вступление: {day_info.get('intro', '')}\n\n"
        f"Вопрос пользователя: {question}"
    )

    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model="google/gemma-4-31b-it:free",
                messages=[
                    {"role": "system", "content": TUTOR_SYSTEM},
                    {"role": "user", "content": context},
                ],
                max_tokens=512,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"Tutor attempt {attempt + 1} failed: {e}")

    return (
        "Извини, временно не могу ответить. "
        "Попробуй позже или напиши /day чтобы получить урок."
    )


async def get_day_summary(day_num):
    day = COURSE_DAYS.get(day_num)
    if not day:
        return "День не найден."

    week = (day_num - 1) // 7 + 1

    sections_text = ""
    for sec_title, items in day.get("sections", []):
        sections_text += f"\n▸ {sec_title}:\n"
        for item in items:
            sections_text += f"  • {item}\n"

    steps_text = ""
    if day.get("steps"):
        steps_text = "\n📋 Шаги:\n"
        for i, (title, desc) in enumerate(day["steps"], 1):
            steps_text += f"{i}. {title} — {desc}\n"

    tip = f"\n💡 Совет: {day['tip']}" if day.get("tip") else ""

    return (
        f"📚 ДЕНЬ {day_num}: {day['title']}\n"
        f"Неделя {week}: {WEEK_NAMES[week]}\n\n"
        f"{day['intro']}\n"
        f"{sections_text}"
        f"{steps_text}"
        f"{tip}"
    )
