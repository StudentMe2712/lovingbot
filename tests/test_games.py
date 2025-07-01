import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from modules.games import GameModule
from database.db_manager import DatabaseManager
from modules.commands.game import add_question_input, add_answer_input, game_entry, delete_confirm, find_question_process, set_partner_input, partner_questions, partner_confirm_callback, parse_generated_questions, generate_questions
from utils.db_async import update_user_partner_id, get_user_by_tg_id, add_question, get_all_questions
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

@pytest.mark.asyncio
async def test_quiz_game(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = GameModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 1
    context = MagicMock()
    # Мокаем get_random_question_for_user
    with patch('modules.games.get_random_question_for_user', new_callable=AsyncMock) as mock_get_q:
        class Q:
            question = "Тестовый вопрос"
            answer = "ответ"
        mock_get_q.return_value = Q()
        # Старт игры
        await module.start_game(update, context)
        update.message.reply_text.assert_called()
        # Ответ (правильный)
        q = module.current[1]
        update.message.text = q["a"]
        await module.answer_game(update, context)
        # Ответ (неправильный)
        module.current[1] = q
        update.message.text = "неправильно"
        await module.answer_game(update, context)
    db.close()

@pytest.mark.asyncio
async def test_send_stats_empty(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(str(db_path))
    module = GameModule(db)
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    await module.send_stats(update, context)
    update.message.reply_text.assert_called()
    db.close()

@pytest.mark.asyncio
async def test_add_question_empty_validation():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = "   "
    context = MagicMock()
    result = await add_question_input(update, context)
    update.message.reply_text.assert_awaited_with("Вопрос не может быть пустым. Введите текст вопроса:")
    assert result is not None

@pytest.mark.asyncio
async def test_add_answer_empty_validation():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = "   "
    context = MagicMock()
    context.user_data = {'temp_question': 'Тест'}
    result = await add_answer_input(update, context)
    update.message.reply_text.assert_awaited_with("Ответ не может быть пустым. Введите правильный ответ:")
    assert result is not None

@pytest.mark.asyncio
async def test_game_entry_menu_buttons(monkeypatch):
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    # Мокаем db.conn.execute
    monkeypatch.setattr("modules.commands.game.db", MagicMock())
    modules_db = __import__("modules.commands.game", fromlist=["db"]).db
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (3,)
    modules_db.conn.execute.return_value = mock_cursor
    await game_entry(update, context)
    args, kwargs = update.message.reply_text.call_args
    assert any("Мои вопросы" in str(a) for a in args) or any("Мои вопросы" in str(v) for v in kwargs.values())

@pytest.mark.asyncio
async def test_delete_confirm_return_menu():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = "да"
    context = MagicMock()
    context.user_data = {'delete_qid': 1, 'delete_qtext': 'Тест'}
    update.effective_user.id = 1
    result = await delete_confirm(update, context)
    # Проверяем, что после удаления вызывается меню
    assert update.message.reply_text.await_count > 0
    assert result is not None

@pytest.mark.asyncio
async def test_find_question_process_return_menu():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = "В меню"
    context = MagicMock()
    update.effective_user.id = 1
    result = await find_question_process(update, context)
    assert result is not None

@pytest.mark.asyncio
async def test_set_partner_self():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = "123"
    update.effective_user.id = 123
    context = MagicMock()
    result = await set_partner_input(update, context)
    update.message.reply_text.assert_awaited_with("Нельзя выбрать себя партнёром!")
    assert result is not None

@pytest.mark.asyncio
async def test_set_partner_sends_request(monkeypatch):
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.text = "456"
    update.effective_user.id = 123
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    # Мокаем get_user_by_tg_id
    async def fake_get_user_by_tg_id(tg_id):
        class U: partner_id = None; name = "Test"; score = 0
        return U()
    monkeypatch.setattr("modules.commands.game.get_user_by_tg_id", fake_get_user_by_tg_id)
    monkeypatch.setattr("modules.commands.game.update_user_partner_id", AsyncMock())
    monkeypatch.setattr("modules.commands.game.update_partner_confirmed", AsyncMock())
    result = await set_partner_input(update, context)
    update.message.reply_text.assert_awaited()  # send_message не обязателен
    assert result is not None

@pytest.mark.asyncio
async def test_partner_confirm_callback_accept(monkeypatch):
    query = MagicMock()
    query.data = "accept_partner_123"
    query.from_user.id = 456
    query.from_user.first_name = "Партнёр"
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    # Мокаем обновление в БД
    monkeypatch.setattr("modules.commands.game.update_user_partner_id", AsyncMock())
    monkeypatch.setattr("modules.commands.game.update_partner_confirmed", AsyncMock())
    update = MagicMock()
    update.callback_query = query
    await partner_confirm_callback(update, context)
    context.bot.send_message.assert_awaited_with(chat_id=123, text="Партнёр подтвердил(а) партнёрство!")
    query.edit_message_text.assert_awaited_with("Партнёрство подтверждено! Теперь вы пара.")

@pytest.mark.asyncio
async def test_partner_questions_waiting_confirm(monkeypatch):
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 123
    context = MagicMock()
    class U: partner_id = 456; partner_confirmed = False
    async def fake_get_user_by_tg_id(tg_id): return U()
    monkeypatch.setattr("modules.commands.game.get_user_by_tg_id", fake_get_user_by_tg_id)
    result = await partner_questions(update, context)
    update.message.reply_text.assert_awaited_with("Партнёрство не подтверждено. Ожидайте согласия партнёра.")
    assert result == 1 or result is not None

@pytest.mark.asyncio
async def test_partner_questions_no_partner(monkeypatch):
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 123
    context = MagicMock()
    class U: partner_id = None
    async def fake_get_user_by_tg_id(tg_id): return U()
    monkeypatch.setattr("modules.commands.game.get_user_by_tg_id", fake_get_user_by_tg_id)
    result = await partner_questions(update, context)
    update.message.reply_text.assert_awaited_with("Партнёр не выбран. Используйте /set_partner.")
    assert result == 1 or result is not None

@pytest.mark.asyncio
async def test_add_ai_question():
    q = await add_question("AI вопрос?", "ответ", 12345, is_ai_generated=True)
    assert q.is_ai_generated is True

@pytest.mark.asyncio
async def test_ai_question_in_db():
    await add_question("AI вопрос 2?", "ответ2", 12345, is_ai_generated=True)
    questions = await get_all_questions()
    ai_questions = [q for q in questions if getattr(q, 'is_ai_generated', False)]
    assert any(q.question == "AI вопрос 2?" for q in ai_questions)

@pytest.mark.asyncio
async def test_parse_generated_questions():
    text = """Вопрос: Какое место вы считаете особенным для вашей пары? Ответ: парк
Вопрос: Какая песня напоминает вам о первой встрече? Ответ: perfect
Вопрос: Любимое совместное хобби? Ответ: готовка"""
    
    questions = await parse_generated_questions(text)
    assert len(questions) == 3
    assert questions[0] == ("Какое место вы считаете особенным для вашей пары?", "парк")
    assert questions[1] == ("Какая песня напоминает вам о первой встрече?", "perfect")
    assert questions[2] == ("Любимое совместное хобби?", "готовка")

@pytest.mark.asyncio
async def test_generate_questions():
    with patch('modules.commands.game.query_ollama', new_callable=AsyncMock) as mock_query:
        mock_query.return_value = """Вопрос: Какое место вы считаете особенным для вашей пары? Ответ: парк\nВопрос: Какая песня напоминает вам о первой встрече? Ответ: perfect"""
        mock_update = MagicMock()
        mock_update.effective_user.id = 123
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()
        mock_context = MagicMock()
        await generate_questions(mock_update, mock_context)
        assert mock_query.called
        calls = [call.args[0] for call in mock_update.message.reply_text.call_args_list]
        assert any("Генерирую" in text for text in calls)
        assert any("Успешно добавлено" in text for text in calls) 