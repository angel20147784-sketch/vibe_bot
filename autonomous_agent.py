#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Автономный ИИ-агент — сам решает что делать и что публиковать"""

import os
import sys
import json
import time
import random
import logging
from urllib.request import urlopen, Request
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
STATE_FILE = "autonomous_agent_state.json"


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    try:
        with open("autonomous_agent.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def ai_generate(prompt, max_tokens=1000):
    """Генерация текста через OpenRouter"""
    if not OPENROUTER_KEY:
        log("Нет OPENROUTER_API_KEY")
        return None

    data = json.dumps({
        "model": "google/gemma-4-31b-it:free",
        "messages": [
            {"role": "system", "content": "Ты — маркетолог и контент-мейкер для Telegram-канала о вайбкодинге и ИИ. Пиши на русском языке. Будь полезным, интересным, без спама и навязывания."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.9
    }).encode("utf-8")

    try:
        req = Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENROUTER_KEY}"
            },
            method="POST"
        )
        resp = urlopen(req, timeout=60)
        result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"Ошибка AI: {e}")
        return None


def fetch_url(url, timeout=15):
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urlopen(req, timeout=timeout)
        return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None


def post_to_telegram(text):
    data = json.dumps({
        "chat_id": CHANNEL_ID,
        "text": text[:4000],
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🚀 Начать", "url": "https://t.me/CODEScodingbot?start=course"}]
            ]
        }
    }).encode("utf-8")

    try:
        req = Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urlopen(req, timeout=30)
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("ok"):
            log("Пост опубликован!")
            return True
        else:
            log(f"Ошибка API: {result}")
            return False
    except Exception as e:
        log(f"Ошибка публикации: {e}")
        return False


# === ФУНКЦИИ ПОИСКА ===

def search_github():
    """Поиск трендов GitHub"""
    html = fetch_url("https://github.com/trending?since=weekly")
    if not html:
        return []
    import re
    repos = []
    matches = re.findall(r'href="(/[^/]+/[^"]+)"[^>]*>\s*<span[^>]*>([^<]+)</span>', html)
    for path, name in matches:
        path = path.strip("/")
        if path.count("/") == 1 and path not in [r["name"] for r in repos]:
            repos.append({"name": name.strip(), "url": f"https://github.com/{path}"})
    return repos[:5]


def search_habr():
    """Поиск свежих статей на Habr"""
    html = fetch_url("https://habr.com/ru/articles/")
    if not html:
        return []
    import re
    articles = []
    matches = re.findall(r'<h2[^>]*><a[^>]*href="(/ru/articles/[^"]+)"[^>]*>([^<]+)</a>', html)
    for path, title in matches:
        articles.append({"name": title.strip(), "url": f"https://habr.com{path}"})
    return articles[:5]


def search_producthunt():
    """Поиск топ-продуктов"""
    html = fetch_url("https://www.producthunt.com")
    if not html:
        return []
    import re
    products = []
    matches = re.findall(r'<a[^>]*href="(/posts/[^"]+)"[^>]*>([^<]+)</a>', html)
    for path, name in matches:
        products.append({"name": name.strip(), "url": f"https://producthunt.com{path}"})
    return products[:5]


# === РЕШЕНИЯ АГЕНТА ===

def decide_action(state):
    """Агент решает что делать"""
    last_actions = state.get("last_actions", [])
    post_count = state.get("total_posts", 0)
    hour = time.localtime().tm_hour

    # Определяем тип контента по времени
    if 6 <= hour < 12:
        time_type = "утро"
    elif 12 <= hour < 18:
        time_type = "день"
    elif 18 <= hour < 23:
        time_type = "вечер"
    else:
        time_type = "ночь"

    # Исключаем повторы
    available_actions = [
        "github_trends",
        "habr_articles",
        "tips",
        "questions",
        "case_study",
        "tool_review",
        "motivation",
        "meme",
        "prompt_recipe",
        "comparison"
    ]

    # Убираем недавние действия
    for action in last_actions[-3:]:
        if action in available_actions:
            available_actions.remove(action)

    if not available_actions:
        available_actions = ["tips", "questions", "motivation"]

    action = random.choice(available_actions)

    # Учитываем время суток
    if time_type == "ночь":
        action = random.choice(["tips", "prompt_recipe", "tool_review"])

    return action, time_type


