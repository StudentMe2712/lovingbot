import pytest
from unittest.mock import AsyncMock, MagicMock
from modules.memories import MemoryModule
from database.db_manager import DatabaseManager

@pytest.mark.asyncio
async def test_add_and_get_memory(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = MemoryModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = ["Тестовое", "воспоминание"]
    await module.add_memory(update, context)
    memory = db.get_random_memory()
    assert memory is not None
    assert "Тестовое" in memory[3] or "Тестовое" in (memory[5] or "")
    db.close()

@pytest.mark.asyncio
async def test_add_photo_memory(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = MemoryModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.photo = [MagicMock(file_id="photo123")]
    update.message.caption = "Фото-тест"
    context = MagicMock()
    await module.add_photo_memory(update, context)
    memory = db.get_random_memory()
    assert memory is not None
    assert memory[2] == "photo"
    assert memory[4] == "photo123"
    db.close()

@pytest.mark.asyncio
async def test_add_voice_memory(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = MemoryModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.voice = MagicMock(file_id="voice123")
    context = MagicMock()
    await module.add_voice_memory(update, context)
    memory = db.get_random_memory()
    assert memory is not None
    assert memory[2] == "voice"
    assert memory[4] == "voice123"
    db.close()

@pytest.mark.asyncio
async def test_send_random_memory_empty(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = MemoryModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    await module.send_random_memory(update, context)
    update.message.reply_text.assert_called()
    db.close() 