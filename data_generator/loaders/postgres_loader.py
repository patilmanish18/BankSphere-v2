"""Loads generated entity data into PostgreSQL, resolving `_index`
references into real database IDs along the way."""

from data_generator.loaders.db_connection import get_connection


def load_branches(branches: list[dict]) -> list[int]:
    """Inserts branches, returns their real database branch_ids in the
    SAME ORDER as the input list.
    """
    conn = get_connection()
    cur = conn.cursor()
    branch_ids = []

    try:
        for b in branches:
            cur.execute(
                """
                INSERT INTO branches
                    (branch_code, branch_name, ifsc_code, city, state, opened_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING branch_id;
                """,
                (b["branch_code"], b["branch_name"], b["ifsc_code"],
                 b["city"], b["state"], b["opened_date"]),
            )
            branch_ids.append(cur.fetchone()[0])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return branch_ids


def load_employees(employees: list[dict], branch_ids: list[int]) -> list[int]:
    """Inserts employees, translating each employee's `branch_index`
    into the real `branch_id` at `branch_ids[branch_index]`.
    """
    conn = get_connection()
    cur = conn.cursor()
    employee_ids = []

    try:
        for e in employees:
            real_branch_id = branch_ids[e["branch_index"]]
            cur.execute(
                """
                INSERT INTO employees
                    (branch_id, first_name, last_name, email, phone, designation, hire_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING employee_id;
                """,
                (real_branch_id, e["first_name"], e["last_name"],
                 e["email"], e["phone"], e["designation"], e["hire_date"]),
            )
            employee_ids.append(cur.fetchone()[0])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return employee_ids


def load_customers(customers: list[dict]) -> list[int]:
    """Inserts customers, returns their real database customer_ids in the
    SAME ORDER as the input list. No FK dependencies, same pattern as
    load_branches.
    """
    conn = get_connection()
    cur = conn.cursor()
    customer_ids = []

    try:
        for c in customers:
            cur.execute(
                """
                INSERT INTO customers
                    (first_name, last_name, dob, gender, email, phone, address,
                     city, state, pincode, pan_number, kyc_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING customer_id;
                """,
                (c["first_name"], c["last_name"], c["dob"], c["gender"],
                 c["email"], c["phone"], c["address"], c["city"], c["state"],
                 c["pincode"], c["pan_number"], c["kyc_status"]),
            )
            customer_ids.append(cur.fetchone()[0])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return customer_ids

def load_accounts(accounts: list[dict], customer_ids: list[int], branch_ids: list[int]) -> list[int]:
    """Inserts accounts, translating each account's `customer_index` and
    `branch_index` into their real database IDs.
    """
    conn = get_connection()
    cur = conn.cursor()
    account_ids = []

    try:
        for a in accounts:
            real_customer_id = customer_ids[a["customer_index"]]
            real_branch_id = branch_ids[a["branch_index"]]
            cur.execute(
                """
                INSERT INTO accounts
                    (account_number, customer_id, branch_id, account_type,
                     balance, currency, status, opened_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING account_id;
                """,
                (a["account_number"], real_customer_id, real_branch_id,
                 a["account_type"], a["balance"], a["currency"],
                 a["status"], a["opened_date"]),
            )
            account_ids.append(cur.fetchone()[0])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return account_ids

def load_cards(cards: list[dict], account_ids: list[int]) -> list[int]:
    """Inserts cards, translating each card's `account_index` into its
    real database `account_id`.
    """
    conn = get_connection()
    cur = conn.cursor()
    card_ids = []

    try:
        for c in cards:
            real_account_id = account_ids[c["account_index"]]
            cur.execute(
                """
                INSERT INTO cards
                    (account_id, card_type, card_number, expiry_date,
                     credit_limit, status, issued_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING card_id;
                """,
                (real_account_id, c["card_type"], c["card_number"],
                 c["expiry_date"], c["credit_limit"], c["status"], c["issued_date"]),
            )
            card_ids.append(cur.fetchone()[0])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return card_ids

