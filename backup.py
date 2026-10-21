import asyncio
import datetime
import random
import shutil
import sys
import time
import uuid
from pathlib import Path
import math
import py7zr
from plyer import notification
from send2trash import send2trash
from sqlalchemy.exc import OperationalError

from database import Resource,async_session


from config import SAVED_RESOURCES_DIRECTORY

COMPRESSED_FORMATS = frozenset({
    ".7z",
    ".avi",
    ".docx",
    ".gif",
    ".img",
    ".iso",
    ".jpg",
    ".mkv",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
    ".pptx",
    ".rar",
    ".gz",
    ".xlsx",
    ".zip",
    ".jpeg",
    ".webp",
    ".heic",
    ".webm",
    ".mov",
    ".flac",
    ".m4a",
    ".ogg",
    ".xz",
    ".bz2",
    ".jar",
    ".apk"
})


def get_resource_type(resource: Path) -> str:
    if resource.is_symlink():
        return "symboliclink"
    elif resource.is_file():
        return "file"
    elif resource.is_dir():
        return "directory"
    else:
        return "other"


def format_resource_size(size: int) -> str:
    if size <= 0:
        return "0 B"

    resource_units = ["B", "KB", "MB", "GB", "TB"]

    index = min((int(size).bit_length() - 1) // 10, len(resource_units) - 1)
    value = round(size / 1024 ** index, 2)
    if value >= 1024 and index < len(resource_units) - 1:
        value, index = 1, index + 1

    return f"{value} {resource_units[index]}"


def create_backup_copy(
    resource_type: str,
    resource: Path,
    backup_directory: Path,
    resource_name: str,
) -> bool | None:
    if resource_type == "file":
        if resource.suffix.lower() not in COMPRESSED_FORMATS:
            with py7zr.SevenZipFile(
                backup_directory / "archive.7z",
                mode="w",
            ) as archive:
                archive.write(
                    file=resource,
                    arcname=resource_name,
                )

            return True

        shutil.copy(
            resource,
            backup_directory / resource_name,
        )

        return False

    if resource_type == "directory":
        contains_uncompressed_files = any(
            file.is_file()
            and file.suffix.lower() not in COMPRESSED_FORMATS
            for file in resource.rglob("*")
        )

        if contains_uncompressed_files:
            with py7zr.SevenZipFile(
                backup_directory / "archive.7z",
                mode="w",
            ) as archive:
                archive.writeall(
                    path=resource,
                    arcname=resource_name,
                )

            return True

        shutil.copytree(
            resource,
            backup_directory / resource_name,
            dirs_exist_ok=True,
        )

        return False

    return None


def show_notification(message: str, title: str) -> None:
    notification.notify(
        title=title,
        message=message,
        app_name="OsmiumSmartestBackupper",
        timeout=5,
    )


async def create_backup():
    resource = Path(sys.argv[1])
    resource_uuid = str(uuid.uuid4())
    resource_name = resource.name

    deleted_at = datetime.datetime.now().strftime(
        "%Y.%m.%d %H:%M:%S"
    )

    backup_directory = (
        SAVED_RESOURCES_DIRECTORY / resource_uuid
    )

    await asyncio.to_thread(
        backup_directory.mkdir,
        parents=True,
        exist_ok=True,
    )

    resource_type = await asyncio.to_thread(
        get_resource_type,
        resource,
    )

    if resource_type == "other":
        await asyncio.to_thread(
            show_notification,
            "The unidentified resource was not deleted.",
            "Error",
        )
        return

    resource_config = {
        "file": {
            "resource_size": lambda : int(resource.stat().st_size),
            "resource_message": (
            "The file has been moved to the Recycle Bin, "
            "and its backup has been saved."
            ),
            "resource_title": "File deletion"
        },
        "directory": {
            "resource_size": lambda: int(
                sum(
                    file.stat().st_size
                    for file in resource.rglob("*")
                    if file.is_file()
                )
            ),
            "resource_message": (
            "The directory has been moved to the Recycle Bin, "
            "and its backup has been saved."
            ),
            "resource_title": "Directory deletion"
        }
    }

    formatted_size = format_resource_size(
        await asyncio.to_thread(
            resource_config[resource_type]["resource_size"]
        )
    )

    message = resource_config[resource_type]["resource_message"]

    title = resource_config[resource_type]["resource_title"]

    is_archived = await asyncio.to_thread(
            create_backup_copy,
            resource_type,
            resource,
            backup_directory,
            resource_name,
        )

    attempt_commit = 0
    while True:
        try:
            async with async_session() as session:
                session.add(
                    Resource(
                        uuid=resource_uuid,
                        name=resource_name,
                        size=formatted_size,
                        is_archived=is_archived,
                        deleted_at=deleted_at,
                    )
                )

                await session.commit()
                break
        except OperationalError:
            attempt_commit += 1
            delay = 0.05 * (2 ** attempt_commit) + random.uniform(0,0.1)
            await asyncio.sleep(delay=delay)


    await asyncio.to_thread(
        send2trash,
        resource,
    )


    await asyncio.to_thread(
        show_notification,
        message,
        title,
    )
