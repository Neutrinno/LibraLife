from collections import defaultdict

from dateutil import parser
from typesense import Client
from app.config import TYPESENSE_HOST, TYPESENSE_PORT, TYPESENSE_PROTOCOL, TYPESENSE_API_KEY
import logging
from typing import Dict, Optional

from app.database.queries import get_all_synonyms
from sqlalchemy.ext.asyncio import AsyncSession
from typesense.exceptions import ObjectNotFound, ServiceUnavailable

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

COLLECTION_NAME = 'libralife_items'

# Объединенная схема для книг и мероприятий
COLLECTION_SCHEMA = {
    'name': COLLECTION_NAME,
    'fields': [
        # Общие поля
        {'name': 'item_type', 'type': 'string', 'facet': True},  # 'book' или 'event'
        # Поле 'id' создается автоматически Typesense, не нужно определять вручную
        {'name': 'title', 'type': 'string', 'locale': 'ru', 'infix': True},
        {'name': 'description', 'type': 'string', 'optional': True, 'locale': 'ru'},
        {'name': 'category', 'type': 'string', 'optional': True, 'facet': True},
        {'name': 'location', 'type': 'string', 'optional': True, 'facet': True},
        
        # Поля для книг
        {'name': 'author', 'type': 'string', 'optional': True, 'locale': 'ru', 'infix': True},
        {'name': 'gost_title', 'type': 'string', 'optional': True, 'locale': 'ru'},
        {'name': 'is_available', 'type': 'bool', 'optional': True},
        
        # Поля для мероприятий
        {'name': 'date', 'type': 'int64', 'optional': True},  # Unix timestamp
        {'name': 'participants_count', 'type': 'int32', 'optional': True},
    ]
}


def init_collection(max_retries: int = 10, retry_delay: int = 3):
    """
    Создает коллекцию в Typesense, только если она не существует.
    Это предотвращает потерю данных при перезапуске сервиса.
    
    Args:
        max_retries: Максимальное количество попыток подключения к Typesense
        retry_delay: Задержка между попытками в секундах
    """
    import time
    
    for attempt in range(1, max_retries + 1):
        try:
            # Пытаемся получить информацию о коллекции
            client.collections[COLLECTION_NAME].retrieve()
            logger.info(f"Collection '{COLLECTION_NAME}' already exists. Skipping creation.")
            return
        except ObjectNotFound:
            # Если получаем ошибку 404, значит коллекции нет - создаем
            logger.info(f"Collection '{COLLECTION_NAME}' not found. Creating...")
            try:
                # Создаем коллекцию с нашей схемой
                client.collections.create(COLLECTION_SCHEMA)
                logger.info(f"Collection '{COLLECTION_NAME}' created successfully.")
                return
            except ServiceUnavailable as e:
                if attempt < max_retries:
                    logger.warning(
                        f"Typesense not ready yet (attempt {attempt}/{max_retries}). "
                        f"Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Failed to create collection '{COLLECTION_NAME}' after {max_retries} attempts: {e}")
                    raise
            except Exception as create_error:
                logger.error(f"Failed to create collection '{COLLECTION_NAME}': {create_error}")
                raise
        except ServiceUnavailable as e:
            # Typesense еще не готов
            if attempt < max_retries:
                logger.warning(
                    f"Typesense not ready yet (attempt {attempt}/{max_retries}). "
                    f"Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Typesense unavailable after {max_retries} attempts: {e}")
                raise
        except Exception as e:
            # Другие ошибки - пробуем еще раз, если есть попытки
            if attempt < max_retries:
                logger.warning(
                    f"Error connecting to Typesense (attempt {attempt}/{max_retries}): {e}. "
                    f"Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Failed to initialize collection after {max_retries} attempts: {e}")
                raise


async def sync_synonyms_with_typesense(session: AsyncSession):
    """
    Читает все синонимы из PostgreSQL и загружает их в Typesense.
    Эта операция перезаписывает существующие синонимы в Typesense.
    """
    logger.info("Starting synonym synchronization with Typesense...")
    try:
        # 1. Получаем все синонимы из базы данных
        synonym_tuples = await get_all_synonyms(session)
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
            try:
                client.collections[COLLECTION_NAME].synonyms.upsert(synonym_id, synonym_data)
            except Exception as e:
                logger.warning(f"Could not upsert synonym {synonym_id}: {e}")

        logger.info("✅ Successfully synchronized synonyms with Typesense.")

    except Exception as e:
        logger.error(f"❌ Failed to synchronize synonyms with Typesense: {e}", exc_info=True)


