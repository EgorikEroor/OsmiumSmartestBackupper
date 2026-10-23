"""Entry point of the context-menu "Delete && Back up" command."""

import asyncio

from backup_creator import create_backup
from database import create_database


async def main() -> None:
    """Prepare the database and back up the resource."""
    await create_database()
    await create_backup()


if __name__ == "__main__":
    asyncio.run(main())