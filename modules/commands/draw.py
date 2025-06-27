from telegram import Update
from telegram.ext import ContextTypes
from utils.sd_pipeline import generate_image_local, generate_image_sd3_local, DEVICE
from io import BytesIO
import asyncio

async def draw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    prompt = ' '.join(arg for arg in args if arg.lower() not in ('sd3', '3'))
    use_sd3 = any(arg.lower() in ('sd3', '3') for arg in args)
    if not prompt:
        await update.message.reply_text("Пожалуйста, укажите описание картинки после /draw [sd3|3] <промпт>.")
        return
    if use_sd3:
        await update.message.reply_text(f"Генерирую изображение через SD3 по запросу: {prompt}\n(Это может занять до 2-3 минут и требует много VRAM)")
        loop = asyncio.get_event_loop()
        image = await loop.run_in_executor(None, generate_image_sd3_local, prompt)
    else:
        await update.message.reply_text(f"Генерирую изображение через SD1.5 по запросу: {prompt}\n(Это может занять до 1 минуты)")
        loop = asyncio.get_event_loop()
        image = await loop.run_in_executor(None, generate_image_local, prompt)
    if image is None:
        await update.message.reply_text("Ошибка генерации изображения. Проверьте логи или попробуйте другой промпт/модель.")
        return
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    await update.message.reply_photo(photo=buffer, caption=f"🎨 Сгенерировано по запросу: {prompt}")
    if DEVICE == "cpu":
        await update.message.reply_text("Внимание: генерация на CPU очень медленная. Для ускорения используйте GPU.") 