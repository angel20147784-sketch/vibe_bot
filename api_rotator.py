#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""API Rotator - automatic switching between providers when rate limited"""

import os
import asyncio
import logging
import time
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Провайдеры API с приоритетами
PROVIDERS = [
    {
        "name": "OpenRouter",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "google/gemma-4-31b-it:free",
        "priority": 1,
        "last_error": 0,
        "error_count": 0,
    },
    {
        "name": "OpenRouter-2",
        "api_key": os.getenv("OPENROUTER_API_KEY_2"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "google/gemma-4-31b-it:free",
        "priority": 2,
        "last_error": 0,
        "error_count": 0,
    },
    {
        "name": "OpenRouter-3",
        "api_key": os.getenv("OPENROUTER_API_KEY_3"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "google/gemma-4-31b-it:free",
        "priority": 3,
        "last_error": 0,
        "error_count": 0,
    },
]

# Состояние
_current_provider_index = 0
_clients = {}


def get_available_providers():
    """Возвращает доступные провайдеры (с API ключом)"""
    return [p for p in PROVIDERS if p.get("api_key")]


def get_client(provider=None):
    """Получает клиент для провайдера"""
    if provider is None:
        provider = get_current_provider()
    
    name = provider["name"]
    if name not in _clients or _clients[name] is None:
        _clients[name] = AsyncOpenAI(
            api_key=provider["api_key"],
            base_url=provider["base_url"],
            timeout=60.0,
        )
    return _clients[name]


def get_current_provider():
    """Получает текущий рабочий провайдер"""
    available = get_available_providers()
    if not available:
        return None
    
    # Сортируем по приоритету и количеству ошибок
    sorted_providers = sorted(available, key=lambda p: (p["error_count"], p["priority"]))
    return sorted_providers[0]


def mark_provider_error(provider_name):
    """Отмечает ошибку провайдера"""
    for p in PROVIDERS:
        if p["name"] == provider_name:
            p["last_error"] = time.time()
            p["error_count"] += 1
            logger.warning(f"⚠️ Provider {provider_name} error count: {p['error_count']}")
            break


def reset_provider(provider_name):
    """Сбрасывает ошибки провайдера"""
    for p in PROVIDERS:
        if p["name"] == provider_name:
            p["error_count"] = 0
            p["last_error"] = 0
            logger.info(f"✅ Provider {provider_name} reset")
            break


def get_provider_status():
    """Возвращает статус всех провайдеров"""
    status = []
    for p in PROVIDERS:
        status.append({
            "name": p["name"],
            "available": bool(p.get("api_key")),
            "errors": p["error_count"],
            "active": p["name"] == get_current_provider()["name"] if get_current_provider() else False,
        })
    return status


async def generate_with_rotation(prompt: str, max_tokens: int = 512) -> tuple:
    """Генерирует контент с автоматическим переключением провайдеров"""
    available = get_available_providers()
    
    if not available:
        return None, "No providers available"
    
    # Сортируем по приоритету и ошибкам
    sorted_providers = sorted(available, key=lambda p: (p["error_count"], p["priority"]))
    
    for provider in sorted_providers:
        try:
            client = get_client(provider)
            response = await client.chat.completions.create(
                model=provider["model"],
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Создай контент для Telegram-канала."},
                ],
                max_tokens=max_tokens,
            )
            reset_provider(provider["name"])
            return response.choices[0].message.content, provider["name"]
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                mark_provider_error(provider["name"])
                logger.warning(f"⚠️ Rate limited on {provider['name']}, trying next...")
                continue
            else:
                logger.error(f"❌ Error on {provider['name']}: {e}")
                continue
    
    return None, "All providers failed"


async def test_providers():
    """Тестирует всех провайдеров"""
    print("🔍 Тестирование провайдеров...\n")
    
    for provider in get_available_providers():
        try:
            client = get_client(provider)
            response = await client.chat.completions.create(
                model=provider["model"],
                messages=[
                    {"role": "user", "content": "Скажи 'OK'"}
                ],
                max_tokens=10,
            )
            print(f"✅ {provider['name']}: работает")
            reset_provider(provider["name"])
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                mark_provider_error(provider["name"])
                print(f"⚠️ {provider['name']}: rate limited")
            else:
                print(f"❌ {provider['name']}: {str(e)[:50]}")


if __name__ == "__main__":
    asyncio.run(test_providers())
