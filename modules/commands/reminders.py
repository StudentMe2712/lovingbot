from telegram import Update
from modules.reminders import RemindersModule
from database.db_manager import DatabaseManager
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger

logger = setup_logger("reminders_command")
data_instance = Data()
db = DatabaseManager()
reminders_module = RemindersModule(db, None)

async def reminders_command(update: Update, context):
    logger.info(f"reminders_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    await reminders_module.list_reminders(update, context) 