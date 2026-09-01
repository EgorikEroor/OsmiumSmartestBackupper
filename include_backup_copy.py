from pathlib import Path
import sys
import uuid
import datetime
import os
from sqlalchemy.orm import sessionmaker
from database import database_engine,Resources
import py7zr
import shutil
from send2trash import send2trash
import locale
import ctypes
from deep_translator import GoogleTranslator
import requests.exceptions
import deep_translator.exceptions
from plyer import notification
def calculation_resource_size(size):
    resource_units=['B','KB','MB','GB','TB']
    units_index=0
    while size>=1024 and units_index<len(resource_units)-1:
        size/=1024
        units_index+=1
    size=round(size,2)
    if size%1==0:
        size=int(size)
    size=f'{size} {resource_units[units_index]}'
    return size
def include_backup_copy():
    resource=Path(sys.argv[1])
    resource_uuid=str(uuid.uuid4())
    resource_name=resource.name
    resource_data_delete=datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    folder_saved_resource=Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData'/'Local'))/'OsmiumSmartestBackupper'/'SavedFiles'/resource_uuid
    folder_saved_resource.mkdir(parents=True,exist_ok=True)
    with sessionmaker(bind=database_engine)() as session:
        if resource.is_file():
            resource_size=calculation_resource_size(resource.stat().st_size)
            if resource.suffix not in ['.7z','.avi','.docx','.gif','.img','.iso','.jpg','.mkv','.mp3','.mp4','.pdf','.png','.pptx','.rar','.tar.gz','.xlsx','.zip']:
                with py7zr.SevenZipFile(folder_saved_resource/'archive.7z',mode='w') as archive:
                    archive.write(file=resource,arcname=resource_name)
                archived_status=True
            else:
                shutil.copy(resource,folder_saved_resource/resource_name)
                archived_status=False
            resource_message='The file has been moved to the Recycle Bin, and its backup has been saved.'
            resource_title='File deletion'
            session.add(Resources(uuid=resource_uuid,name=resource_name,size=resource_size,archived=archived_status,data_delete=resource_data_delete))
            session.commit()
        if resource.is_dir():
            resource_size=calculation_resource_size(float(sum(file.stat().st_size for file in resource.rglob('*') if file.is_file())))
            archived_status=any(file.suffix not in ['.7z','.avi','.docx','.gif','.img','.iso','.jpg','.mkv','.mp3','.mp4','.pdf','.png','.pptx','.rar','.tar.gz','.xlsx','.zip'] for file in resource.rglob('*'))
            if archived_status:
                with py7zr.SevenZipFile(folder_saved_resource/'archive.7z',mode='w') as archive:
                    archive.writeall(path=resource,arcname=resource_name)
            else:
                shutil.copytree(resource,folder_saved_resource/resource_name,dirs_exist_ok=True)
            resource_message='The directory has been moved to the Recycle Bin, and its backup has been saved.'
            resource_title='Directory deletion'
            session.add(Resources(uuid=resource_uuid,name=resource_name,size=resource_size,archived=archived_status,data_delete=resource_data_delete))
            session.commit()
    send2trash(resource)
    client_language=(locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(),'en_US')).split('_')[0]
    try:
        client_message=GoogleTranslator(source='en',target=client_language).translate(resource_message)
        client_title=GoogleTranslator(source='en',target=client_language).translate(resource_title)
    except (requests.exceptions.ConnectionError,deep_translator.exceptions.TranslationNotFound):
        client_message=resource_message
        client_title=resource_title
    notification.notify(title=client_title,message=client_message,app_name='OsmiumSmartestBackupper',timeout=5)