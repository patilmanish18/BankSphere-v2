CREATE TABLE IF NOT EXISTS accounts (
    account_id      SERIAL PRIMARY KEY,
    account_number  VARCHAR(20) UNIQUE NOT NULL,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    branch_id       INTEGER NOT NULL REFERENCES branches(branch_id),
    account_type    VARCHAR(20) NOT NULL CHECK (account_type IN ('SAVINGS','CURRENT','FIXED_DEPOSIT')),
    balance         NUMERIC(15,2) NOT NULL DEFAULT 0,
    currency        VARCHAR(3) NOT NULL DEFAULT 'INR',
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','INACTIVE','CLOSED')),
    opened_date     DATE NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_accounts_branch ON accounts(branch_id);
