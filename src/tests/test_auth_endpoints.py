import json
from http import HTTPStatus

from api.auth import BP_NAME

from database.engine import create_bind
from database.models import Base

import pytest

from sanic import Sanic

from server import create_app

from sqlalchemy.ext.asyncio import async_sessionmaker


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create and drop tables for testing."""
    engine = create_bind()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # run tests

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def db_session():
    """Providing a fresh database session for each test."""
    async with async_sessionmaker() as session:
        yield session


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
        data=json.dumps(credentials),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
