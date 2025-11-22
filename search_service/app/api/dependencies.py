"""
Зависимости для dependency injection
"""
"""
Зависимости для dependency injection
"""
from typing import Generator
from app.database.connection import get_db_connection, return_db_connection
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def get_db() -> Generator:
    """
    Dependency для получения соединения с БД.
    Автоматически закрывает соединение после использования.
    """
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}"
        )
    finally:
        if conn:
            return_db_connection(conn)