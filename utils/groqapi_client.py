import os
import logging
import aiohttp
from config import GROQ_API_KEY

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def generate_text(prompt: str, max_tokens: int = 100) -> str:
    system_instruction = (
        "Ответь только на русском языке, не используй английских слов, не пиши транслитом. "
        "Формулируй ответ естественно, кратко и понятно для русскоязычной пары."
    )
    full_prompt = f"{prompt}\n\n{system_instruction}"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": full_prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_API_URL, headers=headers, json=payload) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.exception(f"GroqAPI error: {e}")
        return None 