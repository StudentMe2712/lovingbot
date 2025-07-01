import asyncio
from telegram import Update
from telegram.ext import CallbackContext
from utils.sd_pipeline import generate_postcard
from utils.logger import setup_logger
from config import HF_API_KEY  # Импортируем ключ API

# Устанавливаем реальный ключ в модуль sd_pipeline
from utils import sd_pipeline
sd_pipeline.HF_API_KEY = HF_API_KEY

logger = setup_logger(__name__)

async def send_message_with_image(
    update: Update,
    context: CallbackContext,
    text: str,
    image_prompt: str = None
):
    """
    Отправляет текстовое сообщение, затем генерирует и отправляет изображение.
    
    :param update: Объект Update от Telegram.
    :param context: Объект CallbackContext от Telegram.
    :param text: Текст для основного сообщения.
    :param image_prompt: Текст для генерации изображения. Если None, используется основной текст.
    """
    # 1. Отправляем текстовое сообщение
    if update.message:
        message = await update.message.reply_text(text, parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.answer()
        message = await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML")
    else:
        logger.warning("send_message_with_image был вызван без message или callback_query")
        return

    # 2. Генерируем и отправляем изображение
    final_image_prompt = image_prompt if image_prompt else text
    
    # Дополнительный промпт для улучшения качества
    enhanced_prompt = f"romantic, cute, {final_image_prompt}, cinematic light, ultra-detailed, 8k"

    try:
        # Показываем пользователю, что генерация началась
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
        
        # Асинхронно генерируем изображение
        image_bytes = await asyncio.to_thread(generate_postcard, enhanced_prompt)

        if image_bytes:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=image_bytes
            )
    except Exception as e:
        logger.error(f"Ошибка при генерации или отправке изображения по промпту '{enhanced_prompt}': {e}")
        # Опционально: можно отправить сообщение об ошибке пользователю
        # await context.bot.send_message(
        #     chat_id=update.effective_chat.id,
        #     text="К сожалению, не удалось создать открытку. Попробуйте позже."
        # ) 