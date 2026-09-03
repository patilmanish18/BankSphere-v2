CREATE TABLE IF NOT EXISTS transactions (
    transaction_id      SERIAL PRIMARY KEY,
    account_id           INTEGER NOT NULL REFERENCES accounts(account_id),
    transaction_type     VARCHAR(20) NOT NULL CHECK (transaction_type IN ('DEPOSIT','WITHDRAWAL','TRANSFER','PAYMENT')),
    amount                NUMERIC(15,2) NOT NULL,
    balance_after         NUMERIC(15,2) NOT NULL,
    description           VARCHAR(200),
    transaction_date      TIMESTAMP NOT NULL,
    created_at            TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
