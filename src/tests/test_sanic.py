from http import HTTPStatus

import pytest

from sanic_testing.testing import SanicASGITestClient

from server import app


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
async def test_invalid_login(credentials):
    test_client = SanicASGITestClient(app)
    response = await test_client.post(app.url_for("login"), data=credentials)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
