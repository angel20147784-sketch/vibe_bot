import aiosqlite
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DB_PATH = "vibe_bot.db"

# Длительность тарифов в днях
PLAN_DAYS = {
    "week": 7,
    "month": 30,
    "year": 365,
}


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
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                plan TEXT,
                expires_at TIMESTAMP,
                reminder_sent INTEGER DEFAULT 0
            )
        """)
        await db.commit()

        # Миграция: добавляем колонки, если БД создана раньше этого обновления
        cursor = await db.execute("PRAGMA table_info(premium_users)")
        existing_cols = {row[1] for row in await cursor.fetchall()}

        if "plan" not in existing_cols:
            await db.execute("ALTER TABLE premium_users ADD COLUMN plan TEXT")
        if "expires_at" not in existing_cols:
            await db.execute("ALTER TABLE premium_users ADD COLUMN expires_at TIMESTAMP")
        if "reminder_sent" not in existing_cols:
            await db.execute("ALTER TABLE premium_users ADD COLUMN reminder_sent INTEGER DEFAULT 0")
        await db.commit()

        # Для уже существующих премиум-пользователей без plan/expires_at —
        # выдаём годовой доступ (365 дней) от текущего момента, чтобы никто
        # не потерял доступ из-за этого обновления.
        backfill_expires = (datetime.utcnow() + timedelta(days=PLAN_DAYS["year"])).isoformat(sep=" ")
        await db.execute(
            """
            UPDATE premium_users
            SET plan = 'year', expires_at = ?
            WHERE expires_at IS NULL
            """,
            (backfill_expires,)
        )
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
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


async def add_premium_user(user_id: int, plan: str = "year"):
    """
    Выдаёт или продлевает премиум-доступ.
    Если у пользователя уже есть активная подписка — новый срок добавляется
    к оставшемуся (а не просто перезаписывает), чтобы продление "сверху"
    было выгодным, а не обрезало уже оплаченное время.
    """
    days = PLAN_DAYS.get(plan, PLAN_DAYS["month"])
    now = datetime.utcnow()

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT expires_at FROM premium_users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()

        if row and row[0]:
            try:
                current_expiry = datetime.fromisoformat(row[0])
            except ValueError:
                current_expiry = now
            base = current_expiry if current_expiry > now else now
        else:
            base = now

        new_expiry = (base + timedelta(days=days)).isoformat(sep=" ")

        await db.execute(
            """
            INSERT INTO premium_users (user_id, plan, expires_at, reminder_sent)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                plan = excluded.plan,
                expires_at = excluded.expires_at,
                reminder_sent = 0
            """,
            (user_id, plan, new_expiry)
        )
        await db.commit()
        return new_expiry


async def is_premium(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT expires_at FROM premium_users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if not row or not row[0]:
            return False
        try:
            expires_at = datetime.fromisoformat(row[0])
        except ValueError:
            return False
        return expires_at > datetime.utcnow()


async def get_premium_info(user_id: int):
    """Возвращает (plan, expires_at: datetime | None) для пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT plan, expires_at FROM premium_users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if not row or not row[1]:
            return None, None
        try:
            expires_at = datetime.fromisoformat(row[1])
        except ValueError:
            return row[0], None
        return row[0], expires_at


async def get_users_expiring_soon(within_hours: int = 24) -> list:
    """
    Возвращает [(user_id, plan, expires_at), ...] для подписок, которые
    истекают в ближайшие `within_hours` часов и ещё не получили напоминание.
    """
    now = datetime.utcnow()
    deadline = now + timedelta(hours=within_hours)
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT user_id, plan, expires_at FROM premium_users
            WHERE expires_at IS NOT NULL
              AND reminder_sent = 0
              AND expires_at <= ?
              AND expires_at > ?
            """,
            (deadline.isoformat(sep=" "), now.isoformat(sep=" "))
        )
        rows = await cursor.fetchall()
        result = []
        for user_id, plan, expires_at in rows:
            try:
                result.append((user_id, plan, datetime.fromisoformat(expires_at)))
            except ValueError:
                continue
        return result


async def mark_reminder_sent(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE premium_users SET reminder_sent = 1 WHERE user_id = ?", (user_id,)
        )
        await db.commit()


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


async def add_referral(referrer_id: int, referred_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
            (referrer_id, referred_id)
        )
        await db.commit()


async def get_referral_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0


async def get_total_referrals() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM referrals")
        result = await cursor.fetchone()
        return result[0] if result else 0
