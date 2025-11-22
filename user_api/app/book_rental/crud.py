from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import uuid

from app.models import BookRental, Book, User
from app.book_rental.schemas import BookRentalCreate, BookRentalExtend


class BookRentalCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rental_by_id(self, rental_id: uuid.UUID) -> Optional[BookRental]:
        result = await self.db.execute(select(BookRental).where(BookRental.id == rental_id))
        return result.scalar_one_or_none()

    async def get_active_rental_by_book(self, book_id: uuid.UUID) -> Optional[BookRental]:
        result = await self.db.execute(
            select(BookRental).where(
                and_(
                    BookRental.book_id == book_id,
                    BookRental.is_returned == False
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_rentals(
            self,
            user_id: uuid.UUID,
            active_only: bool = False,
            skip: int = 0,
            limit: int = 100
    ) -> List[BookRental]:
        query = select(BookRental).where(BookRental.user_id == user_id)

        if active_only:
            query = query.where(BookRental.is_returned == False)

        query = query.order_by(BookRental.taken_date.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_book_rental_history(
            self,
            book_id: uuid.UUID,
            skip: int = 0,
            limit: int = 100
    ) -> List[BookRental]:
        result = await self.db.execute(
            select(BookRental)
            .where(BookRental.book_id == book_id)
            .order_by(BookRental.taken_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_overdue_rentals(self) -> List[BookRental]:
        result = await self.db.execute(
            select(BookRental).where(
                and_(
                    BookRental.is_returned == False,
                    BookRental.due_date < datetime.utcnow()
                )
            ).order_by(BookRental.due_date)
        )
        return result.scalars().all()

    async def get_all_rentals(
            self,
            active_only: bool = False,
            skip: int = 0,
            limit: int = 100
    ) -> List[BookRental]:
        query = select(BookRental)

        if active_only:
            query = query.where(BookRental.is_returned == False)

        query = query.order_by(BookRental.taken_date.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_rental(self, user_id: uuid.UUID, rental_data: BookRentalCreate) -> BookRental:
        # Проверяем существование книги
        book = await self.db.execute(select(Book).where(Book.id == rental_data.book_id))
        book = book.scalar_one_or_none()

        if not book:
            raise ValueError("Book not found")

        # Проверяем доступность книги
        if not book.is_available:
            raise ValueError("Book is not available")

        # Проверяем, не взята ли уже книга
        active_rental = await self.get_active_rental_by_book(rental_data.book_id)
        if active_rental:
            raise ValueError("Book is already taken")

        # Создаем запись о выдаче
        rental = BookRental(
            book_id=rental_data.book_id,
            user_id=user_id,
            due_date=rental_data.due_date,
            notes=rental_data.notes
        )

        # Помечаем книгу как недоступную
        book.is_available = False

        self.db.add(rental)
        await self.db.commit()
        await self.db.refresh(rental)
        return rental

    async def return_book(self, rental_id: uuid.UUID, notes: Optional[str] = None) -> Optional[BookRental]:
        rental = await self.get_rental_by_id(rental_id)
        if not rental or rental.is_returned:
            return None

        # Получаем книгу для обновления статуса
        book = await self.db.execute(select(Book).where(Book.id == rental.book_id))
        book = book.scalar_one_or_none()

        if book:
            book.is_available = True

        # Обновляем запись о выдаче
        rental.is_returned = True
        rental.returned_date = datetime.utcnow()
        if notes:
            rental.notes = notes

        await self.db.commit()
        await self.db.refresh(rental)
        return rental

    async def extend_rental(self, rental_id: uuid.UUID, extend_data: BookRentalExtend) -> Optional[BookRental]:
        rental = await self.get_rental_by_id(rental_id)
        if not rental or rental.is_returned:
            return None

        # Проверяем лимит продлений (максимум 2 продления)
        if rental.extension_count >= 2:
            raise ValueError("Maximum extension limit reached")

        # Обновляем дату возврата
        rental.due_date = extend_data.new_due_date
        rental.is_extended = True
        rental.extension_count += 1
        if extend_data.notes:
            rental.notes = extend_data.notes

        await self.db.commit()
        await self.db.refresh(rental)
        return rental

    async def get_user_rental_stats(self, user_id: uuid.UUID) -> Tuple[int, int, int]:
        # Активные аренды
        active_result = await self.db.execute(
            select(BookRental).where(
                and_(
                    BookRental.user_id == user_id,
                    BookRental.is_returned == False
                )
            )
        )
        active_rentals = len(active_result.scalars().all())

        # Все аренды
        total_result = await self.db.execute(
            select(BookRental).where(BookRental.user_id == user_id)
        )
        total_rentals = len(total_result.scalars().all())

        # Просроченные аренды
        overdue_result = await self.db.execute(
            select(BookRental).where(
                and_(
                    BookRental.user_id == user_id,
                    BookRental.is_returned == False,
                    BookRental.due_date < datetime.utcnow()
                )
            )
        )
        overdue_rentals = len(overdue_result.scalars().all())

        return active_rentals, total_rentals, overdue_rentals

    async def get_rentals_count(self, active_only: bool = False) -> int:
        query = select(BookRental)
        if active_only:
            query = query.where(BookRental.is_returned == False)

        result = await self.db.execute(query)
        return len(result.scalars().all())