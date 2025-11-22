"""
Endpoint для поиска услуг через Typesense
"""
from fastapi import APIRouter, Query, status, HTTPException
from typing import Optional
from app.models.schemas import SearchResponse
from app.services.typesense_client import search_services
from app.services.preprocessor import preprocess_text
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
def search(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    location: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Поиск услуг производственных мощностей."""
    try:
        filters = {}
        if location:
            filters['location'] = location
        if category:
            filters['category'] = category.upper()

        results = search_services(
            query=q,
            page=page,
            per_page=per_page,
            filters=filters if filters else None
        )

        logger.info(f"Search query: '{q}', found: {results['found']}")
        return {
            "query": q,
            "total": results['found'],
            "results": results['hits'],  # hits теперь содержит и score, и document
            "page": results['page'],
            "search_method": "typesense"
        }
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка во время поиска.")


@router.get("/suggest")
def suggest(
    q: str = Query(..., min_length=1, description="Префикс для автодополнения"),
    limit: int = Query(5, ge=1, le=10)
):
    """
    Автодополнение поисковых запросов.
    Используется для поисковой строки.
    """
    try:
        # Эта функция теперь возвращает более сложный объект
        results = search_services(query=q, per_page=limit, page=1)

        # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
        # Достаем заголовок из вложенного словаря 'document'
        suggestions = list(set([
            hit.get('document', {}).get('title', '')
            for hit in results['hits'] if hit.get('document')
        ]))

        # Убираем пустые строки, если они попали в список
        suggestions = [s for s in suggestions if s]

        return {
            "query": q,
            "suggestions": suggestions[:limit]
        }

    except Exception as e:
        logger.error(f"Suggest error: {e}", exc_info=True)
        return {"query": q, "suggestions": []}