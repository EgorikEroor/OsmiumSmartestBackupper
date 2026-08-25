import sys
import datetime
from send2trash import send2trash
from pathlib import Path
import shutil
import uuid
from sqlalchemy.orm import sessionmaker
from database import database_engine,Resources
resource = Path(sys.argv[1])
resource_time = datetime.datetime.now().strftime('%Y.%d.%m %H:%M:%S')
resource_name = resource.name
resource_uuid = str(uuid.uuid4())
folder_saved_files = Path.home() / 'AppData' / 'Local' / 'OsmiumSmartestBackupper' /'SavedFiles' / resource_uuid
folder_saved_files.mkdir(parents=True,exist_ok=True)
resource_units = ['B', 'KB', 'MB', 'GB', 'TB']
units_index = 0
with sessionmaker(bind = database_engine)() as session:
    if resource.is_file():
        file_size = resource.stat().st_size
        while file_size >= 1024 and units_index < len(resource_units) - 1:
            file_size /= 1024
            units_index += 1
        file_size = round(file_size,2)
        if file_size.is_integer():
            file_size = int(file_size)
        session.add(Resources(uuid=resource_uuid,name=resource_name,size=file_size,data_delete=resource_time))
        shutil.copy(resource,folder_saved_files / resource_name)
    if resource.is_dir():
        directory_size = float(sum(file.stat().st_size for file in resource.rglob('*') if file.is_file()))
        while directory_size >= 1024 and units_index < len(resource_units) - 1:
            directory_size /= 1024
            units_index += 1
        function_file_size = round(directory_size,2)
        if function_file_size.is_integer():
            function_file_size = int(function_file_size)
        session.add(Resources(uuid=resource_uuid,name=resource_name,size=directory_size,data_delete=resource_time))
        shutil.copytree(resource,folder_saved_files / resource_name)
send2trash(resource)