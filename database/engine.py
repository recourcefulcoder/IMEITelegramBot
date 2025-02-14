from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine

import app_logic.config as config


url_object = URL.create(
    "postgresql+asyncpg",
    username="postgres",
    password=config.POSTGRES_PASSWORD,
    host=config.HOSTNAME,
    port=5432,
    database="imei_api",
)

bind = create_async_engine(
    url_object,
    pool_pre_ping=True,
)
