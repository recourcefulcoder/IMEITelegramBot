from http import HTTPStatus

from api.auth import BP_NAME

import pytest

from sanic import Sanic

from sanic_testing.testing import SanicASGITestClient

from tests import testvars


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
        app.url_for(f"{BP_NAME}.login"),
        json=credentials,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_valid_credentials_login(app: Sanic):
    credentials = {
        "username": testvars.BOT_NAME,
        "password": testvars.BOT_PASSWORD
    }
    test_client = SanicASGITestClient(app)
    _, response = await test_client.post(
        app.url_for(f"{BP_NAME}.login"),
        json=credentials,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_invalid_refresh_token(app: Sanic):
    pass


@pytest.mark.asyncio
async def test_valid_refresh_token(app: Sanic):
    pass
