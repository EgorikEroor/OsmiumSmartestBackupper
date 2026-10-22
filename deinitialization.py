import subprocess
import sys
import winreg
import shutil
from  config import BINARY_DIRECTORY,SOFTWARECLASSESFILES,SOFTWARECLASSESDIRECTORIES,SHORTCUT_PATH

def delete_app():
    try:
        shutil.rmtree(BINARY_DIRECTORY)
        for root in (SOFTWARECLASSESFILES, SOFTWARECLASSESDIRECTORIES):
            key_path_command = fr'{root}\shell\Delete & Back up\command'
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER,key_path_command)
            key_path_chapter = fr'{root}\shell\Delete & Back up'
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path_chapter)
        if SHORTCUT_PATH.exists():
            SHORTCUT_PATH.unlink()
        curr_file = sys.argv[0]
        cmd_command = f'choice /t 1 /d y > null & del /f /q "{curr_file}"'
        subprocess.Popen(cmd_command,shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except (FileNotFoundError, PermissionError):
        pass

if __name__ == "__main__":
    delete_app()