import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from utils.bot_utils import send_message_with_image

@pytest.mark.asyncio
async def test_send_message_with_image_success():
    """
    Проверяет успешный сценарий: отправка текста и изображения.
    """
    # 1. Настройка моков
    update = MagicMock()
    update.effective_chat.id = 12345
    update.message.reply_text = AsyncMock(return_value=True)
    
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_photo = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    test_text = "Это тестовый текст"
    test_image_bytes = b"someimagedata"

    # 2. Мокаем внешние вызовы
    with patch('utils.bot_utils.asyncio.to_thread', new=AsyncMock(return_value=test_image_bytes)) as mock_to_thread:
        with patch('utils.bot_utils.generate_postcard') as mock_generate_postcard:
            # 3. Вызов функции
            await send_message_with_image(update, context, test_text)

            # 4. Проверки
            # Проверяем, что текстовое сообщение было отправлено
            update.message.reply_text.assert_awaited_once_with(test_text, parse_mode="HTML")
            
            # Проверяем, что был показан статус "upload_photo"
            context.bot.send_chat_action.assert_awaited_once_with(chat_id=12345, action='upload_photo')
            
            # Проверяем, что была вызвана генерация изображения
            mock_to_thread.assert_awaited_once()
            
            # Проверяем, что изображение было отправлено
            context.bot.send_photo.assert_awaited_once()
            sent_photo_args = context.bot.send_photo.call_args
            assert sent_photo_args.kwargs['chat_id'] == 12345
            assert sent_photo_args.kwargs['photo'] == test_image_bytes

@pytest.mark.asyncio
async def test_send_message_with_image_generation_fails():
    """
    Проверяет сценарий, когда генерация изображения вызывает исключение.
    """
    # 1. Настройка моков
    update = MagicMock()
    update.effective_chat.id = 12345
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.bot.send_photo = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    test_text = "Текст для неудачной генерации"
    exception_message = "API Error"

    # 2. Мокаем to_thread, чтобы он вызывал исключение
    with patch('utils.bot_utils.asyncio.to_thread', new=AsyncMock(side_effect=Exception(exception_message))) as mock_to_thread:
        # 3. Вызов функции
        await send_message_with_image(update, context, test_text)

        # 4. Проверки
        # Текст должен был отправиться
        update.message.reply_text.assert_awaited_once_with(test_text, parse_mode="HTML")
        
        # Статус должен был отправиться
        context.bot.send_chat_action.assert_awaited_once_with(chat_id=12345, action='upload_photo')
        
        # Генерация была вызвана
        mock_to_thread.assert_awaited_once()
        
        # А вот фото отправиться не должно было
        context.bot.send_photo.assert_not_awaited() 