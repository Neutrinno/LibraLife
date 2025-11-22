# search_service/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Импортируем настройки
from app.config import (
    DB_HOST, DB_PORT, TYPESENSE_HOST, LOG_LEVEL, ALLOWED_ORIGINS
)
from app.database.connection import check_db_connection

# --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
# Импортируем api_router из пакета app.api (из его __init__.py)
from app.api import api_router

from app.services.typesense_client import init_collection

from app.database.connection import get_db
from app.services.typesense_client import sync_synonyms_with_typesense

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("--- Application Starting Up ---")

    # Логируем ключевые настройки, чтобы всегда знать, с чем работаем
    logger.info("Loaded configuration:")
    logger.info(f"  Database Host: {DB_HOST}")
    logger.info(f"  Database Port: {DB_PORT}")
    logger.info(f"  Typesense Host: {TYPESENSE_HOST}")

    try:
        if not await check_db_connection():
            raise Exception("Database connection health check failed on startup.")
        logger.info("✅ Database connection confirmed.")

        # Инициализируем коллекцию в Typesense
        init_collection()

        try:
            async for session in get_db():
                await sync_synonyms_with_typesense(session)
                break
        except Exception as e:
            logger.error(f"Could not run synonym synchronization during startup: {e}")

    except Exception as e:
        logger.error(f"❌ FATAL: Startup error: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("--- Application Shutting Down ---")


app = FastAPI(
    title="LibraLife Search Service",
    description="Сервис индексации и поиска книг и мероприятий для LibraLife",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["Health"])
def health_check():
    """Проверка общего состояния сервиса"""
    return {"status": "ok"}


@app.get("/", tags=["Root"])
def root():
    """Корневой endpoint с информацией о API"""
    return {"message": "Welcome to LibraLife Search API", "docs": "/docs"}