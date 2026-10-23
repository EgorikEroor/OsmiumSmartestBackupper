import winreg
from pathlib import Path
import shutil
import sys
from win32com.client import Dispatch
from  config import BINARY_DIRECTORY,SOFTWARECLASSESFILES,SOFTWARECLASSESDIRECTORIES,APP_PATH,SHORTCUT_PATH

def create_app():
    BINARY_DIRECTORY.mkdir(parents=True,exist_ok=True)
    for file in (Path(sys._MEIPASS)/'dist').iterdir():
        shutil.move(file,BINARY_DIRECTORY/file.name)
    for root in (SOFTWARECLASSESFILES, SOFTWARECLASSESDIRECTORIES):
        key_path = fr'{root}\shell\Delete && Back up\command'
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,key_path) as key:
            registry_command = fr'"{APP_PATH}" "%1"'
            winreg.SetValue(key,'',winreg.REG_SZ,registry_command)
    SHORTCUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    shortcut = Dispatch('WScript.Shell').CreateShortcut(str(SHORTCUT_PATH))
    shortcut.IconLocation = str(BINARY_DIRECTORY / 'interface_app.exe')
    shortcut.TargetPath = str(BINARY_DIRECTORY / 'interface_app.exe')
    shortcut.WorkingDirectory = str(BINARY_DIRECTORY)
    shortcut.Save()

if __name__ == "__main__":
    create_app()