from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
import uuid
from typing import Optional, List

from models import User
from security import get_password_hash
from schemas import UserCreate, UserUpdate


class UserCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_users_count(self) -> int:
        result = await self.db.execute(select(User))
        return len(result.scalars().all())

    async def create_user(self, user_data: UserCreate) -> User:
        # Проверяем, существует ли пользователь с таким email
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False,
            is_verified=False
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        update_data = user_data.dict(exclude_unset=True)

        # Если обновляется пароль, хешируем его
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))

        if update_data:
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
                .returning(User)
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            user = result.scalar_one_or_none()
            if user:
                await self.db.refresh(user)
            return user
        return None

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        await self.db.execute(delete(User).where(User.id == user_id))
        await self.db.commit()
        return True

    async def deactivate_user(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.update_user(user_id, UserUpdate(is_active=False))

    async def activate_user(self, user_id: uuid.UUID) -> Optional[User]:
        return await self.update_user(user_id, UserUpdate(is_active=True))