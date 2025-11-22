import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import logging
from app.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

logger = logging.getLogger(__name__)

connection_pool = None

def init_db_pool():
    """Инициализация пула соединений с БД"""
    global connection_pool
    
    if connection_pool is not None:
        logger.warning("Connection pool already initialized")
        return
    
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            connect_timeout=5  # Добавлен таймаут
        )
        logger.info("Database connection pool created successfully")
    except psycopg2.OperationalError as e:
        logger.error(f"Cannot connect to database: {e}")
        raise
    except Exception as e:
        logger.error(f"Error creating connection pool: {e}")
        raise

def close_db_pool():
    """Закрытие пула соединений"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        connection_pool = None
        logger.info("Database connection pool closed")

def get_db_connection():
    """Получение соединения из пула"""
    if connection_pool is None:
        raise Exception("Connection pool is not initialized. Call init_db_pool() first")
    
    try:
        connection = connection_pool.getconn()
        if connection.closed:
            connection_pool.putconn(connection)
            raise Exception("Connection is closed")
        return connection
    except Exception as e:
        logger.error(f"Error getting connection from pool: {e}")
        raise

def return_db_connection(connection):
    """Возврат соединения в пул"""
    if connection_pool and connection:
        try:
            connection_pool.putconn(connection)
        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}")

@contextmanager
def get_db():
    """Context manager для работы с БД"""
    connection = None
    try:
        connection = get_db_connection()
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if connection:
            return_db_connection(connection)

def check_db_connection() -> bool:
    """Healthcheck для проверки доступности БД"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
    except Exception as e:
        logger.error(f"Database healthcheck failed: {e}")
        return False