import asyncio
import sys
from pathlib import Path

from models import Base


async def create_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    src_dir = Path(__file__).resolve().parent.parent
    sys.path.append(str(src_dir))

    from engine import create_bind

    asyncio.run(create_db(create_bind()))
