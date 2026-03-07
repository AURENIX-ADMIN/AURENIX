
import os
import logging
from typing import Optional, Dict, Any
import asyncpg
import json

# Config (Should load from env)
DB_DSN = os.getenv("DATABASE_URL")

class LedgerService:
    @staticmethod
    async def record_usage(tenant_id: str, amount: float, description: str, metadata: Optional[Dict] = None) -> str:
        """
        Records a usage transaction in the Double-Entry Ledger.
        This operation is atomic and will fail if funds are insufficient.
        """
        logging.info(f"Recording usage for tenant {tenant_id}: ${amount} - {description}")
        
        try:
            conn = await asyncpg.connect(DB_DSN)
            transaction_id = await conn.fetchval("""
                SELECT record_usage_transaction($1, $2, $3, $4)
            """, tenant_id, amount, description, json.dumps(metadata or {}))
            await conn.close()
            return str(transaction_id)
        except Exception as e:
            logging.error(f"Ledger Transaction Failed: {e}")
            raise e

    @staticmethod
    async def get_balance(tenant_id: str) -> float:
        """
        Gets the current liability (credit) balance for a tenant.
        """
        try:
            conn = await asyncpg.connect(DB_DSN)
            # Find the liability account for this tenant
            balance = await conn.fetchval("""
                SELECT ab.current_balance 
                FROM account_balances ab
                JOIN accounts a ON ab.account_id = a.id
                WHERE a.tenant_id = $1 AND a.type = 'LIABILITY'
            """, tenant_id)
            await conn.close()
            return float(balance) if balance else 0.0
        except Exception as e:
            logging.error(f"Failed to fetch balance: {e}")
            return 0.0

# Integration test if run directly
if __name__ == "__main__":
    import asyncio
    async def test():
        # Use the tenant ID from the verification run
        print("Testing Ledger Service...")
        # Note: In a real run, we'd need a valid tenant ID.
        pass
    # asyncio.run(test())
