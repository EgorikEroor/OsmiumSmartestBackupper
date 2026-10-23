"""Application-wide paths and constants."""

import os
from pathlib import Path

APPLICATION_NAME = "OsmiumSmartestBackupper"
CONTEXT_MENU_NAME = "Delete && Back up"

LOCAL_APP_DATA = Path(
    os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
)
ROAMING_APP_DATA = Path(
    os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
)

APPLICATION_DIRECTORY = LOCAL_APP_DATA / APPLICATION_NAME
SAVED_RESOURCES_DIRECTORY = APPLICATION_DIRECTORY / "saved_resources"
BINARY_DIRECTORY = APPLICATION_DIRECTORY / "binary"
DATABASE_DIRECTORY = APPLICATION_DIRECTORY / "database"
DATABASE_PATH = DATABASE_DIRECTORY / "database_resources.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH.as_posix()}"

REGISTRY_FILES_CLASS_PATH = r"Software\Classes\*"
REGISTRY_DIRECTORIES_CLASS_PATH = r"Software\Classes\Directory"

BACKUP_APP_PATH = str(BINARY_DIRECTORY / "backup_launcher.exe")
INTERFACE_APP_PATH = str(BINARY_DIRECTORY / "interface_launcher.exe")

START_MENU_PROGRAMS = (
    ROAMING_APP_DATA / "Microsoft" / "Windows" / "Start Menu" / "Programs"
)
START_MENU_SHORTCUT_PATH = START_MENU_PROGRAMS / f"{APPLICATION_NAME}.lnk"