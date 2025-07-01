import pytest
from unittest.mock import patch, AsyncMock
from utils.ollama_client import generate_ollama_response
from utils.ollama_mode import get_ollama_mode, set_ollama_mode, get_mode_button_text

@pytest.mark.asyncio
async def test_generate_ollama_response_couple():
    fake_question = "Даулет, что для тебя означает быть романтичным с Камиллой?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category="романтика", user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert "романтичн" in result_lower or "романтика" in result_lower
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_ollama_response_general_date():
    fake_answer = "Я не имею доступа к реальному времени, но могу помочь с любыми другими вопросами!"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_answer)) as mock_gen:
        result = await generate_ollama_response(mode="general", category="", user_name="Даулет", partner_name="Камилла")
        assert "реального времени" in result or "не имею доступа" in result
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_ollama_response_general_joke():
    fake_answer = "Почему кот не играет в покер? Потому что боится мышеловки!"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_answer)) as mock_gen:
        result = await generate_ollama_response(mode="general", category="", user_name="Даулет", partner_name="Камилла")
        assert "кот" in result.lower() and "покер" in result.lower()
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_ollama_response_general_cooking():
    fake_answer = "Положите яйцо в кипящую воду и варите 8-10 минут. Затем остудите в холодной воде."
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_answer)) as mock_gen:
        result = await generate_ollama_response(mode="general", category="", user_name="Даулет", partner_name="Камилла")
        assert "яйц" in result.lower() and ("варит" in result.lower() or "кипят" in result.lower())
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_couple_question_humor():
    category = "юмор"
    conversation_history = "Даулет, какая самая смешная ситуация у вас была с Камиллой?"
    used_questions = "Даулет, какая самая смешная ситуация у вас была с Камиллой?"
    fake_question = "Камилла, что в Даулете всегда заставляет тебя смеяться?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category=category, user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert "смешн" in result_lower or "юмор" in result_lower or "смея" in result_lower
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_couple_question_memory():
    category = "воспоминания"
    conversation_history = "Камилла, какое воспоминание с Даулетом всегда вызывает улыбку?"
    used_questions = "Камилла, какое воспоминание с Даулетом всегда вызывает улыбку?"
    fake_question = "Даулет, в какой момент с Камиллой ты понял, что это особенные отношения?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category=category, user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert "воспоминан" in result_lower or "запомн" in result_lower or "момент" in result_lower
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_couple_question_life():
    category = "быт"
    conversation_history = "Камилла, что в совместном быту с Даулетом приносит больше всего радости?"
    used_questions = "Камилла, что в совместном быту с Даулетом приносит больше всего радости?"
    fake_question = "Даулет, как вы с Камиллой делите домашние дела?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category=category, user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert "быт" in result_lower or "дом" in result_lower or "уют" in result_lower or "делит" in result_lower
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_couple_question_values():
    category = "ценности"
    conversation_history = "Камилла, какая ценность, которую разделяет Даулет, особенно важна для ваших отношений?"
    used_questions = "Камилла, какая ценность, которую разделяет Даулет, особенно важна для ваших отношений?"
    fake_question = "Даулет, в чём ваши с Камиллой взгляды на жизнь совпадают?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category=category, user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert "ценност" in result_lower or "взгляд" in result_lower or "важн" in result_lower or "убежден" in result_lower or "принцип" in result_lower
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_couple_question_crisis():
    category = "кризисы"
    conversation_history = "Даулет, как Камилла поддерживает тебя, когда сложно с учёбой?"
    used_questions = "Даулет, как Камилла поддерживает тебя, когда сложно с учёбой?"
    fake_question = "Камилла, какой сложный период вы с Даулетом прошли вместе и как это вас изменило?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category=category, user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert (
            "кризис" in result_lower or "трудн" in result_lower or "стресс" in result_lower or "испытан" in result_lower or "поддержк" in result_lower
            or "сложн" in result_lower or "период" in result_lower or "измен" in result_lower
        )
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_couple_question_selfgrowth():
    category = "саморазвитие"
    conversation_history = "Камилла, как отношения с Даулетом помогают тебе расти?"
    used_questions = "Камилла, как отношения с Даулетом помогают тебе расти?"
    fake_question = "Даулет, в чём Камилла вдохновляет тебя развиваться и поддерживает твои цели?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category=category, user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert (
            "развит" in result_lower or "рост" in result_lower or "измен" in result_lower or "цель" in result_lower or "саморазв" in result_lower
            or "развива" in result_lower or "вдохнов" in result_lower or "поддерж" in result_lower
        )
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_couple_question_express():
    category = "экспресс"
    conversation_history = ""
    used_questions = ""
    fake_question = "Даулет, что сегодня в Камилле заставило тебя улыбнуться?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category=category, user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert "сегодня" in result_lower or "быстр" in result_lower or "экспресс" in result_lower or "коротк" in result_lower or "улыбн" in result_lower or "чувств" in result_lower
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_couple_question_seasonal():
    category = "сезонный"
    conversation_history = ""
    used_questions = ""
    fake_question = "Камилла, какое зимнее воспоминание с Даулетом согревает тебя?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category=category, user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert "зим" in result_lower or "новый" in result_lower or "год" in result_lower or "сезон" in result_lower or "воспоминан" in result_lower or "праздн" in result_lower
        mock_gen.assert_awaited_once()

@pytest.mark.asyncio
async def test_generate_couple_question_thematic():
    category = "тематический"
    conversation_history = ""
    used_questions = ""
    fake_question = "Даулет, что за эти 3 месяца с Камиллой стало самым дорогим для тебя?"
    with patch("utils.ollama_client.query_ollama_generate", new=AsyncMock(return_value=fake_question)) as mock_gen:
        result = await generate_ollama_response(mode="couple", category=category, user_name="Даулет", partner_name="Камилла")
        result_lower = result.lower()
        assert "даулет" in result_lower
        assert "камилл" in result_lower
        assert "годовщин" in result_lower or "дата" in result_lower or "месяц" in result_lower or "памятн" in result_lower or "событ" in result_lower or "измен" in result_lower
        mock_gen.assert_awaited_once()

class DummyContext:
    def __init__(self):
        self.user_data = {}

def test_ollama_mode_switch():
    ctx = DummyContext()
    # По умолчанию general
    mode, submode = get_ollama_mode(ctx)
    assert mode == "general"
    assert get_mode_button_text(mode) == "Режим: Ассистент 🤖"
    # Переключаем на couple
    set_ollama_mode(ctx, "couple")
    mode, submode = get_ollama_mode(ctx)
    assert mode == "couple"
    assert get_mode_button_text(mode) == "Режим: Пара 👩‍❤️‍👨"
    # Переключаем обратно
    set_ollama_mode(ctx, "general")
    mode, submode = get_ollama_mode(ctx)
    assert mode == "general"
    assert get_mode_button_text(mode) == "Режим: Ассистент 🤖" 