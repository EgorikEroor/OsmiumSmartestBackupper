"""Restoration of backed-up resources."""

import asyncio
import shutil
from pathlib import Path

import py7zr
from sqlalchemy import delete, select

from config import SAVED_RESOURCES_DIRECTORY
from database import BackedUpResource, session_factory


def extract_backup(
    is_archived: bool,
    backup_directory: Path,
    resource_name: str,
    destination_directory: Path,
) -> None:
    """Extract or copy the backed-up resource to the destination."""
    if is_archived:
        with py7zr.SevenZipFile(
            backup_directory / "archive.7z",
            mode="r",
        ) as archive:
            archive.extractall(path=destination_directory)
        return

    backup_path = backup_directory / resource_name

    if backup_path.is_file():
        shutil.copy(backup_path, destination_directory)
    elif backup_path.is_dir():
        shutil.copytree(
            backup_path,
            destination_directory / resource_name,
            dirs_exist_ok=True,
        )


async def restore_backup(
    resource_uuid: str,
    destination_directory: str,
) -> None:
    """Restore a resource and remove its backup and database record."""
    backup_directory = SAVED_RESOURCES_DIRECTORY / resource_uuid

    async with session_factory() as session:
        backup_exists = await asyncio.to_thread(backup_directory.exists)

        if backup_exists:
            result = await session.execute(
                select(
                    BackedUpResource.is_archived,
                    BackedUpResource.resource_name,
                )
                .where(BackedUpResource.backup_uuid == resource_uuid)
            )
            is_archived, resource_name = result.first()

            await asyncio.to_thread(
                extract_backup,
                is_archived,
                backup_directory,
                resource_name,
                Path(destination_directory),
            )

        await session.execute(
            delete(BackedUpResource)
            .where(BackedUpResource.backup_uuid == resource_uuid)
        )
        await session.commit()

        shutil.rmtree(backup_directory)