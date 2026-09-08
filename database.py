from pathlib import Path
import os
from sqlalchemy import Column,String,Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio
folder_database=Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData'/'Local'))/'OsmiumSmartestBackupper'/'Database'
database_engine=create_async_engine(f"sqlite+aiosqlite:///{folder_database/'database_resources.db'}")
Database=declarative_base()
class Resources(Database):
    __tablename__='Resources'
    uuid=Column(String,primary_key=True)
    name=Column(String)
    size=Column(String)
    archived=Column(Boolean)
    data_delete=Column(String)
async def create_database():
    await asyncio.to_thread(folder_database.mkdir,parents=True,exist_ok=True)
    async with database_engine.begin() as engine:
        await engine.run_sync(Database.metadata.create_all)
