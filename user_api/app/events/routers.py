from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
import uuid
import os

from starlette.responses import StreamingResponse

from app.database import get_db
from app.events.schemas import EventCreate, EventUpdate, EventResponse, EventListResponse, EventDocumentData
from app.events.crud import EventCRUD
from app.events.document_generator import EventDocumentGenerator

# ... существующие роутеры пользователей ...

event_router = APIRouter(prefix="/events", tags=["Events"])


@event_router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
        event_data: EventCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Создание нового мероприятия
    """
    crud = EventCRUD(db)
    try:
        event = await crud.create_event(event_data)
        return event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating event: {str(e)}"
        )


@event_router.get("/", response_model=EventListResponse)
async def get_events(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        upcoming_only: bool = Query(False, description="Show only upcoming events"),
        db: AsyncSession = Depends(get_db)
):
    """
    Получение списка мероприятий с пагинацией
    """
    crud = EventCRUD(db)
    events = await crud.get_all_events(skip=skip, limit=limit, upcoming_only=upcoming_only)
    total = await crud.get_events_count(upcoming_only=upcoming_only)

    return EventListResponse(events=events, total=total)


@event_router.get("/{event_id}", response_model=EventResponse)
async def get_event(
        event_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение мероприятия по ID
    """
    crud = EventCRUD(db)
    event = await crud.get_event_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event


@event_router.get("/search/", response_model=EventListResponse)
async def search_events(
        q: str = Query(..., min_length=1, description="Search term"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: AsyncSession = Depends(get_db)
):
    """
    Поиск мероприятий по названию, описанию или локации
    """
    crud = EventCRUD(db)
    events = await crud.search_events(search_term=q, skip=skip, limit=limit)

    return EventListResponse(events=events, total=len(events))


@event_router.get("/date-range/", response_model=EventListResponse)
async def get_events_by_date_range(
        start_date: datetime = Query(..., description="Start date"),
        end_date: datetime = Query(..., description="End date"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: AsyncSession = Depends(get_db)
):
    """
    Получение мероприятий в указанном диапазоне дат
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )

    crud = EventCRUD(db)
    events = await crud.get_events_by_date_range(
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

    return EventListResponse(events=events, total=len(events))


@event_router.put("/{event_id}", response_model=EventResponse)
async def update_event(
        event_id: uuid.UUID,
        event_data: EventUpdate,
        db: AsyncSession = Depends(get_db)
):
    """
    Обновление данных мероприятия
    """
    crud = EventCRUD(db)

    # Проверяем существование мероприятия
    existing_event = await crud.get_event_by_id(event_id)
    if not existing_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    updated_event = await crud.update_event(event_id, event_data)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating event"
        )

    return updated_event


@event_router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
        event_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Удаление мероприятия
    """
    crud = EventCRUD(db)

    # Проверяем существование мероприятия
    existing_event = await crud.get_event_by_id(event_id)
    if not existing_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    success = await crud.delete_event(event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting event"
        )


@event_router.patch("/{event_id}/increment-participants", response_model=EventResponse)
async def increment_participants(
        event_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Увеличение счетчика участников мероприятия
    """
    crud = EventCRUD(db)
    event = await crud.increment_participants(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event


@event_router.patch("/{event_id}/decrement-participants", response_model=EventResponse)
async def decrement_participants(
        event_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Уменьшение счетчика участников мероприятия
    """
    crud = EventCRUD(db)
    event = await crud.decrement_participants(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return event


from fastapi import Response


@event_router.post("/{event_id}/download-report")
async def download_event_report(
        event_id: uuid.UUID,
        document_data: EventDocumentData,
        db: AsyncSession = Depends(get_db)
):
    """
    Генерация и немедленное скачивание отчета о мероприятии
    """
    # Получаем мероприятие из базы данных
    crud = EventCRUD(db)
    event = await crud.get_event_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мероприятие не найдено"
        )

    # Подготавливаем данные для документа
    event_data = {
        'id': event_id,
        'date': event.date,
        'event_type': document_data.event_type,
        'title': event.title,
        'location': event.location or "Не указано",
        'participants_count': event.participants_count,
        'documents_info': document_data.documents_info,
        'content': document_data.content,
        'organizers': document_data.organizers,
        'librarian': document_data.librarian
    }

    # Генерируем документ в памяти
    generator = EventDocumentGenerator()
    file_stream = generator.generate_event_report(event_data)

    # Читаем содержимое файла
    file_content = file_stream.getvalue()

    # Используем Response с байтовым содержимым
    return Response(
        content=file_content,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers={
            'Content-Disposition': 'attachment; filename="event_report.docx"'
        }
    )