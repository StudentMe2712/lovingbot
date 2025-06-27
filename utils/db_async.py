import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
from utils.models import Base, User, QuizQuestion
from sqlalchemy import Integer, String, Text, select, func, update
import logging
import random
import sqlalchemy as sa

load_dotenv()
DATABASE_URL = "postgresql+asyncpg://lovebot_owner:npg_DxWA9hIkEmn8@ep-fancy-snow-a8j72m3q-pooler.eastus2.azure.neon.tech/lovebot"
# Удаляем параметры sslmode и channel_binding из строки подключения
# if DATABASE_URL:
#     DATABASE_URL = DATABASE_URL.split("?")[0].replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl.create_default_context()}
)
async_session = async_sessionmaker(engine, expire_on_commit=False)

logger = logging.getLogger("db_async")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user_by_tg_id(tg_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalar_one_or_none()

async def create_user(tg_id: int, name: str):
    async with async_session() as session:
        try:
            user = User(tg_id=tg_id, name=name)
            session.add(user)
            await session.commit()
            logger.info(f"Пользователь создан: tg_id={tg_id}, name={name}")
            return user
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            await session.rollback()
            raise

async def get_all_questions():
    async with async_session() as session:
        result = await session.execute(select(QuizQuestion))
        return result.scalars().all()

async def add_question(question: str, answer: str, created_by: int):
    async with async_session() as session:
        q = QuizQuestion(question=question, answer=answer, created_by=created_by)
        session.add(q)
        await session.commit()
        return q

async def get_random_question():
    async with async_session() as session:
        result = await session.execute(select(QuizQuestion).order_by(func.random()).limit(1))
        return result.scalar_one_or_none()

STATIC_QUIZ_QUESTIONS = [
    {"question": "Любимый цвет Камиллы?", "answer": "синий"},
    {"question": "Где Даулет сделал предложение?", "answer": "париж"},
    {"question": "Любимое блюдо Даулета?", "answer": "плов"},
    {"question": "Кто раньше встаёт по утрам?", "answer": "камилла"},
    {"question": "Родной город Камиллы?", "answer": "семей"},
    {"question": "Родной город Даулета?", "answer": "алматы"},
    {"question": "Дата рождения Камиллы?", "answer": "15 мая"},
    {"question": "Дата рождения Даулета?", "answer": "20 октября"},
    {"question": "Место знакомства Камиллы и Даулета?", "answer": "университет"},
    {"question": "Дата свадьбы Камиллы и Даулета?", "answer": "14 февраля"},
    {"question": "Хобби Камиллы?", "answer": "рисование"},
    {"question": "Хобби Даулета?", "answer": "футбол"},
    {"question": "Любимый фильм Камиллы?", "answer": "интерстеллар"},
    {"question": "Любимый фильм Даулета?", "answer": "начало"},
    {"question": "Мечта Камиллы?", "answer": "путешествия"},
    {"question": "Мечта Даулета?", "answer": "построить дом"},
    {"question": "Любимая книга Камиллы?", "answer": "1984"},
    {"question": "Любимая книга Даулета?", "answer": "алхимик"},
    {"question": "Есть ли у них домашнее животное?", "answer": "нет"},
    {"question": "Их любимый ресторан?", "answer": "азия"},
    {"question": "Любимое время года Камиллы?", "answer": "весна"},
    {"question": "Любимое время года Даулета?", "answer": "лето"},
    {"question": "Любимый цветок Камиллы?", "answer": "роза"},
    {"question": "Любимый напиток Даулета?", "answer": "кофе"},
    {"question": "Где состоялась их первая встреча?", "answer": "кафе"},
    {"question": "Любимая певица Камиллы?", "answer": "димаш"},
    {"question": "Любимый исполнитель Даулета?", "answer": "скриптонит"},
    {"question": "Куда они впервые поехали в путешествие?", "answer": "алматы"},
    {"question": "Любимый вид отдыха Камиллы?", "answer": "чтение книг"},
    {"question": "Любимый вид отдыха Даулета?", "answer": "смотреть фильмы"},
    {"question": "Есть ли у них семейная традиция?", "answer": "да"},
    {"question": "Любимый вид спорта Камиллы?", "answer": "йога"},
    {"question": "Любимый вид спорта Даулета?", "answer": "баскетбол"},
    {"question": "Их планы на будущее?", "answer": "дети"},
    {"question": "Любимый десерт Камиллы?", "answer": "чизкейк"},
    {"question": "Любимый десерт Даулета?", "answer": "тирамису"},
    {"question": "Их первая совместная головоломка?", "answer": "пазл"},
    {"question": "Любимый напиток Камиллы?", "answer": "чай"},
    {"question": "Любимый жанр книг Даулета?", "answer": "фантастика"},
    {"question": "Любимое телешоу Камиллы?", "answer": "друзья"},
    {"question": "Любимая игра Даулета?", "answer": "dota"},
    {"question": "Как они познакомились впервые?", "answer": "через друзей"},
    {"question": "Детская мечта Камиллы?", "answer": "актриса"},
    {"question": "Детская мечта Даулета?", "answer": "космонавт"},
    {"question": "Их самое любимое место дома?", "answer": "гостиная"},
    {"question": "Любимый праздник Камиллы?", "answer": "новый год"},
    {"question": "Любимый праздник Даулета?", "answer": "наурыз"},
    {"question": "Их первая крупная покупка?", "answer": "машина"},
    {"question": "Лучшая подруга Камиллы?", "answer": "аружан"},
    {"question": "Лучший друг Даулета?", "answer": "ерлан"},
    {"question": "Их любимая кофейня?", "answer": "кофемания"},
    {"question": "Любимый стиль одежды Камиллы?", "answer": "классика"},
    {"question": "Любимый стиль одежды Даулета?", "answer": "спорт"},
    {"question": "Имя их первого домашнего животного?", "answer": "нет"},
    {"question": "Их любимая настольная игра?", "answer": "монополия"},
    {"question": "В каком месяце они больше всего любят путешествовать?", "answer": "июль"},
    {"question": "Любимое блюдо Камиллы, которое готовит Даулет?", "answer": "стейк"},
    {"question": "Любимое блюдо Даулета, которое готовит Камилла?", "answer": "лазанья"},
    {"question": "Их любимая марка автомобиля?", "answer": "mercedes"},
    {"question": "Какой город они мечтают посетить вместе?", "answer": "токио"},
    {"question": "Какое время суток они считают лучшим для прогулок?", "answer": "вечер"},
    {"question": "Любимый вид чая Камиллы?", "answer": "зеленый"},
    {"question": "Любимый вид кофе Даулета?", "answer": "латте"},
    {"question": "Какая у них годовщина свадьбы по счету?", "answer": "первая"},
    {"question": "Любимое совместное занятие на выходных?", "answer": "кино"},
    {"question": "Какой вид искусства Камилла предпочитает?", "answer": "импрессионизм"},
    {"question": "Какой вид спорта они смотрят вместе?", "answer": "хоккей"},
    {"question": "Сколько лет Камилле?", "answer": "25"},
    {"question": "Сколько лет Даулету?", "answer": "27"},
    {"question": "Их любимое место для свиданий?", "answer": "парк"},
    {"question": "Какое учебное заведение они закончили?", "answer": "университет"},
    {"question": "Любимая сладость Камиллы?", "answer": "шоколад"},
    {"question": "Любимая сладость Даулета?", "answer": "мороженое"},
    {"question": "Их любимый цвет для интерьера?", "answer": "бежевый"},
    {"question": "Что они чаще всего слушают в машине?", "answer": "подкасты"},
    {"question": "Какой инструмент Камилла хотела бы освоить?", "answer": "гитара"},
    {"question": "Какой вид активности Даулет предпочитает на природе?", "answer": "походы"},
    {"question": "Их любимый вид транспорта?", "answer": "автомобиль"},
    {"question": "Любимое направление музыки у Камиллы?", "answer": "поп"},
    {"question": "Любимое направление музыки у Даулета?", "answer": "рок"},
    {"question": "Какой язык они хотят выучить вместе?", "answer": "английский"},
    {"question": "Что они ценят друг в друге больше всего?", "answer": "поддержка"},
    {"question": "Их любимое совместное хобби?", "answer": "готовить"},
    {"question": "Какой супергерой нравится Камилле?", "answer": "чудо-женщина"},
    {"question": "Какой супергерой нравится Даулету?", "answer": "бэтмен"},
    {"question": "Их любимый вид фастфуда?", "answer": "пицца"},
    {"question": "Что они предпочитают на завтрак?", "answer": "каша"},
    {"question": "Какой предмет мебели они купили первым в свою квартиру?", "answer": "диван"},
    {"question": "Любимый жанр кино Камиллы?", "answer": "драма"},
    {"question": "Любимый жанр кино Даулета?", "answer": "боевик"},
    {"question": "Какое у них любимое число?", "answer": "7"},
    {"question": "Какой вид отдыха на природе они предпочитают?", "answer": "пикник"},
    {"question": "Их любимое приложение на телефоне?", "answer": "instagram"},
    {"question": "Какое животное они хотели бы завести?", "answer": "собака"},
    {"question": "Их любимый праздник, который они отмечают вместе?", "answer": "день рождения"},
    {"question": "Какой предмет Камилла считает самым важным в своем доме?", "answer": "книги"},
    {"question": "Какой предмет Даулет считает самым важным в своем доме?", "answer": "компьютер"},
    {"question": "Их любимое времяпровождение вечером?", "answer": "сериал"},
    {"question": "Какое блюдо они готовят вместе чаще всего?", "answer": "салат"},
    {"question": "Любимый город в Казахстане?", "answer": "алматы"},
    {"question": "Какое природное явление Камилла любит больше всего?", "answer": "снег"},
    {"question": "Какое природное явление Даулет любит больше всего?", "answer": "солнце"},
    {"question": "Их любимое место для шопинга?", "answer": "торговый центр"},
    {"question": "Какой вид спорта они занимаются вместе?", "answer": "велосипед"},
    {"question": "Их любимый цвет для стен?", "answer": "серый"}
]

async def get_random_question_for_user(user_id):
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    rows = db.conn.execute("SELECT question, answer FROM quiz_questions WHERE created_by != ?", (user_id,)).fetchall()
    if rows:
        q = random.choice(rows)
        class Q: pass
        qobj = Q()
        qobj.question = q[0]
        qobj.answer = q[1]
        return qobj
    return None

async def increment_user_score(tg_id: int):
    async with async_session() as session:
        await session.execute(
            sa.update(User).where(User.tg_id == tg_id).values(score=User.score + 1)
        )
        await session.commit()

async def get_top_users(limit=2):
    async with async_session() as session:
        result = await session.execute(
            select(User).order_by(User.score.desc()).limit(limit)
        )
        return result.scalars().all()

COMPLIMENTS = [
    "Ты молодец!",
    "Великолепно!",
    "Ты справился(ась) отлично!",
    "Блестящий ответ!",
    "Ты супер!",
    "Гениально!",
    "Ты умница!",
    "Восхитительно!",
    "Ты сделал(а) мой день!",
    "Ты лучший(ая)!"
]

def get_random_compliment():
    return random.choice(COMPLIMENTS)

async def update_user_partner_id(tg_id: int, partner_id: int | None):
    async with async_session() as session:
        await session.execute(
            sa.update(User).where(User.tg_id == tg_id).values(partner_id=partner_id)
        )
        await session.commit()

async def update_partner_confirmed(tg_id: int, confirmed: bool):
    async with async_session() as session:
        await session.execute(
            sa.update(User).where(User.tg_id == tg_id).values(partner_confirmed=confirmed)
        )
        await session.commit() 