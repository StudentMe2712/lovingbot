import pytest
from modules.memory_archive import MemoryArchiveModule
from database.db_manager import DatabaseManager
from types import SimpleNamespace
from unittest.mock import AsyncMock
from datetime import datetime, timedelta

@pytest.fixture
def db(tmp_path):
    db = DatabaseManager(str(tmp_path / "test.db"))
    # Добавим таблицу memories, если нет
    db.cursor.execute('''CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    db.conn.commit()
    yield db
    db.close()

@pytest.mark.asyncio
async def test_memory_archive_empty(db):
    module = MemoryArchiveModule(db)
    update = SimpleNamespace(effective_user=SimpleNamespace(id=1), message=AsyncMock())
    context = SimpleNamespace(args=["день"])
    await module.memory_archive(update, context)
    update.message.reply_text.assert_awaited_with("Воспоминаний за выбранный период нет.")

@pytest.mark.asyncio
async def test_memory_archive_with_data(db, tmp_path):
    module = MemoryArchiveModule(db)
    user_id = 1
    now = datetime.now()
    db.cursor.execute(
        "INSERT INTO memories (user_id, type, content, created_at) VALUES (?, ?, ?, ?)",
        (user_id, "text", "Первое воспоминание", (now - timedelta(days=1)).isoformat())
    )
    db.cursor.execute(
        "INSERT INTO memories (user_id, type, content, created_at) VALUES (?, ?, ?, ?)",
        (user_id, "photo", "photo_id_123", now.isoformat())
    )
    db.conn.commit()
    update = SimpleNamespace(effective_user=SimpleNamespace(id=1), message=AsyncMock())
    context = SimpleNamespace(args=["месяц"])
    # Мокаем отправку документа
    update.message.reply_document = AsyncMock()
    await module.memory_archive(update, context)
    assert update.message.reply_document.await_count == 1
    args, kwargs = update.message.reply_document.call_args
    assert "memory_archive.txt" in str(args[0]) 