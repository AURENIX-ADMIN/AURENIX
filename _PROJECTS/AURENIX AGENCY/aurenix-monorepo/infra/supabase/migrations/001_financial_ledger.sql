-- Migration: 001_financial_ledger
-- Description: Sets up the double-entry ledger system for Aurenix Agency OS.
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- 1. Accounts Table
-- Represents the entities in our ledger (e.g., Customer Wallets, System Revenue, External Costs).
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID,
    -- NULL for system accounts
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (
        type IN (
            'ASSET',
            'LIABILITY',
            'EQUITY',
            'REVENUE',
            'EXPENSE'
        )
    ),
    currency TEXT DEFAULT 'USD',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Index for fast lookup by tenant
CREATE INDEX IF NOT EXISTS idx_accounts_tenant_id ON accounts(tenant_id);
-- 2. Transactions Table (The Journal)
-- Groups atomic entries together.
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    description TEXT,
    reference_id TEXT,
    -- External reference (e.g., Stripe Charge ID, Workflow Run ID)
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_transactions_ref ON transactions(reference_id);
-- 3. Ledger Entries Table (The Lines)
-- Individual debit/credit lines.
CREATE TABLE IF NOT EXISTS ledger_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES transactions(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    amount DECIMAL(20, 4) NOT NULL,
    -- Positive only, direction determines logic
    direction TEXT NOT NULL CHECK (direction IN ('DEBIT', 'CREDIT')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_entries_account ON ledger_entries(account_id);
CREATE INDEX IF NOT EXISTS idx_entries_transaction ON ledger_entries(transaction_id);
-- 4. Balance Calculation Helper View
CREATE OR REPLACE VIEW account_balances AS
SELECT a.id AS account_id,
    a.name,
    a.type,
    a.tenant_id,
    COALESCE(
        SUM(
            CASE
                WHEN le.direction = 'DEBIT' THEN le.amount
                ELSE 0
            END
        ),
        0
    ) AS total_debits,
    COALESCE(
        SUM(
            CASE
                WHEN le.direction = 'CREDIT' THEN le.amount
                ELSE 0
            END
        ),
        0
    ) AS total_credits,
    CASE
        WHEN a.type IN ('ASSET', 'EXPENSE') THEN COALESCE(
            SUM(
                CASE
                    WHEN le.direction = 'DEBIT' THEN le.amount
                    ELSE - le.amount
                END
            ),
            0
        )
        ELSE COALESCE(
            SUM(
                CASE
                    WHEN le.direction = 'CREDIT' THEN le.amount
                    ELSE - le.amount
                END
            ),
            0
        )
    END AS current_balance
FROM accounts a
    LEFT JOIN ledger_entries le ON a.id = le.account_id
GROUP BY a.id;
-- 5. Atomic Transaction Function (The Core Logic)
CREATE OR REPLACE FUNCTION record_usage_transaction(
        p_tenant_id UUID,
        p_amount DECIMAL,
        p_description TEXT,
        p_metadata JSONB DEFAULT '{}'
    ) RETURNS UUID AS $$
DECLARE v_transaction_id UUID;
v_customer_account_id UUID;
v_revenue_account_id UUID;
v_current_balance DECIMAL;
BEGIN -- 1. Identify the Customer's Liability Account (Credits Wallet)
-- We assume each tenant has a 'LIABILITY' account representing their prepaid credits.
SELECT id INTO v_customer_account_id
FROM accounts
WHERE tenant_id = p_tenant_id
    AND type = 'LIABILITY'
LIMIT 1;
IF v_customer_account_id IS NULL THEN RAISE EXCEPTION 'No credit account found for tenant %',
p_tenant_id;
END IF;
-- 2. Identify System Revenue Account
-- For now, we pick a default or specific system account.
SELECT id INTO v_revenue_account_id
FROM accounts
WHERE name = 'System Usage Revenue'
    AND type = 'REVENUE'
LIMIT 1;
-- Create revenue account if not exists (for bootstrapping)
IF v_revenue_account_id IS NULL THEN
INSERT INTO accounts (name, type, currency)
VALUES ('System Usage Revenue', 'REVENUE', 'USD')
RETURNING id INTO v_revenue_account_id;
END IF;
-- 3. Check Balance (Optimistic Locking via FOR UPDATE could be added here if high concurrency)
-- Calculate current balance manually to be safe or use the view logic.
-- Liability Balance = Credits - Debits.
SELECT (
        COALESCE(
            SUM(
                CASE
                    WHEN direction = 'CREDIT' THEN amount
                    ELSE 0
                END
            ),
            0
        ) - COALESCE(
            SUM(
                CASE
                    WHEN direction = 'DEBIT' THEN amount
                    ELSE 0
                END
            ),
            0
        )
    ) INTO v_current_balance
FROM ledger_entries
WHERE account_id = v_customer_account_id;
IF v_current_balance < p_amount THEN RAISE EXCEPTION 'Insufficient funds: Balance % is less than required %',
v_current_balance,
p_amount;
END IF;
-- 4. Create Transaction Header
INSERT INTO transactions (description, metadata)
VALUES (p_description, p_metadata)
RETURNING id INTO v_transaction_id;
-- 5. Insert Ledger Entries (Double Entry)
-- Decrease Customer Liability (Debit)
INSERT INTO ledger_entries (transaction_id, account_id, amount, direction)
VALUES (
        v_transaction_id,
        v_customer_account_id,
        p_amount,
        'DEBIT'
    );
-- Increase System Revenue (Credit)
INSERT INTO ledger_entries (transaction_id, account_id, amount, direction)
VALUES (
        v_transaction_id,
        v_revenue_account_id,
        p_amount,
        'CREDIT'
    );
RETURN v_transaction_id;
END;
$$ LANGUAGE plpgsql;
-- 6. RLS Policies (Draft)
-- ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ledger_entries ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
-- Allow tenants to view their own accounts
-- CREATE POLICY "Tenants can view own accounts" ON accounts FOR
-- SELECT USING (auth.uid() = tenant_id);
-- Allow tenants to view entries linked to their accounts
-- CREATE POLICY "Tenants can view own entries" ON ledger_entries FOR
-- SELECT USING (
--         account_id IN (
--             SELECT id
--             FROM accounts
--             WHERE tenant_id = auth.uid()
--         )
--     );