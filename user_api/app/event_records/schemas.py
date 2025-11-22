from pydantic import BaseModel, EmailStr, ConfigDict
from pydantic.v1 import validator
from typing import Optional
import uuid
from datetime import datetime

# ... существующие схемы ...

class EventRegistrationBase(BaseModel):
    name: str
    surname: str
    email: EmailStr

class EventRegistrationCreate(EventRegistrationBase):
    event_id: uuid.UUID

    @validator('name', 'surname')
    def validate_name(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Name and surname cannot be empty')
        return v.strip()

class EventRegistrationResponse(EventRegistrationBase):
    id: uuid.UUID
    event_id: uuid.UUID
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EventRegistrationCancel(BaseModel):
    email: EmailStr