import asyncio


from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import DATABASE_URL,DATABASE_DIRECTORY

database_engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(database_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class Resource(Base):
    __tablename__ = "resources"

    uuid = Column(String, primary_key=True)
    name = Column(String)
    size = Column(String)
    is_archived = Column(Boolean)
    deleted_at = Column(String)


async def create_database():
    await asyncio.to_thread(
        DATABASE_DIRECTORY.mkdir,
        parents=True,
        exist_ok=True,
    )

    async with database_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)