from http import HTTPStatus

import pytest

from sanic_testing.testing import SanicASGITestClient

import server


# @pytest.fixture
# def app():
#     import config
#     from server import app
#     return app


@pytest.mark.parametrize(
    "credentials",
    [
        {
            "password": "valid_password"
        },
        {
            "username": "valid_username",
        },
        {},
        {
            "random_key1": "random_value",
            "key_2": "val2"
        }
    ]
)
@pytest.mark.asyncio
async def test_invalid_login(credentials,):
    test_client = SanicASGITestClient(server.app)
    response = await test_client.post(server.app.url_for("login"), data=credentials)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
