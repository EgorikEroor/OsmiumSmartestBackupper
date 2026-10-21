import os
from pathlib import Path

APPLICATION_DIRECTORY = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "OsmiumSmartestBackupper"
SAVED_RESOURCES_DIRECTORY = APPLICATION_DIRECTORY / "saved_resources"
BINARY_DIRECTORY = APPLICATION_DIRECTORY / "binary"
DATABASE_DIRECTORY = APPLICATION_DIRECTORY / "database"
DATABASE_PATH = DATABASE_DIRECTORY / "database_resources.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH.as_posix()}"