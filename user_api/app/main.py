from fastapi import Depends, FastAPI
from sqlalchemy.orm import declarative_base
from fastapi_users import FastAPIUsers
import logging
import uuid

from app.auth.shemas import UserReadExtended, UserCreateExtended
from app.settings import settings
from app.auth.auth import auth_backend
from app.auth.manager import get_user_manager
from app.auth.database import User


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
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.


