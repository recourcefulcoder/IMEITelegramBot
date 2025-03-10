import datetime
from http import HTTPStatus

from api.auth import BP_NAME as AUTH_BP_NAME

import config

import jwt

import pytest

import pytest_asyncio

from sanic import Sanic

from tests import testvars


def generate_exp_refresh() -> str:
    exp_time = datetime.datetime.now() - datetime.timedelta(minutes=15)
    exp_time = datetime.datetime.timestamp(exp_time)
    return jwt.encode(
        {"sub": testvars.BOT_NAME, "exp": exp_time},
        config.JWT_SECRET_KEY,
        algorithm="HS256",
    )


@pytest_asyncio.fixture
async def bot_tokens(app):
    credentials = {
        "username": testvars.BOT_NAME,
        "password": testvars.BOT_PASSWORD,
    }
    _, response = await app.asgi_client.post(
        app.url_for(f"{AUTH_BP_NAME}.login"),
        json=credentials,
        headers={"Content-Type": "application/json"},
    )
    return response.json


@pytest.mark.parametrize(
    "credentials",
    [
        {"password": "valid_password"},
        {"username": "valid_username"},
        {},
        {"random_key1": "random_value", "key_2": "val2"},
    ],
)
@pytest.mark.asyncio
async def test_invalid_credentials_login(app: Sanic, credentials):
    _, response = await app.asgi_client.post(
        app.url_for(f"{AUTH_BP_NAME}.login"),
        json=credentials,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_valid_credentials_login(app: Sanic):
    credentials = {
        "username": testvars.BOT_NAME,
        "password": testvars.BOT_PASSWORD,
    }
    _, response = await app.asgi_client.post(
        app.url_for(f"{AUTH_BP_NAME}.login"),
        json=credentials,
        headers={"Content-Type": "application/json"},
    )
    keys = response.json.keys()
    assert response.status_code == HTTPStatus.OK
    assert "refresh_token" in keys
    assert "access_token" in keys


@pytest.mark.asyncio
async def test_invalid_refresh_token(app: Sanic):
    data = {"refresh_token": "asjkdhakj"}
    _, response = await app.asgi_client.post(
        app.url_for(f"{AUTH_BP_NAME}.refresh"),
        json=data,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_invalid_refresh_data(app: Sanic):
    data = {"random_key": "asjkdhakj"}
    _, response = await app.asgi_client.post(
        app.url_for(f"{AUTH_BP_NAME}.refresh"),
        json=data,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_expired_refresh_token(app: Sanic):
    token = generate_exp_refresh()
    data = {"refresh_token": token}
    _, response = await app.asgi_client.post(
        app.url_for(f"{AUTH_BP_NAME}.refresh"),
        json=data,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_valid_refresh_token(app: Sanic, bot_tokens):
    _, response = await app.asgi_client.post(
        app.url_for(f"{AUTH_BP_NAME}.refresh"),
        json={"refresh_token": bot_tokens["refresh_token"]},
        headers={"Content-Type": "application/json"},
    )
    keys = response.json.keys()
    assert response.status_code == HTTPStatus.OK
    assert "refresh_token" in keys
    assert "access_token" in keys
