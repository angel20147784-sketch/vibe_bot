#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест локального Kiro API с новым ключом"""

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="http://localhost:20128/v1",
    timeout=30.0
)

print("Тестирование Big Pickle модели...")

response = client.chat.completions.create(
    model="oc/big-pickle",
    messages=[
        {"role": "user", "content": "Привет! Напиши короткий пост о вайбкодинге на русском языке (3-4 предложения)."}
    ],
    max_tokens=200
)

print("\nОтвет:")
print(response.choices[0].message.content)
print("\nAPI работает!")
