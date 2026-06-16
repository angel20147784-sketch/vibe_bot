import logging
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, PreCheckoutQueryHandler, MessageHandler, CallbackQueryHandler, filters, CommandHandler
from db import add_premium_user, is_premium

logger = logging.getLogger(__name__)

PLANS = {
    "week": {
        "title": "Недельная подписка",
        "price": 100,
        "payload": "subscription_week",
        "description": "Доступ к курсу на 7 дней",
    },
    "month": {
        "title": "30-дневный курс",
        "price": 200,
        "payload": "subscription_month",
        "description": "Полный доступ ко всем 30 дням курса",
    },
    "year": {
        "title": "Годовая подписка",
        "price": 1500,
        "payload": "subscription_year",
        "description": "Курс + все будущие обновления на год",
    },
}


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if await is_premium(user_id):
        await update.message.reply_text(
            "⭐ У тебя уже есть полный доступ к курсу!\n\n"
            "Команды:\n"
            "/day — текущий урок\n"
            "/next — следующий день\n"
            "/progress — прогресс"
        )
        return

    keyboard = [
        [InlineKeyboardButton("📅 Неделя — 100 ⭐", callback_data="buy_week")],
        [InlineKeyboardButton("🎓 30-дневный курс — 200 ⭐", callback_data="buy_month")],
        [InlineKeyboardButton("🗓 Год — 1500 ⭐", callback_data="buy_year")],
    ]

    await update.message.reply_text(
        "🎓 30-ДНЕВНЫЙ КУРС ПО ВАЙБКОДИНГУ\n\n"
        "Что тебя ждёт:\n\n"
        "📝 Промпт-инжиниринг\n"
        "Как писать правильные промпты для ИИ\n\n"
        "🛠 Инструменты\n"
        "Cursor, Claude, v0.dev, Replit, Git\n\n"
        "📦 Реальные проекты\n"
        "Соберём приложения за час\n\n"
        "🚀 Деплой\n"
        "Запустим проект в интернете\n\n"
        "💰 Монетизация\n"
        "Заработок на навыках вайбкодинга\n\n"
        "Бесплатно только День 1.\n\n"
        "Выбери подписку:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_key = query.data.replace("buy_", "")
    plan = PLANS.get(plan_key)
    if not plan:
        return

    await context.bot.send_invoice(
        chat_id=query.message.chat.id,
        title=f"Премиум: {plan['title']}",
        description=plan["description"],
        payload=plan["payload"],
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(plan["title"], plan["price"])],
    )


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    valid_payloads = [plan["payload"] for plan in PLANS.values()]
    if query.invoice_payload in valid_payloads:
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Что-то пошло не так. Попробуй снова.")


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    payment = update.message.successful_payment

    purchased_plan = None
    for plan in PLANS.values():
        if plan["payload"] == payment.invoice_payload:
            purchased_plan = plan
            break

    plan_name = purchased_plan["title"] if purchased_plan else "Премиум"

    await add_premium_user(user_id)
    logger.info(f"💰 Новый премиум-пользователь: {user_id} ({user_name}), {plan_name}, {payment.total_amount} Stars")

    from ai_tutor import get_onboarding_text
    onboarding = get_onboarding_text(1)

    await update.message.reply_text(
        f"🎉 Оплата прошла успешно, {user_name}!\n\n"
        f"📦 Ты купил: {plan_name}\n\n"
        f"{onboarding}\n\n"
        "Доступные команды:\n"
        "/day — текущий урок\n"
        "/next — следующий день\n"
        "/tutor — ИИ-наставник\n"
        "/progress — прогресс"
    )


async def premium_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_premium(user_id):
        await update.message.reply_text(
            "🔒 Это команда только для премиум-участников.\n\n"
            "Используй /buy чтобы получить доступ за ⭐ Stars."
        )
        return

    from content_generator import generate_post
    await update.message.reply_text("⏳ Генерирую эксклюзивный пост...")
    post = await generate_post(topic="Продвинутые техники вайбкодинга: реальные паттерны из практики с примерами промптов")
    await update.message.reply_text(f"⭐ Премиум контент\n\n{post}")


async def resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_premium(user_id):
        await update.message.reply_text(
            "🔒 Только для премиум-участников.\n\n"
            "Используй /buy чтобы получить доступ."
        )
        return

    await update.message.reply_text(
        "📚 Топ ресурсов по вайбкодингу\n\n"
        "🛠 Инструменты:\n"
        "• cursor.com — лучший редактор\n"
        "• replit.com — онлайн среда\n"
        "• lovable.dev — веб-приложения\n"
        "• bolt.new — быстрый старт\n\n"
        "🤖 AI-инструменты:\n"
        "• claude.ai — для сложных задач\n"
        "• v0.dev — UI компоненты\n"
        "• github.com/copilot — в редакторе\n\n"
        "🚀 Деплой:\n"
        "• railway.app — бэкенд\n"
        "• vercel.com — фронтенд\n"
        "• supabase.com — база данных\n\n"
        "📖 Обучение:\n"
        "• youtube.com — ищи 'vibe coding tutorial'\n"
        "• x.com — следи за @levels, @tdinh_me"
    )


def register_payment_handlers(app):
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("premium_post", premium_post))
    app.add_handler(CommandHandler("resources", resources))
    app.add_handler(CallbackQueryHandler(buy_callback, pattern=r"^buy_"))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
