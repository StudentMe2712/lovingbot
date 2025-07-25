# Romantic Telegram Bot

## Описание

Модульный Telegram-бот для романтических пар с поддержкой воспоминаний, напоминаний, игр, музыки, вопросов дня, интеграции с Deezer и погодой.

## Структура проекта

- `main.py` — точка входа, регистрация команд
- `modules/commands/` — отдельные обработчики для каждой команды (/start, /help, /game, ...)
- `modules/` — бизнес-логика (игры, музыка, воспоминания, погода и т.д.)
- `utils/` — вспомогательные модули (логгер, user_management, ...)
- `database/` — работа с БД (SQLite)
- `tests/` — автотесты для команд и логики

## Быстрый старт

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Создайте файл `.env` и укажите необходимые переменные:
   ```env
   TELEGRAM_BOT_TOKEN=your_token
   WEATHER_API_KEY=your_weather_api_key
   ```
3. Запустите бота:
   ```bash
   python main.py
   ```

## Запуск тестов

```bash
pytest tests/
```

## Основные команды

- /start — приветствие и меню
- /help — справка
- /game — викторина
- /memory — случайное воспоминание
- /add_memory — добавить воспоминание
- /music — музыкальная рекомендация
- /date_idea — идея для свидания
- /question — вопрос дня
- /mood — оценить настроение
- /compliment — комплимент
- /stats — статистика игр
- /reminders — список напоминаний
- /reminder_add — добавить напоминание
- /reminder_remove — удалить напоминание
- /mood_stats — статистика настроения
- /memory_archive — архив воспоминаний
- /date_idea_advanced — расширенная идея для свидания
- /weather — узнать погоду
- /deezer_music — топ-чарт Deezer

## Проверка кода

```bash
flake8
mypy .
```

## Контакты

Для вопросов и предложений: [ваш email или Telegram] #   l o v e b o t  
 