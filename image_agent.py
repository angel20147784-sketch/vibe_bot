#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Image Agent — генерирует изображения к постам"""

import os
import sys
import json
import time
import random
import logging
import requests
from urllib.request import urlopen, Request
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
STATE_FILE = "image_agent_state.json"


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    try:
        with open("image_agent.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def ai_generate(prompt, max_tokens=500):
    """Генерация текста через OpenRouter"""
    if not OPENROUTER_KEY:
        return None
    data = json.dumps({
        "model": "google/gemma-4-31b-it:free",
        "messages": [
            {"role": "system", "content": "Ты — креативный маркетолог. Генерируешь промпты для создания изображений. Пиши на английском языке для лучшего результата."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.9
    }).encode("utf-8")
    try:
        req = Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {OPENROUTER_KEY}"},
            method="POST"
        )
        resp = urlopen(req, timeout=60)
        result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"Ошибка AI: {e}")
        return None


def generate_image_pollinations(prompt):
    """Генерация изображения через Pollinations.ai (бесплатно)"""
    try:
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&seed={random.randint(1, 10000)}"
        
        response = requests.get(url, timeout=60, allow_redirects=True)
        if response.status_code == 200 and len(response.content) > 1000:
            return response.content
    except Exception as e:
        log(f"Ошибка генерации: {e}")
    return None


def generate_image_fallback(prompt):
    """Альтернативный генератор через另一个 бесплатный API"""
    try:
        import urllib.parse
        encoded = urllib.parse.quote(prompt[:200])
        url = f"https://api.limewire.com/api/image/generation"
        # Pollinations более надёжный
        return None
    except Exception:
        return None


def post_photo_to_telegram(photo_bytes, text):
    """Публикация фото с подписью"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 Начать бесплатно", "url": "https://t.me/CODEScodingbot?start=course"}],
            [{"text": "📖 Посмотреть курс", "url": "https://vibecodes-ten.vercel.app/"}]
        ]
    }
    
    try:
        files = {"photo": ("image.jpg", photo_bytes, "image/jpeg")}
        data = {
            "chat_id": CHANNEL_ID,
            "caption": text[:1024],
            "reply_markup": json.dumps(keyboard)
        }
        
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            data=data,
            files=files,
            timeout=60
        )
        result = r.json()
        if result.get("ok"):
            log("Фото опубликовано!")
            return True
        else:
            log(f"Ошибка API: {result}")
            return False
    except Exception as e:
        log(f"Ошибка публикации: {e}")
        return False


# === ТЕМЫ ДЛЯ ИЗОБРАЖЕНИЙ ===

IMAGE_THEMES = [
    {
        "theme": "cursor_editor",
        "prompt": "Modern code editor interface with AI autocomplete, dark theme, colorful syntax highlighting, futuristic UI design, 4K quality",
        "text": "⚡ Cursor — редактор кода с ИИ\n\nАвтодополнение, генерация компонентов, дебаг — всё голосом.\n\nКурс бесплатный 👇"
    },
    {
        "theme": "ai_brain",
        "prompt": "Glowing AI brain neural network, purple and blue colors, futuristic technology, abstract digital art, clean design",
        "text": "🧠 ИИ пишет код за тебя\n\nClaude, GPT, Gemini — выбирай своего помощника.\n\nНачни бесплатно 👇"
    },
    {
        "theme": "coding_setup",
        "prompt": "Minimalist developer desk setup, ultrawide monitor with code, ambient lighting, cozy workspace, aesthetic photography",
        "text": "💻 Рабочее место вайбкодера\n\nОдин экран + Cursor = готовый проект.\n\nКурс бесплатный 👇"
    },
    {
        "theme": "rocket_launch",
        "prompt": "Rocket launching from laptop screen, digital art, vibrant colors, success concept, modern flat design",
        "text": "🚀 Запусти свой проект за вечер\n\nОт идеи до деплоя — 4 часа.\n\nНачни бесплатно 👇"
    },
    {
        "theme": "money_growth",
        "prompt": "Growing money plant, coins and bills sprouting, green and gold colors, financial growth concept, clean illustration",
        "text": "💰 Вайбкодинг = деньги\n\nФриланс: 15-50К за проект\nSaaS: 100-300К/мес\n\nКурс бесплатный 👇"
    },
    {
        "theme": "team_ai",
        "prompt": "Human team collaborating with AI robots, futuristic office, holographic displays, blue and purple theme, modern illustration",
        "text": "🤝 Человек + ИИ = суперсила\n\nТы думаешь, ИИ делает.\n\nКурс бесплатный 👇"
    },
    {
        "theme": "phone_bot",
        "prompt": "Smartphone showing Telegram bot interface, modern UI, gradient background, tech aesthetic, clean design",
        "text": "📱 Telegram-бот за 1 час\n\nАвтоматизация заявок, записей, оплат.\n\nКурс бесплатный 👇"
    },
    {
        "theme": "saas_dashboard",
        "prompt": "SaaS dashboard with charts and analytics, dark mode, modern UI design, purple accent colors, professional look",
        "text": "📊 SaaS-сервис с подпиской\n\nСоздай свой продукт за вечер.\n\nКурс бесплатный 👇"
    },
    {
        "theme": "lightning_speed",
        "prompt": "Lightning bolt striking code on screen, electric blue and yellow, speed concept, dynamic composition, digital art",
        "text": "⚡ Скорость вайбкодинга\n\n40 минут вместо 40 часов.\n\nКурс бесплатный 👇"
    },
    {
        "theme": "future_tech",
        "prompt": "Futuristic holographic interface, floating code elements, cyberpunk aesthetic, purple and cyan colors, abstract tech art",
        "text": "🔮 Будущее разработки\n\nЧерез 5 лет все будут использовать ИИ.\n\nНачни сегодня 👇"
    },
]


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_theme_index": -1, "total_posts": 0, "last_run": None, "errors": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def run_image_cycle():
    """Один цикл генерации и публикации изображения"""
    log("=" * 40)
    log("🖼️ IMAGE AGENT запущен")
    log("=" * 40)

    state = load_state()

    # Выбираем тему (без повторов)
    last_idx = state.get("last_theme_index", -1)
    available = [i for i in range(len(IMAGE_THEMES)) if i != last_idx]
    theme_idx = random.choice(available)
    theme = IMAGE_THEMES[theme_idx]

    log(f"Тема: {theme['theme']}")

    # Генерируем изображение
    log("Генерация изображения...")
    photo_bytes = generate_image_pollinations(theme["prompt"])

    if photo_bytes:
        log(f"Изображение сгенерировано ({len(photo_bytes)} байт)")

        # Публикуем
        if post_photo_to_telegram(photo_bytes, theme["text"]):
            state["total_posts"] = state.get("total_posts", 0) + 1
            state["last_theme_index"] = theme_idx
            log("Пост опубликован!")
        else:
            state["errors"] = state.get("errors", 0) + 1
    else:
        log("Не удалось сгенерировать изображение")
        state["errors"] = state.get("errors", 0) + 1

    state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)

    log(f"Итого: {state['total_posts']} постов, {state['errors']} ошибок")
    return True


if __name__ == "__main__":
    while True:
        try:
            run_image_cycle()
        except Exception as e:
            log(f"Ошибка: {e}")

        # Ждём 6 часов
        log("Следующий цикл через 6 часов...")
        time.sleep(21600)
