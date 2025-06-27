import random
from utils.db_async import get_random_question_for_user, add_question
from telegram.ext import ConversationHandler
from utils.hf_image_client import generate_image

class GameModule:
    def __init__(self, db=None):
        self.current = {}
        self.db = db

    async def start_game(self, update, context):
        user_id = update.effective_user.id
        q = await get_random_question_for_user(user_id)
        if not q:
            await update.message.reply_text("Нет доступных вопросов в базе, созданных другим пользователем.")
            return
        self.current[user_id] = {"q": q.question, "a": q.answer}
        await update.message.reply_text(q.question)
        # Генерация картинки по вопросу
        image_bytes = await generate_image(q.question)
        if image_bytes:
            await update.message.reply_photo(image_bytes, caption="Сгенерировано по вопросу!")

    async def answer_game(self, update, context):
        user_id = update.effective_user.id
        if user_id not in self.current:
            return  # Просто игнорируем
        answer = update.message.text.strip().lower()
        correct = self.current[user_id]["a"].lower()
        if answer == correct:
            await update.message.reply_text("Правильно! +1 балл 🏆")
        else:
            await update.message.reply_text(f"Неправильно! Правильный ответ: {correct}")
        del self.current[user_id]

    async def add_question_input(self, update, context):
        question_text = update.message.text.strip()
        context.user_data['temp_question'] = question_text
        context.user_data['add_question_state'] = 1
        await update.message.reply_text("Теперь напишите правильный ответ на этот вопрос.")
        return 1

    async def add_answer_input(self, update, context):
        user_id = update.effective_user.id
        question = context.user_data.pop('temp_question', None)
        answer = update.message.text.strip().lower()
        if not question:
            await update.message.reply_text("Произошла ошибка: вопрос не был сохранен. Пожалуйста, начните заново, используя /add_question_start.")
            context.user_data.pop('add_question_state', None)
            return -1
        await add_question(question, answer, user_id)
        await update.message.reply_text("Вопрос успешно добавлен в викторину! Спасибо!")
        context.user_data.pop('add_question_state', None)
        return -1

    async def send_stats(self, update, context):
        avg, count = self.db.get_mood_stats()
        game_stats = self.db.get_game_stats()
        text = "📊 Статистика активности:\n"
        if count:
            text += f"\nСреднее настроение: {avg:.2f} (отметок: {count})"
        else:
            text += "\nНет данных по настроению."
        if game_stats:
            text += "\n\nИгры:"
            for game_type, score in game_stats:
                text += f"\n- {game_type}: {score} очков"
        else:
            text += "\nНет данных по играм."
        await update.message.reply_text(text)

    async def add_question_start(self, update, context):
        await update.message.reply_text("Введите текст нового вопроса для викторины:")
        return 0  # ADD_QUESTION_PROMPT

    async def cancel_add_question(self, update, context):
        context.user_data.pop('temp_question', None)
        context.user_data.pop('add_question_state', None)
        await update.message.reply_text("Добавление вопроса отменено.")
        return ConversationHandler.END 