# search_service/app/database/queries.py
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


# ============= SYNONYMS =============

async def get_synonyms_for_word(session: AsyncSession, word: str) -> List[str]:
    """Получение синонимов для слова"""
    try:
        result = await session.execute(
            text("SELECT synonym FROM synonyms WHERE LOWER(word) = LOWER(:word)"),
            {"word": word}
        )
        synonyms = [row[0] for row in result.fetchall()]
        return synonyms
    except Exception as e:
        logger.error(f"Error fetching synonyms for '{word}': {e}")
        return []


async def get_all_synonyms(session: AsyncSession) -> List[Tuple[str, str]]:
    """
    Получение всех синонимов для загрузки в Typesense.
    Возвращает список кортежей (word, synonym).
    """
    try:
        result = await session.execute(
            text("SELECT word, synonym FROM synonyms ORDER BY word")
        )
        return [(row[0], row[1]) for row in result.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching all synonyms: {e}")
        return []


async def get_all_synonyms_query(session: AsyncSession) -> List[Tuple[str, str]]:
    """Алиас для get_all_synonyms (для совместимости с API)"""
    return await get_all_synonyms(session)


async def add_synonym_query(session: AsyncSession, word: str, synonym: str) -> bool:
    """Добавление синонима с проверкой дубликатов"""
    try:
        # Проверка на существование
        result = await session.execute(
            text("""
                SELECT 1 FROM synonyms 
                WHERE LOWER(word) = LOWER(:word) AND LOWER(synonym) = LOWER(:synonym)
            """),
            {"word": word, "synonym": synonym}
        )

        if result.fetchone():
            logger.info(f"Synonym already exists: {word} -> {synonym}")
            return False

        # Добавление
        await session.execute(
            text("INSERT INTO synonyms (word, synonym) VALUES (LOWER(:word), LOWER(:synonym))"),
            {"word": word, "synonym": synonym}
        )
        await session.commit()

        logger.info(f"Added synonym: {word} -> {synonym}")
        return True

    except Exception as e:
        await session.rollback()
        logger.error(f"Error adding synonym: {e}")
        return False


# ============= SERVICES =============
async def get_service_by_id(session: AsyncSession, service_id: UUID) -> Optional[Dict[str, Any]]:
    """Получение услуги по UUID для индексации."""
    try:
        result = await session.execute(
            text("""
                SELECT 
                    id,
                    title,
                    description,
                    category,
                    price_per_day,
                    location,
                    capacity,
                    technical_specs,
                    supplier_id,
                    supplier_name,
                    active,
                    created_at
                FROM services 
                WHERE id = :service_id AND active = TRUE
            """),
            {"service_id": str(service_id)}
        )
        row = result.fetchone()

        if row:
            # Преобразуем Row в словарь
            service_dict = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'price_per_day': row[4],
                'location': row[5],
                'capacity': row[6],
                'technical_specs': row[7],
                'supplier_id': row[8],
                'supplier_name': row[9],
                'active': row[10],
                'created_at': row[11]
            }
            # Преобразуем UUID и datetime в строки для JSON-сериализации
            for key, value in service_dict.items():
                if isinstance(value, UUID):
                    service_dict[key] = str(value)
                elif hasattr(value, 'isoformat'):
                    service_dict[key] = value.isoformat()
            return service_dict

        return None

    except Exception as e:
        logger.error(f"Error fetching service {service_id}: {e}", exc_info=True)
        return None


