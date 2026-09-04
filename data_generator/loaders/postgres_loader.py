"""Loads generated entity data into PostgreSQL, resolving `_index`
references into real database IDs along the way."""

from data_generator.loaders.db_connection import get_connection


def load_branches(branches: list[dict]) -> list[int]:
    """Inserts branches, returns their real database branch_ids in the
    SAME ORDER as the input list — so `branches[i]` maps to the returned
    `branch_ids[i]`. This ordering guarantee is what lets every other
    loader translate a `branch_index` into a real ID with a simple
    list lookup.
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


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches

    branches = generate_branches(5)
    branch_ids = load_branches(branches)

    print(f"Inserted {len(branch_ids)} branches.")
    print(f"Returned IDs: {branch_ids}")

    # Verify the mapping actually matches what's in the database
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT branch_id, branch_code, branch_name FROM branches WHERE branch_id = ANY(%s) ORDER BY branch_id;",
        (branch_ids,),
    )
    print("\nVerification — rows actually in the database:")
    for row in cur.fetchall():
        print(f"  {row}")
    cur.close()
    conn.close()
