#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Агент поиска и публикации свежей информации"""

import os
import sys
import json
import time
import logging
from urllib.request import urlopen, Request
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
STATE_FILE = "research_agent_state.json"
POSTS_FILE = "telegram_posts.md"


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    try:
        with open("research_agent.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def fetch_url(url, timeout=15):
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urlopen(req, timeout=timeout)
        return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        log(f"Ошибка загрузки {url}: {e}")
        return None


def search_github_trending():
    """Ищет трендовые репозитории на GitHub"""
    html = fetch_url("https://github.com/trending?since=weekly")
    if not html:
        return []

    repos = []
    lines = html.split("\n")
    for i, line in enumerate(lines):
        if 'class="h3 lh-condensed"' in line or "repo-list-name" in line:
            for j in range(max(0, i-2), min(len(lines), i+5)):
                if "href=" in lines[j]:
                    import re
                    match = re.search(r'href="(/[^"]+)"', lines[j])
                    if match:
                        repo = match.group(1).strip("/")
                        if repo.count("/") == 1 and repo not in [r["name"] for r in repos]:
                            repos.append({"name": repo, "url": f"https://github.com/{repo}"})
                            break
    return repos[:10]


def search_mcp_servers():
    """Ищет новые MCP-серверы"""
    html = fetch_url("https://github.com/search?q=mcp+server&type=repositories&s=updated&o=desc")
    if not html:
        return []

    repos = []
    import re
    matches = re.findall(r'href="(/[^/]+/[^/]+)"[^>]*class="[^"]*"', html)
    seen = set()
    for match in matches:
        repo = match.strip("/")
        if repo.count("/") == 1 and repo not in seen and "search" not in repo:
            seen.add(repo)
            repos.append({"name": repo, "url": f"https://github.com/{repo}"})
    return repos[:5]


def generate_research_post(topic, findings):
    """Генерирует пост на основе найденной информации"""
    post = f"🔍 {topic}\n\n"
    for i, item in enumerate(findings[:5], 1):
        post += f"{i}. {item['name']}\n"
        if item.get('description'):
            post += f"   {item['description']}\n"
        post += f"   {item['url']}\n\n"
    post += "#вайбкодинг #ии #github"
    return post


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
        return result.get("ok", False)
    except Exception as e:
        log(f"Ошибка публикации: {e}")
        return False


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_run": None, "published_topics": [], "search_count": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def run_research_cycle():
    """Один цикл поиска и публикации"""
    log("=" * 40)
    log("Запуск цикла поиска")
    log("=" * 40)

    state = load_state()
    state["search_count"] = state.get("search_count", 0) + 1

    # 1. Ищем трендовые репозитории
    log("Поиск трендовых репозиториев...")
    trending = search_github_trending()
    if trending:
        log(f"Найдено трендовых: {len(trending)}")

    # 2. Ищем MCP-серверы
    log("Поиск MCP-серверов...")
    mcp = search_mcp_servers()
    if mcp:
        log(f"Найдено MCP: {len(mcp)}")

    # 3. Генерируем и публикуем пост
    if trending:
        post = generate_research_post("🔥 Тренды на GitHub этой недели", trending)
        if post_to_telegram(post):
            log("Пост с трендами опубликован!")
            state["published_topics"].append("trending_" + time.strftime("%Y%m%d"))
        else:
            log("Ошибка публикации трендов")

    time.sleep(2)

    if mcp:
        post = generate_research_post("🧩 Новые MCP-серверы", mcp)
        if post_to_telegram(post):
            log("Пост с MCP опубликован!")
            state["published_topics"].append("mcp_" + time.strftime("%Y%m%d"))
        else:
            log("Ошибка публикации MCP")

    state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)

    log(f"Цикл завершён. Всего циклов: {state['search_count']}")
    return True


if __name__ == "__main__":
    while True:
        try:
            run_research_cycle()
        except Exception as e:
            log(f"Ошибка: {e}")

        log("Следующий цикл через 6 часов...")
        time.sleep(21600)
