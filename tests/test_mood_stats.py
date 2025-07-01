import pytest
from modules.mood_stats import MoodStatsModule
from database.db_manager import DatabaseManager
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
import asyncio
from utils.db_async import add_mood, get_mood_summary_last_7_days

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

@pytest.mark.asyncio
async def test_mood_summary_last_7_days():
    user_id = 111
    now = datetime.utcnow()
    # Добавляем разные значения настроения за последние 7 дней
    for i, mood in enumerate([5, 4, 3, 2, 1, 4, 5]):
        ts = (now - timedelta(days=i)).isoformat()
        await add_mood(user_id, mood, ts)
    stats = await get_mood_summary_last_7_days(user_id)
    cats = {row[0]: row[1] for row in stats}
    assert cats['😊 Хорошее'] >= 3
    assert cats['😐 Нейтральное'] >= 1
    assert cats['😞 Плохое'] >= 1

@pytest.mark.asyncio
@patch('modules.greetings.DatabaseManager')
@patch('database.db_manager.DatabaseManager.is_partner_blocked', return_value=False)
async def test_partner_notification(mock_is_blocked, mock_dbmanager_ctor, monkeypatch):
    from modules.greetings import GreetingModule
    from unittest.mock import MagicMock, AsyncMock
    class DummyUser:
        partner_id = 222
    async def fake_get_user_by_tg_id(user_id):
        return DummyUser()
    monkeypatch.setattr('utils.db_async.get_user_by_tg_id', fake_get_user_by_tg_id)
    mock_db = MagicMock()
    mock_db.is_partner_blocked.return_value = False
    mock_dbmanager_ctor.return_value = mock_db
    gm = GreetingModule(mock_db)
    class DummyUpdate:
        class User:
            id = 111
            first_name = 'TestUser'
        effective_user = User()
        class Message:
            text = '5'
            async def reply_text(self, text):
                pass
        message = Message()
    update = DummyUpdate()
    context = MagicMock()
    async def debug_send_message(*args, **kwargs):
        print('SEND_MESSAGE_CALL')
    context.bot.send_message = debug_send_message
    await gm.save_mood(update, context) 