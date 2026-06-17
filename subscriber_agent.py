#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AI Agent for finding subscribers"""

import os
import asyncio
import logging
from api_rotator import generate_with_rotation

logger = logging.getLogger(__name__)


SEARCH_QUERIES = [
    "Telegram каналы программирование",
    "Telegram каналы IT",
    "Telegram каналы для начинающих",
    "Telegram каналы технологии",
    "Telegram каналы фриланс",
    "Telegram каналы стартапы",
    "Telegram каналы SaaS",
    "Telegram каналы вайбкодинг",
    "Telegram каналы Cursor",
    "Telegram каналы Claude AI",
]

TARGET_AUDIENCE = {
    "interests": [
        "программирование",
        "IT",
        "технологии",
        "фриланс",
        "стартапы",
        "SaaS",
        "вайбкодинг",
        "Cursor",
        "Claude",
        "создание сайтов",
        "Telegram-боты",
    ],
    "channels": [
        "@codesergo",
        "@tproger",
        "@habr",
        "@vc",
        "@startup",
        "@freelance",
        "@it_kursy",
        "@python_course",
        "@webdev",
        "@javascript",
    ],
    "keywords": [
        "курс программирования",
        "научиться кодить",
        "создать сайт",
        "Telegram-бот",
        "заработать на фрилансе",
        "вайбкодинг",
        "Cursor",
        "Claude",
        "ИИ программирование",
    ],
}

SYSTEM_PROMPT = """Ты — ИИ-агент для поиска подписчиков Telegram-канала @CODEScoding.

Твоя задача:
1. Анализировать целевую аудиторию
2. Предлагать каналы для сотрудничества
3. Генерировать тексты для привлечения
4. Создавать стратегии роста

Формат ответа:
- Конкретные рекомендации
- Списки каналов
- Тексты для постов
- План действий

Пиши на русском языке."""


async def analyze_audience():
    prompt = (
        "Проанализируй целевую аудиторию для Telegram-канала о вайбкодинге.\n\n"
        "Аудитория:\n"
        "- Новички которые хотят создавать приложения\n"
        "- Предприниматели\n"
        "- Фрилансеры\n"
        "- Те кто хочет сменить профессию\n\n"
        "Предложи:\n"
        "1. Топ-10 каналов для сотрудничества\n"
        "2. Интересы аудитории\n"
        "3. Лучшие время для постов\n"
        "4. Стратегии привлечения"
    )

    try:
        content, provider = await generate_with_rotation(
            f"{SYSTEM_PROMPT}\n\n{prompt}", max_tokens=1024
        )
        if content:
            logger.info(f"Audience analysis with {provider}")
            return content
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


async def find_similar_channels():
    prompt = (
        "Найди Telegram-каналы похожие на @CODEScoding.\n\n"
        "Тематика: вайбкодинг, программирование, ИИ\n\n"
        "Предложи:\n"
        "1. Топ-10 каналов по тематике\n"
        "2. Размер аудитории\n"
        "3. Как с ними сотрудничать\n"
        "4. Примерыsuccessful коллабораций"
    )

    try:
        content, provider = await generate_with_rotation(
            f"{SYSTEM_PROMPT}\n\n{prompt}", max_tokens=1024
        )
        if content:
            logger.info(f"Similar channels with {provider}")
            return content
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


async def create_promo_texts():
    prompt = (
        "Создай 5 текстов для привлечения подписчиков в @CODEScoding.\n\n"
        "Форматы:\n"
        "1. Пост для Telegram\n"
        "2. Твит\n"
        "3. Пост для VK\n"
        "4. Статья для Habr\n"
        "5. Видео-скрипт\n\n"
        "Тема: бесплатный курс по вайбкодингу за 30 дней"
    )

    try:
        content, provider = await generate_with_rotation(
            f"{SYSTEM_PROMPT}\n\n{prompt}", max_tokens=1500
        )
        if content:
            logger.info(f"Promo texts with {provider}")
            return content
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


async def growth_strategy():
    prompt = (
        "Составь стратегию роста Telegram-канала @CODEScoding на 30 дней.\n\n"
        "Текущая аудитория: ~100 подписчиков\n"
        "Цель: 1000 подписчиков\n\n"
        "Включи:\n"
        "1. Ежедневные действия\n"
        "2. Недельные задачи\n"
        "3. Каналы продвижения\n"
        "4. Метрики для отслеживания"
    )

    try:
        content, provider = await generate_with_rotation(
            f"{SYSTEM_PROMPT}\n\n{prompt}", max_tokens=1500
        )
        if content:
            logger.info(f"Growth strategy with {provider}")
            return content
    except Exception as e:
        logger.error(f"Error: {e}")
    return None
