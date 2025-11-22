from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.users.schemas import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.users.crud import UserCRUD

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Создание нового пользователя
    """
    crud = UserCRUD(db)
    try:
        user = await crud.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@user_router.get("/", response_model=UserListResponse)
async def get_users(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        db: AsyncSession = Depends(get_db)
):
    """
    Получение списка пользователей с пагинацией
    """
    crud = UserCRUD(db)
    users = await crud.get_all_users(skip=skip, limit=limit)
    total = await crud.get_users_count()

    return UserListResponse(users=users, total=total)


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение пользователя по ID
    """
    crud = UserCRUD(db)
    user = await crud.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@user_router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(
        email: str,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение пользователя по email
    """
    crud = UserCRUD(db)
    user = await crud.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: uuid.UUID,
        user_data: UserUpdate,
        db: AsyncSession = Depends(get_db)
):
    """
    Обновление данных пользователя
    """
    crud = UserCRUD(db)

    # Проверяем существование пользователя
    existing_user = await crud.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Если меняется email, проверяем его уникальность
    if user_data.email and user_data.email != existing_user.email:
        user_with_email = await crud.get_user_by_email(user_data.email)
        if user_with_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

    updated_user = await crud.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )

    return updated_user


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Удаление пользователя
    """
    crud = UserCRUD(db)

    # Проверяем существование пользователя
    existing_user = await crud.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    success = await crud.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )


@user_router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Деактивация пользователя
    """
    crud = UserCRUD(db)
    user = await crud.deactivate_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@user_router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
        user_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Активация пользователя
    """
    crud = UserCRUD(db)
    user = await crud.activate_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user