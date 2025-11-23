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


# ============= BOOKS =============
async def get_book_by_id(session: AsyncSession, book_id: str) -> Optional[Dict[str, Any]]:
    """Получение книги по ID для индексации."""
    try:
        # Конвертируем в int для поиска
        book_id_int = int(book_id)

        result = await session.execute(
            text("""
                SELECT
                    id,
                    author,
                    title,
                    category,
                    gost_title,
                    description,
                    is_available
                FROM books
                WHERE id = :book_id
            """),
            {"book_id": book_id_int}
        )
        row = result.fetchone()

        if row:
            book_dict = {
                'id': str(row[0]),  # Всегда возвращаем как строку
                'author': row[1],
                'title': row[2],
                'category': row[3],
                'gost_title': row[4],
                'description': row[5],
                'is_available': row[6],
                'item_type': 'book'
            }
            return book_dict

        return None

    except ValueError:
        # Если не удалось конвертировать в int, возвращаем None
        logger.error(f"Invalid book_id format: {book_id}")
        return None
    except Exception as e:
        logger.error(f"Error fetching book {book_id}: {e}", exc_info=True)
        return None


async def get_all_books(session: AsyncSession, limit: int = 1000, offset: int = 0, available_only: bool = False) -> List[Dict[str, Any]]:
    """
    Получение всех книг для массовой индексации.
    
    Args:
        session: AsyncSession с БД
        limit: Максимальное количество записей
        offset: Смещение для пагинации
        available_only: Если True, возвращает только доступные книги
    """
    try:
        where_clause = "WHERE is_available = TRUE" if available_only else ""
        result = await session.execute(
            text(f"""
                SELECT 
                    id,
                    author,
                    title,
                    category,
                    gost_title,
                    description,
                    is_available
                FROM books
                {where_clause}
                ORDER BY id ASC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        )
        rows = result.fetchall()

        books = []
        for row in rows:
            # Преобразуем UUID в строку, если это UUID
            book_id = row[0]
            if hasattr(book_id, '__str__'):
                book_id = str(book_id)
            
            book_dict = {
                'id': book_id,
                'author': row[1],
                'title': row[2],
                'category': row[3],
                'gost_title': row[4],
                'description': row[5],
                'is_available': row[6],
                'item_type': 'book'
            }
            books.append(book_dict)

        return books

    except Exception as e:
        logger.error(f"Error fetching books: {e}", exc_info=True)
        return []


# ============= EVENTS =============
async def get_event_by_id(session: AsyncSession, event_id: str) -> Optional[Dict[str, Any]]:
    """Получение мероприятия по ID для индексации."""
    try:
        # Конвертируем в int для поиска
        event_id_int = int(event_id)

        result = await session.execute(
            text("""
                SELECT
                    id,
                    title,
                    description,
                    date,
                    location,
                    participants_count
                FROM events
                WHERE id = :event_id
            """),
            {"event_id": event_id_int}
        )
        row = result.fetchone()

        if row:
            event_dict = {
                'id': str(row[0]),  # Всегда возвращаем как строку
                'title': row[1],
                'description': row[2],
                'date': row[3],
                'location': row[4],
                'participants_count': row[5],
                'item_type': 'event'
            }
            # Преобразуем datetime в строку для JSON-сериализации
            if event_dict.get('date') and hasattr(event_dict['date'], 'isoformat'):
                event_dict['date'] = event_dict['date'].isoformat()
            return event_dict

        return None

    except ValueError:
        # Если не удалось конвертировать в int, возвращаем None
        logger.error(f"Invalid event_id format: {event_id}")
        return None
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {e}", exc_info=True)
        return None


async def get_all_events(session: AsyncSession, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Получение всех мероприятий для массовой индексации.
    """
    try:
        result = await session.execute(
            text("""
                SELECT 
                    id,
                    title,
                    description,
                    date,
                    location,
                    participants_count
                FROM events
                ORDER BY date ASC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        )
        rows = result.fetchall()

        events = []
        for row in rows:
            # Преобразуем UUID в строку, если это UUID
            event_id = row[0]
            if hasattr(event_id, '__str__'):
                event_id = str(event_id)
            
            event_dict = {
                'id': event_id,
                'title': row[1],
                'description': row[2],
                'date': row[3],
                'location': row[4],
                'participants_count': row[5],
                'item_type': 'event'
            }
            # Преобразуем datetime в строку
            if event_dict.get('date') and hasattr(event_dict['date'], 'isoformat'):
                event_dict['date'] = event_dict['date'].isoformat()
            events.append(event_dict)

        return events

    except Exception as e:
        logger.error(f"Error fetching events: {e}", exc_info=True)
        return []


# ============= SERVICES (старые функции, оставлены для обратной совместимости) =============
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
