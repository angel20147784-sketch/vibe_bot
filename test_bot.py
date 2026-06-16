#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тестовый скрипт для проверки генерации постов"""

import asyncio
from content_generator import generate_post

async def test_generate_post():
    print("Тестирование генерации поста...\n")
    try:
        post = await generate_post()
        print("Пост успешно сгенерирован!\n")
        print("=" * 50)
        print(post)
        print("=" * 50)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_generate_post())
