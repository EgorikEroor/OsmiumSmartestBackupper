import sys
import datetime
from send2trash import send2trash
from pathlib import Path
import shutil
import uuid
resource = Path(sys.argv[1])
resource_time = datetime.datetime.now()
resource_name = resource.name
folder_saved_files = Path.home() / 'AppData' / 'Local' / 'OsmiumSmartestBackupper' /'SavedFiles'
folder_saved_files.mkdir(parents=True,exist_ok=True)
if resource.is_file():
    shutil.copy(resource,folder_saved_files / resource_name)
if resource.is_dir():
    shutil.copytree(resource,folder_saved_files / resource_name)
send2trash(resource)