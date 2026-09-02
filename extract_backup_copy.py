from sqlalchemy import select,delete
from sqlalchemy.orm import sessionmaker
from database import Resources,database_engine
import py7zr
from pathlib import Path
import os
import shutil
def extract_backup_copy(resource_uuid,resource_unloading):
    resource=Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData'/'Local'))/'OsmiumSmartestBackupper'/'SavedFiles'/resource_uuid
    with sessionmaker(bind=database_engine)() as session:
        if resource.exists():
                resource_archived_status=session.scalar(select(Resources.archived).where(Resources.uuid==resource_uuid))
                if resource_archived_status:
                    with py7zr.SevenZipFile(resource,mode='r') as archive:
                        archive.extractall(path=resource_unloading)
                else:
                    if resource.is_file():
                        shutil.copy(resource,resource_unloading)
                    if resource.is_dir():
                        shutil.copytree(resource,resource_unloading,dirs_exist_ok=True)
        resource_instructions=delete(Resources).where(Resources.uuid==resource_uuid)
        session.execute(resource_instructions)
        session.commit()