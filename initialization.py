import winreg
from pathlib import Path
import shutil
from win32com.client import Dispatch
import os
from  config import BINARY_DIRECTORY
def create_button():
    BINARY_DIRECTORY.mkdir(parents=True,exist_ok=True)
    for file in Path(Path(__file__).resolve().parent/'dist').iterdir():
        shutil.move(file,BINARY_DIRECTORY/file.name)
    app_path = f'"{BINARY_DIRECTORY / "backup_app.exe"}" "%1"'
    for root in (r'Software\Classes\*', r'Software\Classes\Directory'):
        key_path = fr'{root}\shell\Delete\command'
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,key_path) as key:
            winreg.SetValue(key,'',winreg.REG_SZ,app_path)
    start_menu_programs = Path(os.environ.get('APPDATA')) / 'Microsoft/Windows/Start Menu/Programs'
    shortcut_path = start_menu_programs / 'OsmiumSmartestBackupper.lnk'
    shortcut = Dispatch('WScript.Shell').CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = str(BINARY_DIRECTORY / 'interface_app.exe')
    shortcut.WorkingDirectory = str(BINARY_DIRECTORY)
    shortcut.Save()

if __name__ == "__main__":
    create_button()