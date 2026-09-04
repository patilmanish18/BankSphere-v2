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


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches
    from data_generator.generators.employee_generator import generate_employees

    branches = generate_branches(5)
    branch_ids = load_branches(branches)
    print(f"Inserted {len(branch_ids)} branches. IDs: {branch_ids}")

    employees = generate_employees(branches, 10)
    employee_ids = load_employees(employees, branch_ids)
    print(f"Inserted {len(employee_ids)} employees. IDs: {employee_ids}")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT e.employee_id, e.first_name, e.branch_id, b.branch_name
        FROM employees e
        JOIN branches b ON e.branch_id = b.branch_id
        WHERE e.employee_id = ANY(%s)
        ORDER BY e.employee_id;
        """,
        (employee_ids,),
    )
    print("\nVerification — employees JOINed to their real branch:")
    for row in cur.fetchall():
        print(f"  {row}")
    cur.close()
    conn.close()
