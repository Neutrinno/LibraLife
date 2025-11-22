from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from typing import Optional
from app.api.dependencies import get_db_dependency
from app.database.queries import get_book_by_id, get_event_by_id
from sqlalchemy.ext.asyncio import AsyncSession
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class IndexRequest(BaseModel):
    item_type: str = Field(..., description="Тип элемента: 'book' или 'event'")
    id: int = Field(..., description="ID книги или мероприятия")

    class Config:
        json_schema_extra = {
            "example": {
                "item_type": "book",
                "id": 1
            }
        }


class IndexResponse(BaseModel):
    success: bool
    item_type: str
    item_id: int
    message: str


@router.post("/index", response_model=IndexResponse)
async def index_item_endpoint(
        request: IndexRequest,
        db: AsyncSession = Depends(get_db_dependency)
):
    """Индексация книги или мероприятия в Typesense по ID"""
    logger.info(f"=== Index request for {request.item_type} id={request.id} ===")

    # Валидация типа
    if request.item_type not in ['book', 'event']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="item_type must be 'book' or 'event'"
        )

    try:
        # Получаем данные в зависимости от типа
        if request.item_type == 'book':
            item_dict = await get_book_by_id(db, request.id)
            not_found_msg = f"Book with id {request.id} not found"
        else:  # event
            item_dict = await get_event_by_id(db, request.id)
            not_found_msg = f"Event with id {request.id} not found"

        if not item_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=not_found_msg
            )
        
        from app.services.typesense_client import index_item
        success = index_item(item_dict)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to index {request.item_type} in Typesense"
            )

        return IndexResponse(
            success=True,
            item_type=request.item_type,
            item_id=request.id,
            message=f"{request.item_type.capitalize()} indexed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled indexing error for {request.item_type} {request.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during indexing."
        )


@router.delete("/index/{item_type}/{item_id}")
async def delete_item_endpoint(
    item_type: str,
    item_id: int
):
    """Удаление книги или мероприятия из индекса"""
    try:
        # Валидация типа
        if item_type not in ['book', 'event']:
            raise HTTPException(
                status_code=400,
                detail="item_type must be 'book' or 'event'"
            )

        from app.services.typesense_client import delete_item
        success = delete_item(item_type, item_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete {item_type} from index"
            )
        
        return {
            "success": True,
            "item_type": item_type,
            "item_id": item_id,
            "message": f"{item_type.capitalize()} deleted from index"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


class ReindexResponse(BaseModel):
    success: bool
    books_indexed: int
    books_failed: int
    events_indexed: int
    events_failed: int
    total_indexed: int
    total_failed: int
    message: str


@router.post("/reindex-all", response_model=ReindexResponse)
async def reindex_all_endpoint(
    db: AsyncSession = Depends(get_db_dependency),
    batch_size: int = Query(100, ge=1, le=1000, description="Размер батча для обработки")
):
    """
    Полная переиндексация всех книг и мероприятий в Typesense.
    
    Получает все данные из PostgreSQL и индексирует их в Typesense батчами.
    Полезно после массового импорта данных или при необходимости обновить весь индекс.
    """
    logger.info(f"=== Starting full reindex with batch_size={batch_size} ===")
    
    from app.database.queries import get_all_books, get_all_events
    from app.services.typesense_client import index_item
    
    books_indexed = 0
    books_failed = 0
    events_indexed = 0
    events_failed = 0
    
    try:
        # Индексация книг
        logger.info("Starting books indexing...")
        offset = 0
        while True:
            books = await get_all_books(db, limit=batch_size, offset=offset, available_only=False)
            if not books:
                break
            
            for book in books:
                try:
                    success = index_item(book)
                    if success:
                        books_indexed += 1
                    else:
                        books_failed += 1
                        logger.warning(f"Failed to index book id={book.get('id')}")
                except Exception as e:
                    books_failed += 1
                    logger.error(f"Error indexing book id={book.get('id')}: {e}")
            
            offset += batch_size
            logger.info(f"Processed {offset} books... (indexed: {books_indexed}, failed: {books_failed})")
        
        logger.info(f"Books indexing completed. Indexed: {books_indexed}, Failed: {books_failed}")
        
        # Индексация мероприятий
        logger.info("Starting events indexing...")
        offset = 0
        while True:
            events = await get_all_events(db, limit=batch_size, offset=offset)
            if not events:
                break
            
            for event in events:
                try:
                    success = index_item(event)
                    if success:
                        events_indexed += 1
                    else:
                        events_failed += 1
                        logger.warning(f"Failed to index event id={event.get('id')}")
                except Exception as e:
                    events_failed += 1
                    logger.error(f"Error indexing event id={event.get('id')}: {e}")
            
            offset += batch_size
            logger.info(f"Processed {offset} events... (indexed: {events_indexed}, failed: {events_failed})")
        
        logger.info(f"Events indexing completed. Indexed: {events_indexed}, Failed: {events_failed}")
        
        total_indexed = books_indexed + events_indexed
        total_failed = books_failed + events_failed
        
        success = total_failed == 0
        
        return ReindexResponse(
            success=success,
            books_indexed=books_indexed,
            books_failed=books_failed,
            events_indexed=events_indexed,
            events_failed=events_failed,
            total_indexed=total_indexed,
            total_failed=total_failed,
            message=f"Reindex completed. Indexed: {total_indexed}, Failed: {total_failed}"
        )
        
    except Exception as e:
        logger.error(f"Critical error during reindex: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reindex failed: {str(e)}"
        )


@router.get("/stats")
async def get_index_stats():
    """
    Получение статистики индекса Typesense.
    Показывает количество проиндексированных документов.
    """
    try:
        from app.services.typesense_client import client, COLLECTION_NAME
        
        # Получаем информацию о коллекции
        collection_info = client.collections[COLLECTION_NAME].retrieve()
        
        # Получаем количество документов (делаем пустой поиск)
        search_result = client.collections[COLLECTION_NAME].documents.search({
            'q': '*',
            'per_page': 0  # Не возвращаем результаты, только счетчик
        })
        
        return {
            "collection_name": COLLECTION_NAME,
            "total_documents": search_result.get('found', 0),
            "collection_info": {
                "name": collection_info.get('name'),
                "num_documents": collection_info.get('num_documents', 0),
                "created_at": collection_info.get('created_at')
            }
        }
    except Exception as e:
        logger.error(f"Error getting index stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get index stats: {str(e)}"
        )


@router.get("/health")
async def services_health():
    """Проверка работоспособности"""
    from app.database.connection import check_db_connection
    
    db_ok = await check_db_connection()
    
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected"
    }