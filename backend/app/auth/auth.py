import uuid

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy

from backend.app.auth.manager import get_user_manager
from backend.app.models import User

cookie_transport = CookieTransport(cookie_name = "rcc", cookie_max_age=43200, cookie_samesite="lax", cookie_secure = False)

SECRET = "SECRET"

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=43200)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_user = fastapi_users.current_user(optional=True)
user_authenticator = fastapi_users.authenticator
get_current_user_token = user_authenticator.current_user_token(active=True, verified=False)