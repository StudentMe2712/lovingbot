import random
from config import PERSONALIZATION
from utils.user_management import Data
from utils.bot_utils import send_message_with_image
from utils.db_async import add_mood, get_user_by_tg_id
from utils.ollama_api import query_ollama
from config import KAMILLA_USER_ID
from database.db_manager import DatabaseManager
from telegram import ReplyKeyboardMarkup
from utils.ollama_mode import get_ollama_mode

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
        # Получаем режим и подрежим
        if context:
            mode, submode = get_ollama_mode(context)
        else:
            mode, submode = "general", "standard"
        prompt = f"Придумай интересный вопрос для пары, чтобы они лучше узнали друг друга. Кратко и по-русски.\nРежим: {mode}\nПодрежим: {submode}"
        result = await query_ollama(prompt)
        text_to_send = ""
        if result:
            text_to_send = f"❓ Вопрос дня: {result}"
        else:
            question = self.data.get_common_question()
            text_to_send = f"❓ Вопрос дня: {question}"
            self.data.increment_common_question_index()
        # Для отправки запланированного сообщения нужен bot, а для команды - update
        if context and hasattr(context, 'bot') and not update:
            class FakeUpdate:
                def __init__(self, bot):
                    self.message = None
                    self.callback_query = None
                    self._bot = bot
                @property
                def effective_chat(self):
                    class Chat:
                        id = chat_id
                    return Chat()
            fake_update = FakeUpdate(context.bot)
            await send_message_with_image(fake_update, context, text_to_send, image_prompt=result)
        elif update:
            await send_message_with_image(update, context, text_to_send, image_prompt=result)

    async def ask_mood(self, update, context):
        if context:
            mode, submode = get_ollama_mode(context)
        else:
            mode, submode = "general", "standard"
        prompt = f"Придумай короткий позитивный совет или пожелание для пары на день. Кратко и по-русски.\nРежим: {mode}\nПодрежим: {submode}"
        result = await query_ollama(prompt)
        text = "Оцените ваше настроение от 1 до 10 сегодня 😊"
        if result:
            text += f"\n{result}"
        await send_message_with_image(update, context, text, image_prompt=result)
        keyboard = [[str(i) for i in range(1, 11)]]
        await update.message.reply_text("Ваша оценка:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))

    async def save_mood(self, update, context):
        try:
            mood = int(update.message.text)
        except Exception:
            await update.message.reply_text("Пожалуйста, введите число от 1 до 10.")
            return
        user_id = update.effective_user.id
        from datetime import datetime
        await add_mood(user_id, mood, datetime.now().isoformat())
        await update.message.reply_text(f"Ваше настроение ({mood}) сохранено!")
        # Уведомление партнёру
        user = await get_user_by_tg_id(user_id)
        partner_id = getattr(user, 'partner_id', None)
        db = DatabaseManager()
        if partner_id and not db.is_partner_blocked(partner_id, user_id):
            try:
                await context.bot.send_message(chat_id=partner_id, text=f"💬 У пользователя {update.effective_user.first_name} сегодня настроение: {mood}/10.")
            except Exception:
                pass
        # AI-комплимент при плохом настроении
        if mood <= 3:
            SYSTEM_PROMPT_COMPLIMENT = "Ты - заботливый и поддерживающий бот для пары. Сгенерируй короткое, ободряющее сообщение, комплимент или фразу поддержки для человека, у которого плохое настроение. Используй теплые слова. Максимум 20 слов."
            compliment_text = await query_ollama(f"Настроение пользователя {update.effective_user.first_name} плохое. Напиши что-то поддерживающее.", system_message=SYSTEM_PROMPT_COMPLIMENT)
            await update.message.reply_text(compliment_text)

    async def send_compliment(self, update, context):
        if context:
            mode, submode = get_ollama_mode(context)
        else:
            mode, submode = "general", "standard"
        prompt = f"Напиши короткий, милый и оригинальный комплимент для любимого человека. По-русски.\nРежим: {mode}\nПодрежим: {submode}"
        result = await query_ollama(prompt)
        text_to_send = result if result else random.choice(self.compliments)
        await send_message_with_image(update, context, text_to_send, image_prompt=text_to_send) 