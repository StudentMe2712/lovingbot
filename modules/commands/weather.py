from telegram import Update
from modules.weather import WeatherModule
from config import WEATHER_API_KEY
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger

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
    # Запрашиваем город у пользователя
    await update.message.reply_text("Введите город для прогноза погоды:")
    # Ждём следующий текстовый ответ пользователя
    def check_city(msg):
        return msg.from_user.id == user_id and msg.text
    try:
        city_msg = await context.bot.wait_for('message', timeout=30, check=check_city)
        city = city_msg.text.strip()
        result = await weather_module.get_weather(city)
        await update.message.reply_text(result, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
    # Можно доработать: await weather_module.get_weather(...) 