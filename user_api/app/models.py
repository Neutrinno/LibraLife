import uuid
from enum import Enum

from sqlalchemy import Column, String, Boolean, Date, TIMESTAMP, func, ForeignKey, UUID, Enum as SQLEnum, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ReviewType(Enum):
    BOOK = "book"
    EVENT = "event"

class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    full_name = Column(String, nullable=True)
    registered_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Связи
    reviews = relationship("Review", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class Book(Base):
    """Модель книги"""
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='Уникальный ID')
    author = Column(String(200), nullable=False, comment='Автор')
    title = Column(String(200), nullable=False, comment='Название')
    category = Column(String(100), comment='Категория')
    gost_title = Column(String(200), comment='Название по ГОСТ')
    description = Column(Text, comment='Описание')
    is_available = Column(Boolean, default=True, comment='Наличие')

    # Связи
    reviews = relationship("Review", back_populates="book")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"


class Event(Base):
    """Модель мероприятия"""
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='Уникальный ID')
    title = Column(String(200), nullable=False, comment='Название')
    description = Column(Text, comment='Описание')
    date = Column(DateTime, nullable=False, comment='Дата')
    location = Column(String(200), comment='Локация')
    participants_count = Column(Integer, default=0, comment='Количество участников')

    # Связи
    reviews = relationship("Review", back_populates="event")

    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}')>"


class Review(Base):
    """Модель отзыва"""
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='Уникальный ID')
    review_type = Column(SQLEnum(ReviewType), nullable=False, comment='Тип (book или event)')
    rating = Column(Integer, nullable=False, comment='Оценка')
    description = Column(Text, comment='Описание')

    # Внешние ключи
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False, comment='ID пользователя')
    book_id = Column(Integer, ForeignKey('books.id'), comment='ID книги (если отзыв на книгу)')
    event_id = Column(Integer, ForeignKey('events.id'), comment='ID мероприятия (если отзыв на мероприятие)')

    # Связи
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")
    event = relationship("Event", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, type={self.review_type}, rating={self.rating})>"