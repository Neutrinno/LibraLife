from pydantic import BaseModel, ConfigDict
from pydantic.v1 import validator
from datetime import datetime, timedelta
from typing import Optional
import uuid

class BookRentalBase(BaseModel):
    book_id: uuid.UUID
    due_date: datetime
    notes: Optional[str] = None

class BookRentalCreate(BookRentalBase):
    @validator('due_date')
    def validate_due_date(cls, v):
        if v <= datetime.now():
            raise ValueError('Due date must be in the future')
        max_due_date = datetime.now() + timedelta(days=90)  # Максимум 90 дней
        if v > max_due_date:
            raise ValueError('Due date cannot be more than 90 days in the future')
        return v

class BookRentalReturn(BaseModel):
    notes: Optional[str] = None

class BookRentalExtend(BaseModel):
    new_due_date: datetime
    notes: Optional[str] = None

    @validator('new_due_date')
    def validate_new_due_date(cls, v, values):
        if v <= datetime.now():
            raise ValueError('New due date must be in the future')
        max_extension = datetime.now() + timedelta(days=30)  # Максимум +30 дней от текущей даты
        if v > max_extension:
            raise ValueError('Extension cannot be more than 30 days from now')
        return v

class BookRentalResponse(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    user_id: uuid.UUID
    taken_date: datetime
    due_date: datetime
    returned_date: Optional[datetime] = None
    is_returned: bool
    is_extended: bool
    extension_count: int
    notes: Optional[str] = None
    book_title: Optional[str] = None
    user_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class BookRentalListResponse(BaseModel):
    rentals: list[BookRentalResponse]
    total: int

class UserRentalStats(BaseModel):
    active_rentals: int
    total_rentals: int
    overdue_rentals: int