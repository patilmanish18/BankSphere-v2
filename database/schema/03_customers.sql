CREATE TABLE IF NOT EXISTS customers (
    customer_id     SERIAL PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    dob             DATE NOT NULL,
    gender          VARCHAR(10),
    email           VARCHAR(100) UNIQUE NOT NULL,
    phone           VARCHAR(15) NOT NULL,
    address         VARCHAR(200),
    city            VARCHAR(50),
    state           VARCHAR(50),
    pincode         VARCHAR(10),
    pan_number      VARCHAR(10) UNIQUE NOT NULL,
    kyc_status      VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
