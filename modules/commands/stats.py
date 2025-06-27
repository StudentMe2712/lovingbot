from telegram import Update
from modules.games import GameModule
from database.db_manager import DatabaseManager
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger

logger = setup_logger("stats_command")
data_instance = Data()
db = DatabaseManager()
game_module = GameModule(db)

async def stats_command(update: Update, context):
    logger.info(f"stats_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    await game_module.send_stats(update, context) 