def generate_content(action, time_type, state):
    """Агент генерирует контент на основе решения"""

    if action == "github_trends":
        repos = search_github()
        if repos:
            prompt = f"Напиши короткий Telegram-пост (5-8 строк) о трендах GitHub на этой недели. Репозитории: {', '.join([r['name'] for r in repos[:3]])}. Добавь хэштеги."
            text = ai_generate(prompt)
            if text:
                # Добавляем ссылки
                links = "\n\n".join([f"• {r['name']}: {r['url']}" for r in repos[:5]])
                return f"{text}\n\n{links}"

    elif action == "habr_articles":
        articles = search_habr()
        if articles:
            prompt = f"Напиши Telegram-пост (5-8 строк) о свежих статьях на Habr. Статьи: {', '.join([a['name'] for a in articles[:3]])}. Будь полезным."
            text = ai_generate(prompt)
            if text:
                links = "\n\n".join([f"• {a['name']}: {a['url']}" for a in articles[:3]])
                return f"{text}\n\n{links}"

    elif action == "tips":
        prompt = f"Напиши полезный лайфхак для вайбкодера (5-7 строк). Тема: Cursor, Claude, v0.dev или Supabase. Дай конкретный совет с примером."
        return ai_generate(prompt)

    elif action == "questions":
        prompt = f"Напиши интерактивный пост-вопрос для Telegram-канала о вайбкодинге. Предложи 3-4 варианта ответа. Время суток: {time_type}."
        return ai_generate(prompt)

    elif action == "case_study":
        prompt = f"Напиши короткий кейс (5-7 строк) как кто-то создал проект с помощью ИИ. Укажи: что сделали, сколько времени, какой результат. Стиль: мотивирующий."
        return ai_generate(prompt)

    elif action == "tool_review":
        prompt = f"Напиши обзор инструмента для вайбкодинга (5-8 строк). Выбери: Cursor Rules, v0.dev, Bolt.new, Replit Agent, Windsurf. Расскажи что умеет и зачем нужен."
        return ai_generate(prompt)

    elif action == "motivation":
        prompt = f"Напиши мотивирующий пост для Telegram (3-5 строк) о вайбкодинге. Время суток: {time_type}. Стиль: коротко, энергично, вдохновляюще."
        return ai_generate(prompt)

    elif action == "meme":
        prompt = f"Напиши смешной пост-мем про программирование и ИИ (3-5 строк). Юмор про Cursor, Claude, Copilot или вайбкодинг."
        return ai_generate(prompt)

    elif action == "prompt_recipe":
        prompt = f"Напиши готовый промпт для Claude/Cursor (5-7 строк). Формат: задача + готовый промпт + ожидаемый результат. Тема: создание компонента или сервиса."
        return ai_generate(prompt)

    elif action == "comparison":
        prompt = f"Напиши сравнение двух инструментов для вайбкодинга (5-7 строк). Формат: инструмент A vs инструмент B, плюсы и минусы каждого."
        return ai_generate(prompt)

    return None


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_actions": [],
        "total_posts": 0,
        "last_run": None,
        "errors": 0
    }


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def run_autonomous_cycle():
    """Основной цикл автономного агента"""
    log("=" * 50)
    log("🤖 АВТОНОМНЫЙ АГЕНТ запущен")
    log("=" * 50)

    state = load_state()

    # 1. Агент решает что делать
    action, time_type = decide_action(state)
    log(f"Решение: {action} (время: {time_type})")

    # 2. Генерирует контент
    content = generate_content(action, time_type, state)

    if content:
        # 3. Публикует
        if post_to_telegram(content):
            state["total_posts"] = state.get("total_posts", 0) + 1
            state["last_actions"] = state.get("last_actions", []) + [action]
            if len(state["last_actions"]) > 10:
                state["last_actions"] = state["last_actions"][-10:]
        else:
            state["errors"] = state.get("errors", 0) + 1
    else:
        log("Не удалось сгенерировать контент")
        state["errors"] = state.get("errors", 0) + 1

    state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)

    log(f"Итого постов: {state['total_posts']}, ошибок: {state['errors']}")
    return True


if __name__ == "__main__":
    while True:
        try:
            run_autonomous_cycle()
        except Exception as e:
            log(f"Критическая ошибка: {e}")

        # Случайный интервал 30-90 минут для естественности
        interval = random.randint(1800, 5400)
        log(f"Следующий цикл через {interval//60} мин")
        time.sleep(interval)
