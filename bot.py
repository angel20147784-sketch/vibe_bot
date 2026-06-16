import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from content_generator import generate_post
from scheduler_config import SCHEDULE
from payments import register_payment_handlers
from db import init_db, add_subscriber, remove_subscriber, get_all_subscribers, is_premium, get_course_day, set_course_day, next_course_day, add_premium_user
from course_data import format_day, COURSE_DAYS
from ai_agent import scheduled_autonomous_job
import os

ADMIN_IDS = [6928796982]
PREMIUM_IDS = [8639540904]

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await add_subscriber(user_id)
    
    premium = await is_premium(user_id)
    status = "⭐ Полный доступ" if premium else "🔓 Бесплатный пробный"
    
    await update.message.reply_text(
        "🎓 ВАЙБКОДИНГ ЗА 30 ДНЕЙ\n\n"
        "Научись создавать приложения с помощью ИИ:\n\n"
        "📝 Промпт-инжиниринг\n"
        "🛠 Cursor, Claude, v0.dev\n"
        "📦 Реальные проекты\n"
        "🚀 Деплой в интернет\n"
        "💰 Монетизация\n\n"
        f"Твой статус: {status}\n\n"
        "Команды:\n"
        "/day — урок курса\n"
        "/day 1 — День 1 (бесплатно)\n"
        "/next — следующий день\n"
        "/progress — прогресс\n"
        "/post — пост от ИИ\n"
        "/buy — купить подписку ⭐\n"
        "/stop — отписаться"
    )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await remove_subscriber(user_id)
    await update.message.reply_text("❌ Ты отписан от рассылки.")


async def manual_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Генерирую пост...")
    post = await generate_post()
    await update.message.reply_text(post)


async def start_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    day = await get_course_day(user_id)
    premium = await is_premium(user_id)
    
    status = "⭐ Полный доступ" if premium else "🔓 Бесплатный пробный (День 1)"
    
    await update.message.reply_text(
        "🎓 30-ДНЕВНЫЙ КУРС ПО ВАЙБКОДИНГУ\n\n"
        "Чему научишься:\n"
        "📝 Промпт-инжиниринг\n"
        "🛠 Инструменты: Cursor, Claude, v0.dev\n"
        "📦 Реальные проекты\n"
        "🚀 Деплой и монетизация\n\n"
        f"Статус: {status}\n"
        f"Текущий день: {day}/30\n\n"
        "Команды:\n"
        "/day — текущий день\n"
        "/day 5 — перейти к дню 5\n"
        "/next — следующий день\n"
        "/progress — прогресс\n\n"
        + ("" if premium else "⭐ /buy — купить доступ (200 Stars)")
    )


async def get_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    if args:
        try:
            day_num = int(args[0])
            if day_num < 1 or day_num > 30:
                await update.message.reply_text("❌ Введи номер от 1 до 30.")
                return
            await set_course_day(user_id, day_num)
        except ValueError:
            await update.message.reply_text("❌ Введи число: /day 5")
            return
    else:
        day_num = await get_course_day(user_id)
    
    if day_num > 1 and not await is_premium(user_id):
        await update.message.reply_text(
            "🔒 Доступ к курсу ограничен\n\n"
            "День 1 — бесплатный. Чтобы открыть остальные 29 дней, купи подписку:\n\n"
            "/buy — выбрать подписку\n\n"
            "⭐ 30-дневный курс — 200 Stars"
        )
        return
    
    img_path = os.path.join("images", f"day_{day_num}.png")
    text = format_day(day_num)
    
    if os.path.exists(img_path):
        with open(img_path, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=text)
    else:
        await update.message.reply_text(text)


async def next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current = await get_course_day(user_id)
    
    if current >= 30:
        await update.message.reply_text("🎉 Ты уже прошёл весь курс! Повтори уроки или начни создавать проекты.")
        return
    
    if current >= 1 and not await is_premium(user_id):
        await update.message.reply_text(
            "🔒 Следующий день доступен только по подписке\n\n"
            "/buy — купить доступ к курсу\n\n"
            "⭐ 30-дневный курс — 200 Stars"
        )
        return
    
    new_day = await next_course_day(user_id)
    
    img_path = os.path.join("images", f"day_{new_day}.png")
    text = format_day(new_day)
    
    if os.path.exists(img_path):
        with open(img_path, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=text)
    else:
        await update.message.reply_text(text)


