from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PreprocessRequest(BaseModel):
    """Запрос на предобработку текста (если нужна)"""
    title: str = Field(..., min_length=1, description="Название услуги")
    description: str = Field(..., min_length=1, description="Описание услуги")


class PreprocessResponse(BaseModel):
    """Ответ с обработанными данными"""
    processed_title: str
    processed_description: str


class BookSchema(BaseModel):
    """Схема книги для отображения в результатах поиска"""
    id: str
    item_type: str = "book"
    title: str
    author: Optional[str] = None
    category: Optional[str] = None
    gost_title: Optional[str] = None
    description: Optional[str] = None
    is_available: Optional[bool] = True

    class Config:
        from_attributes = True


class EventSchema(BaseModel):
    """Схема мероприятия для отображения в результатах поиска"""
    id: str
    item_type: str = "event"
    title: str
    description: Optional[str] = None
    date: Optional[str] = None  # ISO format string
    location: Optional[str] = None
    participants_count: Optional[int] = 0

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Ответ на поисковой запрос"""
    query: str = Field(..., description="Исходный запрос пользователя")
    total: int = Field(..., description="Количество найденных результатов")
    results: List[dict] = Field(default_factory=list, description="Список найденных книг и мероприятий")
    search_method: str = Field(default="typesense", description="Метод поиска")
    item_type: Optional[str] = Field(default="all", description="Тип элементов в результатах: 'book', 'event' или 'all'")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "достоевский",
                "total": 5,
                "results": [
                    {
                        "document": {
                            "id": "book_1",
                            "item_type": "book",
                            "title": "Преступление и наказание",
                            "author": "Ф.М. Достоевский",
                            "category": "Классическая литература"
                        },
                        "text_match": 12345
                    },
                    {
                        "document": {
                            "id": "event_5",
                            "item_type": "event",
                            "title": "Лекция о Достоевском",
                            "date": "2024-12-15T18:00:00",
                            "location": "Москва"
                        },
                        "text_match": 10000
                    }
                ],
                "search_method": "typesense",
                "item_type": "all"
            }
        }

class SynonymCreate(BaseModel):
    """Схема для создания синонима (если понадобится в будущем)"""
    word: str = Field(..., min_length=2, description="Основное слово")
    synonym: str = Field(..., min_length=2, description="Синоним")

class SynonymResponse(BaseModel):
    """Ответ при работе с синонимами"""
    id: int
    word: str
    synonym: str
    created_at: datetime