import asyncio

from database import create_database,database_engine
from interface import run_interface


async def main():
    await create_database()
    await database_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
    run_interface()
