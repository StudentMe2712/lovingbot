from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler
from modules.date_ideas_advanced import DateIdeasAdvancedModule
from config import WEATHER_API_KEY
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger
from telegram.ext import filters

logger = setup_logger("date_idea_advanced_command")
data_instance = Data()
date_ideas_advanced_module = DateIdeasAdvancedModule(weather_api_key=WEATHER_API_KEY)

CHOOSE_TYPE, CHOOSE_CITY, SHOW_IDEA = range(3)

def get_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("🏠 Дом", callback_data="дом"),
         InlineKeyboardButton("🌳 Улица", callback_data="улица"),
         InlineKeyboardButton("☕ Кафе", callback_data="кафе")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_city_keyboard():
    from modules.weather import CITIES
    keyboard = [[city] for city in CITIES]
    return InlineKeyboardMarkup(keyboard)

async def start_date_idea_advanced(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"date_idea_advanced: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return ConversationHandler.END
    await update.message.reply_text(
        "Выберите тип свидания:",
        reply_markup=get_type_keyboard()
    )
    return CHOOSE_TYPE

async def type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idea_type = query.data
    context.user_data['idea_type'] = idea_type
    if idea_type == 'улица':
        # Спрашиваем город
        from modules.weather import CITIES
        keyboard = [[city] for city in CITIES]
        await query.edit_message_text("Выберите город:", reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSE_CITY
    # Для других типов — сразу идея
    msg = await date_ideas_advanced_module.date_idea_advanced(query, context, idea_type=idea_type)
    await query.edit_message_text(msg)
    return ConversationHandler.END

async def city_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обработка выбора города для типа 'улица' только через callback_query
    if not hasattr(update, 'callback_query') or not update.callback_query:
        return
    query = update.callback_query
    await query.answer()
    city = query.data
    from modules.weather import CITIES
    if city not in CITIES:
        await query.edit_message_text(f"Неизвестный город: {city}")
        return
    idea_type = context.user_data.get('idea_type', 'улица')
    # Передаём город в модуль
    msg = await date_ideas_advanced_module.date_idea_advanced(update, context, idea_type=idea_type)
    await query.edit_message_text(msg)
    return ConversationHandler.END

async def cancel_date_idea_advanced(update: Update, context):
    await update.message.reply_text(
        "Вы вышли из расширенного меню идей для свидания.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def get_conv_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("date_idea_advanced", start_date_idea_advanced)],
        states={
            CHOOSE_TYPE: [CallbackQueryHandler(type_chosen)],
            CHOOSE_CITY: [CallbackQueryHandler(city_chosen)],
        },
        fallbacks=[CommandHandler("cancel", cancel_date_idea_advanced)],
        allow_reentry=True,
        per_message=True
    ) 