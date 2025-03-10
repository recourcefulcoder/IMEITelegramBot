import pytest

import pytest_asyncio

from sanic_testing import TestManager

from server import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app()
    TestManager(app)
    return app


@pytest_asyncio.fixture(autouse=True)
async def dispose_connections():
    from database.engine import bind

    yield

    await bind.dispose()