async def get_all_services(session: AsyncSession, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Получение всех активных услуг для массовой индексации.

    Args:
        session: AsyncSession с БД
        limit: Максимальное количество записей
        offset: Смещение для пагинации

    Returns:
        Список словарей с данными услуг
    """
    try:
        result = await session.execute(
            text("""
                SELECT 
                    id,
                    title,
                    description,
                    category,
                    location,
                    price_per_day,
                    capacity,
                    technical_specs,
                    is_active,
                    supplier_id,
                    created_at,
                    updated_at
                FROM services
                WHERE is_active = TRUE
                ORDER BY id ASC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        )
        rows = result.fetchall()

        # Преобразуем результаты
        services = []
        for row in rows:
            service_dict = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'location': row[4],
                'price_per_day': row[5],
                'capacity': row[6],
                'technical_specs': row[7],
                'is_active': row[8],
                'supplier_id': row[9],
                'created_at': row[10],
                'updated_at': row[11]
            }
            # Преобразуем timestamp в строку
            if service_dict.get('created_at'):
                service_dict['created_at'] = service_dict['created_at'].isoformat()
            if service_dict.get('updated_at'):
                service_dict['updated_at'] = service_dict['updated_at'].isoformat()
            services.append(service_dict)

        return services

    except Exception as e:
        logger.error(f"Error fetching services: {e}", exc_info=True)
        return []


async def count_active_services(session: AsyncSession) -> int:
    """Подсчёт количества активных услуг"""
    try:
        result = await session.execute(
            text("SELECT COUNT(*) FROM services WHERE is_active = TRUE")
        )
        count = result.scalar()
        return count if count is not None else 0
    except Exception as e:
        logger.error(f"Error counting services: {e}")
        return 0


async def search_services_in_db(
        session: AsyncSession,
        query: str,
        limit: int = 10,
        offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Поиск услуг в PostgreSQL (fallback если Typesense недоступен).
    Использует ILIKE для поиска по нескольким полям.
    """
    try:
        search_pattern = f"%{query}%"

        result = await session.execute(
            text("""
                SELECT 
                    id,
                    title,
                    description,
                    category,
                    location,
                    price_per_day,
                    capacity,
                    technical_specs,
                    supplier_id,
                    created_at
                FROM services
                WHERE is_active = TRUE
                AND (
                    title ILIKE :pattern 
                    OR description ILIKE :pattern
                    OR category ILIKE :pattern
                    OR technical_specs ILIKE :pattern
                    OR location ILIKE :pattern
                )
                ORDER BY 
                    CASE 
                        WHEN title ILIKE :pattern THEN 1
                        WHEN description ILIKE :pattern THEN 2
                        ELSE 3
                    END,
                    created_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {
                "pattern": search_pattern,
                "limit": limit,
                "offset": offset
            }
        )
        rows = result.fetchall()

        # Преобразуем результаты
        services = []
        for row in rows:
            service_dict = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'location': row[4],
                'price_per_day': row[5],
                'capacity': row[6],
                'technical_specs': row[7],
                'supplier_id': row[8],
                'created_at': row[9]
            }
            if service_dict.get('created_at'):
                service_dict['created_at'] = service_dict['created_at'].isoformat()
            services.append(service_dict)

        return services

    except Exception as e:
        logger.error(f"Error searching services in DB: {e}", exc_info=True)
        return []


# ============= SQL QUERY STRINGS (для использования без connection) =============

def get_service_by_id_query() -> str:
    """Возвращает SQL запрос для получения услуги по ID"""
    return """
        SELECT 
            id, title, description, category, location,
            price_per_day, capacity, technical_specs,
            is_active, supplier_id, created_at, updated_at
        FROM services 
        WHERE id = :service_id AND is_active = TRUE
    """


def get_all_services_query() -> str:
    """Возвращает SQL запрос для получения всех активных услуг"""
    return """
        SELECT 
            id, title, description, category, location,
            price_per_day, capacity, technical_specs,
            is_active, supplier_id, created_at, updated_at
        FROM services
        WHERE is_active = TRUE
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset
    """


def search_services_query() -> str:
    """Возвращает SQL запрос для поиска услуг"""
    return """
        SELECT 
            id, title, description, category, location,
            price_per_day, capacity, technical_specs,
            supplier_id, created_at
        FROM services
        WHERE is_active = TRUE
        AND (
            title ILIKE :pattern 
            OR description ILIKE :pattern
            OR category ILIKE :pattern
            OR technical_specs ILIKE :pattern
            OR location ILIKE :pattern
        )
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """
