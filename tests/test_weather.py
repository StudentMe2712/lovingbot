import pytest
from modules.weather import WeatherModule
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_weather_success():
    module = WeatherModule(api_key="key")
    # Мокаем запрос к API
    fake_item = {
        "dt": 1719240000,  # timestamp для 12:00
        "main": {"temp": 25, "humidity": 50},
        "weather": [{"description": "ясно"}],
        "wind": {"speed": 3}
    }
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"list": [fake_item]})
        mock_get.return_value.__aenter__.return_value = mock_resp
        result, image_prompt = await module.get_weather("Астана")
        assert "Астана" in result
        assert "ясно" in result
        assert image_prompt is not None

@pytest.mark.asyncio
async def test_weather_fail():
    module = WeatherModule(api_key="key")
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 404
        mock_resp.text = AsyncMock(return_value="Not found")
        mock_get.return_value.__aenter__.return_value = mock_resp
        result, image_prompt = await module.get_weather("Астана")
        assert "Не удалось получить погоду" in result
        assert image_prompt is None 