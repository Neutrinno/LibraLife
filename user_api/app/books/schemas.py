from pydantic import BaseModel, ConfigDict
from pydantic.v1 import validator
from typing import Optional
import uuid

class BookBase(BaseModel):
    author: str
    title: str
    category: Optional[str] = None
    gost_title: Optional[str] = None
    description: Optional[str] = None
    is_available: Optional[bool] = True

class BookCreate(BookBase):
    @validator('title', 'author')
    def validate_fields(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Field cannot be empty')
        return v.strip()

class BookUpdate(BaseModel):
    author: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
    gost_title: Optional[str] = None
    description: Optional[str] = None
    is_available: Optional[bool] = None

    @validator('title', 'author')
    def validate_fields(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Field cannot be empty')
        return v.strip() if v else v

class BookResponse(BookBase):
    id: uuid.UUID
    reviews_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class BookListResponse(BaseModel):
    books: list[BookResponse]
    total: int