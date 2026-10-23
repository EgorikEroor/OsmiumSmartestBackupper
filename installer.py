"""Installation of the application and its Explorer integration."""

import shutil
import sys
import winreg
from pathlib import Path

from win32com.client import Dispatch

from config import (
    BACKUP_APP_PATH,
    BINARY_DIRECTORY,
    CONTEXT_MENU_NAME,
    INTERFACE_APP_PATH,
    REGISTRY_DIRECTORIES_CLASS_PATH,
    REGISTRY_FILES_CLASS_PATH,
    START_MENU_SHORTCUT_PATH,
)


def install_app() -> None:
    """Copy binaries, add context-menu entries and a Start Menu shortcut."""
    BINARY_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # sys._MEIPASS is the documented PyInstaller bundle directory.
    bundled_directory = Path(sys._MEIPASS) / "dist"
    for bundled_file in bundled_directory.iterdir():
        shutil.move(bundled_file, BINARY_DIRECTORY / bundled_file.name)

    for registry_root in (
        REGISTRY_FILES_CLASS_PATH,
        REGISTRY_DIRECTORIES_CLASS_PATH,
    ):
        menu_key_path = rf"{registry_root}\shell\{CONTEXT_MENU_NAME}"
        command_key_path = rf"{menu_key_path}\command"
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            command_key_path,
        ) as key:
            winreg.SetValue(
                key,
                "",
                winreg.REG_SZ,
                f'"{BACKUP_APP_PATH}" "%1"',
            )

    START_MENU_SHORTCUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    shortcut = Dispatch("WScript.Shell").CreateShortcut(
        str(START_MENU_SHORTCUT_PATH)
    )
    shortcut.IconLocation = INTERFACE_APP_PATH
    shortcut.TargetPath = INTERFACE_APP_PATH
    shortcut.WorkingDirectory = str(BINARY_DIRECTORY)
    shortcut.Save()


if __name__ == "__main__":
    install_app()