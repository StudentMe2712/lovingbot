import pytest
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from modules.reminders import RemindersModule
from tests.mocks import create_mock_update, create_mock_context
from utils.models import Reminder
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_add_reminder():
    db = MagicMock()
    scheduler = MagicMock()
    module = RemindersModule(db, scheduler)
    update = create_mock_update()
    context = create_mock_context()
    context.args = ["2099-12-31", "23:59", "Тестовое", "напоминание"]
    db.add_reminder.return_value = 1
    await module.add_reminder(update, context)
    db.add_reminder.assert_called()
    scheduler.add_job.assert_called()
    update.message.reply_text.assert_awaited()

@pytest.mark.asyncio
async def test_list_reminders_empty():
    db = MagicMock()
    scheduler = MagicMock()
    module = RemindersModule(db, scheduler)
    update = create_mock_update()
    context = create_mock_context()
    db.get_reminders.return_value = []
    await module.list_reminders(update, context)
    update.message.reply_text.assert_awaited()

@pytest.mark.asyncio
async def test_list_reminders_with_data():
    db = MagicMock()
    scheduler = MagicMock()
    module = RemindersModule(db, scheduler)
    update = create_mock_update()
    context = create_mock_context()
    reminders = [
        (1, "Напоминание 1", "2024-07-01T18:00:00", 0),
        (2, "Общее напоминание", "2024-07-02T10:00:00", 1)
    ]
    db.get_reminders.return_value = reminders
    await module.list_reminders(update, context)
    update.message.reply_text.assert_awaited()
    args = update.message.reply_text.call_args[0][0]
    assert "Напоминание 1" in args
    assert "Общее напоминание (для пары)" in args

@pytest.mark.asyncio
async def test_remove_reminder():
    db = MagicMock()
    scheduler = MagicMock()
    module = RemindersModule(db, scheduler)
    update = create_mock_update()
    context = create_mock_context()
    context.args = ["1"]
    db.remove_reminder.return_value = True
    await module.remove_reminder(update, context)
    db.remove_reminder.assert_called()
    update.message.reply_text.assert_awaited()

@pytest.mark.asyncio
async def test_add_shared_reminder():
    db = MagicMock()
    scheduler = MagicMock()
    module = __import__('modules.reminders', fromlist=['RemindersModule']).RemindersModule(db, scheduler)
    update = MagicMock()
    update.effective_user.id = 111
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["2024-07-01", "18:00", "Позвонить", "для_пары"]
    db.add_reminder.return_value = 1
    await module.add_reminder(update, context)
    update.message.reply_text.assert_awaited()

@pytest.mark.asyncio
async def test_send_reminder_blocked_partner():
    db = MagicMock()
    scheduler = MagicMock()
    module = __import__('modules.reminders', fromlist=['RemindersModule']).RemindersModule(db, scheduler)
    db.get_reminders.return_value = [
        (1, "Позвонить", "2024-07-01T18:00:00", 1)
    ]
    db.is_partner_blocked.return_value = True
    with patch('telegram.Bot.send_message', new_callable=AsyncMock) as mock_send_message:
        await module.send_reminder(111, "Позвонить", 1)
        mock_send_message.assert_not_awaited() 