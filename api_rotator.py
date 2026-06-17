#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""API Rotator - automatic switching between providers when rate limited"""

import os
import asyncio
import logging
import time
import requests
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
        "cooldown_until": 0,
    },
    {
        "name": "OpenRouter-2",
        "api_key": os.getenv("OPENROUTER_API_KEY_2"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "google/gemma-4-31b-it:free",
        "priority": 2,
        "last_error": 0,
        "error_count": 0,
        "cooldown_until": 0,
    },
    {
        "name": "OpenRouter-3",
        "api_key": os.getenv("OPENROUTER_API_KEY_3"),
        "base_url": "https://openrouter.ai/api/v1",
        "model": "google/gemma-4-31b-it:free",
        "priority": 3,
        "last_error": 0,
        "error_count": 0,
        "cooldown_until": 0,
    },
]

# Состояние
_clients = {}


def get_available_providers():
    """Возвращает доступные провайдеры (с API ключом)"""
    return [p for p in PROVIDERS if p.get("api_key")]


def get_client(provider):
    """Получает клиент для провайдера"""
    name = provider["name"]
    if name not in _clients or _clients[name] is None:
        _clients[name] = AsyncOpenAI(
            api_key=provider["api_key"],
            base_url=provider["base_url"],
            timeout=15.0,  # Уменьшили таймаут
        )
    return _clients[name]


def get_available_sorted():
    """Возвращает провайдеры, отсортированные по приоритету и ошибкам"""
    available = get_available_providers()
    now = time.time()
    
    # Фильтруем те, что не в кулдауне
    ready = [p for p in available if p.get("cooldown_until", 0) < now]
    
    if not ready:
        # Все в кулдауне - берём с наименьшим кулдауном
        ready = sorted(available, key=lambda p: p.get("cooldown_until", 0))[:1]
    
    return sorted(ready, key=lambda p: (p["error_count"], p["priority"]))


def mark_provider_error(provider_name, cooldown=60):
    """Отмечает ошибку провайдера с кулдауном"""
    for p in PROVIDERS:
        if p["name"] == provider_name:
            p["last_error"] = time.time()
            p["error_count"] += 1
            p["cooldown_until"] = time.time() + cooldown
            logger.warning(f"⚠️ Provider {provider_name} error, cooldown {cooldown}s")
            break


def reset_provider(provider_name):
    """Сбрасывает ошибки провайдера"""
    for p in PROVIDERS:
        if p["name"] == provider_name:
            p["error_count"] = max(0, p["error_count"] - 1)
            p["cooldown_until"] = 0
            break


def get_provider_status():
    """Возвращает статус всех провайдеров"""
    now = time.time()
    status = []
    for p in PROVIDERS:
        in_cooldown = p.get("cooldown_until", 0) > now
        status.append({
            "name": p["name"],
            "available": bool(p.get("api_key")),
            "errors": p["error_count"],
            "in_cooldown": in_cooldown,
            "cooldown_left": max(0, int(p.get("cooldown_until", 0) - now)),
        })
    return status


def generate_sync(prompt: str, max_tokens: int = 512) -> tuple:
    """Синхронная генерация через requests (быстрее при ошибках)"""
    available = get_available_sorted()
    
    for provider in available:
        try:
            r = requests.post(
                f"{provider['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {provider['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": provider["model"],
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": "Создай контент."},
                    ],
                    "max_tokens": max_tokens,
                },
                timeout=15,
            )
            
            if r.status_code == 200:
                reset_provider(provider["name"])
                return r.json()["choices"][0]["message"]["content"], provider["name"]
            
            elif r.status_code == 429:
                mark_provider_error(provider["name"], cooldown=120)
                logger.warning(f"⚠️ 429 on {provider['name']}")
                continue
            
            else:
                logger.error(f"❌ {provider['name']}: {r.status_code}")
                mark_provider_error(provider["name"], cooldown=30)
                continue
                
        except Exception as e:
            logger.error(f"❌ {provider['name']}: {e}")
            mark_provider_error(provider["name"], cooldown=30)
            continue
    
    return None, "All providers failed"


async def generate_with_rotation(prompt: str, max_tokens: int = 512) -> tuple:
    """Генерирует контент с автоматическим переключением провайдеров"""
    # Используем синхронную версию через requests (надёжнее)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: generate_sync(prompt, max_tokens))
