from datetime import datetime
from fastapi_users import schemas
from typing import Optional
from pydantic import ConfigDict

from uuid import UUID


class UserRead(schemas.BaseUser[int]):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    registered_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserCreate(schemas.BaseUserCreate):
    email: str
    password: str
    registered_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserCreateExtended(schemas.BaseUserCreate):
    full_name: str

class UserReadExtended(schemas.BaseUser[int]):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    registered_at: Optional[datetime]