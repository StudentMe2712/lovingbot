from telegram import Update, Bot
from modules.music import MusicModule
from database.db_manager import DatabaseManager
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger

logger = setup_logger("music_command")
data_instance = Data()
db = DatabaseManager()
music_module = MusicModule(db)

async def music_command(update: Update, context):
    logger.info(f"music_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = await data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    await music_module.send_music_recommendation(update, context)

async def deezer_music_command(update: Update, context):
    logger.info(f"deezer_music_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = await data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    await music_module.send_deezer_music(update, context)

# Вариант A — пересылка сообщения по message_id
async def forward_audio_command(update, context):
    try:
        # Пример: /forward_audio <message_id>
        if not context.args:
            await update.message.reply_text("Используйте: /forward_audio <message_id>")
            return
        message_id = int(context.args[0])
        SOURCE_CHANNEL_ID = "@AUDIO_KINGDOM"  # username канала
        YOUR_GROUP_ID = update.effective_chat.id
        bot: Bot = context.bot
        await bot.forward_message(
            chat_id=YOUR_GROUP_ID,
            from_chat_id=SOURCE_CHANNEL_ID,
            message_id=message_id
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка пересылки: {e}")

# Вариант B — отправка по file_id
AUDIO_FILE_IDS = []  # Можно заменить на БД или json

async def save_audio_file_id(update, context):
    # Сохраняем file_id из reply на аудиосообщение
    if update.message.reply_to_message and update.message.reply_to_message.audio:
        file_id = update.message.reply_to_message.audio.file_id
        AUDIO_FILE_IDS.append(file_id)
        await update.message.reply_text(f"file_id сохранён: {file_id}")
    else:
        await update.message.reply_text("Ответьте на аудиосообщение, чтобы сохранить file_id.")

async def send_audio_command(update, context):
    # Отправляем последний сохранённый file_id
    if not AUDIO_FILE_IDS:
        await update.message.reply_text("Нет сохранённых file_id.")
        return
    file_id = AUDIO_FILE_IDS[-1]
    await context.bot.send_audio(chat_id=update.effective_chat.id, audio=file_id) 