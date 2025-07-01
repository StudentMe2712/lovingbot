import pytest
from unittest.mock import AsyncMock, patch
from modules.memory_archive import MemoryArchiveModule
from tests.mocks import create_mock_update, create_mock_context
from utils.models import Memory
from datetime import datetime
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_memory_archive_empty():
    db = MagicMock()
    module = MemoryArchiveModule(db)
    update = create_mock_update()
    update.message.reply_text = AsyncMock()
    context = create_mock_context()
    context.args = ["день"]
    db.get_memories_by_period.return_value = []
    await module.memory_archive(update, context)
    update.message.reply_text.assert_awaited_with("Воспоминаний за выбранный период нет.")

@pytest.mark.asyncio
async def test_memory_archive_with_data():
    db = MagicMock()
    module = MemoryArchiveModule(db)
    update = create_mock_update()
    update.message.reply_document = AsyncMock()
    context = create_mock_context()
    context.args = ["день"]
    memories = [
        (1, "text", "Воспоминание 1", datetime.now().isoformat()),
        (2, "text", "Воспоминание 2", datetime.now().isoformat()),
    ]
    db.get_memories_by_period.return_value = memories
    await module.memory_archive(update, context)
    update.message.reply_document.assert_awaited() 