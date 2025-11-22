"""
Endpoint для поиска книг и мероприятий через Typesense
"""
from fastapi import APIRouter, Query, status, HTTPException
from typing import Optional
from app.models.schemas import SearchResponse
from app.services.typesense_client import search_items
from app.services.preprocessor import preprocess_text
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    location: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    item_type: Optional[str] = Query(None, description="Фильтр по типу: 'book' или 'event'")
):
    """Поиск книг и мероприятий. По умолчанию ищет в обоих типах одновременно."""
    try:
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
            query=q,
            page=page,
            per_page=per_page,
            filters=filters if filters else None,
            item_type=item_type
        )

        logger.info(f"Search query: '{q}', item_type: {item_type or 'all'}, found: {results['found']}")
        return {
            "query": q,
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