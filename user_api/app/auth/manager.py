import logging
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.database import get_user_db, get_async_session, User
from app.auth.shemas import UserCreateExtended

logger = logging.getLogger(__name__)
SECRET = "SECRET"


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def __init__(self, user_db, session: AsyncSession):
        super().__init__(user_db)
        self.session = session

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Вызывается после успешной регистрации пользователя.
        """
        print(f"User {user.id} has registered.")

    async def create(self, user_create: UserCreateExtended, safe: bool = True, **kwargs) -> User:
        """
        Создает пользователя и инициализирует связанные сущности: кошелек, бонусный счет и статус лояльности.
        """
        full_name = user_create.full_name
        user = await super().create(user_create, safe=safe)

        update_dict = {
            "full_name": full_name,
        }
        await self.user_db.update(user, update_dict)

        return user


async def get_user_manager(
    user_db=Depends(get_user_db),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Dependency для получения экземпляра UserManager.
    """
    yield UserManager(user_db, session)
