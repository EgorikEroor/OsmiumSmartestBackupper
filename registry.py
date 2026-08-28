import winreg
import deep_translator.exceptions
import requests.exceptions
from deep_translator import GoogleTranslator
import ctypes
import locale
from ctypes import wintypes
import sqlite3
from pathlib import Path
def create_button():
    client_language = (locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(),'en_US')).split('_')[0]
    try:
        client_button_name = GoogleTranslator(source='en',target=client_language).translate('Delete')
    except requests.exceptions.ConnectionError:
        client_button_name = 'Delete'
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT,fr'*\shell\{client_button_name}') as chapter_1:
        with winreg.CreateKey(chapter_1,'command') as chapter_2:
            winreg.SetValue(chapter_2,'',winreg.REG_SZ,fr'"G:\Programming\MyApps\OSB\dist\main.exe" "%1"')
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT,fr'Directory\shell\{client_button_name}') as chapter_1:
        with winreg.CreateKey(chapter_1,'command') as chapter_2:
            winreg.SetValue(chapter_2,'',winreg.REG_SZ,fr'"G:\Programming\MyApps\OSB\dist\main.exe" "%1"')
path_database = Path.home() / 'AppData' / 'Local' / 'OsmiumSmartestBackupper' / 'Database'
path_database.mkdir(parents=True,exist_ok=True)
create_button()