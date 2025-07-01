import random
from utils.ollama_api import query_ollama
from utils.bot_utils import send_message_with_image
from utils.ollama_mode import get_ollama_mode
# from utils.hf_image_client import generate_image

class DateModule:
    def __init__(self, db):
        self.db = db
        self.ideas = {
            "🏠 Домашние": [
                "Кулинарный поединок",
                "Домашний кинотеатр с попкорном",
                "Танцы под любимые песни",
                "Фотосессия дома",
            ],
            "🌆 Городские": [
                "Прогулка по новому району",
                "Пикник в парке",
                "Посещение музея/выставки",
                "Кафе с необычной атмосферой",
            ],
            "🎯 Активные": [
                "Боулинг или бильярд",
                "Квест или эскейп-рум",
                "Катание на велосипедах",
                "Мини-гольф",
            ],
            "💫 Особенные": [
                "Наблюдение за звездами",
                "Рассвет или закат вместе",
                "Спонтанная поездка в соседний город",
            ],
        }

    async def send_important_date_reminder(self, update, context):
        # TODO: Реализовать напоминание о важной дате
        await update.message.reply_text("Напоминание о важной дате скоро будет!")

    async def send_date_idea(self, update, context):
        # Генерация идеи через LLM
        if context:
            mode, submode = get_ollama_mode(context)
        else:
            mode, submode = "general", "standard"
        prompt = f"Предложи уникальную идею для романтического свидания для пары. Кратко и по-русски.\nРежим: {mode}\nПодрежим: {submode}"
        result = await query_ollama(prompt)
        
        text_to_send = ""
        if result:
            text_to_send = f"💡 Идея для свидания: {result}"
        else:
            # Fallback на локальный список
            category = random.choice(list(self.ideas.keys()))
            idea = random.choice(self.ideas[category])
            text_to_send = f"{category} идея для свидания:\n{idea}"

        await send_message_with_image(
            update=update,
            context=context,
            text=text_to_send,
            image_prompt=f"romantic date idea: {result if result else idea}"
        ) 