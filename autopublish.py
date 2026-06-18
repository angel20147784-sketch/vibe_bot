#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Автопубликация постов из файла"""

import os
import json
import logging
from urllib.request import urlopen, Request
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
STATE_FILE = "autopublish_state.json"


def parse_posts(filename="telegram_posts.md"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    posts = []
    current_post = []

    for line in content.split("\n"):
        stripped = line.strip()
        if stripped == "---":
            if current_post:
                posts.append("\n".join(current_post).strip())
            current_post = []
        elif stripped.startswith("## Пост"):
            if current_post:
                posts.append("\n".join(current_post).strip())
            current_post = []
        elif stripped.startswith("#"):
            if current_post:
                posts.append("\n".join(current_post).strip())
            current_post = []
        elif stripped:
            current_post.append(stripped)

    if current_post:
        posts.append("\n".join(current_post).strip())

    return [p for p in posts if p and len(p) > 20 and not p.startswith("#")]


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"published": []}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def post_to_telegram(text):
    data = json.dumps({
        "chat_id": CHANNEL_ID,
        "text": text,
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
        return result.get("ok", False)
    except Exception as e:
        logger.error(f"Ошибка публикации: {e}")
        return False


async def publish_next_post():
    """Публикует следующий неопубликованный пост"""
    posts = parse_posts()
    if not posts:
        logger.info("Нет постов для публикации")
        return False

    state = load_state()
    published = set(state.get("published", []))
    remaining = [i for i in range(len(posts)) if i not in published]

    if not remaining:
        logger.info("Все посты опубликованы!")
        return False

    idx = remaining[0]
    post = posts[idx]

    logger.info(f"Публикация поста {idx+1}/{len(posts)}...")

    if post_to_telegram(post):
        published.add(idx)
        state["published"] = list(published)
        save_state(state)
        logger.info(f"Пост {idx+1} опубликован!")
        return True
    else:
        logger.error(f"Не удалось опубликовать пост {idx+1}")
        return False


def get_publish_stats():
    """Возвращает статистику публикаций"""
    posts = parse_posts()
    state = load_state()
    published = set(state.get("published", []))
    remaining = [i for i in range(len(posts)) if i not in published]
    return {
        "total": len(posts),
        "published": len(published),
        "remaining": len(remaining)
    }
