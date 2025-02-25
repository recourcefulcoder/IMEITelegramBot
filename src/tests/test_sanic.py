from http import HTTPStatus

from api.auth import BP_NAME

import pytest

from sanic import Sanic

from sanic_testing.testing import SanicASGITestClient

from server import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.parametrize(
    "credentials",
    [
        {"password": "valid_password"},
        {
            "username": "valid_username",
        },
        {},
        {"random_key1": "random_value", "key_2": "val2"},
    ],
)
@pytest.mark.asyncio
async def test_invalid_login(app: Sanic, credentials):
    test_client = SanicASGITestClient(app)
    response = await test_client.post(
        app.url_for(f"{BP_NAME}.login"), data=credentials
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
