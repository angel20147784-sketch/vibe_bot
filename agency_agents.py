#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agency AI Agents - Growth, Sales, Marketing"""

import os
import asyncio
import logging
from api_rotator import generate_with_rotation

logger = logging.getLogger(__name__)


GROWTH_HACKER_PROMPT = """Ты — Growth Hacker, эксперт по росту аудитории.

Твоя экспертиза:
- Вирусные петли и реферальные программы
- Оптимизация воронки конверсии
- A/B тестирование
- Продуктовый рост
- Каналы привлечения

Для Telegram-канала @CODEScoding (курс вайбкодинга):
1. Найди нестандартные каналы роста
2. Предложи вирусные механики
3. Составь план экспериментов
4. Рассчитай метики роста

Формат: конкретные действия, метики, сроки."""

OUTBOUND_STRATEGIST_PROMPT = """Ты — Outbound Strategist, эксперт по привлечению клиентов.

Твоя экспертиза:
- Сигнальный outbound
- Мультиканальные последовательности
- Персонализация
- ICP и сегментация

Для продажи курса вайбкодинга:
1. Определи ICP (идеального клиента)
2. Найди сигналы покупки
3. Создай последовательности сообщений
4. Настрой персонализацию

Формат: шаблоны сообщений, сегменты, метики."""

CONTENT_CREATOR_PROMPT = """Ты — Content Creator, эксперт по созданию контента.

Твоя экспертиза:
- Мультиплатформенный контент
- Редакционные календари
- Копирайтинг
- Сторителлинг

Для Telegram-канала @CODEScoding:
1. Создай контент-план на неделю
2. Напиши 5 постов
3. Предложи форматы контента
4. Определи лучшее время публикации

Формат: готовые тексты, расписание, метики."""

SALES_COACH_PROMPT = """Ты — Sales Coach, эксперт по продажам.

Твоя экспертиза:
- Подготовка к звонкам
- Обработка возражений
- Завершение сделок
- Тренировка продавцов

Для продажи курса вайбкодинга:
1. Создай скрипт продаж
2. Обработай типовые возражения
3. Настройте цепочку касаний
4. Определи триггеры покупки

Формат: скрипты, возражения, ответы."""


async def run_growth_hacker():
    try:
        prompt = f"{GROWTH_HACKER_PROMPT}\n\nДай план роста Telegram-канала @CODEScoding на 30 дней. Текущая аудитория: 100 подписчиков. Цель: 1000."
        content, provider = await generate_with_rotation(prompt, max_tokens=1024)
        if content:
            logger.info(f"Growth Hacker responded with {provider}")
            return content
    except Exception as e:
        logger.error(f"Growth Hacker error: {e}")
    return None


async def run_outbound_strategist():
    try:
        prompt = f"{OUTBOUND_STRATEGIST_PROMPT}\n\nСоздай outbound-стратегию для продажи курса вайбкодинга. Курс: 30 дней, 200 Stars. Целевая аудитория: новички в программировании."
        content, provider = await generate_with_rotation(prompt, max_tokens=1024)
        if content:
            logger.info(f"Outbound responded with {provider}")
            return content
    except Exception as e:
        logger.error(f"Outbound error: {e}")
    return None


async def run_content_creator():
    try:
        prompt = f"{CONTENT_CREATOR_PROMPT}\n\nСоздай контент-план и 5 постов для Telegram-канала @CODEScoding о курсе вайбкодинга."
        content, provider = await generate_with_rotation(prompt, max_tokens=1500)
        if content:
            logger.info(f"Content Creator responded with {provider}")
            return content
    except Exception as e:
        logger.error(f"Content error: {e}")
    return None


async def run_sales_coach():
    try:
        prompt = f"{SALES_COACH_PROMPT}\n\nСоздай скрипт продаж для курса вайбкодинга. Обработай возражения: 'Дорого', 'Нет времени', 'Я не программист'."
        content, provider = await generate_with_rotation(prompt, max_tokens=1024)
        if content:
            logger.info(f"Sales Coach responded with {provider}")
            return content
    except Exception as e:
        logger.error(f"Sales error: {e}")
    return None
