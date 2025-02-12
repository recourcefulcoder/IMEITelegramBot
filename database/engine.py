import os

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine


url_object = URL.create(
    "postgresql+asyncpg",
    username="postgres",
    password=os.getenv("DB_PASSWORD", default="postgres"),
    host="localhost",
    port=5432,
    database="imei_api",
)

bind = create_async_engine(
    url_object,
    pool_pre_ping=True,
)
