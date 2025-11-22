from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import BookRental, Book, User
from app.book_rental.schemas import BookRentalCreate, BookRentalResponse, BookRentalReturn, BookRentalExtend, BookRentalListResponse, \
    UserRentalStats
from app.book_rental.crud import BookRentalCRUD

book_rental_router = APIRouter(prefix="/book-rentals", tags=["Book Rentals"])


@book_rental_router.post("/", response_model=BookRentalResponse, status_code=status.HTTP_201_CREATED)
async def create_book_rental(
        rental_data: BookRentalCreate,
        user_id: uuid.UUID = Query(..., description="ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    """
    Взять книгу в аренду
    """
    crud = BookRentalCRUD(db)
    try:
        rental = await crud.create_rental(user_id, rental_data)

        # Получаем дополнительную информацию для ответа
        book_result = await db.execute(select(Book.title).where(Book.id == rental.book_id))
        book_title = book_result.scalar_one_or_none()

        user_result = await db.execute(select(User.email).where(User.id == rental.user_id))
        user_email = user_result.scalar_one_or_none()

        return BookRentalResponse(
            id=rental.id,
            book_id=rental.book_id,
            user_id=rental.user_id,
            taken_date=rental.taken_date,
            due_date=rental.due_date,
            returned_date=rental.returned_date,
            is_returned=rental.is_returned,
            is_extended=rental.is_extended,
            extension_count=rental.extension_count,
            notes=rental.notes,
            book_title=book_title,
            user_email=user_email
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating book rental: {str(e)}"
        )


@book_rental_router.post("/{rental_id}/return", response_model=BookRentalResponse)
async def return_book(
        rental_id: uuid.UUID,
        return_data: BookRentalReturn,
        db: AsyncSession = Depends(get_db)
):
    """
    Вернуть книгу
    """
    crud = BookRentalCRUD(db)
    rental = await crud.return_book(rental_id, return_data.notes)

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found or book already returned"
        )

    # Получаем дополнительную информацию для ответа
    book_result = await db.execute(select(Book.title).where(Book.id == rental.book_id))
    book_title = book_result.scalar_one_or_none()

    user_result = await db.execute(select(User.email).where(User.id == rental.user_id))
    user_email = user_result.scalar_one_or_none()

    return BookRentalResponse(
        id=rental.id,
        book_id=rental.book_id,
        user_id=rental.user_id,
        taken_date=rental.taken_date,
        due_date=rental.due_date,
        returned_date=rental.returned_date,
        is_returned=rental.is_returned,
        is_extended=rental.is_extended,
        extension_count=rental.extension_count,
        notes=rental.notes,
        book_title=book_title,
        user_email=user_email
    )


@book_rental_router.post("/{rental_id}/extend", response_model=BookRentalResponse)
async def extend_rental(
        rental_id: uuid.UUID,
        extend_data: BookRentalExtend,
        db: AsyncSession = Depends(get_db)
):
    """
    Продлить срок аренды книги
    """
    crud = BookRentalCRUD(db)
    try:
        rental = await crud.extend_rental(rental_id, extend_data)

        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rental not found or book already returned"
            )

        # Получаем дополнительную информацию для ответа
        book_result = await db.execute(select(Book.title).where(Book.id == rental.book_id))
        book_title = book_result.scalar_one_or_none()

        user_result = await db.execute(select(User.email).where(User.id == rental.user_id))
        user_email = user_result.scalar_one_or_none()

        return BookRentalResponse(
            id=rental.id,
            book_id=rental.book_id,
            user_id=rental.user_id,
            taken_date=rental.taken_date,
            due_date=rental.due_date,
            returned_date=rental.returned_date,
            is_returned=rental.is_returned,
            is_extended=rental.is_extended,
            extension_count=rental.extension_count,
            notes=rental.notes,
            book_title=book_title,
            user_email=user_email
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ... остальные эндпоинты для получения списков аренд, статистики и т.д.