from fastapi import Depends, FastAPI
from sqlalchemy.orm import declarative_base
from fastapi_users import FastAPIUsers
import logging
import uuid
from app.auth.auth import auth_backend
from app.auth.manager import get_user_manager
from app.auth.database import User
from app.event_records.routers import event_registration_router
from app.users.router import user_router
from app.events.routers import event_router
from app.books.routers import book_router
from app.book_rental.routers import book_rental_router
from starlette.middleware.cors import CORSMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

Base = declarative_base()


app = FastAPI(title='LibraLife')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(event_router)
app.include_router(event_registration_router)
app.include_router(book_router)
app.include_router(book_rental_router)

