"""
API роутеры для поискового сервиса
"""
from fastapi import APIRouter
from app.api import search, preprocess

api_router = APIRouter()

# Подключаем роутеры с префиксами
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(preprocess.router, prefix="/services", tags=["services"])