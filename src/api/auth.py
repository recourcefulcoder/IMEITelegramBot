import datetime
from functools import wraps
from http import HTTPStatus
from typing import Optional

import config

import jwt

from redis import asyncio as aioredis
from redis import Redis

from sanic import json


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
                    # request.app.config.SECRET,
                    config.JWT_SECRET_KEY,
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
        exp_time = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(minutes=15)
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