def load_loans(loans: list[dict], customer_ids: list[int], branch_ids: list[int]) -> list[int]:
    """Inserts loans, translating each loan's `customer_index` and
    `branch_index` into their real database IDs.
    """
    conn = get_connection()
    cur = conn.cursor()
    loan_ids = []

    try:
        for l in loans:
            real_customer_id = customer_ids[l["customer_index"]]
            real_branch_id = branch_ids[l["branch_index"]]
            cur.execute(
                """
                INSERT INTO loans
                    (customer_id, branch_id, loan_type, principal_amount,
                     interest_rate, tenure_months, emi_amount, status, disbursed_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING loan_id;
                """,
                (real_customer_id, real_branch_id, l["loan_type"],
                 l["principal_amount"], l["interest_rate"], l["tenure_months"],
                 l["emi_amount"], l["status"], l["disbursed_date"]),
            )
            loan_ids.append(cur.fetchone()[0])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return loan_ids

def load_transactions(transactions: list[dict], account_ids: list[int]) -> list[int]:
    """Inserts transactions, translating each transaction's `account_index`
    into its real database `account_id`.
    """
    conn = get_connection()
    cur = conn.cursor()
    transaction_ids = []

    try:
        for t in transactions:
            real_account_id = account_ids[t["account_index"]]
            cur.execute(
                """
                INSERT INTO transactions
                    (account_id, transaction_type, amount, balance_after,
                     description, transaction_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING transaction_id;
                """,
                (real_account_id, t["transaction_type"], t["amount"],
                 t["balance_after"], t["description"], t["transaction_date"]),
            )
            transaction_ids.append(cur.fetchone()[0])
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return transaction_ids

if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches
    from data_generator.generators.employee_generator import generate_employees
    from data_generator.generators.customer_generator import generate_customers
    from data_generator.generators.account_generator import generate_accounts
    from data_generator.generators.card_generator import generate_cards
    from data_generator.generators.loan_generator import generate_loans
    from data_generator.generators.transaction_generator import generate_transactions

    branches = generate_branches(5)
    branch_ids = load_branches(branches)
    print(f"Inserted {len(branch_ids)} branches.")

    employees = generate_employees(branches, 10)
    employee_ids = load_employees(employees, branch_ids)
    print(f"Inserted {len(employee_ids)} employees.")

    customers = generate_customers(8)
    customer_ids = load_customers(customers)
    print(f"Inserted {len(customer_ids)} customers.")

    accounts = generate_accounts(customers, branches, 12)
    account_ids = load_accounts(accounts, customer_ids, branch_ids)
    print(f"Inserted {len(account_ids)} accounts.")

    cards = generate_cards(accounts, 15)
    card_ids = load_cards(cards, account_ids)
    print(f"Inserted {len(card_ids)} cards.")

    loans = generate_loans(customers, branches, 6)
    loan_ids = load_loans(loans, customer_ids, branch_ids)
    print(f"Inserted {len(loan_ids)} loans.")

    transactions = generate_transactions(accounts, 30)
    transaction_ids = load_transactions(transactions, account_ids)
    print(f"Inserted {len(transaction_ids)} transactions. IDs: {transaction_ids}")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT t.transaction_id, t.transaction_type, t.amount, t.balance_after, a.account_number
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE t.transaction_id = ANY(%s)
        ORDER BY t.transaction_id
        LIMIT 10;
        """,
        (transaction_ids,),
    )
    print("\nVerification — first 10 transactions JOINed to real account:")
    for row in cur.fetchall():
        print(f"  {row}")

    # Final full-pipeline sanity check: total row counts across all 7 tables
    print("\nFinal row counts across all tables:")
    for table in ["branches", "employees", "customers", "accounts", "cards", "loans", "transactions"]:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        print(f"  {table}: {cur.fetchone()[0]}")

    cur.close()
    conn.close()
