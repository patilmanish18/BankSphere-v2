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


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches
    from data_generator.generators.employee_generator import generate_employees
    from data_generator.generators.customer_generator import generate_customers

    branches = generate_branches(5)
    branch_ids = load_branches(branches)
    print(f"Inserted {len(branch_ids)} branches. IDs: {branch_ids}")

    employees = generate_employees(branches, 10)
    employee_ids = load_employees(employees, branch_ids)
    print(f"Inserted {len(employee_ids)} employees. IDs: {employee_ids}")

    customers = generate_customers(8)
    customer_ids = load_customers(customers)
    print(f"Inserted {len(customer_ids)} customers. IDs: {customer_ids}")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT customer_id, first_name, pan_number FROM customers WHERE customer_id = ANY(%s) ORDER BY customer_id;",
        (customer_ids,),
    )
    print("\nVerification — customers actually in the database:")
    for row in cur.fetchall():
        print(f"  {row}")
    cur.close()
    conn.close()
