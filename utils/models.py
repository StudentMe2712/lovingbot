from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean, BigInteger, ForeignKey
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(64))
    score: Mapped[int] = mapped_column(Integer, default=0)
    partner_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    partner_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(String(32), default=lambda: datetime.now(timezone.utc).isoformat())

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(Integer)
    media_type: Mapped[str] = mapped_column(String(16), default="text")
    file_id: Mapped[str] = mapped_column(String(128), nullable=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)

class UserMood(Base):
    __tablename__ = "user_mood"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    mood: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[str] = mapped_column(String(32))

class Memory(Base):
    __tablename__ = "memories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(String(128), nullable=True)
    emotion: Mapped[str] = mapped_column(String(16), nullable=True)
    media_type: Mapped[str] = mapped_column(String(16), default="text")
    file_id: Mapped[str] = mapped_column(String(128), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32))

class Reminder(Base):
    __tablename__ = 'reminders'

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(BigInteger, ForeignKey('users.tg_id'))
    text = mapped_column(String, nullable=False)
    remind_at = mapped_column(String, nullable=False)
    shared_with_partner = mapped_column(Boolean, default=False)
    created_at = mapped_column(String, default=lambda: datetime.now(timezone.utc).isoformat()) 