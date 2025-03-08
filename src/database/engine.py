import config

from sqlalchemy import URL
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import create_async_engine

url_object = URL.create(
    "postgresql+asyncpg",
    username=config.POSTGRES_USER,
    password=config.POSTGRES_PASSWORD,
    host=config.HOSTNAME,
    port=5432,
    database=config.POSTGRES_DB,
)


def create_bind():
    return create_async_engine(
        url_object,
        pool_pre_ping=True,
        poolclass=AsyncAdaptedQueuePool,
        pool_recycle=1800,
        echo="debug",
    )
