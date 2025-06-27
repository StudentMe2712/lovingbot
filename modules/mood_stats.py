from database.db_manager import DatabaseManager
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

class MoodStatsModule:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def mood_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        now = datetime.now()
        periods = {
            'день': now - timedelta(days=1),
            'неделя': now - timedelta(days=7),
            'месяц': now - timedelta(days=30)
        }
        msg = "Статистика по настроению:\n"
        for label, since in periods.items():
            moods = [m for m, t in self.db.get_moods(user_id, since=since.isoformat())]
            if moods:
                avg = sum(moods) / len(moods)
                msg += f"За {label}: среднее={avg:.1f}, мин={min(moods)}, макс={max(moods)}, записей={len(moods)}\n"
            else:
                msg += f"За {label}: нет данных\n"
        await update.message.reply_text(msg) 