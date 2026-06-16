#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест различных endpoint для API ключа"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Список возможных endpoint для тестирования
endpoints = [
    "https://api.openrouter.ai/api/v1/chat/completions",
    "https://openrouter.ai/api/v1/chat/completions",
    "https://api.together.xyz/v1/chat/completions",
    "https://api.perplexity.ai/chat/completions",
]

test_payload = {
    "model": "anthropic/claude-3-5-sonnet-20241022",
    "messages": [{"role": "user", "content": "Hi"}],
    "max_tokens": 10
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("Тестирование различных endpoints...\n")

for endpoint in endpoints:
    print(f"Пробую: {endpoint}")
    try:
        response = requests.post(endpoint, json=test_payload, headers=headers, timeout=10)
        print(f"  Статус: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ РАБОТАЕТ! Ответ: {response.json()}")
            break
        else:
            print(f"  Ошибка: {response.text[:200]}")
    except Exception as e:
        print(f"  Ошибка соединения: {str(e)[:100]}")
    print()
