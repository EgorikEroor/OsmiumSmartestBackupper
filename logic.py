import sys
import datetime
from send2trash import send2trash
from pathlib import Path
import shutil
import uuid
from sqlalchemy.orm import sessionmaker
from database import database_engine,Resources
import py7zr
def resource_logic():
    resource = Path(sys.argv[1])
    resource_uuid = str(uuid.uuid4())
    resource_name = resource.name
    resource_time = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    folder_saved_resources = Path.home() / 'AppData' / 'Local' / 'OsmiumSmartestBackupper' /'SavedFiles' / resource_uuid
    folder_saved_resources.mkdir(parents=True,exist_ok=True)
    resource_units = ['B','KB','MB','GB','TB']
    units_index = 0
    with sessionmaker(bind = database_engine)() as session:
        if resource.is_file():
            resource_size = resource.stat().st_size
            while resource_size >= 1024 and units_index < len(resource_units) - 1:
                resource_size /= 1024
                units_index += 1
            resource_size = round(resource_size,2)
            if resource_size % 1 == 0:
                resource_size = int(resource_size)
            if resource.suffix not in ['.7z','.avi','.docx','.gif','.img','.iso','.jpg','.mkv','.mp3','.mp4','.pdf','.png','.pptx','.rar','.tar.gz','.xlsx','.zip']:
                with py7zr.SevenZipFile(folder_saved_resources / 'archive.7z',mode='w') as archive:
                    archive.write(file=resource,arcname=resource_name)
                archived_status = True
            else:
                shutil.copy(resource, folder_saved_resources / resource_name)
                archived_status = False
            session.add(Resources(uuid=resource_uuid,name=resource_name,size=f'{resource_size} {resource_units[units_index]}',archived=archived_status,data_delete=resource_time))
            session.commit()
        if resource.is_dir():
            resource_size = float(sum(file.stat().st_size for file in resource.rglob('*') if file.is_file()))
            while resource_size >= 1024 and units_index < len(resource_units) - 1:
                resource_size /= 1024
                units_index += 1
            resource_size = round(resource_size,2)
            if resource_size % 1 == 0:
                resource_size = int(resource_size)
            archived_status = any(file.suffix not in ['.7z','.avi','.docx','.gif','.img','.iso','.jpg','.mkv','.mp3','.mp4','.pdf','.png','.pptx','.rar','.tar.gz','.xlsx','.zip'] for file in resource.rglob('*'))
            if archived_status:
                with py7zr.SevenZipFile(folder_saved_resources / 'archive.7z', mode='w') as archive:
                    archive.writeall(path=resource,arcname=resource_name)
            else:
                shutil.copytree(resource, folder_saved_resources / resource_name,dirs_exist_ok=True)
            session.add(Resources(uuid=resource_uuid,name=resource_name,size=f'{resource_size} {resource_units[units_index]}',archived=archived_status,data_delete=resource_time))
            session.commit()
    send2trash(resource)