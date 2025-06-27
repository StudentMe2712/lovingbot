import random
from config import PERSONALIZATION
from utils.user_management import Data
from utils.groqapi_client import generate_text
# from utils.hf_image_client import generate_image

class GreetingModule:
    def __init__(self, db):
        self.db = db
        self.data = Data()
        self.questions = {
            "Воспоминания": [
                "Какой момент из вашего прошлого месяца вам больше всего запомнился?",
            ],
            "Мечты": [
                "Если бы у вас была машина времени на один день, когда бы вы хотели побывать вместе?",
            ],
            "Предпочтения": [
                "Идеальный вечер для вас двоих - это...?",
            ],
            "Забавные": [
                "Если бы Камилла была супергероем, какая у неё была бы суперсила?",
            ],
            "Романтичные": [
                "Что в Даулете покорило тебя с первого взгляда, Камилла?",
            ],
            "Планы": [
                "Куда бы вы хотели поехать вместе этим летом?",
            ],
        }
        self.compliments = [
            "Вы — вдохновение друг для друга! 💖",
            "Ваша пара — пример настоящей любви! 💑",
            "Каждый день с вами — праздник! 🎉",
            "Вы делаете этот мир теплее! ☀️",
            "Ваша забота друг о друге — невероятна! 🌸",
            "Вы — команда мечты! ✨",
        ]

    async def send_morning_greeting(self, update=None, context=None):
        chat_id = None
        if update and update.effective_chat:
            chat_id = update.effective_chat.id
        elif context and hasattr(context, 'job') and hasattr(context.job, 'chat_id'):
            chat_id = context.job.chat_id
        else:
            # fallback: используем id группы из настроек, если потребуется
            chat_id = -1002123456789  # заменить на реальный id группы

        text = (
            f"🌅 Доброе утро, {PERSONALIZATION['names'][0]} и {PERSONALIZATION['names'][1]}! "
            "Пусть этот день подарит вам столько же тепла, сколько вы дарите друг другу 💕"
        )
        if context and hasattr(context, 'bot'):
            await context.bot.send_message(chat_id=chat_id, text=text)

    async def send_daily_question(self, update=None, context=None):
        chat_id = None
        if update and update.effective_chat:
            chat_id = update.effective_chat.id
        elif context and hasattr(context, 'job') and hasattr(context.job, 'chat_id'):
            chat_id = context.job.chat_id
        else:
            chat_id = -1002123456789  # заменить на реальный id группы
        prompt = "Придумай интересный вопрос для пары, чтобы они лучше узнали друг друга. Кратко и по-русски."
        result = await generate_text(prompt, max_tokens=60)
        if result:
            text = f"❓ Вопрос дня: {result}"
            # Сначала отправляем текст
            if context and hasattr(context, 'bot'):
                await context.bot.send_message(chat_id=chat_id, text=text)
            elif update and update.message:
                await update.message.reply_text(text)
            # Затем асинхронно отправляем картинку (если получится)
            try:
                # image_bytes = await generate_image(result)
                if image_bytes:
                    if context and hasattr(context, 'bot'):
                        await context.bot.send_photo(chat_id=chat_id, photo=image_bytes, caption="Сгенерировано по вопросу дня!")
                    elif update and update.message:
                        await update.message.reply_photo(image_bytes, caption="Сгенерировано по вопросу дня!")
            except Exception:
                pass  # fallback: не отправлять картинку при ошибке
        else:
            question = self.data.get_common_question()
            text = f"❓ Вопрос дня: {question}"
            if context and hasattr(context, 'bot'):
                await context.bot.send_message(chat_id=chat_id, text=text)
            elif update and update.message:
                await update.message.reply_text(text)
        self.data.increment_common_question_index()

    async def ask_mood(self, update, context):
        prompt = "Придумай короткий позитивный совет или пожелание для пары на день. Кратко и по-русски."
        result = await generate_text(prompt, max_tokens=40)
        keyboard = [[str(i) for i in range(1, 11)]]
        text = "Оцените ваше настроение от 1 до 10 сегодня 😊"
        if result:
            text += f"\n{result}"
            await update.message.reply_text(text)
            try:
                # image_bytes = await generate_image(result)
                if image_bytes:
                    await update.message.reply_photo(image_bytes, caption="Сгенерировано по вашему настроению!")
            except Exception:
                pass
        else:
            await update.message.reply_text(text)

    async def save_mood(self, update, context):
        try:
            mood = int(update.message.text)
        except Exception:
            await update.message.reply_text("Пожалуйста, введите число от 1 до 10.")
            return
        user_id = update.effective_user.id
        from datetime import datetime
        self.db.add_mood(user_id, mood, datetime.now().isoformat())
        await update.message.reply_text(f"Ваше настроение ({mood}) сохранено!")

    async def send_compliment(self, update, context):
        prompt = "Придумай красивый комплимент для пары. Кратко и по-русски."
        result = await generate_text(prompt, max_tokens=40)
        if result:
            await update.message.reply_text(result)
            try:
                # image_bytes = await generate_image(result)
                if image_bytes:
                    await update.message.reply_photo(image_bytes, caption="Сгенерировано по комплименту!")
            except Exception:
                pass
            return
        compliment = random.choice(self.compliments)
        await update.message.reply_text(compliment) 