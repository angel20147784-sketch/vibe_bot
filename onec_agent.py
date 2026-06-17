#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""1C Development Skills Agent - based on cc-1c-skills repository"""

import os
import asyncio
import logging
from api_rotator import generate_with_rotation

logger = logging.getLogger(__name__)

# Конфигурация навыков 1С
SKILLS_INFO = {
    "epf": {
        "name": "Внешние обработки (EPF)",
        "description": "Создание, сборка, разборка XML-обработок 1С",
        "commands": ["/epf-init", "/epf-build", "/epf-dump", "/epf-validate"],
    },
    "erf": {
        "name": "Внешние отчёты (ERF)",
        "description": "Создание и работа с внешними отчётами",
        "commands": ["/erf-init", "/erf-build", "/erf-dump", "/erf-validate"],
    },
    "form": {
        "name": "Управляемые формы",
        "description": "Создание и редактирование форм 1С",
        "commands": ["/form-info", "/form-compile", "/form-validate", "/form-edit"],
    },
    "meta": {
        "name": "Метаданные конфигурации",
        "description": "Работа с объектами метаданных",
        "commands": ["/meta-info", "/meta-compile", "/meta-edit", "/meta-validate"],
    },
    "cf": {
        "name": "Корневая конфигурация",
        "description": "Создание и редактирование конфигурации",
        "commands": ["/cf-info", "/cf-init", "/cf-edit", "/cf-validate"],
    },
    "cfe": {
        "name": "Расширения (CFE)",
        "description": "Создание расширений конфигурации",
        "commands": ["/cfe-init", "/cfe-borrow", "/cfe-validate", "/cfe-diff"],
    },
    "db": {
        "name": "Базы данных",
        "description": "Управление информационными базами",
        "commands": ["/db-list", "/db-create", "/db-dump-cf", "/db-load-cf"],
    },
    "web": {
        "name": "Веб-публикация",
        "description": "Публикация баз через Apache",
        "commands": ["/web-publish", "/web-info", "/web-stop", "/web-test"],
    },
    "role": {
        "name": "Роли",
        "description": "Анализ и создание ролей доступа",
        "commands": ["/role-info", "/role-compile", "/role-validate"],
    },
    "skd": {
        "name": "Схема компоновки данных",
        "description": "Работа с отчётами СКД",
        "commands": ["/skd-info", "/skd-compile", "/skd-edit", "/skd-validate"],
    },
}

ONEC_SYSTEM_PROMPT = """Ты — эксперт по 1С:Предприятие 8.3 и вайбкодингу.

Твоя роль:
- Помогать с разработкой на 1С
- Объяснять концепции простым языком
- Рекомендовать инструменты и подходы
- Связывать 1С с вайбкодингом

Темы:
- Внешние обработки (EPF) и отчёты (ERF)
- Управляемые формы
- Метаданные конфигурации
- Расширения (CFE)
- Работа с базами данных
- Веб-публикация
- Автоматизация через ИИ

Стиль: простой, понятный, с примерами.
Пиши на русском языке."""


async def ask_1c(question: str) -> str:
    """Отвечает на вопросы по 1С"""
    prompt = f"{ONEC_SYSTEM_PROMPT}\n\nВопрос: {question}"
    content, provider = await generate_with_rotation(prompt, max_tokens=1024)
    if content:
        logger.info(f"1C response with {provider}")
        return content
    return "Извини, временно не могу ответить. Попробуй позже."


def get_skills_list() -> str:
    """Возвращает список доступных навыков"""
    text = "📦 НАВЫКИ 1С ДЛЯ ИИ:\n\n"
    for key, skill in SKILLS_INFO.items():
        text += f"🔹 {skill['name']}\n"
        text += f"   {skill['description']}\n"
        text += f"   Команды: {', '.join(skill['commands'][:2])}...\n\n"
    return text


def get_skill_info(skill_key: str) -> str:
    """Возвращает информацию о конкретном навыке"""
    skill = SKILLS_INFO.get(skill_key)
    if not skill:
        return f"❌ Навык '{skill_key}' не найден"
    
    text = f"📦 {skill['name']}\n\n"
    text += f"Описание: {skill['description']}\n\n"
    text += "Команды:\n"
    for cmd in skill['commands']:
        text += f"  • {cmd}\n"
    return text
