import pytest
from unittest.mock import AsyncMock, MagicMock
from modules.music import MusicModule
from database.db_manager import DatabaseManager

@pytest.mark.asyncio
async def test_send_music_recommendation(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = MusicModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    await module.send_music_recommendation(update, context)
    update.message.reply_text.assert_called()
    db.close() 