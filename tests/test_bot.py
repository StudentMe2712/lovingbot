import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from main import start_command, help_command, question_command, memory_command, add_memory_command, date_idea_command, mood_command, compliment_command, stats_command, reminders_command, reminder_add_command, reminder_remove_command, memory_archive_command, weather_command
from tests.mocks import create_mock_update, create_mock_context
import types

# Большинство этих тестов проверяют только, что команда вызывается.
# Реальная логика тестируется в отдельных файлах для каждого модуля.

@pytest.mark.asyncio
async def test_start_command(async_session):
    update = create_mock_update()
    context = create_mock_context()
    await start_command(update, context)
    update.message.reply_text.assert_awaited()
    # Проверяем, что приветствие отправлено (по ключевому слову)
    assert "Для регистрации введите, пожалуйста, ваше имя:" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_help_command():
    update = create_mock_update()
    context = create_mock_context()
    await help_command(update, context)
    update.message.reply_text.assert_awaited()
    assert "Я могу помочь вам создавать и управлять вашими романтическими активностями" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('modules.greetings.GreetingModule.send_daily_question', new_callable=AsyncMock)
async def test_question_command(mock_send_question):
    update = create_mock_update()
    context = create_mock_context()
    await question_command(update, context)
    mock_send_question.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.memories.MemoryModule.send_random_memory', new_callable=AsyncMock)
async def test_memory_command(mock_send_random_memory):
    update = create_mock_update()
    context = create_mock_context()
    await memory_command(update, context)
    mock_send_random_memory.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.memories.MemoryModule.add_memory', new_callable=AsyncMock)
async def test_add_memory_command(mock_add_memory):
    update = create_mock_update()
    context = create_mock_context()
    await add_memory_command(update, context)
    mock_add_memory.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.dates.DateModule.send_date_idea', new_callable=AsyncMock)
async def test_date_idea_command(mock_send_idea):
    update = create_mock_update()
    context = create_mock_context()
    await date_idea_command(update, context)
    mock_send_idea.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.greetings.GreetingModule.ask_mood', new_callable=AsyncMock)
async def test_mood_command(mock_ask_mood):
    update = create_mock_update()
    context = create_mock_context()
    await mood_command(update, context)
    mock_ask_mood.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.greetings.GreetingModule.send_compliment', new_callable=AsyncMock)
async def test_compliment_command(mock_send_compliment):
    update = create_mock_update()
    context = create_mock_context()
    await compliment_command(update, context)
    mock_send_compliment.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.games.GameModule.send_stats', new_callable=AsyncMock)
async def test_mood_stats_command(mock_send_stats):
    update = create_mock_update()
    context = create_mock_context()
    await stats_command(update, context)
    mock_send_stats.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.reminders.RemindersModule.list_reminders', new_callable=AsyncMock)
async def test_reminders_command(mock_list_reminders):
    update = create_mock_update()
    context = create_mock_context()
    await reminders_command(update, context)
    mock_list_reminders.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.reminders.RemindersModule.add_reminder', new_callable=AsyncMock)
async def test_reminder_add_command(mock_add_reminder):
    update = create_mock_update()
    context = create_mock_context()
    await reminder_add_command(update, context)
    mock_add_reminder.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.reminders.RemindersModule.remove_reminder', new_callable=AsyncMock)
async def test_reminder_remove_command(mock_remove_reminder):
    update = create_mock_update()
    context = create_mock_context()
    await reminder_remove_command(update, context)
    mock_remove_reminder.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
@patch('modules.memory_archive.MemoryArchiveModule.memory_archive', new_callable=AsyncMock)
async def test_memory_archive_command(mock_memory_archive):
    update = create_mock_update()
    context = create_mock_context()
    await memory_archive_command(update, context)
    mock_memory_archive.assert_awaited_once_with(update, context)

# @pytest.mark.asyncio
# @patch('modules.weather.WeatherModule.weather_handler', new_callable=AsyncMock)
# async def test_weather_command(mock_weather_handler):
#     update = create_mock_update()
#     context = create_mock_context()
#     await weather_command(update, context)
#     mock_weather_handler.assert_awaited_once_with(update, context)

@pytest.mark.asyncio
async def test_add_and_list_wish(monkeypatch):
    db = MagicMock()
    module = __import__('modules.commands.start', fromlist=['add_wish_command', 'wishlist_command'])
    update = MagicMock()
    context = MagicMock()
    update.effective_user.id = 111
    update.message.reply_text = AsyncMock()
    context.args = ["Полететь на море"]
    db.add_wish.return_value = 1
    monkeypatch.setattr(module, 'db', db)
    await module.add_wish_command(update, context)
    db.get_wishlist.return_value = [(1, "Полететь на море", 0, "2024-07-01T12:00:00")]
    await module.wishlist_command(update, context)
    update.message.reply_text.assert_awaited()

@pytest.mark.asyncio
async def test_done_and_remove_wish(monkeypatch):
    db = MagicMock()
    module = __import__('modules.commands.start', fromlist=['done_wish_command', 'remove_wish_command'])
    update = MagicMock()
    context = MagicMock()
    update.effective_user.id = 111
    update.message.reply_text = AsyncMock()
    context.args = ["1"]
    monkeypatch.setattr(module, 'db', db)
    await module.done_wish_command(update, context)
    db.mark_wish_done.assert_called_with(111, 1, done=True)
    await module.remove_wish_command(update, context)
    db.remove_wish.assert_called_with(111, 1)
    update.message.reply_text.assert_awaited()

@pytest.mark.asyncio
async def test_postcard_command(monkeypatch):
    module = __import__('modules.commands.start', fromlist=['postcard_command'])
    update = MagicMock()
    context = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    context.args = ["романтический закат"]
    monkeypatch.setattr('modules.commands.start.generate_postcard', AsyncMock(return_value=b'fakeimg'))
    await module.postcard_command(update, context)
    update.message.reply_photo.assert_awaited_with(b'fakeimg', caption="Открытка: романтический закат") 