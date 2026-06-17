import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from content_generator import generate_post
from scheduler_config import SCHEDULE
from payments import register_payment_handlers
from db import init_db, add_subscriber, remove_subscriber, get_all_subscribers, is_premium, get_course_day, set_course_day, next_course_day, add_premium_user, add_post, get_all_posts, get_post, update_post, delete_post
from course_data import format_day, COURSE_DAYS
from ai_agent import scheduled_autonomous_job
from ai_tutor import ask_tutor, get_onboarding_text
from subscriber_agent import analyze_audience, find_similar_channels, create_promo_texts, growth_strategy
from active_agent import daily_growth_task, generate_promo_post, find合作_opportunities, comment_on_posts, post_to_channel
from agency_agents import run_growth_hacker, run_outbound_strategist, run_content_creator, run_sales_coach
from self_evolving_agent import run_evolution, EVOLVING_PROMPTS
from onec_agent import ask_1c, get_skills_list, get_skill_info, SKILLS_INFO
import os

ADMIN_IDS = [6928796982, 8639540904]
PREMIUM_IDS = [8639540904]

# Максимальная длина сообщения Telegram
MAX_MESSAGE_LENGTH = 4000


def truncate_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> str:
    """Обрезает сообщение если оно слишком длинное"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "\n\n... (сообщение обрезано)"


def is_private_chat(update: Update) -> bool:
    return update.effective_chat.type == "private"


def is_admin(update: Update) -> bool:
    return update.effective_user.id in ADMIN_IDS


def get_day_keyboard(day_num):
    keyboard = []
    if day_num > 1:
        keyboard.append([InlineKeyboardButton("⬅️ Предыдущий день", callback_data=f"day_{day_num - 1}")])
    if day_num < 30:
        keyboard.append([InlineKeyboardButton("➡️ Следующий день", callback_data=f"day_{day_num + 1}")])
    keyboard.append([InlineKeyboardButton("🏠 Меню", callback_data="menu")])
    return InlineKeyboardMarkup(keyboard)

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
    
    keyboard = [
        [InlineKeyboardButton("📚 Текущий урок", callback_data="day")],
        [InlineKeyboardButton("➡️ Следующий день", callback_data="next")],
        [InlineKeyboardButton("📊 Мой прогресс", callback_data="progress")],
        [InlineKeyboardButton("📝 Пост от ИИ", callback_data="post")],
        [InlineKeyboardButton("🎓 Купить курс", callback_data="buy")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")],
    ]
    
    welcome_text = (
        "🎓 ВАЙБКОДИНГ ЗА 30 ДНЕЙ\n\n"
        "Научись создавать приложения с помощью ИИ:\n\n"
        "📝 Промпт-инжиниринг\n"
        "🛠 Cursor, Claude, v0.dev\n"
        "📦 Реальные проекты\n"
        "🚀 Деплой в интернет\n"
        "💰 Монетизация\n\n"
        f"Твой статус: {status}\n\n"
        "Выбери действие:"
    )
    
    img_path = os.path.join("images", "welcome.png")
    if os.path.exists(img_path):
        with open(img_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo, 
                caption=welcome_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        await update.message.reply_text(
            welcome_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await remove_subscriber(user_id)
    await update.message.reply_text("❌ Ты отписан от рассылки.")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "day":
        day_num = await get_course_day(user_id)
        if day_num > 1 and not await is_premium(user_id):
            await query.message.delete()
            await context.bot.send_message(
                chat_id=user_id,
                text="🔒 Доступ к курсу ограничен\n\n"
                     "День 1 — бесплатный. Чтобы открыть остальные 29 дней, купи подписку:\n\n"
                     "⭐ 30-дневный курс — 200 Stars"
            )
            return
        img_path = os.path.join("images", f"day_{day_num}.png")
        text = format_day(day_num)
        await query.message.delete()
        if os.path.exists(img_path):
            with open(img_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text,
                    reply_markup=get_day_keyboard(day_num)
                )
        else:
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=get_day_keyboard(day_num))
    
    elif data.startswith("day_"):
        try:
            day_num = int(data.split("_")[1])
        except ValueError:
            return
        if day_num < 1 or day_num > 30:
            return
        if day_num > 1 and not await is_premium(user_id):
            await query.message.delete()
            await context.bot.send_message(
                chat_id=user_id,
                text="🔒 Доступ к курсу ограничен\n\n"
                     "День 1 — бесплатный. Чтобы открыть остальные 29 дней, купи подписку:\n\n"
                     "⭐ 30-дневный курс — 200 Stars"
            )
            return
        await set_course_day(user_id, day_num)
        img_path = os.path.join("images", f"day_{day_num}.png")
        text = format_day(day_num)
        await query.message.delete()
        if os.path.exists(img_path):
            with open(img_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text,
                    reply_markup=get_day_keyboard(day_num)
                )
        else:
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=get_day_keyboard(day_num))
    
    elif data == "next":
        current = await get_course_day(user_id)
        if current >= 30:
            await query.message.delete()
            keyboard = [
                [InlineKeyboardButton("🔄 Начать заново", callback_data="day_1")],
                [InlineKeyboardButton("🎓 Купить курс", callback_data="buy")],
                [InlineKeyboardButton("🏠 Меню", callback_data="menu")],
            ]
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 Ты прошёл все 30 дней курса!\n\n"
                     "Теперь ты знаешь:\n"
                     "📝 Промпт-инжиниринг\n"
                     "🛠 Cursor, Claude, v0.dev\n"
                     "📦 Реальные проекты\n"
                     "🚀 Деплой и монетизация\n\n"
                     "Начни зарабатывать на своих навыках!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        if current >= 1 and not await is_premium(user_id):
            await query.message.delete()
            keyboard = [
                [InlineKeyboardButton("🎓 Купить курс — 200 ⭐", callback_data="buy")],
                [InlineKeyboardButton("🏠 Меню", callback_data="menu")],
            ]
            await context.bot.send_message(
                chat_id=user_id,
                text="🔒 Следующий день доступен по подписке\n\n"
                     "Текущий день: бесплатный пробный\n"
                     "Купить полный доступ — 200 ⭐",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        new_day = await next_course_day(user_id)
        img_path = os.path.join("images", f"day_{new_day}.png")
        text = format_day(new_day)
        await query.message.delete()
        if os.path.exists(img_path):
            with open(img_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text,
                    reply_markup=get_day_keyboard(new_day)
                )
        else:
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=get_day_keyboard(new_day))
    
    elif data == "progress":
        day = await get_course_day(user_id)
        premium = await is_premium(user_id)
        pct = int(day / 30 * 100)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        status = "⭐ Подписка активна" if premium else "🔓 Бесплатный доступ"
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📊 Твой прогресс\n\n"
                 f"Статус: {status}\n"
                 f"День {day}/30\n"
                 f"{bar} {pct}%\n\n"
                 f"Тема: {COURSE_DAYS[day]['title']}"
        )
    
    elif data == "post":
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text="⏳ Генерирую пост...")
        post = await generate_post()
        await context.bot.send_message(chat_id=user_id, text=truncate_message(post))
    
    elif data == "buy":
        await query.message.delete()
        from payments import buy
        await buy(update, context)
    
    elif data == "help":
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="❓ ПОМОЩЬ\n\n"
                 "Команды:\n"
                 "/start — главное меню\n"
                 "/day — текущий урок\n"
                 "/day 5 — перейти к дню 5\n"
                 "/next — следующий день\n"
                 "/progress — прогресс\n"
                 "/tutor — ИИ-наставник\n"
                 "/buy — купить подписку\n\n"
                 "Или просто напиши вопрос — отвечу!"
        )
    
    elif data == "menu":
        keyboard = [
            [InlineKeyboardButton("📚 Текущий урок", callback_data="day")],
            [InlineKeyboardButton("➡️ Следующий день", callback_data="next")],
            [InlineKeyboardButton("📊 Мой прогресс", callback_data="progress")],
            [InlineKeyboardButton("📝 Пост от ИИ", callback_data="post")],
            [InlineKeyboardButton("🎓 Купить курс", callback_data="buy")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")],
        ]
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="Выбери действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Админ-кнопки
    elif data == "admin_stats":
        if user_id not in ADMIN_IDS:
            return
        import sqlite3
        db = sqlite3.connect("vibe_bot.db")
        subs = db.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
        premium = db.execute("SELECT COUNT(*) FROM premium_users").fetchone()[0]
        db.close()
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📊 СТАТИСТИКА\n\n"
                 f"👥 Подписчики: {subs}\n"
                 f"⭐ Премиум: {premium}\n"
                 f"📈 Конверсия: {premium/subs*100 if subs else 0:.1f}%"
        )
    
    elif data == "admin_users":
        if user_id not in ADMIN_IDS:
            return
        import sqlite3
        db = sqlite3.connect("vibe_bot.db")
        cursor = db.execute("SELECT user_id FROM subscribers")
        users = [row[0] for row in cursor.fetchall()]
        db.close()
        text = f"📋 База ({len(users)}):\n" + "\n".join([f"• {u}" for u in users[:20]])
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text=text)
    
    elif data == "admin_post":
        if user_id not in ADMIN_IDS:
            return
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text="📝 Генерирую пост...")
        post = await generate_promo_post()
        if post:
            success = await post_to_channel(post)
            if success:
                await add_post(post)
                await context.bot.send_message(chat_id=user_id, text=f"✅ Опубликовано!\n\n{post}")
            else:
                await context.bot.send_message(chat_id=user_id, text="❌ Ошибка публикации")
    
    elif data == "admin_all_posts":
        if user_id not in ADMIN_IDS:
            return
        posts = await get_all_posts(10)
        if not posts:
            await query.message.delete()
            await context.bot.send_message(chat_id=user_id, text="📭 Постов пока нет")
            return
        
        keyboard = []
        for post_id, text, created_at, status in posts:
            short_text = text[:30] + "..." if len(text) > 30 else text
            keyboard.append([InlineKeyboardButton(f"📝 {short_text}", callback_data=f"post_view_{post_id}")])
        keyboard.append([InlineKeyboardButton("➕ Новый пост", callback_data="admin_post")])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="admin_back")])
        
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📋 ВСЕ ПОСТЫ ({len(posts)}):\n\nНажми на пост для просмотра:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("post_view_"):
        if user_id not in ADMIN_IDS:
            return
        post_id = int(data.split("_")[2])
        post = await get_post(post_id)
        if not post:
            await context.bot.send_message(chat_id=user_id, text="❌ Пост не найден")
            return
        
        _, text, created_at, status = post
        
        keyboard = [
            [InlineKeyboardButton("✏️ Редактировать", callback_data=f"post_edit_{post_id}")],
            [InlineKeyboardButton("🗑 Удалить", callback_data=f"post_delete_{post_id}")],
            [InlineKeyboardButton("◀️ Назад", callback_data="admin_all_posts")],
        ]
        
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📝 ПОСТ #{post_id}\n\n"
                 f"Дата: {created_at}\n"
                 f"Статус: {status}\n\n"
                 f"{text}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("post_edit_"):
        if user_id not in ADMIN_IDS:
            return
        post_id = int(data.split("_")[2])
        context.user_data["editing_post_id"] = post_id
        context.user_data["waiting_for_post_edit"] = True
        
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✏️ Отправь новый текст для поста #{post_id}:"
        )
    
    elif data.startswith("post_delete_"):
        if user_id not in ADMIN_IDS:
            return
        post_id = int(data.split("_")[2])
        await delete_post(post_id)
        
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text=f"🗑 Пост #{post_id} удалён!")
    
    elif data.startswith("onec_"):
        skill_key = data.replace("onec_", "")
        if skill_key == "ask":
            context.user_data["waiting_for_1c_question"] = True
            await query.message.delete()
            await context.bot.send_message(
                chat_id=user_id,
                text="❓ Задай вопрос по 1С:Предприятие:"
            )
        else:
            info = get_skill_info(skill_key)
            await query.message.delete()
            await context.bot.send_message(chat_id=user_id, text=info)
    
    elif data == "admin_back":
        if user_id not in ADMIN_IDS:
            return
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 База пользователей", callback_data="admin_users")],
            [InlineKeyboardButton("📝 Опубликовать пост", callback_data="admin_post")],
            [InlineKeyboardButton("📋 Все посты", callback_data="admin_all_posts")],
            [InlineKeyboardButton("🚀 Growth Hacker", callback_data="admin_growth")],
            [InlineKeyboardButton("🎯 Outbound", callback_data="admin_outbound")],
            [InlineKeyboardButton("📝 Контент", callback_data="admin_content")],
            [InlineKeyboardButton("💼 Продажи", callback_data="admin_sales")],
            [InlineKeyboardButton("➕ Добавить пользователей", callback_data="admin_add")],
        ]
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="🔧 АДМИН-ПАНЕЛЬ\n\nВыбери действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "admin_growth":
        if user_id not in ADMIN_IDS:
            return
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text="🚀 Growth Hacker...")
        result = await run_growth_hacker()
        await context.bot.send_message(chat_id=user_id, text=truncate_message(result or "Ошибка"))
    
    elif data == "admin_outbound":
        if user_id not in ADMIN_IDS:
            return
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text="🎯 Outbound...")
        result = await run_outbound_strategist()
        await context.bot.send_message(chat_id=user_id, text=truncate_message(result or "Ошибка"))
    
    elif data == "admin_content":
        if user_id not in ADMIN_IDS:
            return
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text="📝 Контент...")
        result = await run_content_creator()
        await context.bot.send_message(chat_id=user_id, text=truncate_message(result or "Ошибка"))
    
    elif data == "admin_sales":
        if user_id not in ADMIN_IDS:
            return
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text="💼 Продажи...")
        result = await run_sales_coach()
        await context.bot.send_message(chat_id=user_id, text=truncate_message(result or "Ошибка"))
    
    elif data == "admin_add":
        if user_id not in ADMIN_IDS:
            return
        context.user_data["waiting_for_user_ids"] = True
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text="📝 Отправь ID или @username пользователей:"
        )
    
    elif data == "admin_evolve":
        if user_id not in ADMIN_IDS:
            return
        await query.message.delete()
        await context.bot.send_message(chat_id=user_id, text="🧬 Запускаю эволюцию...\n\n1-2 минуты...")
        results = await run_evolution(iterations=3)
        text = "🧬 ЭВОЛЮЦИЯ ЗАВЕРШЕНА!\n\n"
        for content_type, result in results.items():
            text += f"📝 {content_type}: {result['best_score']:.2f}\n"
        await context.bot.send_message(chat_id=user_id, text=text)


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
            await update.message.reply_photo(photo=photo, caption=text, reply_markup=get_day_keyboard(day_num))
    else:
        await update.message.reply_text(text, reply_markup=get_day_keyboard(day_num))


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
            await update.message.reply_photo(photo=photo, caption=text, reply_markup=get_day_keyboard(new_day))
    else:
        await update.message.reply_text(text, reply_markup=get_day_keyboard(new_day))


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
    if not is_private_chat(update):
        return
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
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    username = update.effective_user.username or "нет"
    await update.message.reply_text(f"Твой ID: {user_id}\nUsername: @{username}")


async def run_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🤖 Запускаю ИИ-агента...")
    await scheduled_autonomous_job(context.bot)
    await update.message.reply_text("✅ Агент выполнил публикацию!")


async def analyze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🔍 Анализирую аудиторию...")
    result = await analyze_audience()
    await update.message.reply_text(truncate_message(result or "Ошибка при анализе"))


async def channels_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🔍 Ищу похожие каналы...")
    result = await find_similar_channels()
    await update.message.reply_text(truncate_message(result or "Ошибка при поиске"))


async def promo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("📝 Генерирую тексты...")
    result = await create_promo_texts()
    await update.message.reply_text(truncate_message(result or "Ошибка при генерации"))


async def growth_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("📊 Составляю стратегию роста...")
    result = await growth_strategy()
    await update.message.reply_text(truncate_message(result or "Ошибка при составлении стратегии"))


async def grow_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🚀 Запускаю рост...")
    result = await daily_growth_task()

    text = "✅ Задача роста выполнена!\n\n"

    if result.get("post"):
        text += f"📝 Опубликовано:\n{result['post'][:200]}...\n\n"

    if result.get("opportunities"):
        text += f"🤝 Сотрудничество:\n{result['opportunities'][:200]}...\n\n"

    if result.get("comments"):
        text += f"💬 Комментарии:\n{result['comments'][:200]}..."

    await update.message.reply_text(text)


async def auto_post_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("📝 Генерирую пост...")
    post = await generate_promo_post()
    if post:
        success = await post_to_channel(post)
        if success:
            await update.message.reply_text(f"✅ Пост опубликован!\n\n{post}")
        else:
            await update.message.reply_text("❌ Ошибка публикации")
    else:
        await update.message.reply_text("❌ Ошибка генерации")


async def growth_hacker_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🚀 Growth Hacker анализирует...")
    result = await run_growth_hacker()
    await update.message.reply_text(truncate_message(result or "Ошибка"))


async def outbound_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🎯 Outbound Strategist работает...")
    result = await run_outbound_strategist()
    await update.message.reply_text(truncate_message(result or "Ошибка"))


async def content_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("📝 Content Creator создаёт...")
    result = await run_content_creator()
    await update.message.reply_text(truncate_message(result or "Ошибка"))


async def sales_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("💼 Sales Coach готовит...")
    result = await run_sales_coach()
    await update.message.reply_text(truncate_message(result or "Ошибка"))


async def add_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text(
            "Используй: /addusers 123456 789012 345678\n\n"
            "Или отправь список ID через запятую:\n"
            "/addusers 123456, 789012, 345678"
        )
        return

    added = 0
    for arg in context.args:
        for uid_str in arg.split(","):
            uid_str = uid_str.strip()
            if uid_str.isdigit():
                uid = int(uid_str)
                await add_subscriber(uid)
                added += 1

    await update.message.reply_text(f"✅ Добавлено {added} пользователей в базу!")


async def add_users_text_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    context.user_data["waiting_for_user_ids"] = True
    await update.message.reply_text(
        "📝 Отправь список ID или @никнеймов пользователей\n"
        "(через запятую, пробел или с новой строки):\n\n"
        "Пример:\n"
        "@username1\n"
        "@username2\n"
        "123456789"
    )


async def find_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text("Используй: /finduser @username")
        return

    username = context.args[0].replace("@", "")
    
    await update.message.reply_text(
        f"🔍 Ищу пользователя @{username}...\n\n"
        "Telegram API не позволяет искать по username напрямую.\n\n"
        "Попроси пользователя написать /start боту — его ID автоматически добавится в базу."
    )


async def list_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    import sqlite3
    db = sqlite3.connect("vibe_bot.db")
    cursor = db.execute("SELECT user_id FROM subscribers")
    users = [row[0] for row in cursor.fetchall()]
    db.close()

    if not users:
        await update.message.reply_text("📭 База пуста")
        return

    text = f"📋 База подписчиков ({len(users)}):\n\n"
    for uid in users[:50]:
        text += f"• {uid}\n"
    
    if len(users) > 50:
        text += f"\n... и ещё {len(users) - 50}"

    await update.message.reply_text(text)


async def evolve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🧬 Запускаю эволюцию промптов...\n\nЭто займёт 1-2 минуты...")
    
    results = await run_evolution(iterations=3)
    
    text = "🧬 ЭВОЛЮЦИЯ ЗАВЕРШЕНА!\n\n"
    for content_type, result in results.items():
        text += f"📝 {content_type}:\n"
        text += f"   Лучший счёт: {result['best_score']:.2f}\n"
        text += f"   История: {result['scores']}\n\n"
    
    text += "Промпты автоматически улучшены!"
    
    await update.message.reply_text(text)


async def prompts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    text = "🧬 ТЕКУЩИЕ ПРОМПТЫ:\n\n"
    for content_type, config in EVOLVING_PROMPTS.items():
        text += f"📝 {content_type}:\n"
        text += f"   Текущий счёт: {config['scores'][-1] if config['scores'] else 0:.2f}\n"
        text += f"   Промпт: {config['current'][:100]}...\n\n"
    
    await update.message.reply_text(text)


async def providers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    from api_rotator import get_provider_status
    status = get_provider_status()
    
    text = "🔌 СТАТУС API ПРОВАЙДЕРОВ:\n\n"
    for p in status:
        emoji = "✅" if p["available"] else "❌"
        cooldown = f" (кулдаун {p['cooldown_left']}с)" if p["in_cooldown"] else ""
        text += f"{emoji} {p['name']}{cooldown}\n"
        text += f"   Ошибок: {p['errors']}\n\n"
    
    await update.message.reply_text(text)


async def onec_skills_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    keyboard = []
    for key, skill in SKILLS_INFO.items():
        keyboard.append([InlineKeyboardButton(f"📦 {skill['name']}", callback_data=f"onec_{key}")])
    keyboard.append([InlineKeyboardButton("❓ Вопрос по 1С", callback_data="onec_ask")])
    
    await update.message.reply_text(
        "📦 НАВЫКИ 1С ДЛЯ ИИ\n\n"
        "Выбери категорию или задай вопрос:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def onec_ask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data["waiting_for_1c_question"] = True
    
    await update.message.reply_text(
        "❓ Задай вопрос по 1С:Предприятие\n\n"
        "Примеры:\n"
        "- Как создать внешнюю обработку?\n"
        "- Что такое управляемые формы?\n"
        "- Как подключить ИИ к 1С?"
    )


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_private_chat(update):
        return
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 База пользователей", callback_data="admin_users")],
        [InlineKeyboardButton("📝 Опубликовать пост", callback_data="admin_post")],
        [InlineKeyboardButton("📋 Все посты", callback_data="admin_all_posts")],
        [InlineKeyboardButton("🧬 Эволюция промптов", callback_data="admin_evolve")],
        [InlineKeyboardButton("🚀 Growth Hacker", callback_data="admin_growth")],
        [InlineKeyboardButton("🎯 Outbound", callback_data="admin_outbound")],
        [InlineKeyboardButton("📝 Контент", callback_data="admin_content")],
        [InlineKeyboardButton("💼 Продажи", callback_data="admin_sales")],
        [InlineKeyboardButton("➕ Добавить пользователей", callback_data="admin_add")],
    ]

    await update.message.reply_text(
        "🔧 АДМИН-ПАНЕЛЬ\n\n"
        "Выбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def auto_post_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("📝 Генерирую пост...")
    post = await generate_promo_post()
    if post:
        success = await post_to_channel(post)
        if success:
            await update.message.reply_text(f"✅ Пост опубликован!\n\n{post}")
        else:
            await update.message.reply_text("❌ Ошибка публикации")
    else:
        await update.message.reply_text("❌ Ошибка генерации")


async def growth_hacker_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🚀 Growth Hacker анализирует...")
    result = await run_growth_hacker()
    await update.message.reply_text(truncate_message(result or "Ошибка"))


async def outbound_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("🎯 Outbound Strategist работает...")
    result = await run_outbound_strategist()
    await update.message.reply_text(truncate_message(result or "Ошибка"))


async def content_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("📝 Content Creator создаёт...")
    result = await run_content_creator()
    await update.message.reply_text(truncate_message(result or "Ошибка"))


async def sales_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    await update.message.reply_text("💼 Sales Coach готовит...")
    result = await run_sales_coach()
    await update.message.reply_text(truncate_message(result or "Ошибка"))


async def add_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text(
            "Используй: /addusers 123456 789012 345678\n\n"
            "Или отправь список ID через запятую:\n"
            "/addusers 123456, 789012, 345678"
        )
        return

    added = 0
    for arg in context.args:
        for uid_str in arg.split(","):
            uid_str = uid_str.strip()
            if uid_str.isdigit():
                uid = int(uid_str)
                await add_subscriber(uid)
                added += 1

    await update.message.reply_text(f"✅ Добавлено {added} пользователей в базу!")


async def add_users_text_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    context.user_data["waiting_for_user_ids"] = True
    await update.message.reply_text(
        "📝 Отправь список ID или @никнеймов пользователей\n"
        "(через запятую, пробел или с новой строки):\n\n"
        "Пример:\n"
        "@username1\n"
        "@username2\n"
        "123456789"
    )


async def find_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    if not context.args:
        await update.message.reply_text("Используй: /finduser @username")
        return

    username = context.args[0].replace("@", "")
    
    import requests
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    # Ищем пользователя через chat member API
    # К сожалению, Telegram API не позволяет искать по username напрямую
    # Но мы можем попробовать через chat
    await update.message.reply_text(
        f"🔍 Ищу пользователя @{username}...\n\n"
        "Telegram API не позволяет искать по username напрямую.\n\n"
        "Попроси пользователя написать /start боту — его ID автоматически добавится в базу."
    )


async def list_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Нет доступа.")
        return

    import sqlite3
    db = sqlite3.connect("vibe_bot.db")
    cursor = db.execute("SELECT user_id FROM subscribers")
    users = [row[0] for row in cursor.fetchall()]
    db.close()

    if not users:
        await update.message.reply_text("📭 База пуста")
        return

    text = f"📋 База подписчиков ({len(users)}):\n\n"
    for uid in users[:50]:  # Показываем первые 50
        text += f"• {uid}\n"
    
    if len(users) > 50:
        text += f"\n... и ещё {len(users) - 50}"

    await update.message.reply_text(text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Проверяем, не список ли это ID/никнеймов (админ добавляет пользователей)
    if user_id in ADMIN_IDS and context.user_data.get("waiting_for_user_ids"):
        context.user_data["waiting_for_user_ids"] = False
        added = 0
        not_found = []
        
        for line in text.split("\n"):
            for item in line.replace(",", " ").replace(";", " ").split():
                item = item.strip()
                if not item:
                    continue
                
                if item.startswith("@"):
                    username = item.replace("@", "")
                    not_found.append(item)
                
                elif item.isdigit() and len(item) > 5:
                    uid = int(item)
                    await add_subscriber(uid)
                    added += 1
        
        response = f"✅ Добавлено {added} пользователей в базу!"
        if not_found:
            response += f"\n\n⚠️ Не удалось найти ID для: {', '.join(not_found)}"
            response += "\nПопроси их написать /start боту — ID добавится автоматически."
        
        await update.message.reply_text(response)
        return

    # Проверяем, не редактируется ли пост
    if user_id in ADMIN_IDS and context.user_data.get("waiting_for_post_edit"):
        context.user_data["waiting_for_post_edit"] = False
        post_id = context.user_data.get("editing_post_id")
        if post_id:
            await update_post(post_id, text)
            await update.message.reply_text(f"✅ Пост #{post_id} обновлён!")
            
            post = await get_post(post_id)
            if post:
                keyboard = [
                    [InlineKeyboardButton("✏️ Редактировать", callback_data=f"post_edit_{post_id}")],
                    [InlineKeyboardButton("🗑 Удалить", callback_data=f"post_delete_{post_id}")],
                    [InlineKeyboardButton("◀️ Назад", callback_data="admin_all_posts")],
                ]
                await update.message.reply_text(
                    f"📝 ПОСТ #{post_id}\n\n{post[1]}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            return

    # Проверяем, не вопрос ли по 1С
    if context.user_data.get("waiting_for_1c_question"):
        context.user_data["waiting_for_1c_question"] = False
        await update.message.reply_text("🤔 Думаю над ответом по 1С...")
        answer = await ask_1c(text)
        await update.message.reply_text(truncate_message(answer))
        return

    if not await is_premium(user_id):
        return

    day = await get_course_day(user_id)
    await update.message.reply_text("🤔 Думаю над ответом...")

    answer = await ask_tutor(text, current_day=day)
    await update.message.reply_text(truncate_message(answer))


async def tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_premium(user_id):
        await update.message.reply_text(
            "🔒 ИИ-наставник доступен только по подписке\n\n"
            "/buy — купить доступ"
        )
        return

    day = await get_course_day(user_id)
    onboarding = get_onboarding_text(day)
    await update.message.reply_text(onboarding)


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


async def growth_job(bot: Bot):
    logger.info("🚀 Запускаю задачу роста...")
    await daily_growth_task()


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
    app.add_handler(CommandHandler("tutor", tutor))
    app.add_handler(CommandHandler("analyze", analyze_cmd))
    app.add_handler(CommandHandler("channels", channels_cmd))
    app.add_handler(CommandHandler("promo", promo_cmd))
    app.add_handler(CommandHandler("growth", growth_cmd))
    app.add_handler(CommandHandler("grow", grow_cmd))
    app.add_handler(CommandHandler("autopost", auto_post_cmd))
    app.add_handler(CommandHandler("growthhacker", growth_hacker_cmd))
    app.add_handler(CommandHandler("outbound", outbound_cmd))
    app.add_handler(CommandHandler("content", content_cmd))
    app.add_handler(CommandHandler("sales", sales_cmd))
    app.add_handler(CommandHandler("addusers", add_users_cmd))
    app.add_handler(CommandHandler("adduserslist", add_users_text_cmd))
    app.add_handler(CommandHandler("finduser", find_user_cmd))
    app.add_handler(CommandHandler("listusers", list_users_cmd))
    app.add_handler(CommandHandler("admin", admin_menu))
    app.add_handler(CommandHandler("evolve", evolve_cmd))
    app.add_handler(CommandHandler("prompts", prompts_cmd))
    app.add_handler(CommandHandler("providers", providers_cmd))
    app.add_handler(CommandHandler("1c", onec_skills_cmd))
    app.add_handler(CommandHandler("1cask", onec_ask_cmd))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    register_payment_handlers(app)

    # Обработчики ошибок
    async def error_handler(update, context):
        logger.error(f"Exception while handling an update: {context.error}")
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Произошла ошибка. Попробуй ещё раз."
                )
            except:
                pass

    app.add_error_handler(error_handler)

    logger.info("🤖 Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
