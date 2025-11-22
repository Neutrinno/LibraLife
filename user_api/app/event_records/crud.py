from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, update
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
import uuid

from app.models import EventRecord, Event
from app.event_records.schemas import EventRegistrationCreate


# ... существующий код ...

class EventRegistrationCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_registration_by_id(self, registration_id: uuid.UUID) -> Optional[EventRecord]:
        result = await self.db.execute(select(EventRecord).where(EventRecord.id == registration_id))
        return result.scalar_one_or_none()

    async def get_registration_by_event_and_email(self, event_id: uuid.UUID, email: str) -> Optional[EventRecord]:
        result = await self.db.execute(
            select(EventRecord).where(
                and_(EventRecord.event_id == event_id, EventRecord.email == email)
            )
        )
        return result.scalar_one_or_none()

    async def get_event_registrations(self, event_id: uuid.UUID) -> List[EventRecord]:
        result = await self.db.execute(
            select(EventRecord).where(EventRecord.event_id == event_id).order_by(EventRecord.registered_at)
        )
        return result.scalars().all()

    async def get_user_registrations(self, email: str) -> List[EventRecord]:
        result = await self.db.execute(
            select(EventRecord).where(EventRecord.email == email).order_by(EventRecord.registered_at)
        )
        return result.scalars().all()

    async def create_registration(self, registration_data: EventRegistrationCreate) -> EventRecord:
        # Проверяем существование мероприятия
        event = await self.db.execute(select(Event).where(Event.id == registration_data.event_id))
        event = event.scalar_one_or_none()

        if not event:
            raise ValueError("Event not found")

        # Проверяем, не записан ли уже пользователь
        existing_registration = await self.get_registration_by_event_and_email(
            registration_data.event_id, registration_data.email
        )
        if existing_registration:
            raise ValueError("User already registered for this event")

        # Проверяем максимальное количество участников
        if event.max_participants is not None:
            current_registrations = await self.get_event_registrations(registration_data.event_id)
            if len(current_registrations) >= event.max_participants:
                raise ValueError("Event is full")

        registration = EventRecord(
            event_id=registration_data.event_id,
            name=registration_data.name,
            surname=registration_data.surname,
            email=registration_data.email
        )

        self.db.add(registration)

        # Увеличиваем счетчик участников
        new_count = (event.participants_count or 0) + 1
        await self.db.execute(
            update(Event)
            .where(Event.id == registration_data.event_id)
            .values(participants_count=new_count)
        )

        await self.db.commit()
        await self.db.refresh(registration)
        return registration

    async def cancel_registration(self, event_id: uuid.UUID, email: str) -> bool:
        registration = await self.get_registration_by_event_and_email(event_id, email)
        if not registration:
            return False

        # Получаем мероприятие для уменьшения счетчика
        event = await self.db.execute(select(Event).where(Event.id == event_id))
        event = event.scalar_one_or_none()

        if event:
            new_count = max(0, (event.participants_count or 0) - 1)
            await self.db.execute(
                update(Event)
                .where(Event.id == event_id)
                .values(participants_count=new_count)
            )

        await self.db.execute(delete(EventRecord).where(EventRecord.id == registration.id))
        await self.db.commit()
        return True

    async def cancel_registration_by_id(self, registration_id: uuid.UUID) -> bool:
        registration = await self.get_registration_by_id(registration_id)
        if not registration:
            return False

        # Получаем мероприятие для уменьшения счетчика
        event = await self.db.execute(select(Event).where(Event.id == registration.event_id))
        event = event.scalar_one_or_none()

        if event:
            new_count = max(0, (event.participants_count or 0) - 1)
            await self.db.execute(
                update(Event)
                .where(Event.id == registration.event_id)
                .values(participants_count=new_count)
            )

        await self.db.execute(delete(EventRecord).where(EventRecord.id == registration_id))
        await self.db.commit()
        return True

    async def get_registrations_count(self, event_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(EventRecord).where(EventRecord.event_id == event_id)
        )
        return len(result.scalars().all())