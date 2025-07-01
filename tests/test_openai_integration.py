import pytest
from unittest.mock import AsyncMock, patch
from utils import ollama_api
from tests.mocks import create_mock_update, create_mock_context
from modules.dates import DateModule
from modules.greetings import GreetingModule

@pytest.mark.skip(reason="Отключено на время отладки основной логики, зависящей от БД")
@pytest.mark.asyncio
@patch('utils.ollama_api.query_ollama', new_callable=AsyncMock)
async def test_ollama_integration_in_modules(mock_query_ollama):
    """
    Проверяет, что различные модули корректно вызывают query_ollama.
    """
    # 1. Настройка
    mock_query_ollama.return_value = "Ответ от Ollama"
    
    update = create_mock_update()
    context = create_mock_context()
    
    # 2. Тестируем DateModule
    date_module = DateModule(db=None)
    await date_module.send_date_idea(update, context)
    mock_query_ollama.assert_awaited()
    
    # 3. Тестируем GreetingModule
    greeting_module = GreetingModule(db=MagicMock())
    await greeting_module.send_daily_question(update, context)
    await greeting_module.send_compliment(update, context)
    
    # 4. Проверяем общее количество вызовов
    # (1 от date_idea + 1 от question + 1 от compliment)
    assert mock_query_ollama.await_count == 3