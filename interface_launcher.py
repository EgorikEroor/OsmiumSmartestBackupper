"""Entry point of the graphical interface."""

import asyncio

from database import create_database, database_engine
from main_window import run_main_window


async def main() -> None:
    """Prepare the database before the window starts."""
    await create_database()
    await database_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
    run_main_window()