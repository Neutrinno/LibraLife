"""
Зависимости для dependency injection
"""
from typing import AsyncGenerator
from app.database.connection import get_db
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def get_db_dependency() -> AsyncGenerator:
    """
    Dependency для получения сессии с БД.
    Автоматически закрывает сессию после использования.
    """
    async for session in get_db():
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database session error: {str(e)}"
            )
