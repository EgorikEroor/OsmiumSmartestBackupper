import winreg
import requests.exceptions
from deep_translator import GoogleTranslator
import ctypes
import locale
from ctypes import wintypes
client_language = (locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(),'en_US')).split('_')[0]
try:
    client_button_name = GoogleTranslator(source='en',target=client_language).translate('Delete')
except requests.exceptions.ConnectionError:
    client_button_name = 'Delete'
with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT,fr'*\shell\{client_button_name}') as chapter_1:
    with winreg.CreateKey(chapter_1,'command') as chapter_2:
        winreg.SetValue(chapter_2,'',winreg.REG_SZ,fr'"G:\Programming\MyApps\OSB\dist\logic.exe" "%1"')
