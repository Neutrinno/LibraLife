from fastapi import FastAPI

from backend.app.auth.auth import fastapi_users
from backend.app.auth.shemas import UserRead, UserCreate
from backend.app.settings import settings

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(fastapi_users.authenticator),
    prefix=settings.auth.prefix,
    tags=[settings.auth.tags]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=settings.auth.prefix,
    tags=[settings.auth.tags]
)

@app.get("/")
async def root():
    return {"message": "LibraLife API"}
