from telegram import Update
from modules.mood_stats import MoodStatsModule
from database.db_manager import DatabaseManager
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger

logger = setup_logger("mood_stats_command")
data_instance = Data()
db = DatabaseManager()
mood_stats_module = MoodStatsModule(db)

async def mood_stats_command(update: Update, context):
    logger.info(f"mood_stats_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    await mood_stats_module.mood_stats(update, context) 