async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    day = await get_course_day(user_id)
    premium = await is_premium(user_id)
    pct = int(day / 30 * 100)
    
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    
    status = "⭐ Подписка активна" if premium else "🔓 Бесплатный доступ"
    locked = "" if premium else f"\n\n🔒 Доступны дни 1-1.\nДля полного доступа: /buy"
    
    await update.message.reply_text(
        f"📊 Твой прогресс\n\n"
        f"Статус: {status}\n"
        f"День {day}/30\n"
        f"{bar} {pct}%\n\n"
        f"Текущая тема: {COURSE_DAYS[day]['title']}"
        f"{locked}"
    )


async def course_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎓 МЕНЮ КУРСА\n\n"
        "/start_course — начать курс\n"
        "/day — текущий день\n"
        "/day N — перейти к дню N\n"
        "/next — следующий день\n"
        "/progress — прогресс\n\n"
        "Команды бота:\n"
        "/post — пост от ИИ\n"
        "/buy — премиум доступ\n"
        "/stop — отписаться"
    )


async def grant_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return
    
    if not context.args:
        await update.message.reply_text("Используй: /grant <user_id>")
        return
    
    try:
        target_id = int(context.args[0])
        await add_premium_user(target_id)
        await update.message.reply_text(f"✅ Подписка выдана пользователю {target_id}")
    except ValueError:
        await update.message.reply_text("❌ Неверный ID")


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "нет"
    await update.message.reply_text(f"Твой ID: {user_id}\nUsername: @{username}")


async def run_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🤖 Запускаю ИИ-агента...")
    await scheduled_autonomous_job(context.bot)
    await update.message.reply_text("✅ Агент выполнил публикацию!")


async def publish_to_channel(bot: Bot, post: str):
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=post)
        logger.info("✅ Пост опубликован в канал")
    except Exception as e:
        logger.error(f"❌ Ошибка публикации в канал: {e}")


async def _send_one(bot: Bot, user_id: int, text: str):
    try:
        await bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        logger.warning(f"Не удалось отправить {user_id}: {e}")
        await remove_subscriber(user_id)


async def send_to_subscribers(bot: Bot, post: str, premium_post: str):
    subscribers = await get_all_subscribers()
    if not subscribers:
        return

    tasks = []
    for user_id in subscribers:
        if await is_premium(user_id):
            text = f"⭐ Премиум рассылка\n\n{premium_post}"
        else:
            text = post
        tasks.append(_send_one(bot, user_id, text))

    await asyncio.gather(*tasks)


async def scheduled_job(bot: Bot):
    logger.info("🕐 Запускаю плановую публикацию...")

    await scheduled_autonomous_job(bot)

    post = await generate_post()
    premium = await generate_post(topic="Продвинутые техники вайбкодинга: реальные паттерны из практики с примерами промптов")

    await send_to_subscribers(bot, post, premium)


async def post_init(application: Application):
    await init_db()
    for uid in PREMIUM_IDS:
        await add_premium_user(uid)
        logger.info(f"✅ Premium granted to {uid}")

    scheduler = AsyncIOScheduler()
    for job in SCHEDULE:
        scheduler.add_job(
            scheduled_job,
            CronTrigger(hour=job["hour"], minute=job["minute"]),
            kwargs={"bot": application.bot},
            id=job["id"],
        )
        logger.info(f"📅 Задача {job['id']} запланирована на {job['hour']}:{job['minute']:02d}")

    scheduler.start()
    logger.info("✅ Планировщик запущен")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("post", manual_post))
    app.add_handler(CommandHandler("start_course", start_course))
    app.add_handler(CommandHandler("day", get_day))
    app.add_handler(CommandHandler("next", next_day))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("menu", course_menu))
    app.add_handler(CommandHandler("grant", grant_premium))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("agent", run_agent))
    register_payment_handlers(app)

    logger.info("🤖 Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
