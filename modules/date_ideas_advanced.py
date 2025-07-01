from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from modules.weather import WeatherModule
import random
import asyncio
from typing import List, Dict, Any
import json
from utils.ollama_api import query_ollama
from utils.ollama_mode import get_ollama_mode
# from utils.groqapi_client import generate_text

IDEAS = {
    'дом': [
        'Устроить домашний кинотеатр',
        'Приготовить ужин вместе',
        'Поиграть в настольные игры',
        'Совместный творческий вечер'
    ],
    'улица': [
        'Прогулка в парке',
        'Пикник на природе',
        'Катание на велосипедах',
        'Фотосессия на улице'
    ],
    'кафе': [
        'Посетить новое кафе',
        'Завтрак вне дома',
        'Вечер в кофейне с настолками'
    ]
}

MAIN_MENU = [
    ["Игра 🎲", "Музыка 🎵", "Воспоминание 📸"],
    ["Добавить воспоминание ➕📸", "Идея для свидания 💡", "Вопрос дня ❓"],
    ["Настроение 😊", "Комплимент 💬", "Статистика 📊"],
    ["Напоминания ⏰", "Архив воспоминаний 🗂️", "Расшир. свидание 🗺️"],
    ["Deezer музыка 🟦", "Погода ☀️"]
]

class DateIdeasAdvancedModule:
    def __init__(self, weather_api_key: str = None):
        self.weather_api_key = weather_api_key
        self.weather = WeatherModule(weather_api_key) if weather_api_key else None

    async def date_idea_advanced(self, update: Update, context: ContextTypes.DEFAULT_TYPE, idea_type=None):
        if not idea_type:
            keyboard = [["дом", "улица", "кафе"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(
                "Выберите тип свидания: дом, улица, кафе (например: /date_idea_advanced улица)",
                reply_markup=reply_markup
            )
            return
        # Генерация идеи через LLM
        if context:
            mode, submode = get_ollama_mode(context)
        else:
            mode, submode = "general", "standard"
        prompt = f"Придумай уникальную идею для свидания в стиле: {idea_type}. Кратко и по-русски.\nРежим: {mode}\nПодрежим: {submode}"
        result = await query_ollama(prompt, model="llama3")
        # Погода (если выбран 'улица')
        weather_info = ''
        city = None
        if idea_type == 'улица' and self.weather:
            # Получаем город из context.user_data, если есть
            if hasattr(context, 'user_data') and 'city' in context.user_data:
                city = context.user_data['city']
            elif hasattr(update, 'callback_query') and update.callback_query:
                city = update.callback_query.data
            elif hasattr(update, 'message') and update.message:
                city = update.message.text.strip()
            if not city or city not in self.weather.CITIES:
                city = 'Астана'
            weather_info = await self.weather.get_weather(city)
        if result:
            msg = f"Идея для свидания: {result}\n"
            await update.message.reply_text(msg)
        else:
            idea = random.choice(IDEAS[idea_type])
            msg = f"Идея для свидания: {idea}\n"
            await update.message.reply_text(msg)
        if weather_info:
            if isinstance(weather_info, tuple):
                weather_text, weather_image = weather_info
                await update.message.reply_text(f"Погода: {weather_text}")
                if weather_image:
                    await update.message.reply_photo(weather_image, caption="Сгенерировано по погоде!")
            else:
                await update.message.reply_text(f"Погода: {weather_info}")
        return None 