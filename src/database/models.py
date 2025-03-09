import bcrypt

from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.expression import select

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    username = Column(String(100), unique=True)
    email = Column(String(100))
    password = Column(String)

    @staticmethod
    def hash_password(password: str) -> str:
        pwhash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return pwhash.decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password.encode("utf-8")
        )

    def set_password(self, password: str) -> str:
        self.password = type(self).hash_password(password)
        return self.password


async def get_db_metadata(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return Base.metadata


async def create_user(
    async_session, username, password, email="example@example.com"
):
    user = User(username=username, email=email)
    user.set_password(password)
    async with async_session() as session:
        async with session.begin():
            session.add(user)


async def check_pass(engine, username, password):
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar()

            return user.check_password(password)
