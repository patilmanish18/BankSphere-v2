CREATE TABLE IF NOT EXISTS loans (
    loan_id             SERIAL PRIMARY KEY,
    customer_id         INTEGER NOT NULL REFERENCES customers(customer_id),
    branch_id           INTEGER NOT NULL REFERENCES branches(branch_id),
    loan_type           VARCHAR(20) NOT NULL CHECK (loan_type IN ('HOME','PERSONAL','AUTO','EDUCATION')),
    principal_amount    NUMERIC(15,2) NOT NULL,
    interest_rate       NUMERIC(5,2) NOT NULL,
    tenure_months       INTEGER NOT NULL,
    emi_amount          NUMERIC(15,2) NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CLOSED','DEFAULTED')),
    disbursed_date      DATE NOT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_loans_customer ON loans(customer_id);
