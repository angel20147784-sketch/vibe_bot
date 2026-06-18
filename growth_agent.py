#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Growth Agent — этичный рост подписчиков через контент и вовлечение"""

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
STATE_FILE = "growth_agent_state.json"


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    try:
        with open("growth_agent.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def ai_generate(prompt, max_tokens=800):
    """Генерация через AI"""
    if not OPENROUTER_KEY:
        return None
    data = json.dumps({
        "model": "google/gemma-4-31b-it:free",
        "messages": [
            {"role": "system", "content": "Ты — эксперт по Telegram-маркетингу. Пиши на русском. Будь конкретным и полезным."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.8
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


def post_to_telegram(text):
    data = json.dumps({
        "chat_id": CHANNEL_ID,
        "text": text[:4000],
        "reply_markup": {"inline_keyboard": [[{"text": "🚀 Начать", "url": "https://t.me/CODEScodingbot?start=course"}]]}
    }).encode("utf-8")
    try:
        req = Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        resp = urlopen(req, timeout=30)
        return json.loads(resp.read().decode("utf-8")).get("ok", False)
    except Exception as e:
        log(f"Ошибка: {e}")
        return False


# === СТРАТЕГИИ РОСТА ===

TARGET_CHANNELS = [
    "@tproger", "@habr", "@vc", "@python_course",
    "@webdev", "@javascript", "@freelance", "@startup",
    "@it_kursy", "@codesergo", "@ai_hub", "@devops",
    "@gamedev", "@mobiledev", "@datascience"
]


def strategy_crosspost(state):
    """Кросс-постинг: публикует полезный контент в других каналах"""
    log("Стратегия: кросс-постинг")

    prompt = (
        "Напиши полезный пост для Telegram-канала о программировании/ИИ.\n"
        "Тема: вайбкодинг, Cursor, Claude, автоматизация.\n"
        "Формат: 5-8 строк, полезный совет или инструкция.\n"
        "В конце естественно упомяни канал @CODEScoding.\n"
        "Без спама, без навязывания — просто полезный контент."
    )
    content = ai_generate(prompt)
    if content:
        return {"action": "crosspost", "content": content, "channels": random.sample(TARGET_CHANNELS, 3)}
    return None


def strategy_engagement(state):
    """Вовлечение: создаёт посты для вовлечения аудитории"""
    log("Стратегия: вовлечение")

    prompt = (
        "Создай интерактивный пост для Telegram-канала о вайбкодинге.\n"
        "Формат: вопрос + 4 варианта ответа (эmozи + текст)\n"
        "Пример:\n"
        "Какой инструмент ты используешь больше всего?\n"
        "🔥 Cursor\n"
        "🧠 Claude\n"
        "🎨 v0.dev\n"
        "☁️ Vercel\n\n"
        "Напиши свой вариант. Не повторяй пример."
    )
    content = ai_generate(prompt)
    if content:
        return {"action": "engagement", "content": content}
    return None


def strategy_collab(state):
    """Сотрудничество: предложения о коллаборации"""
    log("Стратегия: сотрудничество")

    prompt = (
        "Напиши сообщение-предложение о сотрудничестве для Telegram-канала.\n"
        "Формат: короткое, вежливое, с конкретным предложением.\n"
        "Пример: 'Привет! Видел твой канал про Python. У нас курс по вайбкодингу — maybe обмен постами?'\n"
        "Напиши 3 варианта для разных каналов."
    )
    content = ai_generate(prompt)
    if content:
        return {"action": "collab", "content": content}
    return None


def strategy_seo(state):
    """SEO: посты оптимизированные под поиск"""
    log("Стратегия: SEO")

    prompt = (
        "Напиши SEO-оптимизированный пост для Telegram.\n"
        "Тема: 'Как создать Telegram-бота с помощью ИИ за 30 минут'\n"
        "Формат: заголовок + 5 шагов + результат\n"
        "Ключевые слова: telegram бот, ИИ, курсор, Claude, вайбкодинг"
    )
    content = ai_generate(prompt)
    if content:
        return {"action": "seo", "content": content}
    return None


def strategy_social_proof(state):
    """Социальное доказательство: отзывы и кейсы"""
    log("Стратегия: социальное доказательство")

    prompt = (
        "Напиши пост-кейс для Telegram о успехе ученика.\n"
        "Формат: Имя + Проблема + Решение + Результат (цифры)\n"
        "Пример: 'Мария, 25 лет. Хотела сменить профессию. За месяц изучила Cursor. Сейчас зарабатывает 50К/мес на фрилансе.'\n"
        "Напиши 2 варианта."
    )
    content = ai_generate(prompt)
    if content:
        return {"action": "social_proof", "content": content}
    return None


STRATEGIES = [
    strategy_crosspost,
    strategy_engagement,
    strategy_collab,
    strategy_seo,
    strategy_social_proof,
]


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_actions": 0, "last_actions": [], "last_run": None, "errors": 0, "subscribers_gained": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def run_growth_cycle():
    """Один цикл работы growth-агента"""
    log("=" * 40)
    log("📈 GROWTH AGENT запущен")
    log("=" * 40)

    state = load_state()

    # Выбираем стратегию (без повторов)
    available = [s for s in STRATEGIES if s.__name__ not in state.get("last_actions", [])[-2:]]
    if not available:
        available = STRATEGIES

    strategy = random.choice(available)
    result = strategy(state)

    if result:
        content = result["content"]

        # Добавляем CTA
        cta = random.choice([
            "\n\n📢 Больше такого в @CODEScoding",
            "\n\n🔥 Подписывайся @CODEScoding",
            "\n\n💡 Ещё лайфхаков: @CODEScoding",
            "\n\n🚀 Курс бесплатный: @CODEScoding",
        ])
        full_post = content + cta

        if post_to_telegram(full_post):
            state["total_actions"] = state.get("total_actions", 0) + 1
            state["last_actions"] = state.get("last_actions", []) + [strategy.__name__]
            if len(state["last_actions"]) > 10:
                state["last_actions"] = state["last_actions"][-10:]
            log(f"Опубликовано: {strategy.__name__}")
        else:
            state["errors"] = state.get("errors", 0) + 1
    else:
        log("Не удалось сгенерировать контент")
        state["errors"] = state.get("errors", 0) + 1

    state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)

    log(f"Итого: {state['total_actions']} действий, {state['errors']} ошибок")
    return True


if __name__ == "__main__":
    while True:
        try:
            run_growth_cycle()
        except Exception as e:
            log(f"Ошибка: {e}")

        interval = random.randint(3600, 7200)
        log(f"Следующий цикл через {interval//60} мин")
        time.sleep(interval)
