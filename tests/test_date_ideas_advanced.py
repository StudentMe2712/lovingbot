import pytest
from modules.date_ideas_advanced import DateIdeasAdvancedModule
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_date_idea_advanced_dom():
    module = DateIdeasAdvancedModule()
    update = SimpleNamespace(message=AsyncMock())
    context = SimpleNamespace(args=["дом"])
    msg = await module.date_idea_advanced(update, context, idea_type="дом")
    assert "Идея для свидания:" in msg

@pytest.mark.asyncio
async def test_date_idea_advanced_ulitsa_with_weather():
    module = DateIdeasAdvancedModule(weather_api_key="dummy")
    update = SimpleNamespace(message=AsyncMock())
    context = SimpleNamespace(args=["улица"])
    # Мокаем WeatherModule.get_weather
    with patch.object(module.weather, 'get_weather', AsyncMock(return_value="Москва: 20°C, ясно")):
        msg = await module.date_idea_advanced(update, context, idea_type="улица")
        assert "Идея для свидания:" in msg
        assert "Погода: Москва: 20°C, ясно" in msg

@pytest.mark.asyncio
async def test_date_idea_advanced_no_args():
    module = DateIdeasAdvancedModule()
    update = SimpleNamespace(message=AsyncMock())
    context = SimpleNamespace(args=[])
    await module.date_idea_advanced(update, context)
    update.message.reply_text.assert_awaited()
    args, kwargs = update.message.reply_text.call_args
    assert "Выберите тип свидания" in args[0] 