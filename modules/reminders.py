from database.db_manager import DatabaseManager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import ContextTypes
from dateutil import parser as date_parser
import datetime

class RemindersModule:
    def __init__(self, db: DatabaseManager, scheduler: AsyncIOScheduler):
        self.db = db
        self.scheduler = scheduler

    async def add_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Формат: /reminder_add <дата/время> <текст напоминания>\nПример: /reminder_add 2024-06-10 18:00 Позвонить любимой")
            return
        try:
            remind_at = date_parser.parse(args[0] + (" " + args[1] if len(args) > 2 else ""))
            text = " ".join(args[2:]) if len(args) > 2 else args[1]
        except Exception:
            await update.message.reply_text("Не удалось распознать дату/время. Пример: 2024-06-10 18:00")
            return
        if remind_at < datetime.datetime.now():
            await update.message.reply_text("Дата/время уже прошли!")
            return
        user_id = update.effective_user.id
        reminder_id = self.db.add_reminder(user_id, text, remind_at.isoformat())
        self.scheduler.add_job(self.send_reminder, 'date', run_date=remind_at, args=[update.effective_chat.id, text, reminder_id])
        await update.message.reply_text(f"Напоминание добавлено: {remind_at.strftime('%d.%m.%Y %H:%M')} — {text}")

    async def send_reminder(self, chat_id, text, reminder_id):
        from telegram import Bot
        # context7: Application.get_instance() не используется, нужен токен
        # Лучше передавать bot через context, но для простоты:
        # TODO: заменить на context.bot, если будет доступен
        bot = Bot(token="BOT_TOKEN")
        await bot.send_message(chat_id=chat_id, text=f"🔔 Напоминание: {text}")
        # После отправки удалить напоминание из БД
        self.db.remove_reminder(chat_id, reminder_id)

    async def list_reminders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        reminders = self.db.get_reminders(user_id)
        if not reminders:
            await update.message.reply_text("У вас нет активных напоминаний.")
            return
        msg = "Ваши напоминания:\n"
        for rid, text, dt in reminders:
            msg += f"#{rid}: {dt.replace('T', ' ')} — {text}\n"
        await update.message.reply_text(msg)

    async def remove_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if not args or not args[0].isdigit():
            await update.message.reply_text("Формат: /reminder_remove <id>\nПосмотреть id: /reminders")
            return
        user_id = update.effective_user.id
        reminder_id = int(args[0])
        self.db.remove_reminder(user_id, reminder_id)
        await update.message.reply_text(f"Напоминание #{reminder_id} удалено.") 