# search_service/app/database/queries.py
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


# ============= SYNONYMS =============

def get_synonyms_for_word(connection, word: str) -> List[str]:
    """Получение синонимов для слова"""
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT synonym FROM synonyms WHERE LOWER(word) = LOWER(%s)",
            (word,)
        )
        synonyms = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return synonyms
    except Exception as e:
        logger.error(f"Error fetching synonyms for '{word}': {e}")
        return []


def get_all_synonyms(connection) -> List[Tuple[str, str]]:
    """
    Получение всех синонимов для загрузки в Typesense.
    Возвращает список кортежей (word, synonym).
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT word, synonym FROM synonyms ORDER BY word")
        results = cursor.fetchall()
        cursor.close()
        return results
    except Exception as e:
        logger.error(f"Error fetching all synonyms: {e}")
        return []


def get_all_synonyms_query(connection) -> List[Tuple[str, str]]:
    """Алиас для get_all_synonyms (для совместимости с API)"""
    return get_all_synonyms(connection)


def add_synonym_query(connection, word: str, synonym: str) -> bool:
    """Добавление синонима с проверкой дубликатов"""
    try:
        cursor = connection.cursor()

        # Проверка на существование
        cursor.execute(
            "SELECT 1 FROM synonyms WHERE LOWER(word) = LOWER(%s) AND LOWER(synonym) = LOWER(%s)",
            (word, synonym)
        )

        if cursor.fetchone():
            cursor.close()
            logger.info(f"Synonym already exists: {word} -> {synonym}")
            return False

        # Добавление
        cursor.execute(
            "INSERT INTO synonyms (word, synonym) VALUES (LOWER(%s), LOWER(%s))",
            (word, synonym)
        )
        connection.commit()
        cursor.close()

        logger.info(f"Added synonym: {word} -> {synonym}")
        return True

    except Exception as e:
        connection.rollback()
        logger.error(f"Error adding synonym: {e}")
        return False


# ============= SERVICES =============
def get_service_by_id(connection, service_id: UUID) -> Optional[Dict[str, Any]]:
    """Получение услуги по UUID для индексации."""
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
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
            WHERE id = %s AND active = TRUE
            """,
            (str(service_id),)  # Передаем UUID как строку
        )
        result = cursor.fetchone()
        cursor.close()

        if result:
            service_dict = dict(result)
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


def get_all_services(connection, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Получение всех активных услуг для массовой индексации.

    Args:
        connection: Соединение с БД
        limit: Максимальное количество записей
        offset: Смещение для пагинации

    Returns:
        Список словарей с данными услуг
    """
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
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
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )
        results = cursor.fetchall()
        cursor.close()

        # Преобразуем результаты
        services = []
        for row in results:
            service_dict = dict(row)
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


def count_active_services(connection) -> int:
    """Подсчёт количества активных услуг"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM services WHERE is_active = TRUE")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except Exception as e:
        logger.error(f"Error counting services: {e}")
        return 0


def search_services_in_db(
        connection,
        query: str,
        limit: int = 10,
        offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Поиск услуг в PostgreSQL (fallback если Typesense недоступен).
    Использует ILIKE для поиска по нескольким полям.
    """
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        search_pattern = f"%{query}%"

        cursor.execute(
            """
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
                title ILIKE %s 
                OR description ILIKE %s
                OR category ILIKE %s
                OR technical_specs ILIKE %s
                OR location ILIKE %s
            )
            ORDER BY 
                CASE 
                    WHEN title ILIKE %s THEN 1
                    WHEN description ILIKE %s THEN 2
                    ELSE 3
                END,
                created_at DESC
            LIMIT %s OFFSET %s
            """,
            (
                search_pattern, search_pattern, search_pattern,
                search_pattern, search_pattern,
                search_pattern, search_pattern,
                limit, offset
            )
        )
        results = cursor.fetchall()
        cursor.close()

        # Преобразуем результаты
        services = []
        for row in results:
            service_dict = dict(row)
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
        WHERE id = %s AND is_active = TRUE
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
        LIMIT %s OFFSET %s
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
            title ILIKE %s 
            OR description ILIKE %s
            OR category ILIKE %s
            OR technical_specs ILIKE %s
            OR location ILIKE %s
        )
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """