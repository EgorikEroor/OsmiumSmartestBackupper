import asyncio
import shutil
from pathlib import Path

import py7zr
from sqlalchemy import delete
from sqlalchemy import select


from database import Resource
from config import  SAVED_RESOURCES_DIRECTORY, async_session





def unload_resource(
    is_archived: bool,
    backup_directory: Path,
    resource_name: str,
    destination_directory: Path,
) -> None:
    if is_archived:
        with py7zr.SevenZipFile(
            backup_directory / "archive.7z",
            mode="r",
        ) as archive:
            archive.extractall(
                path=destination_directory
            )

    else:
        resource_path = (
            backup_directory / resource_name
        )

        if resource_path.is_file():
            shutil.copy(
                resource_path,
                destination_directory,
            )

        elif resource_path.is_dir():
            shutil.copytree(
                resource_path,
                destination_directory / resource_name,
                dirs_exist_ok=True,
            )

    shutil.rmtree(backup_directory)


async def restore_backup(
    resource_uuid: str,
    destination_directory: str,
) -> None:
    backup_directory = (
        SAVED_RESOURCES_DIRECTORY / resource_uuid
    )

    async with async_session() as session:
        directory_exists = await asyncio.to_thread(
            backup_directory.exists
        )

        if directory_exists:
            is_archived, resource_name = await session.execute(
                select(Resource.is_archived, Resource.name)
                .where(Resource.uuid == resource_uuid)
            ).first()

            await asyncio.to_thread(
                unload_resource,
                is_archived,
                backup_directory,
                resource_name,
                Path(destination_directory),
            )

        await session.execute(
            delete(Resource).where(
                Resource.uuid == resource_uuid
            )
        )

        await session.commit()