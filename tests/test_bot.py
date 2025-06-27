import pytest
from unittest.mock import AsyncMock, MagicMock
from modules.commands.start import start_command
from modules.commands.help import help_command
from modules.commands.game import game_command
from modules.commands.question import question_command
from modules.commands.memory import memory_command
from modules.commands.add_memory import add_memory_command
from modules.commands.music import music_command
from modules.commands.date_idea import date_idea_command
from modules.commands.mood import mood_command
from modules.commands.compliment import compliment_command
from modules.commands.stats import stats_command
from modules.commands.reminders import reminders_command
from modules.commands.reminder_add import reminder_add_command
from modules.commands.reminder_remove import reminder_remove_command
from modules.commands.mood_stats import mood_stats_command
from modules.commands.memory_archive import memory_archive_command
from modules.commands.weather import weather_command

@pytest.mark.asyncio
async def test_start_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.effective_user.username = "testuser"
    context = MagicMock()
    await start_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_help_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await help_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_game_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await game_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_question_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    await question_command(update, context)
    # Проверяем, что хотя бы один из методов был вызван
    assert update.message.reply_text.await_count > 0 or context.bot.send_message.await_count > 0

@pytest.mark.asyncio
async def test_memory_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await memory_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_add_memory_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await add_memory_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_music_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await music_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_date_idea_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await date_idea_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_mood_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await mood_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_compliment_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await compliment_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_stats_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await stats_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_reminders_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await reminders_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_reminder_add_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await reminder_add_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_reminder_remove_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await reminder_remove_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_mood_stats_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await mood_stats_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_memory_archive_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await memory_archive_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_weather_command():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    await weather_command(update, context)
    update.message.reply_text.assert_called() 