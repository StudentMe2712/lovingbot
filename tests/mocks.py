from unittest.mock import AsyncMock, MagicMock

def create_mock_update():
    """Создает полный мок для объекта telegram.Update."""
    update = MagicMock()
    
    # Атрибуты пользователя
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.effective_user.username = "testuser"
    
    # Атрибуты чата
    update.effective_chat = MagicMock()
    update.effective_chat.id = 12345
    
    # Атрибуты сообщения
    update.message = MagicMock()
    update.message.message_id = 123
    update.message.text = "test message"
    
    # Моки методов для ответа
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    update.message.reply_voice = AsyncMock()
    update.message.reply_video = AsyncMock()
    
    # Атрибуты для callback query
    update.callback_query = MagicMock()
    update.callback_query.data = "test_callback_data"
    update.callback_query.answer = AsyncMock()
    
    # Делаем так, чтобы effective_message работал и для message, и для callback_query
    update.effective_message = update.message

    return update

def create_mock_context():
    """Создает полный мок для объекта telegram.ext.CallbackContext."""
    context = MagicMock()
    
    # Атрибуты бота
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_photo = AsyncMock()
    context.bot.send_chat_action = AsyncMock()
    
    # Хранилище данных
    context.user_data = {}
    context.chat_data = {}
    context.bot_data = {}
    
    # Аргументы команды
    context.args = []
    
    return context 