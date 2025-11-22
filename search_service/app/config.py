"""
Конфигурация приложения
Настройки загружаются из переменных окружения
"""
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT"))
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

TYPESENSE_HOST = os.environ.get("TYPESENSE_HOST")
TYPESENSE_PORT = os.environ.get("TYPESENSE_PORT")
TYPESENSE_PROTOCOL = os.environ.get("TYPESENSE_PROTOCOL")
TYPESENSE_API_KEY = os.environ.get("TYPESENSE_API_KEY")

SERVICE_PORT = int(os.environ.get("SERVICE_PORT"))
LOG_LEVEL = os.environ.get("LOG_LEVEL")

ALLOWED_ORIGINS_STR = os.environ.get("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = ALLOWED_ORIGINS_STR.split(",") if ALLOWED_ORIGINS_STR != "*" else ["*"]