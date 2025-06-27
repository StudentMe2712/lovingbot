from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from modules.games import GameModule
from database.db_manager import DatabaseManager
from utils.user_management import Data, UserStatus
from utils.logger import setup_logger
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from utils.db_async import add_question, get_random_question_for_user, increment_user_score, get_top_users, get_random_compliment, update_user_partner_id, get_user_by_tg_id, update_partner_confirmed
from modules.commands.start import send_welcome
from unittest.mock import MagicMock
import random

logger = setup_logger("game_command")
data_instance = Data()
db = DatabaseManager()
game_module = GameModule(db)

CHOOSE_ACTION, ADD_QUESTION, ADD_ANSWER, WAIT_ANSWER, WAIT_NEXT_ACTION, CHOOSE_DELETE_CONFIRM, MYQUESTIONS, DELETE_QUESTION, FIND_QUESTION, ADD_VOICE_QUESTION, ADD_MEDIA_QUESTION, ADD_MEDIA_ANSWER = range(12)
MYQUESTIONS_PAGE_SIZE = 10

HINTS = [
    "Подумайте о любимых моментах вместе!",
    "Вспомните, что любит ваш партнёр — это может быть ответом!",
    "Не бойтесь ошибаться — главное, что вы вместе!",
    "Попробуйте задать вопрос о совместных планах или мечтах.",
    "Иногда ответ проще, чем кажется!"
]

PARTNER_TG_ID = 123456789  # TODO: заменить на реальный tg_id партнёра или сделать выбор

SET_PARTNER = 1000

def get_hint():
    return random.choice(HINTS)

def get_game_conv_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("game", game_entry),
            MessageHandler(filters.Regex("^Игра.*$"), game_entry),
            CommandHandler("set_partner", set_partner_command),
        ],
        states={
            CHOOSE_ACTION: [
                MessageHandler(filters.Regex("^Добавить вопрос$"), add_question_start),
                MessageHandler(filters.Regex("^Добавить голосовой вопрос$"), add_voice_question_start),
                MessageHandler(filters.Regex("^Добавить медиа вопрос$"), add_media_question_start),
                MessageHandler(filters.Regex("^Ответить на вопрос$"), ask_question),
                MessageHandler(filters.Regex("^Мои вопросы$"), myquestions_entry),
                MessageHandler(filters.Regex("^Вопросы партнёра$"), partner_questions),
                MessageHandler(filters.Regex("^Статистика пары$"), partner_stats),
                MessageHandler(filters.Regex("^Удалить вопрос$"), delete_question_entry),
                MessageHandler(filters.Regex("^Поиск вопроса$"), find_question_entry),
                MessageHandler(filters.Regex("^В главное меню$"), go_main_menu),
            ],
            ADD_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_question_input)],
            ADD_VOICE_QUESTION: [MessageHandler(filters.VOICE, add_voice_question_input)],
            ADD_MEDIA_QUESTION: [MessageHandler(filters.PHOTO | filters.VIDEO, add_media_question_input)],
            ADD_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_answer_input)],
            WAIT_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)],
            WAIT_NEXT_ACTION: [
                MessageHandler(filters.Regex("^Следующий вопрос$"), ask_question),
                MessageHandler(filters.Regex("^Выйти$"), exit_game),
                MessageHandler(filters.Regex("^В главное меню$"), go_main_menu),
            ],
            MYQUESTIONS: [
                MessageHandler(filters.Regex("^Далее$"), myquestions_next),
                MessageHandler(filters.Regex("^Назад$"), myquestions_prev),
                MessageHandler(filters.Regex("^В меню$"), myquestions_menu),
                CallbackQueryHandler(myquestions_inline_delete, pattern=r"^delete_myq_\d+$"),
            ],
            DELETE_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_question_process)],
            CHOOSE_DELETE_CONFIRM: [MessageHandler(filters.Regex("^(Да|Нет)$"), delete_confirm)],
            FIND_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, find_question_process),
                CallbackQueryHandler(find_inline_delete, pattern=r"^delete_searchq_\d+_.+")
            ],
            SET_PARTNER: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_partner_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel_game)],
        allow_reentry=True
    )

