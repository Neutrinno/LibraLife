from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List, Optional

from app.database import get_db
from app.models import Book
from app.books.schemas import BookCreate, BookUpdate, BookResponse, BookListResponse
from app.books.crud import BookCRUD

# ... существующие роутеры ...

book_router = APIRouter(prefix="/books", tags=["Books"])


@book_router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
        book_data: BookCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Создание новой книги
    """
    crud = BookCRUD(db)
    try:
        book = await crud.create_book(book_data)
        return BookResponse(
            id=book.id,
            author=book.author,
            title=book.title,
            category=book.category,
            gost_title=book.gost_title,
            description=book.description,
            is_available=book.is_available,
            reviews_count=0
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating book: {str(e)}"
        )


@book_router.get("/", response_model=BookListResponse)
async def get_books(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        available_only: bool = Query(False, description="Show only available books"),
        db: AsyncSession = Depends(get_db)
):
    """
    Получение списка книг с пагинацией
    """
    crud = BookCRUD(db)
    books = await crud.get_all_books(skip=skip, limit=limit, available_only=available_only)
    total = await crud.get_books_count(available_only=available_only)

    return BookListResponse(
        books=[
            BookResponse(
                id=book.id,
                author=book.author,
                title=book.title,
                category=book.category,
                gost_title=book.gost_title,
                description=book.description,
                is_available=book.is_available,
                reviews_count=len(book.reviews) if book.reviews else 0
            ) for book in books
        ],
        total=total
    )


@book_router.get("/{book_id}", response_model=BookResponse)
async def get_book(
        book_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение книги по ID
    """
    crud = BookCRUD(db)
    book = await crud.get_book_by_id(book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return BookResponse(
        id=book.id,
        author=book.author,
        title=book.title,
        category=book.category,
        gost_title=book.gost_title,
        description=book.description,
        is_available=book.is_available,
        reviews_count=len(book.reviews) if book.reviews else 0
    )


@book_router.get("/search/", response_model=BookListResponse)
async def search_books(
        q: str = Query(..., min_length=1, description="Search term"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: AsyncSession = Depends(get_db)
):
    """
    Поиск книг по названию, автору, категории или описанию
    """
    crud = BookCRUD(db)
    books = await crud.search_books(search_term=q, skip=skip, limit=limit)

    return BookListResponse(
        books=[
            BookResponse(
                id=book.id,
                author=book.author,
                title=book.title,
                category=book.category,
                gost_title=book.gost_title,
                description=book.description,
                is_available=book.is_available,
                reviews_count=len(book.reviews) if book.reviews else 0
            ) for book in books
        ],
        total=len(books)
    )


@book_router.get("/category/{category}", response_model=BookListResponse)
async def get_books_by_category(
        category: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: AsyncSession = Depends(get_db)
):
    """
    Получение книг по категории
    """
    crud = BookCRUD(db)
    books = await crud.get_books_by_category(category=category, skip=skip, limit=limit)

    return BookListResponse(
        books=[
            BookResponse(
                id=book.id,
                author=book.author,
                title=book.title,
                category=book.category,
                gost_title=book.gost_title,
                description=book.description,
                is_available=book.is_available,
                reviews_count=len(book.reviews) if book.reviews else 0
            ) for book in books
        ],
        total=len(books)
    )


@book_router.get("/author/{author}", response_model=BookListResponse)
async def get_books_by_author(
        author: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: AsyncSession = Depends(get_db)
):
    """
    Получение книг по автору
    """
    crud = BookCRUD(db)
    books = await crud.get_books_by_author(author=author, skip=skip, limit=limit)

    return BookListResponse(
        books=[
            BookResponse(
                id=book.id,
                author=book.author,
                title=book.title,
                category=book.category,
                gost_title=book.gost_title,
                description=book.description,
                is_available=book.is_available,
                reviews_count=len(book.reviews) if book.reviews else 0
            ) for book in books
        ],
        total=len(books)
    )


@book_router.put("/{book_id}", response_model=BookResponse)
async def update_book(
        book_id: uuid.UUID,
        book_data: BookUpdate,
        db: AsyncSession = Depends(get_db)
):
    """
    Обновление данных книги
    """
    crud = BookCRUD(db)

    # Проверяем существование книги
    existing_book = await crud.get_book_by_id(book_id)
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    updated_book = await crud.update_book(book_id, book_data)
    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating book"
        )

    return BookResponse(
        id=updated_book.id,
        author=updated_book.author,
        title=updated_book.title,
        category=updated_book.category,
        gost_title=updated_book.gost_title,
        description=updated_book.description,
        is_available=updated_book.is_available,
        reviews_count=len(updated_book.reviews) if updated_book.reviews else 0
    )


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
        book_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Удаление книги
    """
    crud = BookCRUD(db)

    # Проверяем существование книги
    existing_book = await crud.get_book_by_id(book_id)
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    success = await crud.delete_book(book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting book"
        )


@book_router.patch("/{book_id}/available", response_model=BookResponse)
async def mark_book_available(
        book_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Пометить книгу как доступную
    """
    crud = BookCRUD(db)
    book = await crud.mark_as_available(book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return BookResponse(
        id=book.id,
        author=book.author,
        title=book.title,
        category=book.category,
        gost_title=book.gost_title,
        description=book.description,
        is_available=book.is_available,
        reviews_count=len(book.reviews) if book.reviews else 0
    )


@book_router.patch("/{book_id}/unavailable", response_model=BookResponse)
async def mark_book_unavailable(
        book_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Пометить книгу как недоступную
    """
    crud = BookCRUD(db)
    book = await crud.mark_as_unavailable(book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return BookResponse(
        id=book.id,
        author=book.author,
        title=book.title,
        category=book.category,
        gost_title=book.gost_title,
        description=book.description,
        is_available=book.is_available,
        reviews_count=len(book.reviews) if book.reviews else 0
    )