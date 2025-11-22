from pydantic import BaseModel, ConfigDict
from pydantic.v1 import validator
from datetime import datetime, timezone
from typing import Optional, Union
import uuid


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Union[str, datetime]  # Принимаем строку или datetime
    location: Optional[str] = None
    participants_count: Optional[int] = 0


class EventCreate(EventBase):
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('participants_count')
    def validate_participants_count(cls, v):
        if v < 0:
            raise ValueError('Participants count cannot be negative')
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    participants_count: Optional[int] = None

    @validator('title')
    def validate_title(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v


    @validator('participants_count')
    def validate_participants_count(cls, v):
        if v is not None and v < 0:
            raise ValueError('Participants count cannot be negative')
        return v


class EventResponse(EventBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    events: list[EventResponse]
    total: int