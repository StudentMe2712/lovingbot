import pytest
from modules.mood_stats import MoodStatsModule
from database.db_manager import DatabaseManager
from types import SimpleNamespace
from unittest.mock import AsyncMock
from datetime import datetime, timedelta

@pytest.fixture
def db(tmp_path):
    db = DatabaseManager(str(tmp_path / "test.db"))
    yield db
    db.close()

@pytest.mark.asyncio
async def test_mood_stats_empty(db):
    module = MoodStatsModule(db)
    update = SimpleNamespace(effective_user=SimpleNamespace(id=1), message=AsyncMock())
    context = SimpleNamespace()
    await module.mood_stats(update, context)
    # Должно быть "нет данных" по всем периодам
    text = "".join([c[0][0] for c in update.message.reply_text.call_args_list])
    assert "нет данных" in text

@pytest.mark.asyncio
async def test_mood_stats_periods(db):
    module = MoodStatsModule(db)
    user_id = 1
    now = datetime.now()
    # За месяц: 3 записи
    db.add_mood(user_id, 5, (now - timedelta(days=20)).isoformat())
    db.add_mood(user_id, 7, (now - timedelta(days=5)).isoformat())
    db.add_mood(user_id, 9, now.isoformat())
    update = SimpleNamespace(effective_user=SimpleNamespace(id=1), message=AsyncMock())
    context = SimpleNamespace()
    await module.mood_stats(update, context)
    args, kwargs = update.message.reply_text.call_args
    text = args[0]
    assert "среднее" in text
    assert "мин=5" in text
    assert "макс=9" in text
    assert "записей=3" in text 