import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
import os
import re

from utils.models import Base # Убедитесь, что модели импортируются для создания таблиц

# Находим alembic.ini
ALEMBIC_INI_PATH = os.path.join(os.path.dirname(__file__), '..', 'alembic.ini')
alembic_cfg = Config(ALEMBIC_INI_PATH)

# Получаем URL БД из alembic.ini, но ЗАМЕНЯЕМ диалект на asyncpg
raw_url = alembic_cfg.get_main_option("sqlalchemy.url")
if raw_url and raw_url.startswith("postgresql://"):
    DATABASE_URL = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = raw_url

if not DATABASE_URL:
    raise ValueError("Не найден sqlalchemy.url в alembic.ini.")

# Удаляем ?sslmode=... и &channel_binding=... из строки подключения
DATABASE_URL = re.sub(r'[?&]sslmode=[^&]*', '', DATABASE_URL)
DATABASE_URL = re.sub(r'[?&]channel_binding=[^&]*', '', DATABASE_URL)
# Убираем лишний ? или & в конце
DATABASE_URL = DATABASE_URL.rstrip('?&')

# Создаем "движок" с правильными параметрами для SSL
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"ssl": "require"} # Передаем ssl как аргумент
)

# Создаем фабрику сессий
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncSession:
    """
    Фикстура для создания асинхронной сессии для каждого теста.
    Создает чистую БД в памяти для каждого тестового запуска.
    """
    # Получаем URL из alembic.ini
    config = Config("alembic.ini")
    url = config.get_main_option("sqlalchemy.url")

    # Извлекаем параметры sslmode и channel_binding из URL
    ssl_params = {}
    if 'sslmode' in url:
        url, _, sslmode = url.partition('?sslmode=')
        if '&' in sslmode:
            sslmode, _, rest = sslmode.partition('&')
            url = f"{url}?{rest}"
        ssl_params['ssl'] = sslmode
    
    if 'channel_binding' in url:
        # channel_binding не является стандартным параметром connect_args, его нужно удалить
        url = re.sub(r'[?&]channel_binding=[^&]*', '', url).rstrip('?&')

    # Используем уже обработанный DATABASE_URL с async-драйвером
    engine = create_async_engine(DATABASE_URL, connect_args=ssl_params)

    # Применяем миграции
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", url) # Убедимся, что alembic тоже использует чистый url

    async with engine.begin() as connection:
        await connection.run_sync(lambda sync_conn: command.upgrade(alembic_cfg, "head"))

    # Создаем сессию
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = AsyncSessionLocal()

    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """
    Фикстура для управления циклом событий asyncio в рамках сессии.
    Это решает проблемы с 'Event loop is closed'.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close() 