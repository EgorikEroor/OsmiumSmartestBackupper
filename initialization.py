import winreg
from pathlib import Path
import shutil
from win32com.client import Dispatch
import os
from  config import BINARY_DIRECTORY,SOFTWARECLASSESFILES,SOFTWARECLASSESDIRECTORIES,APP_PATH,SHORTCUT_PATH
def create_app():
    BINARY_DIRECTORY.mkdir(parents=True,exist_ok=True)
    for file in Path(Path(__file__).resolve().parent/'dist').iterdir():
        shutil.move(file,BINARY_DIRECTORY/file.name)
    for root in (SOFTWARECLASSESFILES, SOFTWARECLASSESDIRECTORIES):
        key_path = fr'{root}\shell\Delete & Back up\command'
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,key_path) as key:
            winreg.SetValue(key,'',winreg.REG_SZ,APP_PATH)
    shortcut = Dispatch('WScript.Shell').CreateShortcut(str(SHORTCUT_PATH))
    shortcut.TargetPath = str(BINARY_DIRECTORY / 'interface_app.exe')
    shortcut.WorkingDirectory = str(BINARY_DIRECTORY)
    shortcut.Save()

if __name__ == "__main__":
    create_app()