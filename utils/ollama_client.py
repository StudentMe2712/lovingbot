import httpx
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "mistral:latest"
COUPLE_MODEL = "pairs-questions"  # название кастомной модели

async def test_ollama_api_status():
    url = f"{OLLAMA_BASE_URL}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            log.info(f"Ollama API доступен. Статус: {response.status_code}")
            models_info = response.json()
            log.info(f"Доступные модели: {[m['name'] for m in models_info.get('models', [])]}")
            return True
    except httpx.RequestError as exc:
        log.error(f"Ollama API недоступен. Ошибка: {exc}")
        return False
    except Exception as e:
        log.error(f"Неизвестная ошибка при проверке Ollama API: {e}")
        return False

async def query_ollama_generate(prompt: str, model: str = DEFAULT_MODEL, system_message: str = None) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"
    full_prompt = f"{system_message}\n{prompt}" if system_message else prompt
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
    }
    log.info(f"Отправка запроса на генерацию к Ollama (модель: {model})...")
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            if 'response' in result:
                log.info("Ответ от Ollama получен успешно.")
                return result['response'].strip()
            else:
                log.warning(f"Неожиданный формат ответа от /api/generate: {result}")
                return "Извините, не удалось получить корректный ответ от ИИ."
    except httpx.RequestError as exc:
        log.error(f"Ошибка запроса к Ollama (/api/generate): {exc}")
        return "Извините, Ollama недоступна или произошла сетевая ошибка."
    except json.JSONDecodeError:
        log.error(f"Ошибка декодирования JSON ответа Ollama: {response.text}")
        return "Извините, Ollama вернула некорректный ответ."
    except Exception as e:
        log.error(f"Неизвестная ошибка при запросе к Ollama (/api/generate): {e}")
        return "Произошла неизвестная ошибка при взаимодействии с ИИ."

async def query_ollama_chat(user_message: str, model: str = DEFAULT_MODEL, system_message: str = None) -> str:
    url = f"{OLLAMA_BASE_URL}/api/chat"
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": user_message})
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    log.info(f"Отправка запроса к Ollama (модель: {model}, режим чата)...")
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            if 'message' in result and 'content' in result['message']:
                log.info("Ответ от Ollama получен успешно.")
                return result['message']['content'].strip()
            else:
                log.warning(f"Неожиданный формат ответа от /api/chat: {result}")
                return "Извините, не удалось получить корректный ответ от ИИ."
    except httpx.RequestError as exc:
        log.error(f"Ошибка запроса к Ollama (/api/chat): {exc}")
        return "Извините, Ollama недоступна или произошла сетевая ошибка."
    except json.JSONDecodeError:
        log.error(f"Ошибка декодирования JSON ответа Ollama: {response.text}")
        return "Извините, Ollama вернула некорректный ответ."
    except Exception as e:
        log.error(f"Неизвестная ошибка при запросе к Ollama (/api/chat): {e}")
        return "Произошла неизвестная ошибка при взаимодействии с ИИ."

async def generate_ollama_response(
    mode: str = "general",
    category: str = "",
    conversation_history: str = "",
    used_questions: str = "",
    user_name: str = "Даулет",
    partner_name: str = "Камилла",
    seasonal_context: str = ""
) -> str:
    """
    Универсальная генерация ответа Ollama: режим couple — вопросы для пар, режим general — обычный ассистент.
    """
    prompt = (
        f"Категория: {category}\n"
        f"История: {conversation_history}\n"
        f"Использованные вопросы: {used_questions}\n"
        f"Режим: {mode}\n"
        f"Сезон/Событие: {seasonal_context}\n"
        f"Вопрос:"
    )
    try:
        question = await query_ollama_generate(
            prompt,
            model=COUPLE_MODEL,
            system_message=None
        )
        log.info(f"Ответ Ollama ({mode}): {question}")
        return question
    except Exception as e:
        log.error(f"Ошибка генерации ответа Ollama: {e}")
        return "Не удалось сгенерировать ответ."

async def main():
    log.info("Начинаем тестирование Ollama API...")
    if not await test_ollama_api_status():
        log.error("Ollama API не запущен или недоступен. Убедитесь, что Ollama установлена и запущена.")
        return
    log.info("\n--- Тестирование /api/generate ---")
    prompt_gen = "Расскажи мне интересный факт о космосе."
    response_gen = await query_ollama_generate(prompt_gen, model=DEFAULT_MODEL)
    log.info(f"Запрос: {prompt_gen}\nОтвет: {response_gen}")
    prompt_gen_with_system = "Напиши короткий стишок про кота."
    system_gen = "Ты - поэт, пишущий короткие и милые стишки."
    response_gen_with_system = await query_ollama_generate(prompt_gen_with_system, model=DEFAULT_MODEL, system_message=system_gen)
    log.info(f"Запрос (с системным промптом): {prompt_gen_with_system}\nОтвет: {response_gen_with_system}")
    log.info("\n--- Тестирование диалогового режима /api/chat ---")
    user_msg = "Привет, бот! Как тебя зовут?"
    response_chat = await query_ollama_chat(user_msg, model=DEFAULT_MODEL)
    log.info(f"Запрос: {user_msg}\nОтвет: {response_chat}")
    user_msg_with_system = "Дай мне совет по тайм-менеджменту."
    system_chat = "Ты - эксперт по продуктивности и тайм-менеджменту. Давай краткие и действенные советы."
    response_chat_with_system = await query_ollama_chat(user_msg_with_system, model=DEFAULT_MODEL, system_message=system_chat)
    log.info(f"Запрос (с системным промптом): {user_msg_with_system}\nОтвет: {response_chat_with_system}")
    log.info("\nТестирование Ollama API завершено.")

if __name__ == "__main__":
    asyncio.run(main()) 