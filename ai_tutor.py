#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AI Tutor - guides users after subscription"""

import os
import logging
from api_rotator import generate_with_rotation
from course_data import COURSE_DAYS, WEEK_NAMES

logger = logging.getLogger(__name__)


TUTOR_SYSTEM = """Ты — живой ИИ-наставник Telegram-канала @codesergo. Ты общаешься как друг, помогаешь с вайбкодингом.

Твоя роль:
- Отвечать на ВСЕ вопросы пользователей (не только по курсу)
- Помогать с кодом, ошибками, идеями
- Объяснять сложные темы простым языком
- Мотивировать и поддерживать
- Давать практические советы и примеры кода

Стиль общения:
- Живой, дружелюбный, как друг
- Используй эмодзи (3-5 в ответе)
- Пиши развёрнуто (3-8 абзацев)
- Давай конкретные примеры кода когда уместно
- Задавай уточняющие вопросы чтобы лучше понять задачу
- Если не знаешь ответ — скажи честно, но предложи варианты

Темы которые ты знаешь:
- Вайбкодинг: Cursor, Claude, v0.dev, Replit
- Программирование: HTML, CSS, JavaScript, Python, React
- Telegram-боты: python-telegram-bot
- Деплой: Vercel, Railway, GitHub
- Монетизация: SaaS, фриланс, Telegram-боты
- 1С:Предприятие (базовые вопросы)

Формат ответа:
- Всегда отвечай на русском языке
- Пиши полноценными предложениями
- Давай примеры когда это уместно
- Если вопрос не по теме — всё равно ответь, помоги"""


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
            prompt = f"{TUTOR_SYSTEM}\n\n{context}"
            content, provider = await generate_with_rotation(prompt, max_tokens=512)
            if content:
                logger.info(f"Tutor responded with {provider}")
                return content
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
