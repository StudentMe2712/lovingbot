from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from utils.user_management import Data, UserStatus
from config import PERSONALIZATION
from utils.logger import setup_logger
from utils.db_async import get_user_by_tg_id, create_user
from database.db_manager import DatabaseManager
from datetime import datetime
from utils.sd_pipeline import generate_postcard
from utils.ollama_mode import get_ollama_mode, get_mode_button_text, set_ollama_mode

logger = setup_logger("start_command")
data_instance = Data()
db = DatabaseManager()

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
    "/block_partner - заблокировать партнёра\n"
    "/unblock_partner - разблокировать партнёра\n"
    "/wishlist - список желаний\n"
    "/add_wish - добавить желание\n"
    "/done_wish - отметить желание как выполненное\n"
    "/remove_wish - удалить желание\n"
    "/postcard - создать открытку по описанию\n"
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
    "/block_partner - заблокировать партнёра\n"
    "/unblock_partner - разблокировать партнёра\n"
    "/wishlist - список желаний\n"
    "/add_wish - добавить желание\n"
    "/done_wish - отметить желание как выполненное\n"
    "/remove_wish - удалить желание\n"
    "/postcard - создать открытку по описанию\n"
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

async def send_welcome(update: Update, context=None):
    if context:
        mode, _ = get_ollama_mode(context)
    else:
        mode = "general"
    mode_button = [get_mode_button_text(mode)]
    keyboard = [mode_button,
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

async def block_partner_command(update, context):
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Формат: /block_partner <tg_id партнёра>")
        return
    partner_id = int(context.args[0])
    db.block_partner(user_id, partner_id)
    await update.message.reply_text(f"Партнёр с ID {partner_id} заблокирован.")

async def unblock_partner_command(update, context):
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Формат: /unblock_partner <tg_id партнёра>")
        return
    partner_id = int(context.args[0])
    db.unblock_partner(user_id, partner_id)
    await update.message.reply_text(f"Партнёр с ID {partner_id} разблокирован.")

async def wishlist_command(update, context):
    user_id = update.effective_user.id
    wishes = db.get_wishlist(user_id)
    if not wishes:
        await update.message.reply_text("Ваш список желаний пуст.")
        return
    msg = "Ваш wishlist:\n"
    for wid, item, done, created_at in wishes:
        status = "✅" if done else "❌"
        msg += f"#{wid}: {item} {status} (добавлено {created_at})\n"
    await update.message.reply_text(msg)

async def add_wish_command(update, context):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Формат: /add_wish <желание>")
        return
    item = " ".join(context.args)
    db.add_wish(user_id, item, datetime.now().isoformat())
    await update.message.reply_text(f"Желание добавлено: {item}")

async def done_wish_command(update, context):
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Формат: /done_wish <id желания>")
        return
    wish_id = int(context.args[0])
    db.mark_wish_done(user_id, wish_id, done=True)
    await update.message.reply_text(f"Желание #{wish_id} отмечено как выполненное!")

async def remove_wish_command(update, context):
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Формат: /remove_wish <id желания>")
        return
    wish_id = int(context.args[0])
    db.remove_wish(user_id, wish_id)
    await update.message.reply_text(f"Желание #{wish_id} удалено.")

async def postcard_command(update, context):
    if not context.args:
        await update.message.reply_text("Формат: /postcard <описание открытки>")
        return
    prompt = " ".join(context.args)
    await update.message.reply_text("Генерирую открытку... Это может занять до 1 минуты.")
    try:
        print("[DEBUG] Перед вызовом generate_postcard")
        image_bytes = await generate_postcard(prompt)
        print(f"[DEBUG] После generate_postcard, image_bytes: {image_bytes}")
        print("[DEBUG] После generate_postcard, перед reply_photo")
        await update.message.reply_photo(image_bytes, caption=f"Открытка: {prompt}")
        print("[DEBUG] После reply_photo")
    except Exception as e:
        print(f"[DEBUG] В except postcard_command: {e}")
        await update.message.reply_text(f"Ошибка генерации открытки: {e}")

async def toggle_ollama_mode_handler(update, context):
    mode, submode = get_ollama_mode(context)
    new_mode = "couple" if mode == "general" else "general"
    set_ollama_mode(context, new_mode)
    await update.message.reply_text(f"Режим переключён: {get_mode_button_text(new_mode)}")
    await send_welcome(update, context)

def get_start_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel_start)],
        allow_reentry=True
    ) 