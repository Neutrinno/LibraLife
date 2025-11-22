from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
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


@router.get("/health")
async def services_health():
    """Проверка работоспособности"""
    from app.database.connection import check_db_connection
    
    db_ok = await check_db_connection()
    
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected"
    }