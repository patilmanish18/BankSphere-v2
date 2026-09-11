"""Orchestrates the full synthetic data pipeline: truncates existing data,
generates all 7 entities in dependency order, loads them into PostgreSQL
(resolving FK references), then exports dirty CSV copies to data/raw/.
"""

from data_generator.config import ROW_COUNTS, DIRTY_DATA_RATE
from data_generator.loaders.db_connection import get_connection

from data_generator.generators.branch_generator import generate_branches
from data_generator.generators.employee_generator import generate_employees
from data_generator.generators.customer_generator import generate_customers
from data_generator.generators.account_generator import generate_accounts
from data_generator.generators.card_generator import generate_cards
from data_generator.generators.loan_generator import generate_loans
from data_generator.generators.transaction_generator import generate_transactions

from data_generator.loaders.postgres_loader import (
    load_branches, load_employees, load_customers, load_accounts,
    load_cards, load_loans, load_transactions,
)

from data_generator.utils.dirty_injector import (
    inject_nulls, inject_duplicates, corrupt_date_formats
)
from data_generator.loaders.csv_exporter import export_to_csv

# Which fields get dirty-injected per entity, and which date fields
# are eligible for format corruption. Keyed by entity name.
DIRTY_CONFIG = {
    "branches": {"nullable": ["branch_name"], "dates": ["opened_date"]},
    "employees": {"nullable": ["phone"], "dates": ["hire_date"]},
    "customers": {"nullable": ["address", "phone"], "dates": ["dob"]},
    "accounts": {"nullable": [], "dates": ["opened_date"]},
    "cards": {"nullable": [], "dates": ["expiry_date", "issued_date"]},
    "loans": {"nullable": [], "dates": ["disbursed_date"]},
    "transactions": {"nullable": ["description"], "dates": ["transaction_date"]},
}


def apply_dirty(rows, entity_name):
    cfg = DIRTY_CONFIG[entity_name]
    dirty = rows
    if cfg["nullable"]:
        dirty = inject_nulls(dirty, cfg["nullable"], rate=DIRTY_DATA_RATE)
    dirty = inject_duplicates(dirty, rate=DIRTY_DATA_RATE)
    if cfg["dates"]:
        dirty = corrupt_date_formats(dirty, cfg["dates"], rate=DIRTY_DATA_RATE * 2)
    return dirty


def truncate_all():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "TRUNCATE branches, employees, customers, accounts, cards, loans, transactions "
        "RESTART IDENTITY CASCADE;"
    )
    conn.commit()
    cur.close()
    conn.close()
    print("Truncated all tables.\n")


def run():
    truncate_all()

    branches = generate_branches(ROW_COUNTS["branches"])
    branch_ids = load_branches(branches)
    export_to_csv(apply_dirty(branches, "branches"), "branches")
    print(f"branches: {len(branch_ids)} loaded, CSV exported.")

    employees = generate_employees(branches, ROW_COUNTS["employees"])
    employee_ids = load_employees(employees, branch_ids)
    export_to_csv(apply_dirty(employees, "employees"), "employees")
    print(f"employees: {len(employee_ids)} loaded, CSV exported.")

    customers = generate_customers(ROW_COUNTS["customers"])
    customer_ids = load_customers(customers)
    export_to_csv(apply_dirty(customers, "customers"), "customers")
    print(f"customers: {len(customer_ids)} loaded, CSV exported.")

    accounts = generate_accounts(customers, branches, ROW_COUNTS["accounts"])
    account_ids = load_accounts(accounts, customer_ids, branch_ids)
    export_to_csv(apply_dirty(accounts, "accounts"), "accounts")
    print(f"accounts: {len(account_ids)} loaded, CSV exported.")

    cards = generate_cards(accounts, ROW_COUNTS["cards"])
    card_ids = load_cards(cards, account_ids)
    export_to_csv(apply_dirty(cards, "cards"), "cards")
    print(f"cards: {len(card_ids)} loaded, CSV exported.")

    loans = generate_loans(customers, branches, ROW_COUNTS["loans"])
    loan_ids = load_loans(loans, customer_ids, branch_ids)
    export_to_csv(apply_dirty(loans, "loans"), "loans")
    print(f"loans: {len(loan_ids)} loaded, CSV exported.")

    transactions = generate_transactions(accounts, ROW_COUNTS["transactions"])
    transaction_ids = load_transactions(transactions, account_ids)
    export_to_csv(apply_dirty(transactions, "transactions"), "transactions")
    print(f"transactions: {len(transaction_ids)} loaded, CSV exported.")

    print("\nFull pipeline complete.")


if __name__ == "__main__":
    run()
