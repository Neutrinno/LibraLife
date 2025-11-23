"""
Endpoint для поиска книг и мероприятий через Typesense
"""
from fastapi import APIRouter, Query, status, HTTPException, Depends
from typing import Optional
from app.models.schemas import SearchResponse
from app.services.typesense_client import search_items, find_similar_items
from app.database.queries import get_book_by_id, get_event_by_id
from app.api.dependencies import get_db_dependency
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.preprocessor import preprocess_text
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def search(
    q: Optional[str] = Query("*", max_length=200, description="Поисковый запрос. Используйте '*' для получения всех результатов"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    location: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    item_type: Optional[str] = Query(None, description="Фильтр по типу: 'book' или 'event'")
):
    """
    Поиск книг и мероприятий. По умолчанию ищет в обоих типах одновременно.
    
    Если q не указан или равен '*', возвращает все результаты с учетом фильтров.
    """
    try:
        # Если запрос пустой или не указан, используем '*' для получения всех результатов
        search_query = q if q and q.strip() and q != "*" else "*"
        
        filters = {}
        if location:
            filters['location'] = location
        if category:
            filters['category'] = category

        # Валидация item_type
        if item_type and item_type not in ['book', 'event']:
            raise HTTPException(
                status_code=400,
                detail="item_type must be 'book' or 'event'"
            )

        results = search_items(
            query=search_query,
            page=page,
            per_page=per_page,
            filters=filters if filters else None,
            item_type=item_type
        )

        logger.info(f"Search query: '{search_query}', item_type: {item_type or 'all'}, found: {results['found']}")
        return {
            "query": q or "*",
            "total": results['found'],
            "results": results['hits'],  # hits содержит document и score
            "page": results['page'],
            "search_method": "typesense",
            "item_type": item_type or "all"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка во время поиска.")


@router.get("/suggest")
async def suggest(
    q: str = Query(..., min_length=1, description="Префикс для автодополнения"),
    limit: int = Query(5, ge=1, le=10),
    item_type: Optional[str] = Query(None, description="Фильтр по типу: 'book' или 'event'")
):
    """
    Автодополнение поисковых запросов.
    Используется для поисковой строки.
    Возвращает заголовки книг и/или мероприятий.
    """
    try:
        # Валидация item_type
        if item_type and item_type not in ['book', 'event']:
            raise HTTPException(
                status_code=400,
                detail="item_type must be 'book' or 'event'"
            )

        results = search_items(query=q, per_page=limit, page=1, item_type=item_type)

        # Достаем заголовок из вложенного словаря 'document'
        suggestions = list(set([
            hit.get('document', {}).get('title', '')
            for hit in results['hits'] if hit.get('document')
        ]))

        # Убираем пустые строки
        suggestions = [s for s in suggestions if s]

        return {
            "query": q,
            "suggestions": suggestions[:limit],
            "item_type": item_type or "all"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Suggest error: {e}", exc_info=True)
        return {"query": q, "suggestions": []}


@router.get("/books/{book_id}/similar")
async def get_similar_books(
    book_id: str,
    limit: int = Query(10, ge=1, le=50, description="Количество похожих книг"),
    db: AsyncSession = Depends(get_db_dependency)
):
    """
    Получение похожих книг на основе текущей книги.
    Похожесть определяется по названию, автору и категории через Typesense.
    """
    try:
        # Получаем данные книги из БД
        book_data = await get_book_by_id(db, book_id)

        if not book_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        # Ищем похожие книги через Typesense
        similar_items = find_similar_items(book_data, limit=limit)

        logger.info(f"Similar books for book {book_id}: found {len(similar_items)} items")

        return {
            "current_book": book_data,
            "similar_books": similar_items,
            "total": len(similar_items)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting similar books for {book_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting similar books"
        )


@router.get("/events/{event_id}/similar")
async def get_similar_events(
    event_id: str,
    limit: int = Query(10, ge=1, le=50, description="Количество похожих мероприятий"),
    db: AsyncSession = Depends(get_db_dependency)
):
    """
    Получение похожих мероприятий на основе текущего мероприятия.
    Похожесть определяется по названию, описанию и локации через Typesense.
    Возвращает только будущие мероприятия.
    """
    try:
        # Получаем данные мероприятия из БД
        event_data = await get_event_by_id(db, event_id)

        if not event_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Ищем похожие мероприятия через Typesense
        similar_items = find_similar_items(event_data, limit=limit)

        logger.info(f"Similar events for event {event_id}: found {len(similar_items)} items")

        return {
            "current_event": event_data,
            "similar_events": similar_items,
            "total": len(similar_items)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting similar events for {event_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting similar events"
        )