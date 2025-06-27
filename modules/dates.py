import random
from utils.groqapi_client import generate_text
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
        prompt = "Предложи уникальную идею для романтического свидания для пары. Кратко и по-русски."
        result = await generate_text(prompt, max_tokens=300)
        if result:
            await update.message.reply_text(f"💡 Идея для свидания: {result}")
            # image_bytes = await generate_image(result)
            return
        # Fallback на локальный список
        category = random.choice(list(self.ideas.keys()))
        idea = random.choice(self.ideas[category])
        text = f"{category} идея для свидания:\n{idea}"
        await update.message.reply_text(text) 