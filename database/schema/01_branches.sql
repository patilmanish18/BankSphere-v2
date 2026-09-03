CREATE TABLE IF NOT EXISTS branches (
    branch_id       SERIAL PRIMARY KEY,
    branch_code     VARCHAR(10) UNIQUE NOT NULL,
    branch_name     VARCHAR(100) NOT NULL,
    ifsc_code       VARCHAR(11) UNIQUE NOT NULL,
    city            VARCHAR(50) NOT NULL,
    state           VARCHAR(50) NOT NULL,
    opened_date     DATE NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
