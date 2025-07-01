import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from modules.dates import DateModule
from tests.mocks import create_mock_update, create_mock_context

@pytest.mark.asyncio
@patch('modules.dates.query_ollama', new_callable=AsyncMock)
@patch('modules.dates.send_message_with_image', new_callable=AsyncMock)
async def test_send_date_idea_uses_util(mock_send_with_image, mock_query_ollama, tmp_path):
    """
    Проверяет, что send_date_idea корректно использует send_message_with_image.
    """
    # 1. Настройка
    mock_db = MagicMock()
    date_module = DateModule(mock_db)
    
    update = create_mock_update()
    context = create_mock_context()
    
    # Мокаем ответ от LLM
    generated_idea = "Поход в кино"
    mock_query_ollama.return_value = generated_idea

    # 2. Вызов
    await date_module.send_date_idea(update, context)

    # 3. Проверки
    mock_query_ollama.assert_awaited_once()
    mock_send_with_image.assert_awaited_once()
    _, kwargs = mock_send_with_image.await_args
    text = kwargs.get("text")
    image_prompt = kwargs.get("image_prompt")
    assert text and "Идея для свидания" in text
    assert generated_idea in text
    assert image_prompt and generated_idea in image_prompt

@pytest.mark.asyncio
@patch('modules.dates.query_ollama', new_callable=AsyncMock)
@patch('modules.dates.send_message_with_image', new_callable=AsyncMock)
async def test_send_date_idea_fallback(mock_send_with_image, mock_query_ollama, tmp_path):
    """
    Проверяет, что send_date_idea отправляет сообщение без картинки, если LLM не вернул идею.
    """
    # 1. Настройка
    mock_db = MagicMock()
    date_module = DateModule(mock_db)
    
    update = create_mock_update()
    context = create_mock_context()
    
    # Мокаем ответ от LLM (пустой)
    mock_query_ollama.return_value = None

    # 2. Вызов
    await date_module.send_date_idea(update, context)

    # 3. Проверки
    mock_query_ollama.assert_awaited_once()
    mock_send_with_image.assert_awaited_once()
    _, kwargs = mock_send_with_image.await_args
    text = kwargs.get("text")
    image_prompt = kwargs.get("image_prompt")
    assert text and "идея для свидания" in text.lower()
    assert image_prompt and "romantic date idea" in image_prompt 