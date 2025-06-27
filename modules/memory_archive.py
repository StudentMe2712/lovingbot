from database.db_manager import DatabaseManager
from telegram import Update, InputFile, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import io

class MemoryArchiveModule:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def memory_archive(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        periods = {
            'день': timedelta(days=1),
            'неделя': timedelta(days=7),
            'месяц': timedelta(days=30),
            'все': None
        }
        if not context.args or context.args[0] not in periods:
            keyboard = [["день", "неделя", "месяц", "все"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(
                "Выберите период для архива: день, неделя, месяц, все (например: /memory_archive неделя)",
                reply_markup=reply_markup
            )
            return
        period = context.args[0]
        user_id = update.effective_user.id
        since = None
        if periods[period]:
            since = (datetime.now() - periods[period]).isoformat()
        memories = self.db.get_memories_by_period(user_id, since)
        if not memories:
            await update.message.reply_text("Воспоминаний за выбранный период нет.")
            return
        # Формируем текстовый архив
        archive = io.StringIO()
        for mid, mtype, content, created_at in memories:
            archive.write(f"[{created_at.replace('T', ' ')}] {mtype}: {content}\n")
        archive.seek(0)
        await update.message.reply_document(document=InputFile(archive, filename="memory_archive.txt"), caption="Ваш архив воспоминаний") 