from telegram import Update
from modules.dates import DateModule
from database.db_manager import DatabaseManager
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger

logger = setup_logger("date_idea_command")
data_instance = Data()
db = DatabaseManager()
date_module = DateModule(db)

async def date_idea_command(update: Update, context):
    logger.info(f"date_idea_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    await date_module.send_date_idea(update, context) 