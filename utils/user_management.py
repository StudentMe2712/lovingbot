import json
import os
from enum import Enum
from datetime import datetime
from utils.db_async import get_user_by_tg_id, create_user

class UserStatus(Enum):
    ALLOWED = 1
    NOT_ALLOWED = 2
    NEED_TO_START = 3

class CommonQuestionCategory(Enum):
    PAST_AND_FUTURE = "past_and_future"
    PERSONAL_GROWTH = "personal_growth"
    DREAMS_AND_AMBITIONS = "dreams_and_ambitions"
    VALUES_AND_EMOTIONAL_INTIMACY = "values_and_emotional_intimacy"
    JUST_FOR_FUN = "just_for_fun"

class Data:
    def __init__(self, data_file=None, template_file=None):
        self.data_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = data_file or os.path.join(self.data_dir, "data.json")
        self.template_file = template_file or os.path.join(self.data_dir, "data_template.json")
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._load_template()

    def _load_template(self):
        if os.path.exists(self.template_file):
            with open(self.template_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"users": {}, "last_command": {}, "user_responses": {}}
        self._save_data(data)
        return data

    def _save_data(self, data):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def store_user(self, user):
        # user: telegram.User
        db_user = await get_user_by_tg_id(user.id)
        if not db_user:
            await create_user(user.id, user.first_name or "")

    async def get_user_status(self, user_id):
        db_user = await get_user_by_tg_id(user_id)
        if db_user:
            return UserStatus.ALLOWED
        # Можно добавить логику NEED_TO_START если нужно
        return UserStatus.NOT_ALLOWED

    def get_common_question(self, questions_file=None):
        """
        Получить случайный вопрос из случайной категории, сохранить индекс для ротации
        """
        import random
        questions_file = questions_file or os.path.join(self.data_dir, "common_questions.json")
        categories = [c.value for c in CommonQuestionCategory]
        category = random.choice(categories)
        self.common_question_category = category
        # Индекс последнего вопроса по категории
        if "common_question_last_index" not in self.data:
            self.data["common_question_last_index"] = {c: 0 for c in categories}
        try:
            with open(questions_file, "r", encoding="utf-8") as f:
                questions = json.load(f)
        except Exception:
            return ""
        idx = self.data["common_question_last_index"].get(category, 0)
        question = questions.get(category, [""])[idx]
        return question

    def increment_common_question_index(self):
        category = getattr(self, "common_question_category", None)
        if not category:
            return
        questions_file = os.path.join(self.data_dir, "common_questions.json")
        try:
            with open(questions_file, "r", encoding="utf-8") as f:
                questions = json.load(f)
        except Exception:
            return
        total = len(questions.get(category, []))
        idx = self.data["common_question_last_index"].get(category, 0)
        idx = (idx + 1) % total if total else 0
        self.data["common_question_last_index"][category] = idx
        self._save_data(self.data) 