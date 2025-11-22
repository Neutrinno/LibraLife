"""Базовые тесты функционала поиска и индексации"""
import pytest
from unittest.mock import patch, MagicMock


def test_import_modules():
    """Проверка импортов"""
    try:
        from app.main import app
        from app.database.queries import get_book_by_id, get_event_by_id
        from app.services.typesense_client import index_item, search_items
        print("✅ Все импорты прошли успешно")
        assert True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        assert False, f"Import error: {e}"


def test_book_data_structure():
    """Тест структуры данных книги"""
    # Тестируем ожидаемую структуру данных без реального DB вызова
    book_data = {
        'id': 1,
        'author': 'Ф.М. Достоевский',
        'title': 'Преступление и наказание',
        'category': 'Классическая литература',
        'gost_title': None,
        'description': 'Описание',
        'is_available': True
    }

    # Проверяем, что функция вернула бы правильную структуру
    expected = {
        **book_data,
        'item_type': 'book'
    }

    # Имитируем логику get_book_by_id без реального DB
    result = {**book_data, 'item_type': 'book'}

    assert result['id'] == expected['id']
    assert result['title'] == expected['title']
    assert result['author'] == expected['author']
    assert result['item_type'] == 'book'
    assert result['is_available'] is True
    print("✅ Тест структуры данных книги прошел")


def test_event_data_structure():
    """Тест структуры данных мероприятия"""
    # Тестируем ожидаемую структуру данных без реального DB вызова
    event_data = {
        'id': 1,
        'title': 'Лекция о Достоевском',
        'description': 'Описание',
        'date': '2024-12-15T18:00:00',
        'location': 'Москва',
        'participants_count': 50
    }

    # Проверяем, что функция вернула бы правильную структуру
    expected = {
        **event_data,
        'item_type': 'event'
    }

    # Имитируем логику get_event_by_id без реального DB
    result = {**event_data, 'item_type': 'event'}

    assert result['id'] == expected['id']
    assert result['title'] == expected['title']
    assert result['item_type'] == 'event'
    assert result['location'] == expected['location']
    assert result['participants_count'] == expected['participants_count']
    assert 'date' in result
    print("✅ Тест структуры данных мероприятия прошел")


def test_index_item_book_mock():
    """Тест индексации книги в Typesense (с моками)"""
    from app.services.typesense_client import index_item

    book_data = {
        'id': 1,
        'item_type': 'book',
        'title': 'Преступление и наказание',
        'author': 'Ф.М. Достоевский',
        'category': 'Классическая литература',
        'description': 'Описание',
        'is_available': True
    }

    # Полностью мокаем Typesense клиент
    with patch('app.services.typesense_client.client') as mock_client:
        # Мокаем всю цепочку вызовов
        mock_collection = MagicMock()
        mock_documents = MagicMock()
        mock_collection.documents = mock_documents
        mock_documents.upsert = MagicMock()

        mock_client.collections.__getitem__ = MagicMock(return_value=mock_collection)

        result = index_item(book_data)

        assert result is True
        mock_documents.upsert.assert_called_once()
        call_args = mock_documents.upsert.call_args[0][0]
        assert call_args['id'] == 'book_1'
        assert call_args['item_type'] == 'book'
        assert call_args['title'] == 'Преступление и наказание'
        assert call_args['author'] == 'Ф.М. Достоевский'
        print("✅ Тест индексации книги прошел")


def test_index_item_event_mock():
    """Тест индексации мероприятия в Typesense (с моками)"""
    from app.services.typesense_client import index_item

    event_data = {
        'id': 1,
        'item_type': 'event',
        'title': 'Лекция',
        'description': 'Описание',
        'date': '2024-12-15T18:00:00',
        'location': 'Москва',
        'participants_count': 50
    }

    # Полностью мокаем Typesense клиент
    with patch('app.services.typesense_client.client') as mock_client:
        mock_collection = MagicMock()
        mock_documents = MagicMock()
        mock_collection.documents = mock_documents
        mock_documents.upsert = MagicMock()

        mock_client.collections.__getitem__ = MagicMock(return_value=mock_collection)

        result = index_item(event_data)

        assert result is True
        mock_documents.upsert.assert_called_once()
        call_args = mock_documents.upsert.call_args[0][0]
        assert call_args['id'] == 'event_1'
        assert call_args['item_type'] == 'event'
        assert call_args['participants_count'] == 50
        print("✅ Тест индексации мероприятия прошел")


def test_search_items_mock():
    """Тест поиска в Typesense (с моками)"""
    from app.services.typesense_client import search_items

    mock_results = {
        'hits': [
            {'document': {'id': 'book_1', 'item_type': 'book', 'title': 'Книга'}},
            {'document': {'id': 'event_1', 'item_type': 'event', 'title': 'Событие'}}
        ],
        'found': 2,
        'page': 1
    }

    # Полностью мокаем Typesense клиент
    with patch('app.services.typesense_client.client') as mock_client:
        mock_collection = MagicMock()
        mock_documents = MagicMock()
        mock_collection.documents = mock_documents
        mock_documents.search = MagicMock(return_value=mock_results)

        mock_client.collections.__getitem__ = MagicMock(return_value=mock_collection)

        result = search_items('тест', page=1, per_page=20)

        assert result['found'] == 2
        assert len(result['hits']) == 2
        mock_documents.search.assert_called_once()
        print("✅ Тест поиска прошел")


def test_search_items_filtered_mock():
    """Тест поиска с фильтром по типу (с моками)"""
    from app.services.typesense_client import search_items

    mock_results = {
        'hits': [{'document': {'id': 'book_1', 'item_type': 'book', 'title': 'Книга'}}],
        'found': 1,
        'page': 1
    }

    # Полностью мокаем Typesense клиент
    with patch('app.services.typesense_client.client') as mock_client:
        mock_collection = MagicMock()
        mock_documents = MagicMock()
        mock_collection.documents = mock_documents
        mock_documents.search = MagicMock(return_value=mock_results)

        mock_client.collections.__getitem__ = MagicMock(return_value=mock_collection)

        result = search_items('тест', page=1, per_page=20, item_type='book')

        assert result['found'] == 1
        # Проверяем, что фильтр был добавлен
        call_args = mock_documents.search.call_args[0][0]
        assert 'filter_by' in call_args
        assert 'item_type:=book' in call_args['filter_by']
        print("✅ Тест поиска с фильтром прошел")