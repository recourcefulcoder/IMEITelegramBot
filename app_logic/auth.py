from functools import wraps
from http import HTTPStatus

import jwt

from sanic import json

from sanic_jwt import exceptions


def protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            if not request.token:
                return json(
                    {"error": "Missing token"}, HTTPStatus.UNAUTHORIZED
                )
            try:
                payload = jwt.decode(
                    request.token,
                    request.app.config.SECRET,
                    algorithms=["HS256"],
                )
                if payload.get("type") != "access":
                    raise exceptions.AuthenticationFailed("Invalid token type")
                response = await f(request, *args, **kwargs)
                return response
            except jwt.ExpiredSignatureError:
                return json(
                    {"error": "Token expired"}, HTTPStatus.UNAUTHORIZED
                )
            except jwt.InvalidTokenError:
                return json(
                    {"error": "Invalid token"}, HTTPStatus.UNAUTHORIZED
                )

        return decorated_function

    return decorator(wrapped)
