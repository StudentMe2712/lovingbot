import httpx
import json
import logging

log = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"

async def query_ollama(prompt: str, model: str = "phi", system_message: str = None) -> str:
    """
    Отправляет текстовый запрос в Ollama API и возвращает ответ.
    Использует /api/generate для простой генерации текста.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "messages": messages
    }

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            if 'response' in result:
                return result['response'].strip()
            elif 'message' in result and 'content' in result['message']:
                return result['message']['content'].strip()
            else:
                log.error(f"Неожиданный формат ответа от Ollama: {result}")
                return "Извините, не удалось получить корректный ответ от ИИ."
    except httpx.RequestError as exc:
        log.error(f"Ошибка запроса к Ollama: {exc}")
        return "Извините, Ollama недоступна или произошла сетевая ошибка."
    except json.JSONDecodeError:
        log.error(f"Ошибка декодирования JSON ответа Ollama: {response.text}")
        return "Извините, Ollama вернула некорректный ответ."
    except Exception as e:
        log.error(f"Неизвестная ошибка при запросе к Ollama: {e}")
        return "Произошла неизвестная ошибка при взаимодействии с ИИ." 