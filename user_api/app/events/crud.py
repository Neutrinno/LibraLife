from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List
import uuid

from app.models import Event
from app.events.schemas import EventCreate, EventUpdate


# ... существующий UserCRUD ...

class EventCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_event_by_id(self, event_id: uuid.UUID) -> Optional[Event]:
        result = await self.db.execute(select(Event).where(Event.id == event_id))
        return result.scalar_one_or_none()

    async def get_all_events(
            self,
            skip: int = 0,
            limit: int = 100,
            upcoming_only: bool = False
    ) -> List[Event]:
        query = select(Event)

        if upcoming_only:
            # Используем naive datetime для совместимости с БД
            now = datetime.utcnow()
            query = query.where(Event.date >= now)

        query = query.order_by(Event.date).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_events_by_date_range(
            self,
            start_date: datetime,
            end_date: datetime,
            skip: int = 0,
            limit: int = 100
    ) -> List[Event]:
        result = await self.db.execute(
            select(Event)
            .where(and_(Event.date >= start_date, Event.date <= end_date))
            .order_by(Event.date)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_events_count(self, upcoming_only: bool = False) -> int:
        query = select(Event)
        if upcoming_only:
            # Используем naive datetime для совместимости с БД
            now = datetime.utcnow()
            query = query.where(Event.date >= now)

        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def create_event(self, event_data: EventCreate) -> Event:
        event = Event(
            title=event_data.title,
            description=event_data.description,
            date=event_data.date,
            location=event_data.location,
            participants_count=event_data.participants_count
        )

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def update_event(self, event_id: uuid.UUID, event_data: EventUpdate) -> Optional[Event]:
        update_data = event_data.model_dump(exclude_unset=True)

        if update_data:
            stmt = (
                update(Event)
                .where(Event.id == event_id)
                .values(**update_data)
                .returning(Event)
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            event = result.scalar_one_or_none()
            if event:
                await self.db.refresh(event)
            return event
        return None

    async def delete_event(self, event_id: uuid.UUID) -> bool:
        event = await self.get_event_by_id(event_id)
        if not event:
            return False

        await self.db.execute(delete(Event).where(Event.id == event_id))
        await self.db.commit()
        return True

    async def increment_participants(self, event_id: uuid.UUID) -> Optional[Event]:
        event = await self.get_event_by_id(event_id)
        if not event:
            return None

        new_count = (event.participants_count or 0) + 1
        stmt = (
            update(Event)
            .where(Event.id == event_id)
            .values(participants_count=new_count)
            .returning(Event)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        updated_event = result.scalar_one_or_none()
        if updated_event:
            await self.db.refresh(updated_event)
        return updated_event

    async def decrement_participants(self, event_id: uuid.UUID) -> Optional[Event]:
        event = await self.get_event_by_id(event_id)
        if not event:
            return None

        # Не позволяем уйти в отрицательные значения
        new_count = max(0, event.participants_count - 1)

        stmt = (
            update(Event)
            .where(Event.id == event_id)
            .values(participants_count=new_count)
            .returning(Event)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        updated_event = result.scalar_one_or_none()
        if updated_event:
            await self.db.refresh(updated_event)
        return updated_event

    async def search_events(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Event]:
        result = await self.db.execute(
            select(Event)
            .where(
                or_(
                    Event.title.ilike(f"%{search_term}%"),
                    Event.description.ilike(f"%{search_term}%"),
                    Event.location.ilike(f"%{search_term}%")
                )
            )
            .order_by(Event.date)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()