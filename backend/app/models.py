import uuid

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, UUID, Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    full_name = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    registered_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

