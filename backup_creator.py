"""Creation of backups for resources deleted via the context menu."""

import asyncio
import datetime
import random
import shutil
import sys
import uuid
from pathlib import Path

import py7zr
from plyer import notification
from send2trash import send2trash
from sqlalchemy.exc import OperationalError

from config import APPLICATION_NAME, SAVED_RESOURCES_DIRECTORY
from database import BackedUpResource, session_factory

ALREADY_COMPRESSED_EXTENSIONS = frozenset({
    ".7z",
    ".apk",
    ".bz2",
    ".flac",
    ".gz",
    ".heic",
    ".jar",
    ".jpeg",
    ".jpg",
    ".m4a",
    ".mkv",
    ".mp3",
    ".mp4",
    ".ogg",
    ".pdf",
    ".png",
    ".rar",
    ".webm",
    ".webp",
    ".xz",
    ".zip",
})

# Notification (title, message) for every supported resource type.
DELETION_NOTIFICATIONS = {
    "file": (
        "File deletion",
        "The file has been moved to the Recycle Bin, "
        "and its backup has been saved.",
    ),
    "directory": (
        "Directory deletion",
        "The directory has been moved to the Recycle Bin, "
        "and its backup has been saved.",
    ),
}

SIZE_UNITS = ("B", "KB", "MB", "GB", "TB")


def get_resource_type(resource_path: Path) -> str:
    """Return "file", "directory" or "other" for the given path."""
    if resource_path.is_file():
        return "file"
    if resource_path.is_dir():
        return "directory"
    return "other"


def format_size(size_in_bytes: int) -> str:
    """Convert a size in bytes to a human-readable string."""
    if size_in_bytes <= 0:
        return "0 B"

    unit_index = 0
    value = float(size_in_bytes)
    while value >= 1024 and unit_index < len(SIZE_UNITS) - 1:
        value /= 1024
        unit_index += 1
    return f"{round(value, 2)} {SIZE_UNITS[unit_index]}"


def calculate_resource_size(resource_path: Path, resource_type: str) -> int:
    """Return the total size of a file or directory in bytes."""
    if resource_type == "file":
        return int(resource_path.stat().st_size)

    return int(
        sum(
            file_path.stat().st_size
            for file_path in resource_path.rglob("*")
            if file_path.is_file()
        )
    )


def store_backup_copy(
    resource_type: str,
    resource_path: Path,
    backup_directory: Path,
    resource_name: str,
) -> bool | None:
    """Store a backup copy of the resource.

    Return True if the copy was packed into a 7z archive, False if it
    was copied as is, and None if the resource type is unsupported.
    """
    if resource_type == "file":
        if resource_path.suffix.lower() not in ALREADY_COMPRESSED_EXTENSIONS:
            with py7zr.SevenZipFile(
                backup_directory / "archive.7z",
                mode="w",
            ) as archive:
                archive.write(file=resource_path, arcname=resource_name)
            return True

        shutil.copy2(resource_path, backup_directory / resource_name)
        return False

    if resource_type == "directory":
        has_uncompressed_files = any(
            file_path.is_file()
            and file_path.suffix.lower() not in ALREADY_COMPRESSED_EXTENSIONS
            for file_path in resource_path.rglob("*")
        )

        if has_uncompressed_files:
            with py7zr.SevenZipFile(
                backup_directory / "archive.7z",
                mode="w",
            ) as archive:
                archive.writeall(path=resource_path, arcname=resource_name)
            return True

        shutil.copytree(
            resource_path,
            backup_directory / resource_name,
            symlinks=True,
        )
        return False

    return None


def show_notification(message: str, title: str) -> None:
    """Show a desktop notification."""
    notification.notify(
        title=title,
        message=message,
        app_name=APPLICATION_NAME,
        timeout=5,
    )


async def save_resource_record(
    resource_record: BackedUpResource,
) -> None:
    """Save the record to the database, retrying while it is locked."""
    commit_attempt = 0
    while True:
        try:
            async with session_factory() as session:
                session.add(resource_record)
                await session.commit()
                break
        except OperationalError:
            commit_attempt += 1
            delay = 0.05 * (2 ** commit_attempt) + random.uniform(0, 0.1)
            await asyncio.sleep(delay)


async def create_backup() -> None:
    """Back up the resource passed in argv, then move it to the bin."""
    resource_path = Path(sys.argv[1])
    resource_type = await asyncio.to_thread(get_resource_type, resource_path)

    if resource_type == "other":
        await asyncio.to_thread(
            show_notification,
            "The unidentified resource was not deleted.",
            "Error",
        )
        return

    resource_uuid = str(uuid.uuid4())
    resource_name = resource_path.name
    deleted_at = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    backup_directory = SAVED_RESOURCES_DIRECTORY / resource_uuid

    await asyncio.to_thread(
        backup_directory.mkdir,
        parents=True,
        exist_ok=True,
    )

    size_in_bytes = await asyncio.to_thread(
        calculate_resource_size,
        resource_path,
        resource_type,
    )
    notification_title, notification_message = (
        DELETION_NOTIFICATIONS[resource_type]
    )

    is_archived = await asyncio.to_thread(
        store_backup_copy,
        resource_type,
        resource_path,
        backup_directory,
        resource_name,
    )

    await save_resource_record(
        BackedUpResource(
            backup_uuid=resource_uuid,
            resource_name=resource_name,
            formatted_size=format_size(size_in_bytes),
            is_archived=is_archived,
            deleted_at=deleted_at,
        )
    )

    await asyncio.to_thread(send2trash, resource_path)
    await asyncio.to_thread(
        show_notification,
        notification_message,
        notification_title,
    )