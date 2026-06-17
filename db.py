import aiosqlite
import logging

logger = logging.getLogger(__name__)

DB_PATH = "vibe_bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS premium_users (
                user_id INTEGER PRIMARY KEY,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS course_progress (
                user_id INTEGER PRIMARY KEY,
                current_day INTEGER DEFAULT 1,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                channel_msg_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'published'
            )
        """)
        await db.commit()
    logger.info("✅ База данных инициализирована")


async def add_subscriber(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)", (user_id,)
        )
        await db.commit()


async def remove_subscriber(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM subscribers WHERE user_id = ?", (user_id,))
        await db.commit()


async def get_all_subscribers() -> set[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM subscribers")
        rows = await cursor.fetchall()
        return {row[0] for row in rows}


async def add_premium_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO premium_users (user_id) VALUES (?)", (user_id,)
        )
        await db.commit()


async def is_premium(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM premium_users WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone() is not None


async def get_course_day(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT current_day FROM course_progress WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]
        await db.execute(
            "INSERT INTO course_progress (user_id, current_day) VALUES (?, 1)", (user_id,)
        )
        await db.commit()
        return 1


async def set_course_day(user_id: int, day: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO course_progress (user_id, current_day) VALUES (?, ?)",
            (user_id, day)
        )
        await db.commit()


async def next_course_day(user_id: int) -> int:
    current = await get_course_day(user_id)
    if current < 30:
        await set_course_day(user_id, current + 1)
        return current + 1
    return current


async def add_post(text: str, channel_msg_id: int = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO posts (text, channel_msg_id) VALUES (?, ?)",
            (text, channel_msg_id)
        )
        await db.commit()
        return cursor.lastrowid


async def get_all_posts(limit: int = 20) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, text, created_at, status FROM posts ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return await cursor.fetchall()


async def get_post(post_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, text, created_at, status FROM posts WHERE id = ?",
            (post_id,)
        )
        return await cursor.fetchone()


async def update_post(post_id: int, text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE posts SET text = ? WHERE id = ?",
            (text, post_id)
        )
        await db.commit()


async def delete_post(post_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        await db.commit()
