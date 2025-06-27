from telegram import Update
from modules.memories import MemoryModule
from database.db_manager import DatabaseManager
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger

logger = setup_logger("memory_command")
data_instance = Data()
db = DatabaseManager()
memory_module = MemoryModule(db)

async def memory_command(update: Update, context):
    logger.info(f"memory_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    await memory_module.send_random_memory(update, context) 