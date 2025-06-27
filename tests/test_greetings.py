import pytest
from unittest.mock import AsyncMock, MagicMock
from modules.greetings import GreetingModule
from modules.dates import DateModule
from database.db_manager import DatabaseManager

@pytest.mark.asyncio
async def test_send_daily_question(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = GreetingModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    await module.send_daily_question(update=None, context=context)
    context.bot.send_message.assert_called()
    db.close()

@pytest.mark.asyncio
async def test_send_compliment(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = GreetingModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    await module.send_compliment(update, context)
    update.message.reply_text.assert_called()
    db.close()

@pytest.mark.asyncio
async def test_save_mood_valid(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = GreetingModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = "7"
    update.effective_user.id = 123
    context = MagicMock()
    await module.save_mood(update, context)
    update.message.reply_text.assert_called()
    db.close()

@pytest.mark.asyncio
async def test_save_mood_invalid(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = GreetingModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = "abc"
    update.effective_user.id = 123
    context = MagicMock()
    await module.save_mood(update, context)
    update.message.reply_text.assert_called()
    db.close()

@pytest.mark.asyncio
async def test_send_date_idea(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = DateModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    await module.send_date_idea(update, context)
    update.message.reply_text.assert_called()
    db.close() 