import sys
import asyncio
import nest_asyncio
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import PERSONALIZATION, NOTIFICATION_SETTINGS, TELEGRAM_BOT_TOKEN, WEATHER_API_KEY
from modules.greetings import GreetingModule
from modules.games import GameModule
from modules.memories import MemoryModule
from modules.music import MusicModule
from modules.dates import DateModule
from modules.reminders import RemindersModule
from modules.mood_stats import MoodStatsModule
from modules.memory_archive import MemoryArchiveModule
from modules.date_ideas_advanced import DateIdeasAdvancedModule
from modules.weather import WeatherModule, CITIES
from database.db_manager import DatabaseManager
import logging
import os
from modules.channel_music import send_channel_music
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger
from modules.commands.start import get_start_conv_handler, start_command, toggle_ollama_mode_handler, wishlist_command, add_wish_command, done_wish_command, remove_wish_command, postcard_command, block_partner_command, unblock_partner_command
from modules.commands.help import help_command
from modules.commands.game import get_game_conv_handler, game_stats, EXTRA_COMMANDS, toggle_ollama_mode_game_handler
from modules.commands.question import question_command
from modules.commands.memory import memory_command
from modules.commands.add_memory import add_memory_command
from modules.commands.music import music_command, deezer_music_command, forward_audio_command, save_audio_file_id, send_audio_command
from modules.commands.date_idea import date_idea_command
from modules.commands.mood import mood_command
from modules.commands.compliment import compliment_command
from modules.commands.stats import stats_command
from modules.commands.reminder_add import reminder_add_command
from modules.commands.reminder_remove import reminder_remove_command
from modules.commands.mood_stats import mood_stats_command
from modules.commands.memory_archive import memory_archive_command
from modules.commands.date_idea_advanced import get_conv_handler
from utils.db_async import init_db
from modules.commands.draw import draw_command
from modules.commands.reminders import reminders_command
from modules.commands.weather import weather_command
from utils.ollama_mode import get_mode_button_text

