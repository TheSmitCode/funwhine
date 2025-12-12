from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core import security
from app.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to read JWT token from cookie and attach it to request.state.token.
    Can be extended to enforce auth globally.
    """

    async def dispatch(self, request: Request, call_next):
        raw_token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        if raw_token and raw_token.lower().startswith("bearer "):
            request.state.token = raw_token.split(" ", 1)[1]
        else:
            request.state.token = None
        response = await call_next(request)
        return response
