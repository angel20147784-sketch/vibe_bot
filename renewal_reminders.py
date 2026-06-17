import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application

from db import get_users_expiring_soon, mark_reminder_sent

logger = logging.getLogger(__name__)

PLAN_LABELS = {
    "week": "Недельная подписка",
    "month": "30-дневный курс",
    "year": "Годовая подписка",
}


async def check_and_send_reminders(app: Application):
    """
    Раз в час проверяет, у кого подписка истекает в течение 24 часов,
    и присылает напоминание с предложением продлить.
    Каждому пользователю напоминание отправляется один раз (флаг reminder_sent).
    """
    expiring = await get_users_expiring_soon(within_hours=24)

    if not expiring:
        return

    keyboard = [
        [InlineKeyboardButton("📅 +Неделя — 100 ⭐", callback_data="buy_week")],
        [InlineKeyboardButton("🎓 +Месяц — 200 ⭐", callback_data="buy_month")],
        [InlineKeyboardButton("🗓 +Год — 1500 ⭐", callback_data="buy_year")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    for user_id, plan, expires_at in expiring:
        plan_label = PLAN_LABELS.get(plan, "Премиум-доступ")
        time_str = expires_at.strftime("%d.%m.%Y %H:%M")

        text = (
            f"⏰ Твой доступ ({plan_label}) истекает {time_str}!\n\n"
            "Продли сейчас, чтобы не потерять доступ к курсу и не прерывать обучение:"
        )

        try:
            await app.bot.send_message(chat_id=user_id, text=text, reply_markup=markup)
            await mark_reminder_sent(user_id)
            logger.info(f"📨 Напоминание о продлении отправлено: {user_id}")
        except Exception as e:
            logger.error(f"Не удалось отправить напоминание {user_id}: {e}")
            # Помечаем как отправленное всё равно, чтобы не зациклиться на
            # пользователе, который заблокировал бота
            await mark_reminder_sent(user_id)


def register_renewal_job(scheduler, app: Application):
    """
    Регистрирует часовую проверку истекающих подписок в существующем
    APScheduler. Вызывать после создания AsyncIOScheduler в bot.py,
    например:

        from renewal_reminders import register_renewal_job
        register_renewal_job(scheduler, app)
    """
    scheduler.add_job(
        check_and_send_reminders,
        "interval",
        hours=1,
        args=[app],
        id="renewal_reminders",
        replace_existing=True,
    )
    logger.info("✅ Задача напоминаний о продлении зарегистрирована (раз в час)")
