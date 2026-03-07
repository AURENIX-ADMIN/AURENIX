
import asyncio
import asyncpg
import uuid

DB_DSN = "postgresql://aurenix:aurenix_password@localhost:5432/aurenix_db"

async def verify_logic():
    print(f"Connecting to {DB_DSN}...")
    conn = await asyncpg.connect(DB_DSN)
    
    # 1. Setup Test Tenant
    tenant_id = str(uuid.uuid4())
    print(f"Created Test Tenant ID: {tenant_id}")
    
    # 2. Open Account (Liability - Customer Credits)
    # In real system, this happens on signup
    account_id = await conn.fetchval("""
        INSERT INTO accounts (tenant_id, name, type) 
        VALUES ($1, 'Test Wallet', 'LIABILITY') 
        RETURNING id
    """, tenant_id)
    print(f"Created Liability Account: {account_id}")
    
    # 3. Fund Account (Simulate Stripe Payment)
    # Debit Cash (Asset), Credit Customer Liability
    # For simplicity here, we just care about the Liability side having a credit balance.
    # We will manually insert a 'Top Up' transaction.
    
    # First, get or create a Cash Asset account for the system
    cash_account_id = await conn.fetchval("""
        INSERT INTO accounts (name, type) 
        VALUES ('System Bank', 'ASSET') 
        ON CONFLICT DO NOTHING
        RETURNING id
    """)
    if not cash_account_id:
        cash_account_id = await conn.fetchval("SELECT id FROM accounts WHERE name = 'System Bank'")

    # Transaction: Client pays $100
    trx_id = await conn.fetchval("""
        INSERT INTO transactions (description) VALUES ('Initial Top Up $100') RETURNING id
    """)
    
    # Asset Increase (Debit)
    await conn.execute("""
        INSERT INTO ledger_entries (transaction_id, account_id, amount, direction)
        VALUES ($1, $2, 100.00, 'DEBIT')
    """, trx_id, cash_account_id)
    
    # Liability Increase (Credit) - This gives the user "spending power"
    await conn.execute("""
        INSERT INTO ledger_entries (transaction_id, account_id, amount, direction)
        VALUES ($1, $2, 100.00, 'CREDIT')
    """, trx_id, account_id)
    
    print("Funded Account with $100.00")
    
    # 4. Check Balance
    # We expect Liability Balance to be 100 (Credit - Debit)
    balance = await conn.fetchval("""
        SELECT current_balance FROM account_balances WHERE account_id = $1
    """, account_id)
    print(f"Current Balance (Liability): {balance}")
    assert float(balance) == 100.00, f"Expected 100.00, got {balance}"
    
    # 5. Execute Usage (Success Case)
    print("Attempting to spend $10.00...")
    usage_trx_id = await conn.fetchval("SELECT record_usage_transaction($1, 10.00, 'AI Inference Task')", tenant_id)
    print(f"Usage Transaction Recorded: {usage_trx_id}")
    
    # 6. Verify New Balance
    new_balance = await conn.fetchval("""
        SELECT current_balance FROM account_balances WHERE account_id = $1
    """, account_id)
    print(f"New Balance: {new_balance}")
    assert float(new_balance) == 90.00, f"Expected 90.00, got {new_balance}"
    
    # 7. Execute Usage (Fail Case - Kill Switch)
    print("Attempting to spend $100.00 (Should Fail)...")
    try:
        await conn.fetchval("SELECT record_usage_transaction($1, 100.00, 'Overdraft Task')", tenant_id)
        print("CRITICAL FAILURE: Transaction should have been rejected!")
        exit(1)
    except asyncpg.exceptions.RaiseError as e:
        print(f"SUCCESS: Transaction rejected as expected. Error: {e}")
        
    print("\n>>> ALL SYSTEM VERIFICATION TESTS PASSED <<<")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_logic())
