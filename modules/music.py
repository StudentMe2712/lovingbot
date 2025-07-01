import random
from utils.ollama_api import query_ollama
from utils.ollama_mode import get_ollama_mode
# from utils.groqapi_client import generate_text
import aiohttp

class MusicModule:
    def __init__(self, db):
        self.db = db
        self.tracks = [
            ("Imagine Dragons - Believer", "🔥 Для заряда энергией и хорошего настроения!", "https://youtu.be/7wtfhZwyrcc"),
            ("The Weeknd - Blinding Lights", "✨ Для романтического настроения!", "https://youtu.be/4NRXx6U8ABQ"),
            ("Ed Sheeran - Shape of You", "💃 Для танцев вдвоём!", "https://youtu.be/JGwWNGJdvx8"),
            ("Coldplay - Viva La Vida", "🌅 Для вдохновения!", "https://youtu.be/dvgZkm1xWPE"),
            ("Maroon 5 - Memories", "🎶 Для воспоминаний!", "https://youtu.be/SlPhMPnQ58k"),
        ]

    async def send_music_recommendation(self, update, context):
        if context:
            mode, submode = get_ollama_mode(context)
        else:
            mode, submode = "general", "standard"
        prompt = f"Предложи одну случайную популярную песню (исполнитель - название) и коротко опиши для какого настроения она подходит. Формат: Исполнитель - Название | Описание.\nРежим: {mode}\nПодрежим: {submode}"
        result = await query_ollama(prompt)
        if result:
            await update.message.reply_text(f"🎵 {result}")
            return
        # Fallback на локальный список
        track, mood, link = random.choice(self.tracks)
        text = f"🎵 {track}\n💬 {mood}\n🔗 {link}"
        await update.message.reply_text(text) 

    async def send_deezer_music(self, update, context):
        url = "https://api.deezer.com/chart"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    tracks = data.get("tracks", {}).get("data", [])
                    if not tracks:
                        await update.message.reply_text("Не удалось получить топ-треки Deezer.")
                        return
                    import random
                    track = random.choice(tracks)
                    title = track.get("title")
                    artist = track.get("artist", {}).get("name")
                    link = track.get("link")
                    msg = f"🎵 {title} — {artist}\n🔗 {link}"
                    await update.message.reply_text(msg)
        except Exception as e:
            await update.message.reply_text(f"Ошибка Deezer: {e}") 

async def get_music_recommendation(prompt: str, context=None) -> str:
    """
    Получает музыкальную рекомендацию от Groq API (или Ollama).
    """
    if context:
        mode, submode = get_ollama_mode(context)
    else:
        mode, submode = "general", "standard"
    full_prompt = f"Посоветуй 1 песню по такому запросу: '{prompt}'. В ответе укажи только исполнителя и название песни, без лишних слов.\nРежим: {mode}\nПодрежим: {submode}"
    recommendation = await query_ollama(full_prompt)
    return recommendation 