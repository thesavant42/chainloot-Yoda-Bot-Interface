# Test for Asyncronous Postgresql connectivity
# change DB credentials to real ones
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio

async def test():
    engine = create_async_engine("postgresql+asyncpg://root:root@192.168.1.98:5432/postgres")
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())
    await engine.dispose()

asyncio.run(test())