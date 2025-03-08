import datetime
from functools import wraps
from http import HTTPStatus
from typing import Optional

import config

import database.models as models

import jwt

from redis import Redis
from redis import asyncio as aioredis

from sanic import Blueprint, json

from sqlalchemy.sql.expression import select


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
                    request.app.config.JWT_SECRET_KEY,
                    algorithms=["HS256"],
                )
                if payload.get("type") != "access":
                    return json(
                        {"error": "Invalid token type"},
                        HTTPStatus.UNAUTHORIZED,
                    )
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


class TokenManager:
    def __init__(self):
        self.redis: Optional[Redis] = None

    async def init_redis(self):
        self.redis = await aioredis.from_url(
            config.REDIS_URL, decode_responses=True
        )

    @staticmethod
    async def create_access_token(identity: str):
        """Generate access token from userdata"""
        exp_time = (
            datetime.datetime.now(datetime.timezone.utc)
            + config.ACCESS_TOKEN_EXPIRE
        )
        payload = {
            "sub": identity,
            "exp": exp_time,
            "type": "access",
        }
        return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm="HS256")

    async def create_refresh_token(self, username: str) -> str:
        """Generate a refresh token and store it in Redis"""
        exp_time = (
            datetime.datetime.now(datetime.timezone.utc)
            + config.REFRESH_TOKEN_EXPIRE
        )
        refresh_token = jwt.encode(
            {"sub": username, "exp": exp_time},
            config.JWT_SECRET_KEY,
            algorithm="HS256",
        )

        await self.redis.setex(
            f"refresh:{username}",
            config.REFRESH_TOKEN_EXPIRE,
            refresh_token,
        )

        return refresh_token

    async def verify_refresh_token(self, refresh_token: str) -> Optional[str]:
        """Verify refresh token from Redis"""
        try:
            payload = jwt.decode(
                refresh_token, config.JWT_SECRET_KEY, algorithms=["HS256"]
            )
            username = payload["sub"]

            # Retrieve stored refresh token from Redis
            stored_token = await self.redis.get(f"refresh:{username}")
            if stored_token and stored_token == refresh_token:
                return username  # Token is valid
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token

        return None  # Token not found or mismatched

    async def delete_refresh_token(self, username: str) -> None:
        """Remove refresh token from Redis"""
        await self.redis.delete(f"refresh:{username}")


BP_NAME = "auth"
bp = Blueprint(BP_NAME, url_prefix="/auth")


@bp.post("/login", name="login")
async def do_login(request):
    data = request.json
    if not data or "password" not in data or "username" not in data:
        return json(
            {
                "error": "Invalid credential format: "
                "missing username and/or password"
            },
            HTTPStatus.BAD_REQUEST,
        )

    print("before starting session query")
    result = await request.ctx.session.execute(
        select(models.User).where(models.User.username == data["username"])
    )

    print("result achieved")

    user = result.scalar()
    if not user or not user.check_password(data["password"]):
        return json(
            {"error": "Invalid password"},
            HTTPStatus.UNAUTHORIZED,
            )

    print("user validated")

    access_token = await TokenManager.create_access_token(data["username"])
    refresh_token = (
        await request.app.config.token_manager.create_refresh_token(
            data["username"]
        )
    )

    return json(
        {"access_token": access_token, "refresh_token": refresh_token},
        HTTPStatus.OK,
    )


@bp.post("/refresh", name="refresh")
async def refresh(request):
    refresh_token = request.json.get("refresh_token")

    if not refresh_token:
        return json(
            {"error": "Missing refresh token"}, status=HTTPStatus.BAD_REQUEST
        )

    username = await request.app.config.token_manager.verify_refresh_token(
        refresh_token
    )

    if not username:
        return json(
            {"error": "Invalid refresh token"}, status=HTTPStatus.UNAUTHORIZED
        )

    await request.app.config.token_manager.delete_refresh_token(username)

    new_refresh_token = (
        await request.app.config.token_manager.create_refresh_token(username)
    )
    new_access_token = await TokenManager.create_access_token(username)

    return json(
        {"access_token": new_access_token, "refresh_token": new_refresh_token},
        HTTPStatus.OK,
    )
