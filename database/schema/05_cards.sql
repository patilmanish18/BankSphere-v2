CREATE TABLE IF NOT EXISTS cards (
    card_id         SERIAL PRIMARY KEY,
    account_id      INTEGER NOT NULL REFERENCES accounts(account_id),
    card_type       VARCHAR(10) NOT NULL CHECK (card_type IN ('DEBIT','CREDIT')),
    card_number     VARCHAR(16) UNIQUE NOT NULL,
    expiry_date     DATE NOT NULL,
    credit_limit    NUMERIC(15,2),
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','BLOCKED','EXPIRED')),
    issued_date     DATE NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cards_account ON cards(account_id);
