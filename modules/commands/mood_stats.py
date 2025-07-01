from telegram import Update
from modules.mood_stats import MoodStatsModule
from database.db_manager import DatabaseManager
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger
from utils.db_async import get_mood_summary_last_7_days, get_user_by_tg_id

logger = setup_logger("mood_stats_command")
data_instance = Data()
db = DatabaseManager()
mood_stats_module = MoodStatsModule(db)

async def mood_stats_command(update: Update, context):
    logger.info(f"mood_stats_command: {update.effective_user.id}")
    user_id = update.effective_user.id
    user = await get_user_by_tg_id(user_id)
    partner_id = getattr(user, 'partner_id', None)
    text = "📊 Статистика настроения за 7 дней:\n"
    for uid, label in [(user_id, "Вы"), (partner_id, "Партнёр")]:
        if not uid:
            continue
        stats = await get_mood_summary_last_7_days(uid)
        text += f"\n<b>{label}:</b>\n"
        if stats:
            for row in stats:
                text += f"{row[0]} — {row[1]} дн.\n"
        else:
            text += "Нет данных за последние 7 дней.\n"
    await update.message.reply_text(text, parse_mode="HTML") 