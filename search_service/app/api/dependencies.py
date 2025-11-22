"""
Зависимости для dependency injection
"""
from typing import AsyncGenerator
from app.database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

async def get_db_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения асинхронной сессии БД.
    Автоматически закрывает сессию после использования.
    """
    async for session in get_db():
        yield session
