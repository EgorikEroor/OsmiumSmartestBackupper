import asyncio
from sqlalchemy import select,delete
from database import Resources,database_engine
import py7zr
from pathlib import Path
import os
import shutil
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession
async_session=async_sessionmaker(database_engine,class_=AsyncSession,expire_on_commit=False)
def directory_exist(directory):
    return directory.exists()
def resource_unloading(archived_status,folder_resource,resource_name,folder_unloading):
    if archived_status:
        with py7zr.SevenZipFile(folder_resource/'archive.7z', mode='r') as archive:
            archive.extractall(path=folder_unloading)
    else:
        resource_path=folder_resource/resource_name
        if resource_path.is_file():
            shutil.copy(resource_path,folder_unloading)
        if resource_path.is_dir():
            shutil.copytree(resource_path,folder_unloading,dirs_exist_ok=True)
    shutil.rmtree(folder_resource)
async def extract_backup_copy(resource_uuid,directory_unloading):
    directory_resource=Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData'/'Local'))/'OsmiumSmartestBackupper'/'SavedResources'/resource_uuid
    async with async_session() as session:
        directory_status_exist=await asyncio.to_thread(directory_exist,directory_resource)
        if directory_status_exist:
            archived_status=await session.scalar(select(Resources.archived).where(Resources.uuid == resource_uuid))
            resource_name=await session.scalar(select(Resources.name).where(Resources.uuid == resource_uuid))
            await asyncio.to_thread(resource_unloading,archived_status,directory_resource,resource_name,directory_unloading)
        await session.execute(delete(Resources).where(Resources.uuid==resource_uuid))
        await session.commit()