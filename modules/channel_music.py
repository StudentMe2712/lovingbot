from pyrogram import Client
from config import API_ID, API_HASH

CHANNEL_USERNAME = "AUDIO_KINGDOM"

async def get_last_channel_audios(limit=5):
    async with Client("music_session", api_id=API_ID, api_hash=API_HASH) as app:
        audios = []
        async for msg in app.get_chat_history(CHANNEL_USERNAME, limit=50):
            if msg.audio:
                audios.append(msg.audio.file_id)
                if len(audios) >= limit:
                    break
        return audios

# Функция для PTB handler
async def send_channel_music(update, context):
    audios = await get_last_channel_audios()
    if not audios:
        await update.message.reply_text("Нет аудиофайлов в канале.")
        return
    for audio_id in audios:
        await update.message.reply_audio(audio=audio_id) 