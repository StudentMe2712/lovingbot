import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from modules.reminders import RemindersModule
from database.db_manager import DatabaseManager
from types import SimpleNamespace

@pytest.fixture
def db(tmp_path):
    db = DatabaseManager(str(tmp_path / "test.db"))
    yield db
    db.close()

@pytest.fixture
def scheduler():
    sched = MagicMock()
    sched.add_job = MagicMock()
    return sched

@pytest.mark.asyncio
async def test_add_and_list_reminder(db, scheduler):
    module = RemindersModule(db, scheduler)
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=1),
        effective_chat=SimpleNamespace(id=1),
        message=AsyncMock()
    )
    context = SimpleNamespace(args=["2099-12-31", "23:59", "Test reminder"])
    await module.add_reminder(update, context)
    reminders = db.get_reminders(1)
    assert len(reminders) == 1
    assert "Test reminder" in reminders[0][1]

@pytest.mark.asyncio
async def test_remove_reminder(db, scheduler):
    module = RemindersModule(db, scheduler)
    # Добавляем напоминание
    rid = db.add_reminder(1, "Test", "2099-12-31T23:59:00")
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=1),
        message=AsyncMock()
    )
    context = SimpleNamespace(args=[str(rid)])
    await module.remove_reminder(update, context)
    reminders = db.get_reminders(1)
    assert len(reminders) == 0

@pytest.mark.asyncio
async def test_list_reminders_empty(db, scheduler):
    module = RemindersModule(db, scheduler)
    update = SimpleNamespace(
        effective_user=SimpleNamespace(id=1),
        message=AsyncMock()
    )
    context = SimpleNamespace()
    await module.list_reminders(update, context)
    update.message.reply_text.assert_awaited_with("У вас нет активных напоминаний.") 