def index_item(item_data: dict) -> bool:
    """
    Индексация книги или мероприятия в Typesense.
    item_data должен содержать поле 'item_type': 'book' или 'event'
    """
    try:
        item_type = item_data.get('item_type')
        if item_type not in ['book', 'event']:
            logger.error(f"Invalid item_type: {item_type}. Must be 'book' or 'event'")
            return False

        # Формируем базовый документ
        document = {
            'id': f"{item_type}_{item_data['id']}",  # Уникальный ID: book_1, event_5
            'item_type': item_type,
            'title': item_data.get('title', ''),
            'description': item_data.get('description') or '',
            'category': item_data.get('category') or '',
            'location': item_data.get('location') or '',
        }

        # Добавляем поля в зависимости от типа
        if item_type == 'book':
            document['author'] = item_data.get('author') or ''
            document['gost_title'] = item_data.get('gost_title') or ''
            document['is_available'] = item_data.get('is_available', True)
        elif item_type == 'event':
            # Преобразуем дату в Unix timestamp
            date_ts = 0
            if item_data.get('date'):
                if isinstance(item_data['date'], str):
                    date_ts = int(parser.isoparse(item_data['date']).timestamp())
                else:
                    # Если уже datetime объект
                    date_ts = int(item_data['date'].timestamp())
            document['date'] = date_ts
            document['participants_count'] = item_data.get('participants_count', 0)

        import json
        logger.debug(f"Preparing to index {item_type}: {json.dumps(document, indent=2, ensure_ascii=False)}")

        client.collections[COLLECTION_NAME].documents.upsert(document)
        logger.info(f"{item_type.capitalize()} {document['id']} indexed successfully.")
        return True

    except Exception as e:
        logger.error(f"Error indexing item: {e}", exc_info=True)
        return False


def delete_item(item_type: str, item_id: int) -> bool:
    """Удаление книги или мероприятия из индекса"""
    try:
        document_id = f"{item_type}_{item_id}"
        client.collections[COLLECTION_NAME].documents[document_id].delete()
        logger.info(f"Document {document_id} deleted from index")
        return True
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        return False


def search_items(
        query: str,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict] = None,
        item_type: Optional[str] = None  # 'book', 'event' или None (все)
):
    """
    Поиск книг и/или мероприятий в Typesense.
    
    Args:
        query: Поисковый запрос
        page: Номер страницы
        per_page: Количество результатов на странице
        filters: Дополнительные фильтры (category, location)
        item_type: Фильтр по типу ('book', 'event' или None для всех)
    """
    try:
        # Если запрос '*' или пустой, возвращаем все результаты (без поиска по тексту)
        is_wildcard = query == '*' or not query.strip()
        
        # Базовые поля для поиска (общие для книг и мероприятий)
        search_params = {
            'q': query,
            'per_page': per_page,
            'page': page,
        }
        
        if not is_wildcard:
            # Параметры поиска по тексту только если это не wildcard запрос
            search_params.update({
                'query_by': 'title,author,description,gost_title',  # author и gost_title только для книг, но это ок
                'query_by_weights': '4,3,2,1',
                'prefix': 'true',
                'num_typos': 2,
                'sort_by': '_text_match:desc,date:desc'  # Сначала релевантность, потом дата (для мероприятий)
            })
        else:
            # Для wildcard запроса сортируем просто по дате или ID
            search_params['sort_by'] = 'date:desc'

        # Построение фильтров
        filter_strings = []
        
        # Фильтр по типу элемента
        if item_type and item_type in ['book', 'event']:
            filter_strings.append(f"item_type:={item_type}")
        
        # Дополнительные фильтры
        if filters:
            if filters.get('category'):
                filter_strings.append(f"category:={filters['category']}")
            if filters.get('location'):
                filter_strings.append(f"location:='{filters['location']}'")
            if filters.get('is_available') is not None and item_type == 'book':
                filter_strings.append(f"is_available:={str(filters['is_available']).lower()}")

        if filter_strings:
            search_params['filter_by'] = ' && '.join(filter_strings)

        results = client.collections[COLLECTION_NAME].documents.search(search_params)
        return {
            'hits': results['hits'],  # Возвращаем полный hit с document и score
            'found': results['found'],
            'page': results['page']
        }
    except Exception as e:
        logger.error(f"Error searching items: {e}", exc_info=True)
        return {'hits': [], 'found': 0, 'page': 1}


# Оставляем старую функцию для обратной совместимости (если где-то используется)
def search_services(query: str, page: int = 1, per_page: int = 20, filters: Optional[Dict] = None):
    """Старая функция для обратной совместимости. Использует search_items."""
    return search_items(query, page, per_page, filters)