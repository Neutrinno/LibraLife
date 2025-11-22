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


class IndexRequest(BaseModel):
    """Запрос на индексацию услуги - только ID"""
    id: int = Field(..., description="ID услуги в PostgreSQL")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1
            }
        }


class IndexResponse(BaseModel):
    """Ответ при индексации"""
    success: bool
    service_id: int
    message: str

class ServiceSchema(BaseModel):
    """Схема услуги для отображения в результатах поиска"""
    id: str
    title: str
    description: str
    category: Optional[str] = None
    location: Optional[str] = None
    price_per_day: Optional[float] = None
    capacity: Optional[str] = None
    technical_specs: Optional[str] = None
    is_active: bool
    supplier_id: int
    created_at: Optional[int] = None

    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    """Ответ на поисковой запрос"""
    query: str = Field(..., description="Исходный запрос пользователя")
    total: int = Field(..., description="Количество найденных результатов")
    results: List[dict] = Field(default_factory=list, description="Список найденных услуг")
    search_method: str = Field(default="typesense", description="Метод поиска")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "трактор",
                "total": 5,
                "results": [
                    {
                        "id": "1",
                        "title": "Трактор МТЗ 82.1",
                        "description": "Универсальный трактор",
                        "price_per_day": 5000.0,
                        "location": "Екатеринбург"
                    }
                ],
                "search_method": "typesense"
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