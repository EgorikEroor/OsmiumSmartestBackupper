"""Removal of the application and its Explorer integration."""

import shutil
import subprocess
import sys
import winreg

from config import (
    APPLICATION_DIRECTORY,
    SAVED_RESOURCES_DIRECTORY,
    BINARY_DIRECTORY,
    DATABASE_DIRECTORY,
    CONTEXT_MENU_NAME,
    REGISTRY_DIRECTORIES_CLASS_PATH,
    REGISTRY_FILES_CLASS_PATH,
    START_MENU_SHORTCUT_PATH,
)


def uninstall_app() -> None:
    """Remove binaries, context-menu entries and the shortcut."""
    try:
        shutil.rmtree(SAVED_RESOURCES_DIRECTORY)
        shutil.rmtree(BINARY_DIRECTORY)
        shutil.rmtree(DATABASE_DIRECTORY)
        shutil.rmtree(APPLICATION_DIRECTORY)
    except (FileNotFoundError, OSError):
        pass
    for registry_root in (
        REGISTRY_FILES_CLASS_PATH,
        REGISTRY_DIRECTORIES_CLASS_PATH,
    ):
        menu_key_path = rf"{registry_root}\shell\{CONTEXT_MENU_NAME}"
        try:
            winreg.DeleteKey(
                winreg.HKEY_CURRENT_USER,
                rf"{menu_key_path}\command",
            )
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, menu_key_path)
        except (FileNotFoundError, OSError):
            continue

    if START_MENU_SHORTCUT_PATH.exists():
        try:
            START_MENU_SHORTCUT_PATH.unlink()
        except OSError:
            pass

    current_executable = sys.argv[0]
    delete_command = (
        "choice /c y /n /t 1 /d y > nul & "
        f'del /f /q "{current_executable}"'
    )
    subprocess.Popen(
        delete_command,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    uninstall_app()