import subprocess
import sys
import winreg
import shutil
from  config import BINARY_DIRECTORY,SOFTWARECLASSESFILES,SOFTWARECLASSESDIRECTORIES,SHORTCUT_PATH

def delete_app():
    try:
        shutil.rmtree(BINARY_DIRECTORY)
    except (FileNotFoundError, OSError):
        pass
        for root in (SOFTWARECLASSESFILES, SOFTWARECLASSESDIRECTORIES):
            key_path_command = fr'{root}\shell\Delete && Back up\command'
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER,key_path_command)
                key_path_chapter = fr'{root}\shell\Delete && Back up'
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path_chapter)
            except (FileNotFoundError, OSError):
                continue
        if SHORTCUT_PATH.exists():
            try:
                SHORTCUT_PATH.unlink()
            except OSError:
                pass
        curr_file = sys.argv[0]
        cmd_command = f'choice /c y /n /t 1 /d y > nul & del /f /q "{curr_file}"'
        subprocess.Popen(cmd_command,shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    delete_app()