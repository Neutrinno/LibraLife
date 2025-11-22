import uuid

class UserResponse():
    id: uuid.UUID
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool
    registered_at: str
