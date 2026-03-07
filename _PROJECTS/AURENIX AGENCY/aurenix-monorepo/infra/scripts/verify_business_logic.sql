DO $$
DECLARE v_tenant_id UUID := uuid_generate_v4();
v_account_id UUID;
v_trx_id UUID;
v_balance DECIMAL;
v_usage_trx_id UUID;
BEGIN RAISE NOTICE 'Starting Verification for Tenant: %',
v_tenant_id;
-- 1. Create Account
INSERT INTO accounts (tenant_id, name, type)
VALUES (v_tenant_id, 'Test Wallet', 'LIABILITY')
RETURNING id INTO v_account_id;
RAISE NOTICE 'Created Liability Account: %',
v_account_id;
-- 2. Fund Account ($100)
INSERT INTO transactions (description)
VALUES ('Initial Top Up $100')
RETURNING id INTO v_trx_id;
-- Credit Liability (Customer gets credits)
INSERT INTO ledger_entries (transaction_id, account_id, amount, direction)
VALUES (v_trx_id, v_account_id, 100.00, 'CREDIT');
-- Debit Cash (System gets cash - simplifying asset side for test)
-- We just care about the customer balance here.
-- 3. Verify Balance
SELECT current_balance INTO v_balance
FROM account_balances
WHERE account_id = v_account_id;
IF v_balance != 100.00 THEN RAISE EXCEPTION 'Balance mismatch! Expected 100.00, got %',
v_balance;
END IF;
RAISE NOTICE 'Funded Balance Verified: %',
v_balance;
-- 4. Execute Usage ($10)
SELECT record_usage_transaction(v_tenant_id, 10.00, 'AI Inference Task') INTO v_usage_trx_id;
RAISE NOTICE 'Usage Transaction Recorded: %',
v_usage_trx_id;
-- 5. Verify New Balance
SELECT current_balance INTO v_balance
FROM account_balances
WHERE account_id = v_account_id;
IF v_balance != 90.00 THEN RAISE EXCEPTION 'Balance mismatch after usage! Expected 90.00, got %',
v_balance;
END IF;
RAISE NOTICE 'Post-Usage Balance Verified: %',
v_balance;
-- 6. Kill Switch Test (Overdraft)
BEGIN PERFORM record_usage_transaction(v_tenant_id, 100.00, 'Overdraft Task');
RAISE EXCEPTION 'Kill Switch FAILED! Transaction should have been rejected.';
EXCEPTION
WHEN OTHERS THEN IF SQLERRM LIKE '%Insufficient funds%' THEN RAISE NOTICE 'SUCCESS: Kill Switch activated. Error detected: %',
SQLERRM;
ELSE RAISE EXCEPTION 'Unexpected error: %',
SQLERRM;
END IF;
END;
RAISE NOTICE '>>> ALL SYSTEM VERIFICATION TESTS PASSED <<<';
END $$;