if sys.platform.startswith("win") and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    logger = setup_logger("main")
    db = DatabaseManager()
    greeting_module = GreetingModule(db)
    game_module = GameModule(db)
    memory_module = MemoryModule(db)
    music_module = MusicModule(db)
    date_module = DateModule(db)
    reminders_module = RemindersModule(db, None)
    mood_stats_module = MoodStatsModule(db)
    memory_archive_module = MemoryArchiveModule(db)
    date_ideas_advanced_module = DateIdeasAdvancedModule(weather_api_key=WEATHER_API_KEY)
    weather_module = WeatherModule(api_key=WEATHER_API_KEY)

    async def help_command(update, context):
        help_text = (
            "\n".join([
                "Вы можете управлять мной с помощью этих команд:",
                "/game - викторина о вас",
                "/music - музыкальная рекомендация",
                "/memory - случайное воспоминание",
                "/add_memory - добавить воспоминание",
                "/date_idea - идея для свидания",
                "/question - вопрос дня",
                "/mood - оценить настроение",
                "/compliment - получить комплимент",
                "/stats - статистика игр",
                "/reminders - список напоминаний",
                "/reminder_add - добавить напоминание",
                "/reminder_remove - удалить напоминание",
                "/mood_stats - статистика настроения",
                "/memory_archive - архив воспоминаний",
                "/date_idea_advanced - расширенная идея для свидания",
                "/weather - узнать погоду",
                "/deezer_music - топ-чарт Deezer",
                "/block_partner - заблокировать партнёра",
                "/unblock_partner - разблокировать партнёра",
                "/wishlist - список желаний",
                "/add_wish - добавить желание",
                "/done_wish - отметить желание как выполненное",
                "/remove_wish - удалить желание",
                "/postcard - создать открытку по описанию"
            ])
        )
        await update.message.reply_text(help_text)

    RUS_COMMANDS = {
        "Игры 🎲": game_module.start_game,
        "Музыка 🎵": music_module.send_music_recommendation,
        "Погода ☀️": weather_command,
        "Воспоминания 📸": memory_module.send_random_memory,
        "Добавить воспоминание ➕📸": memory_module.add_memory,
        "Архив воспоминаний 🗂️": memory_archive_command,
        "Идея для свидания 💡": date_module.send_date_idea,
        "Расшир. свидание 🗺️": date_ideas_advanced_module.date_idea_advanced,
        "Вопрос дня ❓": greeting_module.send_daily_question,
        "Желания 🎁": wishlist_command,
        "Добавить желание ➕🎁": add_wish_command,
        "Выполнить желание ✅": done_wish_command,
        "Удалить желание ❌": remove_wish_command,
        "Создать открытку 🖼️": postcard_command,
        "Комплимент 💬": greeting_module.send_compliment,
        "Настроение 😊": greeting_module.ask_mood,
        "Статистика 📊": game_module.send_stats,
        "Напоминания ⏰": reminders_module.list_reminders,
        "Добавить напоминание ➕⏰": reminder_add_command,
        "Удалить напоминание ❌⏰": reminder_remove_command,
        "Deezer музыка 🟦": music_module.send_deezer_music,
        "Заблокировать партнёра 🚫": block_partner_command,
        "Разблокировать партнёра 🔓": unblock_partner_command,
        "Помощь /help": help_command,
        "В главное меню": None
    }

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    scheduler = AsyncIOScheduler()  # без event_loop!
    reminders_module.scheduler = scheduler  # передаём scheduler после создания

    # Сначала только регистрация через /start
    app.add_handler(get_start_conv_handler())
    app.add_handler(get_game_conv_handler())
    # Остальные обработчики (MessageHandler(filters.TEXT & ~filters.COMMAND)) добавлять только после регистрации пользователя

    # --- Погода: FSM ---
    async def handle_weather_city(update, context):
        logger.info(f"[Погода] handle_weather_city: user_id={update.effective_user.id if update.effective_user else 'unknown'}")
        keyboard = [[city] for city in CITIES]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        context.user_data['weather_state'] = 'choose_city'
        await update.message.reply_text("Выберите город:", reply_markup=reply_markup)

    async def handle_weather_fsm(update, context):
        # Обработка /cancel
        if update.message.text.strip().lower() == '/cancel':
            context.user_data['weather_state'] = None
            await update.message.reply_text(
                "Вы вышли из режима выбора погоды.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        state = context.user_data.get('weather_state')
        if state == 'choose_city':
            city = update.message.text.strip()
            reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
            if city not in CITIES:
                await update.message.reply_text(f"Неизвестный город: {city}", reply_markup=reply_markup)
                return
            try:
                result = await weather_module.get_weather(city)
                await update.message.reply_text(result, reply_markup=reply_markup, parse_mode="HTML")
            except Exception as e:
                await update.message.reply_text(f"Ошибка при получении погоды: {e}", reply_markup=reply_markup)
            context.user_data['weather_state'] = None
            return
        # Если не погода — обычная логика (например, игра)
        await game_module.answer_game(update, context)

    # --- END FSM ---

    # --- Настроение: FSM ---
    async def handle_mood_fsm(update, context):
        # Обработка /cancel
        if update.message.text.strip().lower() == '/cancel':
            context.user_data['mood_state'] = None
            await update.message.reply_text(
                "Вы вышли из режима оценки настроения.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        state = context.user_data.get('mood_state')
        if state == 'ask_mood':
            try:
                mood = int(update.message.text)
            except Exception:
                await update.message.reply_text("Пожалуйста, введите число от 1 до 10.")
                return
            user_id = update.effective_user.id
            from datetime import datetime
            db.add_mood(user_id, mood, datetime.now().isoformat())
            await update.message.reply_text(f"Ваше настроение ({mood}) сохранено!", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
            context.user_data['mood_state'] = None
            return
        # Если не настроение — обычная логика
        await handle_weather_fsm(update, context)

    # --- END FSM ---

    # В handle_rus_menu добавляю вызов FSM
    async def handle_rus_menu(update, context):
        logger.info(f"handle_rus_menu: {update.message.text}")
        if update.message.text == "В главное меню":
            from modules.commands.start import start_command
            await start_command(update, context)
            return
        if update.message.text == "Погода ☀️":
            await handle_weather_city(update, context)
            return
        handler = RUS_COMMANDS.get(update.message.text)
        if handler:
            await handler(update, context)
        else:
            logger.info(f"Нет обработчика для: {update.message.text}")

    # Заменяю глобальный MessageHandler (filters.TEXT & ~filters.COMMAND) на FSM-обработчик
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_weather_fsm))

    # Обработчик выбора типа свидания для расширенного меню
    async def handle_date_type_choice(update, context):
        date_types = ["дом", "улица", "кафе"]
        if update.message.text.lower() in date_types:
            # Получаем идею
            await date_ideas_advanced_module.date_idea_advanced(update, context)
            # Показываем кнопку возврата
            reply_markup = ReplyKeyboardMarkup([
                ["В главное меню"]
            ], resize_keyboard=True)
            await update.message.reply_text("Вы можете вернуться в главное меню.", reply_markup=reply_markup)

    app.add_handler(CommandHandler("memory", memory_command))
    app.add_handler(CommandHandler("add_memory", add_memory_command))
    app.add_handler(MessageHandler(filters.PHOTO, memory_module.add_photo_memory))
    app.add_handler(MessageHandler(filters.VIDEO, memory_module.add_video_memory))
    app.add_handler(MessageHandler(filters.VOICE, memory_module.add_voice_memory))
    app.add_handler(CommandHandler("music", music_command))
    app.add_handler(CommandHandler("deezer_music", deezer_music_command))
    app.add_handler(CommandHandler("question", question_command))
    app.add_handler(CommandHandler("date_idea", date_idea_command))
    app.add_handler(CommandHandler("mood", mood_command))
    app.add_handler(MessageHandler(filters.Regex(r'^[1-9]$|^10$'), greeting_module.save_mood))
    app.add_handler(CommandHandler("compliment", compliment_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("reminder_add", reminder_add_command))
    app.add_handler(CommandHandler("reminders", reminders_module.list_reminders))
    app.add_handler(CommandHandler("reminder_remove", reminder_remove_command))
    app.add_handler(CommandHandler("mood_stats", mood_stats_command))
    app.add_handler(CommandHandler("memory_archive", memory_archive_command))
    app.add_handler(get_conv_handler())
    app.add_handler(MessageHandler(filters.Regex(r"^дом$|^улица$|^кафе$"), handle_date_type_choice), group=0)
    app.add_handler(MessageHandler(filters.Regex(r"^Игра.*$|^Музыка.*$|^Воспоминание.*$|^Добавить воспоминание.*$|^Идея для свидания.*$|^Вопрос дня.*$|^Настроение.*$|^Комплимент.*$|^Статистика.*$|^Напоминания.*$|^Архив воспоминаний.*$|^Расшир. свидание.*$|^Deezer музыка.*$|^Погода.*$|^В главное меню$"), handle_rus_menu), group=1)
    app.add_handler(CommandHandler("game_stats", game_stats))
    # Регистрирую дополнительные команды для вопросов
    for cmd in EXTRA_COMMANDS:
        app.add_handler(cmd)
    app.add_handler(CommandHandler("forward_audio", forward_audio_command))
    app.add_handler(CommandHandler("save_audio_file_id", save_audio_file_id))
    app.add_handler(CommandHandler("send_audio", send_audio_command))
    app.add_handler(CommandHandler("draw", draw_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (filters.Regex(f'^{get_mode_button_text("general")}$') | filters.Regex(f'^{get_mode_button_text("couple")}$')), toggle_ollama_mode_handler))
    app.add_handler(MessageHandler(filters.TEXT & (filters.Regex(f'^{get_mode_button_text("general")}$') | filters.Regex(f'^{get_mode_button_text("couple")}$')), toggle_ollama_mode_game_handler))

    # Пример расписания (JobQueue через APScheduler)
    scheduler.add_job(greeting_module.send_morning_greeting, 'cron', hour=9, minute=0)
    scheduler.add_job(music_module.send_music_recommendation, 'cron', hour=18, minute=0, args=[None, None])
    scheduler.add_job(greeting_module.send_daily_question, 'cron', hour=12, minute=0, args=[None, None])
    scheduler.add_job(greeting_module.send_daily_question, 'cron', hour=18, minute=0, args=[None, None])
    # TODO: добавить остальные задачи

    # Главная клавиатура для возврата
    MAIN_MENU = [
        ["Игры 🎲", "Музыка 🎵", "Погода ☀️"],
        ["Воспоминания 📸", "Добавить воспоминание ➕📸", "Архив воспоминаний 🗂️"],
        ["Идея для свидания 💡", "Расшир. свидание 🗺️", "Вопрос дня ❓"],
        ["Желания 🎁", "Добавить желание ➕🎁", "Выполнить желание ✅", "Удалить желание ❌"],
        ["Создать открытку 🖼️"],
        ["Комплимент 💬", "Настроение 😊", "Статистика 📊"],
        ["Напоминания ⏰", "Добавить напоминание ➕⏰", "Удалить напоминание ❌⏰"],
        ["Deezer музыка 🟦"],
        ["Заблокировать партнёра 🚫", "Разблокировать партнёра 🔓"],
        ["Помощь /help"]
    ]

    await init_db()

    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever() 