from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import logging

from app.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

logger = logging.getLogger(__name__)

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    """Async generator для получения сессии БД"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def check_db_connection() -> bool:
    """Healthcheck для проверки доступности БД"""
    try:
        from sqlalchemy import text
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database healthcheck failed: {e}")
        return False
