class MemoryModule:
    def __init__(self, db):
        self.db = db

    async def add_memory(self, update, context):
        if context.args:
            text = " ".join(context.args)
            # Ожидаем, что пользователь может ввести: текст; #теги; эмоция
            # Пример: "Сегодня был отличный день! #отдых, #лето радость"
            tags = None
            emotion = None
            if ';' in text:
                parts = text.split(';')
                content = parts[0].strip()
                if len(parts) > 1:
                    tags = parts[1].replace('#', '').strip()
                if len(parts) > 2:
                    emotion = parts[2].strip()
            else:
                content = text
            self.db.add_memory(type="text", content=content, tags=tags, emotion=emotion)
            await update.message.reply_text("Воспоминание сохранено!" + (f"\nТеги: {tags}" if tags else "") + (f"\nЭмоция: {emotion}" if emotion else ""))
        else:
            await update.message.reply_text("Пожалуйста, отправьте текст, фото или видео для добавления воспоминания.\n\nМожно добавить теги и эмоцию через точку с запятой: \nПример: Сегодня был отличный день!; #отдых, #лето; радость")

    async def add_photo_memory(self, update, context):
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            caption = update.message.caption or "Фото-воспоминание"
            tags = None
            emotion = None
            if caption and ';' in caption:
                parts = caption.split(';')
                description = parts[0].strip()
                if len(parts) > 1:
                    tags = parts[1].replace('#', '').strip()
                if len(parts) > 2:
                    emotion = parts[2].strip()
            else:
                description = caption
            self.db.add_memory(type="photo", content="", file_id=file_id, description=description, tags=tags, emotion=emotion)
            await update.message.reply_text("Фото-воспоминание сохранено!" + (f"\nТеги: {tags}" if tags else "") + (f"\nЭмоция: {emotion}" if emotion else ""))
        else:
            await update.message.reply_text("Пожалуйста, отправьте фото для сохранения в архив воспоминаний.\n\nМожно добавить теги и эмоцию через точку с запятой в подписи к фото.")

    async def add_video_memory(self, update, context):
        if update.message.video:
            file_id = update.message.video.file_id
            caption = update.message.caption or "Видео-воспоминание"
            tags = None
            emotion = None
            if caption and ';' in caption:
                parts = caption.split(';')
                description = parts[0].strip()
                if len(parts) > 1:
                    tags = parts[1].replace('#', '').strip()
                if len(parts) > 2:
                    emotion = parts[2].strip()
            else:
                description = caption
            self.db.add_memory(type="video", content="", file_id=file_id, description=description, tags=tags, emotion=emotion)
            await update.message.reply_text("Видео-воспоминание сохранено!" + (f"\nТеги: {tags}" if tags else "") + (f"\nЭмоция: {emotion}" if emotion else ""))
        else:
            await update.message.reply_text("Пожалуйста, отправьте видео для сохранения в архив воспоминаний.\n\nМожно добавить теги и эмоцию через точку с запятой в подписи к видео.")

    async def add_voice_memory(self, update, context):
        if update.message.voice:
            file_id = update.message.voice.file_id
            # Для голосовых — только эмоция через caption
            emotion = update.message.caption.strip() if update.message.caption else None
            self.db.add_memory(type="voice", content="", file_id=file_id, description="Голосовое воспоминание", emotion=emotion)
            await update.message.reply_text("Голосовое воспоминание сохранено!" + (f"\nЭмоция: {emotion}" if emotion else ""))
        else:
            await update.message.reply_text("Пожалуйста, отправьте голосовое сообщение для сохранения в архив воспоминаний.\n\nМожно добавить эмоцию в подписи к голосовому.")

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