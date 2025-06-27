from telegram import Update
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger

logger = setup_logger("help_command")
data_instance = Data()

HELP_MESSAGE = (
    "Я могу помочь вам создавать и управлять вашими романтическими активностями. Вот что я умею:\n\n"
    "Вы можете управлять мной с помощью этих команд:\n\n"
    "/game - викторина о вас\n"
    "/music - музыкальная рекомендация\n"
    "/memory - случайное воспоминание\n"
    "/add_memory - добавить воспоминание\n"
    "/date_idea - идея для свидания\n"
    "/question - вопрос дня\n"
    "/mood - оценить настроение\n"
    "/compliment - получить комплимент\n"
    "/stats - статистика игр\n"
    "/reminders - список напоминаний\n"
    "/reminder_add - добавить напоминание\n"
    "/reminder_remove - удалить напоминание\n"
    "/mood_stats - статистика настроения\n"
    "/memory_archive - архив воспоминаний\n"
    "/date_idea_advanced - расширенная идея для свидания\n"
    "/weather - узнать погоду\n"
    "/set_partner - выбрать или изменить партнёра (введите его Telegram ID)\n"
    "/deezer_music - топ-чарт Deezer\n"
    "/forward_audio - переслать трек из канала по message_id\n"
    "/save_audio_file_id - сохранить file_id аудио (ответом на аудиосообщение)\n"
    "/send_audio - отправить последний сохранённый file_id\n"
    "\n\n"
    "Настройки и управление:\n"
    "/check_api - проверить доступность внешних сервисов\n"
    "\n\n"
    "Для быстрого доступа используйте меню ниже.\n\n"
    "В игровом меню доступны:\n"
    "- Вопросы партнёра — посмотреть вопросы, добавленные партнёром\n"
    "- Статистика пары — суммарные очки и вопросы вашей пары"
)

async def help_command(update: Update, context):
    logger.info(f"help_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown") 