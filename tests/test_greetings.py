import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from modules.greetings import GreetingModule
from tests.mocks import create_mock_update, create_mock_context

@pytest.mark.asyncio
@patch('modules.greetings.send_message_with_image', new_callable=AsyncMock)
@patch('modules.greetings.query_ollama', new_callable=AsyncMock)
async def test_send_daily_question_uses_util(mock_query_ollama, mock_send_with_image):
    """
    Проверяет, что send_daily_question корректно использует send_message_with_image.
    """
    mock_db = MagicMock()
    module = GreetingModule(mock_db)
    
    update = create_mock_update()
    context = create_mock_context()
    
    generated_question = "Что тебя сегодня порадовало?"
    mock_query_ollama.return_value = generated_question

    await module.send_daily_question(update, context)

    mock_query_ollama.assert_awaited_once()
    mock_send_with_image.assert_awaited_once()
    args, kwargs = mock_send_with_image.await_args
    assert args[0] == update
    assert args[1] == context
    text = kwargs.get("text") if "text" in kwargs else (args[2] if len(args) > 2 else None)
    image_prompt = kwargs.get("image_prompt") if "image_prompt" in kwargs else (args[3] if len(args) > 3 else None)
    assert text and "Вопрос дня" in text
    assert image_prompt == generated_question

@pytest.mark.skip(reason="Требует интеграции с реальным scheduler и мок времени")
@pytest.mark.asyncio
async def test_send_daily_question_scheduled():
    pass

@pytest.mark.asyncio
@patch('modules.greetings.add_mood', new_callable=AsyncMock)
@patch('modules.greetings.get_user_by_tg_id', new_callable=AsyncMock)
async def test_save_mood_valid(mock_get_user, mock_add_mood):
    module = GreetingModule(db=MagicMock())
    update = create_mock_update()
    update.message.text = "7"
    context = create_mock_context()
    user = MagicMock()
    user.partner_id = 12345
    mock_get_user.return_value = user

    await module.save_mood(update, context)

    mock_add_mood.assert_awaited_once()
    update.message.reply_text.assert_awaited_with("Ваше настроение (7) сохранено!")

@pytest.mark.asyncio
async def test_save_mood_invalid():
    module = GreetingModule(db=MagicMock())
    update = create_mock_update()
    update.message.text = "abc"
    context = create_mock_context()

    await module.save_mood(update, context)
    update.message.reply_text.assert_awaited_with("Пожалуйста, введите число от 1 до 10.")

@pytest.mark.asyncio
@patch('modules.greetings.get_user_by_tg_id', new_callable=AsyncMock)
@patch('modules.greetings.add_mood', new_callable=AsyncMock)
@patch('modules.greetings.DatabaseManager.is_partner_blocked', return_value=False)
async def test_save_mood_partner_notification(mock_is_blocked, mock_add_mood, mock_get_user):
    module = GreetingModule(db=MagicMock())
    update = create_mock_update()
    context = create_mock_context()
    update.message.text = "8"
    
    mock_user = MagicMock()
    mock_user.partner_id = 222
    mock_get_user.return_value = mock_user

    await module.save_mood(update, context)

    context.bot.send_message.assert_awaited_with(
        chat_id=222, 
        text=f"💬 У пользователя {update.effective_user.first_name} сегодня настроение: 8/10."
    )

@pytest.mark.asyncio
@patch('modules.greetings.get_user_by_tg_id', new_callable=AsyncMock)
@patch('modules.greetings.add_mood', new_callable=AsyncMock)
@patch('modules.greetings.DatabaseManager.is_partner_blocked', return_value=True)
async def test_save_mood_blocked_partner(mock_is_blocked, mock_add_mood, mock_get_user):
    module = GreetingModule(db=MagicMock())
    update = create_mock_update()
    context = create_mock_context()
    update.message.text = "8"
    
    mock_user = MagicMock()
    mock_user.partner_id = 222
    mock_get_user.return_value = mock_user
    
    await module.save_mood(update, context)

    context.bot.send_message.assert_not_awaited() 