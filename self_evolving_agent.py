#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Self-Evolving Content Agent - based on Hermes Agent Self-Evolution principles"""

import os
import json
import asyncio
import logging
import random
from openai import AsyncOpenAI
from datetime import datetime

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
        )
    return _client


# Словарь с промптами для эволюции
EVOLVING_PROMPTS = {
    "post": {
        "current": """Ты — маркетолог Telegram-канала @CODEScoding.
Создай рекламный пост о бесплатном курсе вайбкодинга.
Курс: 30 дней, бесплатно
Чему научишься: Cursor, Claude, v0.dev
Формат: 3-5 строк, эмодзи, ссылка t.me/CODEScodingbot
Стиль: живой, мотивирующий""",
        
        "variants": [
            """Ты — маркетолог Telegram-канала @CODEScoding.
Создай вирусный пост о курсе вайбкодинга.
Используй триггеры: страх упустить, социальное доказательство, срочность.
Формат: вопрос + ответ + призыв к действию.""",
            
            """Ты — маркетолог Telegram-канала @CODEScoding.
Создай пост-историю о том, как кто-то начал зарабатывать на вайбкодинге.
Формат: проблема -> решение -> результат.
Эмоции + конкретика.""",
            
            """Ты — маркетолог Telegram-канала @CODEScoding.
Создай пост с лайфхаками по вайбкодингу.
5 полезных советов + ссылка на курс.
Формат: список с эмодзи.""",
        ],
        
        "scores": [],
    },
    
    "welcome": {
        "current": """Ты — наставник Telegram-бота @CODEScodingbot.
Напиши приветственное сообщение для нового подписчика.
Курс: 30 дней по вайбкодингу
Бесплатно: День 1
Платно: 200 Stars
Стиль: дружелюбный, мотивирующий""",
        
        "variants": [
            """Ты — наставник Telegram-бота @CODEScodingbot.
Напиши приветствие с акцентом на быстрый результат.
"Создашь первое приложение за час!"
Формат: 3 предложения + команда /day""",
            
            """Ты — наставник Telegram-бота @CODEScodingbot.
Напиши приветствие с социальным доказательством.
"100+ человек уже прошли курс!"
Формат: цифры + benefits + призыв""",
        ],
        
        "scores": [],
    },
}


async def generate_with_prompt(prompt: str, max_tokens: int = 512) -> str:
    client = get_client()
    try:
        response = await client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Создай контент для Telegram-канала о вайбкодинге."},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


async def evaluate_content(content: str) -> float:
    """Оценивает качество контента по критериям"""
    score = 0.0
    
    # Длина
    if 50 < len(content) < 500:
        score += 0.2
    
    # Эмодзи
    if any(c in content for c in "🚀💡✨🎯🔥💪"):
        score += 0.2
    
    # Ссылка
    if "t.me/" in content:
        score += 0.2
    
    # Призыв к действию
    if any(word in content.lower() for word in ["нажми", "перейди", "подпишись", "начни"]):
        score += 0.2
    
    # Конкретика
    if any(word in content for word in ["30 дней", "бесплатно", "Cursor", "Claude"]):
        score += 0.2
    
    return min(score, 1.0)


async def evolve_content_type(content_type: str, iterations: int = 3):
    """Эволюционирует промпт для конкретного типа контента"""
    config = EVOLVING_PROMPTS.get(content_type)
    if not config:
        return
    
    logger.info(f"🧬 Начинаю эволюцию для: {content_type}")
    
    best_prompt = config["current"]
    best_score = 0.0
    
    # Текущий лучший
    content = await generate_with_prompt(best_prompt)
    if content:
        best_score = await evaluate_content(content)
        config["scores"] = [best_score]
    
    # Пробуем варианты
    for i, variant in enumerate(config["variants"]):
        content = await generate_with_prompt(variant)
        if content:
            score = await evaluate_content(content)
            config["scores"].append(score)
            
            if score > best_score:
                best_score = score
                best_prompt = variant
                logger.info(f"✅ Новый лучший вариант #{i+1}: {score:.2f}")
    
    # Мутируем лучший промпт
    mutation_prompt = f"""Вот успешный промпт для создания постов в Telegram:

{best_prompt}

Предложи 2 улучшенных варианта этого промпта. Сделай их более эффективными.
Формат: просто промпты, через пустую строку."""
    
    client = get_client()
    try:
        response = await client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[
                {"role": "system", "content": mutation_prompt},
                {"role": "user", "content": "Улучши промпт."},
            ],
            max_tokens=512,
        )
        mutations = response.choices[0].message.content.split("\n\n")
        
        for mutation in mutations[:2]:
            if len(mutation) > 50:
                content = await generate_with_prompt(mutation)
                if content:
                    score = await evaluate_content(content)
                    if score > best_score:
                        best_score = score
                        best_prompt = mutation
                        logger.info(f"🧬 Мутация улучшила: {score:.2f}")
    except Exception as e:
        logger.error(f"Mutation error: {e}")
    
    # Сохраняем лучший промпт
    config["current"] = best_prompt
    config["scores"].append(best_score)
    
    logger.info(f"🏆 Лучший промпт для {content_type}: {best_score:.2f}")
    
    return {
        "type": content_type,
        "best_score": best_score,
        "scores": config["scores"],
        "prompt": best_prompt[:200] + "...",
    }


async def run_evolution(iterations: int = 3):
    """Запускает полную эволюцию всех типов контента"""
    logger.info("🧬 Запускаю эволюцию контента...")
    
    results = {}
    for content_type in EVOLVING_PROMPTS.keys():
        result = await evolve_content_type(content_type, iterations)
        if result:
            results[content_type] = result
    
    return results


if __name__ == "__main__":
    asyncio.run(run_evolution())
