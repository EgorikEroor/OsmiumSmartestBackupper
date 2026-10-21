import asyncio

from backup import create_backup
from database import create_database


async def main():
    await create_database()
    await create_backup()


if __name__ == "__main__":
    asyncio.run(main())