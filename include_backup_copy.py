import asyncio
import sys
from pathlib import Path
import uuid
import datetime
import os
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
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession
compressed_formats=['.7z','.avi','.docx','.gif','.img','.iso','.jpg','.mkv','.mp3','.mp4','.pdf','.png','.pptx','.rar','.gz','.xlsx','.zip']
async_session=async_sessionmaker(database_engine,class_=AsyncSession,expire_on_commit=False)
def resource_type(resource):
    if resource.is_file():
        return 'file'
    elif resource.is_dir():
        return 'directory'
    else:
        return 'other'
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
def set_archive_status(selected_resource_type,resource,folder_saved_resources,resource_name):
    if selected_resource_type=='file':
        if resource.suffix not in compressed_formats:
            with py7zr.SevenZipFile(folder_saved_resources/'archive.7z',mode='w') as archive:
                archive.write(file=resource,arcname=resource_name)
            archived_status = True
        else:
            shutil.copy(resource,folder_saved_resources/resource_name)
            archived_status = False
    elif selected_resource_type=='directory':
        archived_status=any(file.is_file() and file.suffix.lower() not in compressed_formats for file in resource.rglob('*'))
        if archived_status:
            with py7zr.SevenZipFile(folder_saved_resources/'archive.7z',mode='w') as archive:
                archive.writeall(path=resource,arcname=resource_name)
        else:
            shutil.copytree(resource,folder_saved_resources/resource_name,dirs_exist_ok=True)
    else:
        return None
    return archived_status
def translation(resource_message,resource_title):
    client_language=(locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(), 'en_US')).split('_')[0]
    try:
        client_message = GoogleTranslator(source='en',target=client_language).translate(resource_message)
        client_title = GoogleTranslator(source='en',target=client_language).translate(resource_title)
    except (requests.exceptions.ConnectionError, deep_translator.exceptions.TranslationNotFound):
        client_message=resource_message
        client_title=resource_title
    return client_message,client_title
def send_resource_to_trash(resource):
        send2trash(resource)
def client_notification(client_message,client_title):
    notification.notify(title=client_title,message=client_message,app_name='OsmiumSmartestBackupper',timeout=5)
async def include_backup_copy():
    resource=Path(sys.argv[1])
    resource_uuid=str(uuid.uuid4())
    resource_name=resource.name
    resource_data_delete=datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    folder_saved_resources=Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData'/'Local'))/'OsmiumSmartestBackupper'/'SavedResources'/resource_uuid
    await asyncio.to_thread(folder_saved_resources.mkdir,parents=True,exist_ok=True)
    resource_status_type = await asyncio.to_thread(resource_type,resource)
    if resource_status_type=='file':
        resource_bytes_size=await asyncio.to_thread(lambda: resource.stat().st_size)
        resource_formated_size=calculation_resource_size(resource_bytes_size)
        archived_status=await asyncio.to_thread(set_archive_status,resource_status_type,resource,folder_saved_resources,resource_name)
        resource_message=f'The file has been moved to the Recycle Bin, and its backup has been saved.'
        resource_title='File deletion'
    elif resource_status_type=='directory':
        resource_bytes_size=await asyncio.to_thread(lambda: float(sum(file.stat().st_size for file in resource.rglob('*') if file.is_file())))
        resource_formated_size=calculation_resource_size(resource_bytes_size)
        archived_status = await asyncio.to_thread(set_archive_status,resource_status_type,resource,folder_saved_resources,resource_name)
        resource_message=f'The directory has been moved to the Recycle Bin, and its backup has been saved.'
        resource_title='Directory deletion'
    else:
        return
    await asyncio.to_thread(send_resource_to_trash,resource)
    async with async_session() as session:
        session.add(Resources(uuid=resource_uuid,name=resource_name,size=resource_formated_size,archived=archived_status,data_delete=resource_data_delete))
        await session.commit()
    client_message,client_title=await asyncio.to_thread(translation,resource_message,resource_title)
    await asyncio.to_thread(client_notification,client_message,client_title)