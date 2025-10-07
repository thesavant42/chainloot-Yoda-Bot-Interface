import asyncio
import asyncpg

async def create_tables():
    conn = await asyncpg.connect('postgresql://root:root@192.168.1.98:5432/chainlit')
    
    # Drop tables in reverse dependency order
    await conn.execute('DROP TABLE IF EXISTS "Feedback" CASCADE;')
    await conn.execute('DROP TABLE IF EXISTS "Element" CASCADE;')
    await conn.execute('DROP TABLE IF EXISTS "Step" CASCADE;')
    await conn.execute('DROP TABLE IF EXISTS "Thread" CASCADE;')
    await conn.execute('DROP TABLE IF EXISTS "User" CASCADE;')
    
    # Users table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS "User" (
            "id" UUID PRIMARY KEY,
            "identifier" TEXT NOT NULL UNIQUE,
            "metadata" JSONB NOT NULL,
            "createdAt" TIMESTAMP,
            "updatedAt" TIMESTAMP
        );
    ''')
    
    # Threads table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS "Thread" (
            "id" UUID PRIMARY KEY,
            "createdAt" TIMESTAMP,
            "updatedAt" TIMESTAMP,
            "name" TEXT,
            "userId" UUID,
            "metadata" JSONB,
            "tags" TEXT[],
            "deletedAt" TIMESTAMP,
            FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE
        );
    ''')
    
    # Steps table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS "Step" (
            "id" UUID PRIMARY KEY,
            "threadId" UUID,
            "parentId" UUID,
            "name" TEXT,
            "type" TEXT NOT NULL,
            "input" TEXT,
            "output" TEXT,
            "metadata" JSONB,
            "createdAt" TIMESTAMP,
            "startTime" TIMESTAMP,
            "endTime" TIMESTAMP,
            "showInput" TEXT,
            "isError" BOOLEAN,
            FOREIGN KEY ("threadId") REFERENCES "Thread"("id") ON DELETE CASCADE
        );
    ''')
    
    # Elements table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS "Element" (
            "id" UUID PRIMARY KEY,
            "threadId" UUID,
            "stepId" UUID,
            "metadata" JSONB,
            "mime" TEXT,
            "name" TEXT NOT NULL,
            "objectKey" TEXT,
            "url" TEXT,
            "chainlitKey" TEXT,
            "display" TEXT,
            "size" TEXT,
            "language" TEXT,
            "page" INT,
            "props" JSONB,
            FOREIGN KEY ("threadId") REFERENCES "Thread"("id") ON DELETE CASCADE
        );
    ''')
    
    # Feedbacks table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS "Feedback" (
            "id" UUID PRIMARY KEY,
            "forId" UUID NOT NULL,
            "threadId" UUID NOT NULL,
            "value" INT NOT NULL,
            "comment" TEXT,
            FOREIGN KEY ("threadId") REFERENCES "Thread"("id") ON DELETE CASCADE
        );
    ''')
    
    await conn.close()
    print('Tables created')

asyncio.run(create_tables())