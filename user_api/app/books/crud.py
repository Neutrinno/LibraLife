from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
import uuid

from app.models import Book, Review
from app.books.schemas import BookCreate, BookUpdate




class BookCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_book_by_id(self, book_id: uuid.UUID) -> Optional[Book]:
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.reviews))
            .where(Book.id == book_id)
        )
        return result.scalar_one_or_none()

    async def get_book_by_title_author(self, title: str, author: str) -> Optional[Book]:
        result = await self.db.execute(
            select(Book).where(
                and_(Book.title.ilike(title), Book.author.ilike(author))
            )
        )
        return result.scalar_one_or_none()

    async def get_all_books(
            self,
            skip: int = 0,
            limit: int = 100,
            available_only: bool = False
    ) -> List[Book]:
        query = select(Book).options(selectinload(Book.reviews))

        if available_only:
            query = query.where(Book.is_available == True)

        query = query.order_by(Book.title).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_books_by_category(
            self,
            category: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Book]:
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.reviews))
            .where(Book.category.ilike(f"%{category}%"))
            .order_by(Book.title)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_books_by_author(
            self,
            author: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Book]:
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.reviews))
            .where(Book.author.ilike(f"%{author}%"))
            .order_by(Book.title)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search_books(
            self,
            search_term: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Book]:
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.reviews))
            .where(
                or_(
                    Book.title.ilike(f"%{search_term}%"),
                    Book.author.ilike(f"%{search_term}%"),
                    Book.category.ilike(f"%{search_term}%"),
                    Book.description.ilike(f"%{search_term}%")
                )
            )
            .order_by(Book.title)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_books_count(self, available_only: bool = False) -> int:
        query = select(Book)
        if available_only:
            query = query.where(Book.is_available == True)

        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def create_book(self, book_data: BookCreate) -> Book:
        # Проверяем, существует ли книга с таким названием и автором
        existing_book = await self.get_book_by_title_author(book_data.title, book_data.author)
        if existing_book:
            raise ValueError("Book with this title and author already exists")

        book = Book(
            author=book_data.author,
            title=book_data.title,
            category=book_data.category,
            gost_title=book_data.gost_title,
            description=book_data.description,
            is_available=book_data.is_available
        )

        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book, ["reviews"])
        return book

    async def update_book(self, book_id: uuid.UUID, book_data: BookUpdate) -> Optional[Book]:
        update_data = book_data.model_dump(exclude_unset=True)

        if update_data:
            stmt = (
                update(Book)
                .where(Book.id == book_id)
                .values(**update_data)
                .returning(Book)
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            book = result.scalar_one_or_none()
            if book:
                # Загружаем reviews после обновления
                await self.db.refresh(book, ["reviews"])
            return book
        return None

    async def delete_book(self, book_id: uuid.UUID) -> bool:
        book = await self.get_book_by_id(book_id)
        if not book:
            return False

        await self.db.execute(delete(Book).where(Book.id == book_id))
        await self.db.commit()
        return True

    async def mark_as_available(self, book_id: uuid.UUID) -> Optional[Book]:
        return await self.update_book(book_id, BookUpdate(is_available=True))

    async def mark_as_unavailable(self, book_id: uuid.UUID) -> Optional[Book]:
        return await self.update_book(book_id, BookUpdate(is_available=False))

    async def get_books_with_reviews_count(self, skip: int = 0, limit: int = 100) -> List[Book]:
        # Подзапрос для подсчета отзывов
        reviews_count_subquery = (
            select(
                Review.book_id,
                func.count(Review.id).label('reviews_count')
            )
            .where(Review.book_id.isnot(None))
            .group_by(Review.book_id)
            .subquery()
        )

        result = await self.db.execute(
            select(
                Book,
                func.coalesce(reviews_count_subquery.c.reviews_count, 0).label('reviews_count')
            )
            .outerjoin(reviews_count_subquery, Book.id == reviews_count_subquery.c.book_id)
            .order_by(Book.title)
            .offset(skip)
            .limit(limit)
        )

        books_with_counts = []
        for book, reviews_count in result:
            book.reviews_count = reviews_count
            books_with_counts.append(book)

        return books_with_counts