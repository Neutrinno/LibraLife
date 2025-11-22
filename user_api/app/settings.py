from pydantic import BaseModel
from pydantic.v1 import BaseSettings


class AuthPrefix(BaseModel):
    prefix: str = "/auth"
    tags: str = "auth"

class Users(BaseModel):
    prefix: str = "/users"
    tags: str = "users"

class Settings(BaseSettings):
    auth: AuthPrefix = AuthPrefix()
    users: Users = Users()

settings = Settings()