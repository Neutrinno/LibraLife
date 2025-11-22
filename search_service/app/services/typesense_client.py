from collections import defaultdict

from dateutil import parser
from typesense import Client
from app.config import TYPESENSE_HOST, TYPESENSE_PORT, TYPESENSE_PROTOCOL, TYPESENSE_API_KEY
import logging
from typing import Dict, Optional

from app.database.queries import get_all_synonyms
from typesense.exceptions import ObjectNotFound

logger = logging.getLogger(__name__)

# Инициализация клиента Typesense
client = Client({
    'nodes': [{
        'host': TYPESENSE_HOST,
        'port': TYPESENSE_PORT,
        'protocol': TYPESENSE_PROTOCOL
    }],
    'api_key': TYPESENSE_API_KEY,
    'connection_timeout_seconds': 2
})

COLLECTION_NAME = 'services'

# Обновленная схема, соответствующая базе данных [1]
COLLECTION_SCHEMA = {
    'name': COLLECTION_NAME,
    'fields': [
        {'name': 'title', 'type': 'string', 'locale': 'ru', 'infix': True},
        {'name': 'description', 'type': 'string', 'optional': True, 'locale': 'ru'},
        {'name': 'category', 'type': 'string', 'facet': True},
        {'name': 'location', 'type': 'string', 'optional': True, 'facet': True},
        {'name': 'capacity', 'type': 'string', 'optional': True},
        {'name': 'technical_specs', 'type': 'string', 'optional': True, 'locale': 'ru'},
        {'name': 'supplier_id', 'type': 'string', 'facet': True},
        {'name': 'supplier_name', 'type': 'string', 'optional': True, 'locale': 'ru', 'infix': True},
        {'name': 'price_per_day', 'type': 'float', 'optional': True},
        {'name': 'created_at', 'type': 'int64'},
    ],
    'default_sorting_field': 'created_at'
}


def init_collection():
    """
    Создает коллекцию в Typesense, только если она не существует.
    Это предотвращает потерю данных при перезапуске сервиса.
    """
    try:
        # Пытаемся получить информацию о коллекции
        client.collections[COLLECTION_NAME].retrieve()
        logger.info(f"Collection '{COLLECTION_NAME}' already exists. Skipping creation.")
    except Exception:
        # Если получаем ошибку (404 Not Found), значит коллекции нет
        logger.info(f"Collection '{COLLECTION_NAME}' not found. Creating...")
        try:
            # Создаем коллекцию с нашей схемой
            client.collections.create(COLLECTION_SCHEMA)
            logger.info(f"Collection '{COLLECTION_NAME}' created successfully.")
        except Exception as create_error:
            logger.error(f"Failed to create collection '{COLLECTION_NAME}': {create_error}")
            raise create_error


def sync_synonyms_with_typesense(db_connection):
    """
    Читает все синонимы из PostgreSQL и загружает их в Typesense.
    Эта операция перезаписывает существующие синонимы в Typesense.
    """
    logger.info("Starting synonym synchronization with Typesense...")
    try:
        # 1. Получаем все синонимы из базы данных
        synonym_tuples = get_all_synonyms(db_connection)
        if not synonym_tuples:
            logger.info("No synonyms found in the database. Skipping sync.")
            return

        # 2. Группируем синонимы по основному слову (root word)
        # defaultdict(list) - удобный способ создать словарь со списками
        # получится {'трактор': ['мтз', 'беларус'], 'станок': ['чпу']}
        grouped_synonyms = defaultdict(list)
        for word, synonym in synonym_tuples:
            grouped_synonyms[word].append(synonym)

        logger.info(f"Found {len(synonym_tuples)} synonym pairs, grouped into {len(grouped_synonyms)} root words.")
        # 3. Загружаем каждый набор синонимов в Typesense
        for root_word, synonyms_list in grouped_synonyms.items():
            synonym_id = f"syn-{root_word}"  # Уникальный ID для набора синонимов

            # Формируем тело запроса для Typesense API
            synonym_data = {
                "synonyms": [root_word] + synonyms_list  # [трактор, мтз, беларус]
            }
            # Для односторонних синонимов, если нужно:
            # synonym_data = {
            #     "root": root_word,
            #     "synonyms": synonyms_list
            # }

            logger.debug(f"Upserting synonym: {synonym_id} -> {synonym_data}")
            client.collections[COLLECTION_NAME].synonyms.upsert(synonym_id, synonym_data)

        logger.info("✅ Successfully synchronized synonyms with Typesense.")

    except Exception as e:
        logger.error(f"❌ Failed to synchronize synonyms with Typesense: {e}", exc_info=True)


# app/services/typesense_client.py
# ... (импорты и другие функции) ...

def index_service(service_data: dict) -> bool:
    """Индексация услуги в Typesense"""
    try:
        # Преобразуем дату в Unix timestamp
        created_at_ts = 0
        if service_data.get('created_at'):
            from dateutil import parser
            created_at_ts = int(parser.isoparse(service_data['created_at']).timestamp())

        document = {
            'id': str(service_data['id']),
            'title': service_data.get('title', ''),
            'description': service_data.get('description', ''),
            'category': service_data.get('category', ''),
            'location': service_data.get('location', ''),
            'capacity': service_data.get('capacity', ''),
            'technical_specs': service_data.get('technical_specs', ''),
            'supplier_id': str(service_data.get('supplier_id', '')),
            'supplier_name': service_data.get('supplier_name', ''),
            'price_per_day': float(service_data.get('price_per_day', 0.0)) if service_data.get(
                'price_per_day') else 0.0,
            'created_at': created_at_ts
        }

        # --- ДОБАВЬТЕ ЭТОТ ЛОГ ---
        import json
        logger.info(f"--- DEBUG: Preparing to index document ---")
        logger.info(json.dumps(document, indent=2, ensure_ascii=False))
        logger.info(f"----------------------------------------")

        client.collections[COLLECTION_NAME].documents.upsert(document)
        logger.info(f"Document {document['id']} indexed successfully.")
        return True

    except Exception as e:
        logger.error(f"Error indexing service: {e}", exc_info=True)
        return False


def delete_service(service_id: int) -> bool:
    """Удаление услуги из индекса"""
    try:
        client.collections[COLLECTION_NAME].documents[str(service_id)].delete()
        logger.info(f"Document {service_id} deleted from index")
        return True
    except Exception as e:
        logger.error(f"Error deleting service: {e}")
        return False


def search_services(
        query: str,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict] = None
):
    try:
        search_params = {
            'q': query,
            'query_by': 'title,supplier_name,description,technical_specs',
            'query_by_weights': '4,3,2,1',
            'prefix': 'true',
            'num_typos': 2,
            'per_page': per_page,
            'page': page,
            'sort_by': '_text_match:desc,created_at:desc'
            # Фильтр по 'active' теперь не нужен, т.к. мы индексируем только активные услуги
        }
        # Построение фильтров из словаря
        if filters:
            filter_strings = []
            if filters.get('category'):
                filter_strings.append(f"category:={filters['category']}")
            if filters.get('location'):
                filter_strings.append(f"location:='{filters['location']}'")
            # ... можно добавить другие фильтры ...

            if filter_strings:
                search_params['filter_by'] = ' && '.join(filter_strings)

        results = client.collections[COLLECTION_NAME].documents.search(search_params)
        return {
            'hits': results['hits'],  # Возвращаем полный hit, а не только document
            'found': results['found'],
            'page': results['page']
        }
    except Exception as e:
        logger.error(f"Error searching: {e}", exc_info=True)
        return {'hits': [], 'found': 0, 'page': 1}