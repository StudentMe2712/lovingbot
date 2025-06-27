from telegram import Update
from modules.memory_archive import MemoryArchiveModule
from database.db_manager import DatabaseManager
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger

logger = setup_logger("memory_archive_command")
data_instance = Data()
db = DatabaseManager()
memory_archive_module = MemoryArchiveModule(db)

async def memory_archive_command(update: Update, context):
    logger.info(f"memory_archive_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    await memory_archive_module.memory_archive(update, context) 