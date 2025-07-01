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
    if msg is None:
        # Если функция ничего не возвращает, проверяем текст в reply_text
        update.message.reply_text.assert_awaited()
        args, kwargs = update.message.reply_text.call_args
        assert "Идея для свидания:" in args[0]
    else:
        assert "Идея для свидания:" in msg

@pytest.mark.asyncio
async def test_date_idea_advanced_ulitsa_with_weather(monkeypatch):
    with patch('modules.date_ideas_advanced.WeatherModule') as MockWeatherModule, \
         patch('modules.date_ideas_advanced.query_ollama', new_callable=AsyncMock) as mock_query_ollama:
        # Настраиваем мок WeatherModule
        mock_weather_instance = MockWeatherModule.return_value
        mock_weather_instance.get_weather = AsyncMock(return_value="Москва: 20°C, ясно")
        # monkeypatch для CITIES
        monkeypatch.setattr('modules.date_ideas_advanced.WeatherModule.CITIES', ["Москва", "Астана", "Семей"])
        # Настраиваем мок Ollama
        mock_query_ollama.return_value = "Прогулка по парку"
        # Создаем экземпляр тестируемого модуля
        module = DateIdeasAdvancedModule(weather_api_key="dummy")
        module.weather.CITIES = ["Москва", "Астана", "Семей"]
        update = SimpleNamespace(message=AsyncMock())
        context = SimpleNamespace(args=["улица"])
        context.user_data = {'city': 'Москва'} # Устанавливаем город
        await module.date_idea_advanced(update, context, idea_type="улица")
        # Проверяем, что была вызвана генерация идеи
        mock_query_ollama.assert_awaited()
        # Проверяем, что был вызван метод получения погоды
        mock_weather_instance.get_weather.assert_awaited_with("Москва")
        # Проверяем итоговое сообщение
        update.message.reply_text.assert_awaited()
        calls = update.message.reply_text.call_args_list
        assert any("Прогулка по парку" in call.args[0] for call in calls)
        assert any("Погода: Москва: 20°C, ясно" in call.args[0] for call in calls)

@pytest.mark.asyncio
async def test_date_idea_advanced_no_args():
    module = DateIdeasAdvancedModule()
    update = SimpleNamespace(message=AsyncMock())
    context = SimpleNamespace(args=[])
    await module.date_idea_advanced(update, context)
    update.message.reply_text.assert_awaited()
    args, kwargs = update.message.reply_text.call_args
    assert "Выберите тип свидания" in args[0] 