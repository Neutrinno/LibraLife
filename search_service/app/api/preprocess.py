from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from app.database.connection import get_db
from app.database.queries import get_service_by_id_query
import logging
import traceback

from app.database.queries import get_service_by_id

router = APIRouter()
logger = logging.getLogger(__name__)


class IndexRequest(BaseModel):
    id: UUID

class IndexResponse(BaseModel):
    success: bool
    service_id: UUID
    message: str


def get_db_dependency():
    """Dependency для FastAPI"""
    try:
        with get_db() as conn:
            yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}"
        )


@router.post("/index", response_model=IndexResponse)
def index_service_endpoint(
        request: IndexRequest,
        db=Depends(get_db_dependency)
):
    """Индексация услуги в Typesense по UUID"""
    logger.info(f"=== Index request for service_id={request.id} ===")

    try:
        service_dict = get_service_by_id(db, request.id)

        if not service_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with id {request.id} not found or inactive"
            )
        
        from app.services.typesense_client import index_service
        success = index_service(service_dict)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to index service in Typesense"
            )

        return IndexResponse(
            success=True,
            service_id=request.id,
            message="Service indexed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unhandled indexing error for service {request.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during indexing."
        )


@router.delete("/index/{service_id}")
def delete_service_endpoint(service_id: int):
    """Удаление услуги из индекса"""
    try:
        from app.services.typesense_client import delete_service
        success = delete_service(service_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete service from index"
            )
        
        return {
            "success": True,
            "service_id": service_id,
            "message": "Service deleted from index"
        }
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/health")
def services_health():
    """Проверка работоспособности"""
    from app.database.connection import check_db_connection
    
    db_ok = check_db_connection()
    
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected"
    }