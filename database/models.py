import bcrypt

from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.expression import select


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    username = Column(String(100))
    email = Column(String(100))
    password = Column(String)

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password.encode("utf-8")
        )

    def set_password(self, password: str) -> str:
        pwhash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.password = pwhash.decode("utf-8")
        return self.password


async def create_user(
    engine, async_session, username, password, email="example@example.com"
):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    user = User(username=username, email=email)
    user.set_password(password)
    async with async_session() as session:
        async with session.begin():
            session.add(user)

    await engine.dispose()


async def check_pass(engine, username, password):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar()
            print(f"PASSWORDS_MATCH: {user.check_password(password)}")

    await engine.dispose()
