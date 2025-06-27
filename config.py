import os
from dotenv import load_dotenv

load_dotenv()

PERSONALIZATION = {
    "names": ["Даулет", "Камилла"],
    "relationship_start": "2024-01-01",
    "preferences": {
        "morning_time": "09:00",
        "evening_time": "21:00",
        "weekend_mode": True
    }
}

NOTIFICATION_SETTINGS = {
    "morning_greetings": True,
    "daily_questions": True,
    "music_recommendations": True,
    "game_notifications": True,
    "memory_reminders": True
}

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
API_ID = "your_api_id"  # Получить на my.telegram.org
API_HASH = "your_api_hash"  # Получить на my.telegram.org
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") 