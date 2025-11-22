from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr, validator
import uuid

from database import get_async_session
from models import User
from security import get_password_hash

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: UserRegister,
        db: AsyncSession = Depends(get_async_session)
):
    """
    Регистрация нового пользователя
    """
    # Проверяем, существует ли пользователь с таким email
    existing_user = await db.execute(
        User.__table__.select().where(User.email == user_data.email)
    )
    existing_user = existing_user.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    try:
        new_user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False,
            is_verified=False
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            registered_at=new_user.registered_at.isoformat()
        )

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user"
        )