import asyncio
from database import create_database
from include_backup_copy import include_backup_copy
async def main():
    await create_database()
    await include_backup_copy()
if __name__=='__main__':
    asyncio.run(main())