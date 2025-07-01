from telegram import Update
from modules.weather import WeatherModule
from config import WEATHER_API_KEY
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger
from utils.bot_utils import send_message_with_image

logger = setup_logger("weather_command")
data_instance = Data()
weather_module = WeatherModule(api_key=WEATHER_API_KEY)

async def weather_command(update: Update, context):
    logger.info(f"weather_command: {update.effective_user.id}")
    user = update.effective_user
    user_id = user.id
    user_status = data_instance.get_user_status(user_id)
    if user_status == UserStatus.NOT_ALLOWED:
        await update.message.reply_text("❌ Вы не авторизованы для использования этого бота.")
        return
    
    await update.message.reply_text("Введите город для прогноза погоды:")
    
    # Контекст ConversationHandler здесь не используется, поэтому
    # можно просто ожидать следующее сообщение от нужного пользователя.
    # Но для продакшена лучше использовать ConversationHandler.
    context.user_data['waiting_for_city'] = True


async def handle_city_input(update: Update, context):
    """
    Обрабатывает ввод города после команды /weather.
    """
    if not context.user_data.get('waiting_for_city'):
        # Это не ответ на наш запрос, игнорируем
        return

    city = update.message.text.strip()
    context.user_data['waiting_for_city'] = False

    try:
        weather_text, image_prompt = await weather_module.get_weather(city)
        if image_prompt:
            await send_message_with_image(update, context, weather_text, image_prompt)
        else:
            await update.message.reply_text(weather_text, parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке погоды для города '{city}': {e}")
        await update.message.reply_text(f"Произошла непредвиденная ошибка: {e}")
    # Можно доработать: await weather_module.get_weather(...) 