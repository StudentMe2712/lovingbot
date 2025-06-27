class MemoryModule:
    def __init__(self, db):
        self.db = db

    async def add_memory(self, update, context):
        if context.args:
            text = " ".join(context.args)
            self.db.add_memory(type="text", content=text)
            await update.message.reply_text("Воспоминание сохранено!")
        else:
            await update.message.reply_text("Пожалуйста, отправьте текст, фото или видео для добавления воспоминания.")

    async def add_photo_memory(self, update, context):
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            caption = update.message.caption or "Фото-воспоминание"
            self.db.add_memory(type="photo", content="", file_id=file_id, description=caption)
            await update.message.reply_text("Фото-воспоминание сохранено!")
        else:
            await update.message.reply_text("Пожалуйста, отправьте фото для сохранения в архив воспоминаний.")

    async def add_video_memory(self, update, context):
        if update.message.video:
            file_id = update.message.video.file_id
            caption = update.message.caption or "Видео-воспоминание"
            self.db.add_memory(type="video", content="", file_id=file_id, description=caption)
            await update.message.reply_text("Видео-воспоминание сохранено!")
        else:
            await update.message.reply_text("Пожалуйста, отправьте видео для сохранения в архив воспоминаний.")

    async def add_voice_memory(self, update, context):
        if update.message.voice:
            file_id = update.message.voice.file_id
            self.db.add_memory(type="voice", content="", file_id=file_id, description="Голосовое воспоминание")
            await update.message.reply_text("Голосовое воспоминание сохранено!")
        else:
            await update.message.reply_text("Пожалуйста, отправьте голосовое сообщение для сохранения в архив воспоминаний.")

    async def send_random_memory(self, update, context):
        memory = self.db.get_random_memory()
        if memory:
            _, date, type_, content, file_id, description = memory
            if type_ == "photo" and file_id:
                await update.message.reply_photo(photo=file_id, caption=f"📸 {description or 'Фото-воспоминание'}\n({date})")
            elif type_ == "voice" and file_id:
                await update.message.reply_voice(voice=file_id, caption=f"🎤 {description or 'Голосовое воспоминание'}\n({date})")
            else:
                text = f"📸 Воспоминание от {date}: {description or content}"
                await update.message.reply_text(text)
        else:
            await update.message.reply_text("Пока нет воспоминаний. Добавьте первое!") 