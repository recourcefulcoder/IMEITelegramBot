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

echo_value = False
if config.SANIC_DEBUG:
    echo_value = "debug"

bind = create_async_engine(
    url_object,
    pool_pre_ping=True,
    poolclass=AsyncAdaptedQueuePool,
    echo=echo_value,
)
