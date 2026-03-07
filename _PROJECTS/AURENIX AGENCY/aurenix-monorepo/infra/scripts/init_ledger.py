
import asyncio
import asyncpg
import os

# DB Config (matching docker-compose)
DB_DSN = "postgresql://aurenix:aurenix_password@localhost:5432/aurenix_db"

async def init_db():
    print(f"Connecting to {DB_DSN}...")
    try:
        conn = await asyncpg.connect(DB_DSN)
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    print("Connected. Applying migration 001_financial_ledger.sql...")
    
    with open('../supabase/migrations/001_financial_ledger.sql', 'r') as f:
        migration_sql = f.read()
    
    # Clean up SQL slightly to work with asyncpg if needed (usually fine)
    # asyncpg execute supports multiple statements using ;
    try:
        await conn.execute(migration_sql)
        print("Migration applied successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_db())