async def game_entry(update: Update, context):
    user_id = update.effective_user.id
    user_questions = db.conn.execute("SELECT COUNT(*) FROM quiz_questions WHERE created_by = ?", (user_id,)).fetchone()[0]
    if user_questions < 3:
        await update.message.reply_text("У вас мало своих вопросов! Добавьте новый, чтобы сделать игру интереснее.")
    keyboard = [
        ["Добавить вопрос", "Добавить голосовой вопрос", "Добавить медиа вопрос"],
        ["Ответить на вопрос"],
        ["Мои вопросы", "Вопросы партнёра", "Статистика пары"],
        ["Удалить вопрос", "Поиск вопроса"],
        ["В главное меню"]
    ]
    await update.message.reply_text("Выберите действие:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CHOOSE_ACTION

async def add_question_start(update: Update, context):
    examples = [
        "Любимый цвет?",
        "Где вы познакомились?",
        "Любимое блюдо?",
        "Самое яркое воспоминание?",
        "Кто раньше встаёт по утрам?"
    ]
    text = "Введите текст нового вопроса для викторины.\n\nПримеры вопросов:\n" + '\n'.join(f"- {ex}" for ex in examples)
    await update.message.reply_text(text)
    return ADD_QUESTION

async def add_question_input(update: Update, context):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("Вопрос не может быть пустым. Введите текст вопроса:")
        return ADD_QUESTION
    context.user_data['temp_question'] = text
    await update.message.reply_text("Введите правильный ответ:")
    return ADD_ANSWER

async def add_voice_question_start(update: Update, context):
    await update.message.reply_text("Отправьте голосовое сообщение с вопросом:")
    return ADD_VOICE_QUESTION

async def add_voice_question_input(update: Update, context):
    user_id = update.effective_user.id
    if not update.message.voice:
        await update.message.reply_text("Пожалуйста, отправьте голосовое сообщение.")
        return ADD_VOICE_QUESTION
    file_id = update.message.voice.file_id
    context.user_data['temp_file_id'] = file_id
    context.user_data['temp_media_type'] = 'voice'
    await update.message.reply_text("Введите правильный ответ на голосовой вопрос:")
    return ADD_ANSWER

async def add_media_question_start(update: Update, context):
    await update.message.reply_text("Отправьте фото или видео с вопросом:")
    return ADD_MEDIA_QUESTION

async def add_media_question_input(update: Update, context):
    user_id = update.effective_user.id
    file_id = None
    media_type = None
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        media_type = 'photo'
    elif update.message.video:
        file_id = update.message.video.file_id
        media_type = 'video'
    else:
        await update.message.reply_text("Пожалуйста, отправьте фото или видео.")
        return ADD_MEDIA_QUESTION
    context.user_data['temp_file_id'] = file_id
    context.user_data['temp_media_type'] = media_type
    await update.message.reply_text("Введите правильный ответ на медиа вопрос:")
    return ADD_ANSWER

async def add_answer_input(update: Update, context):
    user_id = update.effective_user.id
    question = context.user_data.pop('temp_question', None)
    answer = update.message.text.strip().lower()
    file_id = context.user_data.pop('temp_file_id', None)
    media_type = context.user_data.pop('temp_media_type', None)
    if not answer:
        await update.message.reply_text("Ответ не может быть пустым. Введите правильный ответ:")
        if file_id and media_type:
            context.user_data['temp_file_id'] = file_id
            context.user_data['temp_media_type'] = media_type
        else:
            context.user_data['temp_question'] = question
        return ADD_ANSWER
    if not question and not file_id:
        await update.message.reply_text("Ошибка: вопрос не был сохранён. Попробуйте снова.")
        return await game_entry(update, context)
    try:
        if file_id and media_type:
            await add_question("", answer, user_id, media_type=media_type, file_id=file_id)
            await update.message.reply_text("Медиа-вопрос успешно добавлен! Можете добавить ещё или ответить на чужой.")
        else:
            await add_question(question, answer, user_id)
            await update.message.reply_text("Вопрос успешно добавлен! Можете добавить ещё или ответить на чужой.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при добавлении вопроса: {e}")
    return await game_entry(update, context)

async def ask_question(update: Update, context):
    user_id = update.effective_user.id
    q = await get_random_question_for_user(user_id)
    if not q:
        await update.message.reply_text("Нет доступных вопросов. Добавьте свой!")
        return CHOOSE_ACTION
    context.user_data['current_q'] = q.question
    context.user_data['current_a'] = q.answer
    if hasattr(q, 'media_type') and q.media_type and q.media_type != 'text':
        if q.media_type == 'voice':
            await update.message.reply_voice(q.file_id)
        elif q.media_type == 'photo':
            await update.message.reply_photo(q.file_id)
        elif q.media_type == 'video':
            await update.message.reply_video(q.file_id)
        await update.message.reply_text("Ответьте на медиа-вопрос:")
    else:
        await update.message.reply_text(f"Вопрос: {q.question}")
    return WAIT_ANSWER

async def check_answer(update: Update, context):
    user_id = update.effective_user.id
    answer = update.message.text.strip().lower()
    correct = context.user_data.get('current_a', '').lower()
    if answer == correct:
        await increment_user_score(user_id)
        compliment = get_random_compliment()
        await update.message.reply_text(f"Правильно! {compliment} +1 балл 🏆")
        context.user_data['wrong_count'] = 0
    else:
        await update.message.reply_text(f"Неправильно! Правильный ответ: {correct}")
        context.user_data['wrong_count'] = context.user_data.get('wrong_count', 0) + 1
        if context.user_data['wrong_count'] >= 3:
            hint = get_hint()
            await update.message.reply_text(f"Подсказка: {hint}")
            context.user_data['wrong_count'] = 0
    # Подсказка: если у пользователя мало вопросов — предложить добавить
    user_questions = db.conn.execute("SELECT COUNT(*) FROM quiz_questions WHERE created_by = ?", (user_id,)).fetchone()[0]
    if user_questions < 3:
        await update.message.reply_text("У вас мало своих вопросов! Добавьте новый, чтобы сделать игру интереснее.")
    keyboard = [["Следующий вопрос"], ["Выйти"]]
    await update.message.reply_text("Что дальше?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return WAIT_NEXT_ACTION

async def exit_game(update: Update, context):
    await update.message.reply_text(
        "Вы вышли из игры. Возвращайтесь, когда захотите!",
        reply_markup=ReplyKeyboardRemove()
    )
    await send_welcome(update)
    return ConversationHandler.END

async def cancel_game(update: Update, context):
    await update.message.reply_text(
        "Вы вышли из игры. Возвращайтесь, когда захотите!",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def game_stats(update: Update, context):
    top = await get_top_users()
    text = "🏆 Топ игроков:\n"
    for i, user in enumerate(top, 1):
        text += f"{i}. {user.name} — {user.score} очков\n"
    await update.message.reply_text(text)

async def myquestions_entry(update: Update, context):
    context.user_data['myquestions_page'] = 0
    return await show_myquestions(update, context)

async def show_myquestions(update: Update, context):
    user_id = update.effective_user.id if hasattr(update, 'effective_user') and update.effective_user else update.callback_query.from_user.id
    page = context.user_data.get('myquestions_page', 0)
    rows = db.conn.execute("SELECT id, question FROM quiz_questions WHERE created_by = ? ORDER BY id", (user_id,)).fetchall()
    if not rows:
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text("У вас нет добавленных вопросов.", reply_markup=ReplyKeyboardMarkup([["В меню"]], resize_keyboard=True))
        else:
            await update.callback_query.edit_message_text("У вас нет добавленных вопросов.")
        return MYQUESTIONS
    start = page * MYQUESTIONS_PAGE_SIZE
    end = start + MYQUESTIONS_PAGE_SIZE
    page_rows = rows[start:end]
    text = f"Ваши вопросы (стр. {page+1}):\n"
    inline_keyboard = []
    for idx, (qid, qtext) in enumerate(page_rows, start + 1):
        text += f"{idx}. {qtext} (id: {qid})\n"
        inline_keyboard.append([InlineKeyboardButton(f"Удалить {idx}", callback_data=f"delete_myq_{qid}")])
    keyboard = []
    if start > 0:
        keyboard.append(["Назад"])
    if end < len(rows):
        keyboard.append(["Далее"])
    keyboard.append(["В меню"])
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        await update.message.reply_text("Для удаления вопроса используйте кнопки ниже:", reply_markup=InlineKeyboardMarkup(inline_keyboard))
    else:
        await update.callback_query.edit_message_text(text)
        await update.callback_query.message.reply_text("Для удаления вопроса используйте кнопки ниже:", reply_markup=InlineKeyboardMarkup(inline_keyboard))
    return MYQUESTIONS

async def myquestions_next(update: Update, context):
    context.user_data['myquestions_page'] = context.user_data.get('myquestions_page', 0) + 1
    return await show_myquestions(update, context)

async def myquestions_prev(update: Update, context):
    context.user_data['myquestions_page'] = max(context.user_data.get('myquestions_page', 0) - 1, 0)
    return await show_myquestions(update, context)

async def myquestions_menu(update: Update, context):
    return await game_entry(update, context)

async def delete_question_entry(update: Update, context):
    await update.message.reply_text("Введите id вопроса для удаления:", reply_markup=ReplyKeyboardMarkup([["В меню"]], resize_keyboard=True))
    return DELETE_QUESTION

async def delete_question_process(update: Update, context):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "В меню":
        return await game_entry(update, context)
    try:
        qid = int(text)
    except Exception:
        await update.message.reply_text("Некорректный id. Попробуйте снова или нажмите 'В меню'.")
        return DELETE_QUESTION
    row = db.conn.execute("SELECT question FROM quiz_questions WHERE id = ? AND created_by = ?", (qid, user_id)).fetchone()
    if not row:
        await update.message.reply_text("Вопрос не найден или не принадлежит вам.")
        return DELETE_QUESTION
    context.user_data['delete_qid'] = qid
    context.user_data['delete_qtext'] = row[0]
    keyboard = [["Да"], ["Нет"]]
    await update.message.reply_text(f"Удалить вопрос: {row[0]}?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CHOOSE_DELETE_CONFIRM

async def delete_confirm(update: Update, context):
    user_id = update.effective_user.id
    answer = update.message.text.strip().lower()
    qid = context.user_data.get('delete_qid')
    qtext = context.user_data.get('delete_qtext')
    try:
        if answer == "да":
            db.conn.execute("DELETE FROM quiz_questions WHERE id = ? AND created_by = ?", (qid, user_id))
            db.conn.commit()
            await update.message.reply_text(f"Вопрос удалён: {qtext}", reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text("Удаление отменено.", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await update.message.reply_text(f"Ошибка при удалении вопроса: {e}")
    context.user_data.pop('delete_qid', None)
    context.user_data.pop('delete_qtext', None)
    return await game_entry(update, context)

async def find_question_entry(update: Update, context):
    await update.message.reply_text("Введите текст для поиска:", reply_markup=ReplyKeyboardMarkup([["В меню"]], resize_keyboard=True))
    return FIND_QUESTION

async def find_question_process(update: Update, context):
    user_id = update.effective_user.id if hasattr(update, 'effective_user') and update.effective_user else update.callback_query.from_user.id
    text = update.message.text.strip() if hasattr(update, 'message') and update.message else update.callback_query.data
    if text == "В меню":
        return await game_entry(update, context)
    search = text
    try:
        rows = db.conn.execute("SELECT id, question FROM quiz_questions WHERE created_by = ? AND question LIKE ? ORDER BY id LIMIT 10", (user_id, f"%{search}%")).fetchall()
    except Exception as e:
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text(f"Ошибка поиска: {e}", reply_markup=ReplyKeyboardMarkup([["В меню"]], resize_keyboard=True))
        else:
            await update.callback_query.edit_message_text(f"Ошибка поиска: {e}")
        return FIND_QUESTION
    if not rows:
        if hasattr(update, 'message') and update.message:
            await update.message.reply_text("Совпадений не найдено.", reply_markup=ReplyKeyboardMarkup([["В меню"]], resize_keyboard=True))
        else:
            await update.callback_query.edit_message_text("Совпадений не найдено.")
        return FIND_QUESTION
    result = f"Результаты поиска по '{search}':\n"
    inline_keyboard = []
    for idx, (qid, qtext) in enumerate(rows, 1):
        result += f"{idx}. {qtext} (id: {qid})\n"
        inline_keyboard.append([InlineKeyboardButton(f"Удалить {idx}", callback_data=f"delete_searchq_{qid}_{search}")])
    if hasattr(update, 'message') and update.message:
        await update.message.reply_text(result, reply_markup=InlineKeyboardMarkup(inline_keyboard))
    else:
        await update.callback_query.edit_message_text(result)
        await update.callback_query.message.reply_text("Для удаления вопроса используйте кнопки ниже:", reply_markup=InlineKeyboardMarkup(inline_keyboard))
    return FIND_QUESTION

async def find_inline_delete(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data.startswith("delete_searchq_"):
        parts = data.split("_", 3)
        qid = int(parts[2])
        search = parts[3]
        row = db.conn.execute("SELECT question FROM quiz_questions WHERE id = ? AND created_by = ?", (qid, user_id)).fetchone()
        if not row:
            await query.answer("Вопрос не найден или не принадлежит вам.", show_alert=True)
            return
        db.conn.execute("DELETE FROM quiz_questions WHERE id = ? AND created_by = ?", (qid, user_id))
        db.conn.commit()
        await query.answer("Вопрос удалён.", show_alert=True)
        # Обновить результаты поиска
        class DummyMessage:
            def __init__(self, query, search):
                self.text = search
                self.reply_text = query.message.reply_text
        dummy_update = MagicMock()
        dummy_update.effective_user = query.from_user
        dummy_update.message = DummyMessage(query, search)
        await find_question_process(dummy_update, context)

async def go_main_menu(update: Update, context):
    await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=ReplyKeyboardRemove())
    await send_welcome(update)
    return ConversationHandler.END

async def myquestions_inline_delete(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data.startswith("delete_myq_"):
        qid = int(data.split("_")[-1])
        row = db.conn.execute("SELECT question FROM quiz_questions WHERE id = ? AND created_by = ?", (qid, user_id)).fetchone()
        if not row:
            await query.answer("Вопрос не найден или не принадлежит вам.", show_alert=True)
            return
        db.conn.execute("DELETE FROM quiz_questions WHERE id = ? AND created_by = ?", (qid, user_id))
        db.conn.commit()
        await query.answer("Вопрос удалён.", show_alert=True)
        # Обновить список
        context.user_data['myquestions_page'] = context.user_data.get('myquestions_page', 0)
        await show_myquestions(update, context)

async def set_partner_command(update, context):
    await update.message.reply_text("Введите Telegram ID партнёра:")
    return SET_PARTNER

async def set_partner_input(update, context):
    user_id = update.effective_user.id
    try:
        partner_id = int(update.message.text.strip())
        if partner_id == user_id:
            await update.message.reply_text("Нельзя выбрать себя партнёром!")
            return ConversationHandler.END
        partner = await get_user_by_tg_id(partner_id)
        if not partner:
            await update.message.reply_text("Пользователь с таким ID не найден. Попросите партнёра зарегистрироваться.")
            return ConversationHandler.END
        await update_user_partner_id(user_id, partner_id)
        await update.message.reply_text("Партнёр успешно сохранён!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")
    return ConversationHandler.END

async def partner_questions(update: Update, context):
    user_id = update.effective_user.id
    user = await get_user_by_tg_id(user_id)
    partner_id = getattr(user, 'partner_id', None)
    if not partner_id:
        await update.message.reply_text("Партнёр не выбран. Используйте /set_partner.")
        return CHOOSE_ACTION
    if not getattr(user, 'partner_confirmed', False):
        await update.message.reply_text("Партнёрство не подтверждено. Ожидайте согласия партнёра.")
        return CHOOSE_ACTION
    rows = db.conn.execute("SELECT id, question FROM quiz_questions WHERE created_by = ? ORDER BY id", (partner_id,)).fetchall()
    if not rows:
        await update.message.reply_text("У партнёра нет добавленных вопросов.")
        return CHOOSE_ACTION
    text = "Вопросы партнёра:\n"
    for idx, (qid, qtext) in enumerate(rows, 1):
        text += f"{idx}. {qtext} (id: {qid})\n"
    await update.message.reply_text(text)
    return CHOOSE_ACTION

async def partner_stats(update: Update, context):
    user_id = update.effective_user.id
    user = await get_user_by_tg_id(user_id)
    partner_id = getattr(user, 'partner_id', None)
    if not partner_id:
        await update.message.reply_text("Партнёр не выбран. Используйте /set_partner.")
        return CHOOSE_ACTION
    if not getattr(user, 'partner_confirmed', False):
        await update.message.reply_text("Партнёрство не подтверждено. Ожидайте согласия партнёра.")
        return CHOOSE_ACTION
    partner = await get_user_by_tg_id(partner_id)
    user_q = db.conn.execute("SELECT COUNT(*) FROM quiz_questions WHERE created_by = ?", (user_id,)).fetchone()[0]
    partner_q = db.conn.execute("SELECT COUNT(*) FROM quiz_questions WHERE created_by = ?", (partner_id,)).fetchone()[0]
    text = f"Статистика пары:\n"
    text += f"{user.name}: {user.score} очков, {user_q} вопросов\n"
    text += f"Партнёр: {partner.name}: {partner.score} очков, {partner_q} вопросов\n"
    text += f"Суммарно: {user.score + partner.score} очков, {user_q + partner_q} вопросов\n"
    await update.message.reply_text(text)
    return CHOOSE_ACTION

# EXTRA_COMMANDS теперь:
EXTRA_COMMANDS = [
    CommandHandler("game", game_entry),
    CommandHandler("game_stats", game_stats),
]

# Экспорт для тестов и других модулей
__all__ = [
    # ... другие функции ...
    "partner_confirm_callback",
]

async def partner_confirm_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    if data.startswith("accept_partner_"):
        partner_id = int(data.split("_")[-1])
        await update_user_partner_id(user_id, partner_id)
        await update_partner_confirmed(user_id, True)
        await update_partner_confirmed(partner_id, True)
        await context.bot.send_message(chat_id=partner_id, text=f"{query.from_user.first_name} подтвердил(а) партнёрство!")
        await query.edit_message_text("Партнёрство подтверждено! Теперь вы пара.")
    elif data.startswith("decline_partner_"):
        partner_id = int(data.split("_")[-1])
        await update_partner_confirmed(user_id, False)
        await update_partner_confirmed(partner_id, False)
        await context.bot.send_message(chat_id=partner_id, text=f"{query.from_user.first_name} отклонил(а) партнёрство.")
        await query.edit_message_text("Партнёрство отклонено.") 