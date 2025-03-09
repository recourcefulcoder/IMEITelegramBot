import config

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

url_object = URL.create(
    "postgresql+asyncpg",
    username=config.POSTGRES_USER,
    password=config.POSTGRES_PASSWORD,
    host=config.HOSTNAME,
    port=5432,
    database=config.POSTGRES_DB,
)


def create_bind():
    echo_value = False
    if config.SANIC_DEBUG:
        echo_value = "debug"

    return create_async_engine(
        url_object,
        pool_pre_ping=True,
        poolclass=AsyncAdaptedQueuePool,
        pool_recycle=1800,
        echo=echo_value,
    )
