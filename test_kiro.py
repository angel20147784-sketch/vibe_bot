#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест Kiro-специфичных endpoints"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Kiro-специфичные варианты
endpoints = [
    ("https://api.kiro.ai/openai/v1/chat/completions", "anthropic/claude-3-5-sonnet-20241022"),
    ("https://kiro.ai/api/v1/chat/completions", "anthropic/claude-3-5-sonnet-20241022"),
    ("https://api.kiro.ai/v1/messages", "claude-3-5-sonnet-20241022"),  # Anthropic формат
]

print("Тестирование Kiro endpoints...\n")

for endpoint, model in endpoints:
    print(f"Пробую: {endpoint}")
    print(f"Модель: {model}")

    try:
        # Попробуем OpenAI формат
        if "chat/completions" in endpoint:
            response = requests.post(
                endpoint,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                },
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=10,
                verify=False  # Игнорируем SSL проблемы
            )
        else:
            # Anthropic формат
            response = requests.post(
                endpoint,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                },
                headers={
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                timeout=10,
                verify=False
            )

        print(f"  Статус: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ РАБОТАЕТ!")
            print(f"  Ответ: {response.text[:200]}")
            break
        else:
            print(f"  Ошибка: {response.text[:300]}")
    except Exception as e:
        print(f"  Ошибка: {str(e)[:150]}")
    print()
