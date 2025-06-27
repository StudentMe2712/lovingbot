from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(64))
    score: Mapped[int] = mapped_column(Integer, default=0)
    partner_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    partner_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(Integer)
    media_type: Mapped[str] = mapped_column(String(16), default="text")
    file_id: Mapped[str] = mapped_column(String(128), nullable=True) 