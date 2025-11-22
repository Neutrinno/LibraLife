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

# --- Auth: login / logout ---
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=settings.auth.prefix,
    tags=[settings.auth.tags],
)


# --- Protected route ---
current_user = fastapi_users.current_user()


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return {"email": user.email, "full_name": user.full_name}
