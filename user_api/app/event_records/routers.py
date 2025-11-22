from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List

from app.database import get_db
from app.models import EventRecord
from app.event_records.schemas import EventRegistrationCreate, EventRegistrationResponse, EventRegistrationCancel
from app.event_records.crud import EventRegistrationCRUD

# ... существующие роутеры ...

event_registration_router = APIRouter(prefix="/event-registrations", tags=["Event Registrations"])


@event_registration_router.post("/register", response_model=EventRegistrationResponse,
                                status_code=status.HTTP_201_CREATED)
async def register_for_event(
        registration_data: EventRegistrationCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Запись пользователя на мероприятие
    """
    crud = EventRegistrationCRUD(db)
    try:
        registration = await crud.create_registration(registration_data)
        return registration
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering for event: {str(e)}"
        )


@event_registration_router.post("/cancel", status_code=status.HTTP_200_OK)
async def cancel_event_registration(
        cancel_data: EventRegistrationCancel,
        event_id: uuid.UUID = Query(..., description="ID мероприятия"),
        db: AsyncSession = Depends(get_db)
):
    """
    Отмена записи на мероприятие по email
    """
    crud = EventRegistrationCRUD(db)
    success = await crud.cancel_registration(event_id, cancel_data.email)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    return {"message": "Registration cancelled successfully"}


@event_registration_router.delete("/{registration_id}", status_code=status.HTTP_200_OK)
async def cancel_registration_by_id(
        registration_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Отмена записи на мероприятие по ID регистрации
    """
    crud = EventRegistrationCRUD(db)
    success = await crud.cancel_registration_by_id(registration_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    return {"message": "Registration cancelled successfully"}


@event_registration_router.get("/event/{event_id}", response_model=List[EventRegistrationResponse])
async def get_event_registrations(
        event_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение всех записей на конкретное мероприятие
    """
    crud = EventRegistrationCRUD(db)
    registrations = await crud.get_event_registrations(event_id)
    return registrations


@event_registration_router.get("/user/{email}", response_model=List[EventRegistrationResponse])
async def get_user_registrations(
        email: str,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение всех записей пользователя по email
    """
    crud = EventRegistrationCRUD(db)
    registrations = await crud.get_user_registrations(email)
    return registrations


@event_registration_router.get("/{registration_id}", response_model=EventRegistrationResponse)
async def get_registration(
        registration_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о конкретной записи
    """
    crud = EventRegistrationCRUD(db)
    registration = await crud.get_registration_by_id(registration_id)

    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    return registration