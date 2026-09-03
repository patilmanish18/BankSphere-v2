CREATE TABLE IF NOT EXISTS employees (
    employee_id     SERIAL PRIMARY KEY,
    branch_id       INTEGER NOT NULL REFERENCES branches(branch_id),
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    phone           VARCHAR(15) NOT NULL,
    designation     VARCHAR(50) NOT NULL,
    hire_date       DATE NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_employees_branch ON employees(branch_id);
