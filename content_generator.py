import os
import random
import asyncio
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
            default_headers={
                "HTTP-Referer": "https://t.me/codesergo",
                "X-Title": "VibeBot",
            },
        )
    return _client


TOPICS = [
    "День 1-3: Что такое вайбкодинг и почему это меняет правила игры",
    "День 4-7: Выбор инструмента — Cursor vs Windsurf vs Replit",
    "День 8-10: Первый проект с нуля за 1 час",
    "День 11-14: Как правильно писать промпты для кода",
    "День 15-17: Деплой приложения без DevOps-знаний",
    "День 18-21: Работа с базами данных через ИИ",
    "День 22-24: Создание Telegram-бота вайбкодингом",
    "День 25-27: Как монетизировать то, что ты создал",
    "День 28-30: Итоги месяца — что ты умеешь теперь",
    "Лайфхак: как исправлять ошибки, которые ты не понимаешь",
    "Мифы о вайбкодинге — разбираем популярные страхи",
    "Реальные проекты, созданные вайбкодингом за неделю",
    "Стек новичка: 5 инструментов которые нужны с первого дня",
    "Как не застрять: что делать когда ИИ не понимает задачу",
    "Вайбкодинг vs традиционное программирование — честное сравнение",
]


def get_course_topic(day_num: int) -> str:
    from course_data import COURSE_DAYS, WEEK_NAMES
    day = COURSE_DAYS.get(day_num)
    if not day:
        return None
    week = (day_num - 1) // 7 + 1
    return f"День {day_num}: {day['title']} — {day['intro']}"

SYSTEM_PROMPT = """Ты — автор Telegram-канала об обучении вайбкодингу за месяц.
Твоя аудитория — новички, которые хотят научиться создавать приложения с помощью ИИ-инструментов (Cursor, Claude, ChatGPT), не будучи программистами.

ВАЖНО: Пиши ТОЛЬКО на русском языке. Никаких английских слов, кроме названий инструментов.

Стиль написания:
- Живой, честный, мотивирующий
- Без занудства и сложных терминов
- Используй эмодзи активно (минимум 3-5 в каждом посте)
- Структурируй текст абзацами

Формат поста:
- Цепляющий заголовок с эмодзи
- 3-5 коротких абзацев основного текста
- Каждый абзац — 2-3 предложения максимум
- Практический совет или задание в конце
- Длина: 200-350 слов
- Язык: только русский

НЕ используй Markdown-разметку (*, _, [], ()). Пиши обычным текстом с эмодзи.
Никогда не используй символы: * _ [ ] ( ) ~ ` > # + - = | { } . ! для форматирования."""


async def generate_post(topic: str | None = None, retries: int = 3) -> str:
    if topic is None:
        topic = random.choice(TOPICS)

    client = get_client()

    for attempt in range(retries):
        try:
            response = await client.chat.completions.create(
                model="google/gemma-4-31b-it:free",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Напиши пост на тему: {topic}"},
                ],
                max_tokens=1024,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.warning(f"Попытка {attempt + 1}/{retries} не удалась: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)

    return (
        f"📌 {topic}\n\n"
        "Привет! Сегодня не удалось сгенерировать пост — API временно недоступен.\n"
        "Попробуй позже или используй /post чтобы запросить пост вручную."
    )


async def generate_post_on_theme(custom_theme: str) -> str:
    return await generate_post(topic=custom_theme)
