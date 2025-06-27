from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from utils.user_management import Data, UserStatus
from config import PERSONALIZATION
from utils.logger import setup_logger
from utils.db_async import get_user_by_tg_id, create_user

logger = setup_logger("start_command")
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
    "\n\n"
    "Настройки и управление:\n"
    "/check_api - проверить доступность внешних сервисов\n"
    "\n\n"
    "Для быстрого доступа используйте меню ниже.\n\n"
    "В игровом меню доступны:\n"
    "/game - начать игру\n"
    "/add_question - добавить вопрос\n"
    "/my_questions - мои вопросы\n"
    "/partner_questions - вопросы партнёра\n"
    "/game_stats - статистика игры\n"
    "Deezer музыка\n"
)

BOTFATHER_STYLE_MESSAGE = (
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
    "/deezer_music - топ-чарт Deezer\n"
    "\n\n"
    "Настройки и управление:\n"
    "/check_api - проверить доступность внешних сервисов\n"
    "\n\n"
    "Для быстрого доступа используйте меню ниже."
)

ASK_NAME = 1

async def start_command(update: Update, context):
    logger.info(f"start_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    db_user = await get_user_by_tg_id(user_id)
    # Новое лаконичное приветствие
    welcome_text = (
        "👋 Добро пожаловать!\n\n"
        "Чтобы начать работу, просто напишите /start.\n\n"
        "Все команды доступны через / (выпадающий список Telegram).\n"
        "\n\n*Рекомендуем начать с /start!*"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")
    if not db_user:
        await update.message.reply_text(
            "Для регистрации введите, пожалуйста, ваше имя:")
        return ASK_NAME
    # Уже зарегистрирован
    await send_welcome(update)
    return ConversationHandler.END

async def ask_name(update: Update, context):
    name = update.message.text.strip()
    user = update.effective_user
    user_id = user.id
    print(f"[ask_name] user_id={user_id}, name={name}")
    logger.info(f"[ask_name] user_id={user_id}, name={name}")
    try:
        print(f"[ask_name] call create_user({user_id}, {name})")
        logger.info(f"[ask_name] call create_user({user_id}, {name})")
        await create_user(user_id, name)
        await update.message.reply_text(f"Спасибо, {name}! Вы успешно зарегистрированы.")
        await send_welcome(update)
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        await update.message.reply_text(f"Ошибка при регистрации: {e}")
    return ConversationHandler.END

async def send_welcome(update: Update):
    keyboard = [
        ["Игра 🎲", "Музыка 🎵", "Воспоминание 📸"],
        ["Добавить воспоминание ➕📸", "Идея для свидания 💡", "Вопрос дня ❓"],
        ["Настроение 😊", "Комплимент 💬", "Статистика 📊"],
        ["Напоминания ⏰", "Архив воспоминаний 🗂️", "Расшир. свидание 🗺️"],
        ["Погода ☀️"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🌅 Добро пожаловать! Я ваш романтичный бот-ассистент. Для списка команд используйте меню ниже.",
        reply_markup=reply_markup
    )
    await update.message.reply_text(BOTFATHER_STYLE_MESSAGE)

async def cancel_start(update: Update, context):
    await update.message.reply_text(
        "Регистрация отменена. Вы можете начать заново в любой момент.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def get_start_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel_start)],
        allow_reentry=True
    ) 