"""Database engine, session factory and the ORM model."""

from sqlalchemy import Boolean, Column, String
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from config import DATABASE_DIRECTORY, DATABASE_URL

database_engine = create_async_engine(DATABASE_URL)
session_factory = async_sessionmaker(
    database_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


class BackedUpResource(Base):
    """A deleted file or directory that has a stored backup."""

    __tablename__ = "backed_up_resources"

    backup_uuid = Column(String, primary_key=True)
    resource_name = Column(String)
    formatted_size = Column(String)
    is_archived = Column(Boolean)
    deleted_at = Column(String)


async def create_database() -> None:
    """Create the database directory and all missing tables."""
    DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    async with database_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)