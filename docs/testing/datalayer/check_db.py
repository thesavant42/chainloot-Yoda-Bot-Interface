import asyncio
import asyncpg
import os
from dotenv import load_dotenv
load_dotenv()

async def check_data():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))

    users = await conn.fetch('SELECT * FROM "User"')
    print(f'Users: {len(users)}')
    for user in users:
        print(f'  {user}')

    threads = await conn.fetch('SELECT * FROM "Thread"')
    print(f'Threads: {len(threads)}')
    for thread in threads:
        print(f'  {thread}')

    steps = await conn.fetch('SELECT * FROM "Step"')
    print(f'Steps: {len(steps)}')
    for step in steps[:10]:  # Show first 10
        print(f'  {step}')

    await conn.close()

asyncio.run(check_data())