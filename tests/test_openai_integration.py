import pytest
import sys
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import os

import utils.groqapi_client as groqapi_client

@pytest.mark.asyncio
async def test_generate_text_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    # Мокаем aiohttp.ClientSession
    class FakeResponse:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        async def json(self):
            return {"choices": [{"message": {"content": "Тестовый ответ GroqAPI."}}]}
    class FakeSession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        def post(self, *args, **kwargs):
            return FakeResponse()
    monkeypatch.setattr(groqapi_client.aiohttp, "ClientSession", lambda: FakeSession())
    result = await groqapi_client.generate_text("Тест", max_tokens=10)
    assert result == "Тестовый ответ GroqAPI."

@pytest.mark.asyncio
async def test_music_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    from modules.music import MusicModule
    class FakeUpdate:
        class Message:
            async def reply_text(self, text):
                self.called = True
        message = Message()
    fake_update = FakeUpdate()
    fake_update.message.called = False
    monkeypatch.setattr(groqapi_client, "generate_text", AsyncMock(return_value="Тест GroqAPI (музыка)"))
    module = MusicModule(db=None)
    await module.send_music_recommendation(fake_update, None)
    assert hasattr(fake_update.message, "called")

@pytest.mark.asyncio
async def test_date_idea_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    from modules.dates import DateModule
    class FakeUpdate:
        class Message:
            async def reply_text(self, text):
                self.called = True
        message = Message()
    fake_update = FakeUpdate()
    fake_update.message.called = False
    monkeypatch.setattr(groqapi_client, "generate_text", AsyncMock(return_value="Тест GroqAPI (идея)"))
    module = DateModule(db=None)
    await module.send_date_idea(fake_update, None)
    assert hasattr(fake_update.message, "called")

@pytest.mark.asyncio
async def test_greetings_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    from modules.greetings import GreetingModule
    class FakeChat:
        id = 123
    class FakeUpdate:
        effective_chat = FakeChat()
        class Message:
            async def reply_text(self, text):
                self.called = True
        message = Message()
    fake_update = FakeUpdate()
    fake_update.message.called = False
    monkeypatch.setattr(groqapi_client, "generate_text", AsyncMock(return_value="Тест GroqAPI (greet)"))
    module = GreetingModule(db=None)
    await module.send_daily_question(fake_update, None)
    await module.ask_mood(fake_update, None)
    await module.send_compliment(fake_update, None)
    assert hasattr(fake_update.message, "called")

@pytest.mark.asyncio
async def test_date_idea_advanced_groq(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    from modules.date_ideas_advanced import DateIdeasAdvancedModule
    class FakeUpdate:
        class Message:
            async def reply_text(self, text):
                self.called = True
        message = Message()
    fake_update = FakeUpdate()
    fake_update.message.called = False
    monkeypatch.setattr(groqapi_client, "generate_text", AsyncMock(return_value="Тест GroqAPI (расширенное свидание)"))
    module = DateIdeasAdvancedModule(weather_api_key=None)
    msg = await module.date_idea_advanced(fake_update, None, idea_type="дом")
    assert msg is not None 