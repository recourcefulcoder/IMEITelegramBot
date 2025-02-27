import json
from http import HTTPStatus

from api.auth import BP_NAME

from database.engine import create_bind
from database.models import Base, User

import pytest

from sanic import Sanic

from server import create_app

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Session


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create and drop tables for testing."""
    engine = create_bind()

    admin = User(username="admin", email="admin@example.com")
    admin.set_password("admin")
    # async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    with Session(engine) as session:
        session.add(admin)
        session.commit()

    yield  # run tests

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
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
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_valid_credentials_login(app: Sanic):
    credentials = {"username": "admin", "password": "admin"}
    # credentials = {}
    _, response = await app.asgi_client.post(
        app.url_for(f"{BP_NAME}.login"),
        data=json.dumps(credentials),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_invalid_refresh_token(app: Sanic):
    pass


@pytest.mark.asyncio
async def test_valid_refresh_token(app: Sanic):
    pass
