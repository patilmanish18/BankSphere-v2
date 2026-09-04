"""Generates synthetic account records, tied to existing customers and branches."""

import random
from datetime import date, timedelta
from faker import Faker
from data_generator.config import RANDOM_SEED

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

ACCOUNT_TYPES = ["SAVINGS", "CURRENT", "FIXED_DEPOSIT"]
ACCOUNT_TYPE_WEIGHTS = [0.65, 0.25, 0.10]

STATUSES = ["ACTIVE", "INACTIVE", "CLOSED"]
STATUS_WEIGHTS = [0.85, 0.10, 0.05]


def _customer_turns_18(dob: date) -> date:
    """Returns the date the customer turned 18 — an account can't
    legally exist before this."""
    try:
        return dob.replace(year=dob.year + 18)
    except ValueError:
        # handles Feb 29 birthdays on non-leap 18th year
        return dob.replace(year=dob.year + 18, day=28)


def generate_accounts(customers: list[dict], branches: list[dict], count: int) -> list[dict]:
    """Generate `count` synthetic account records.

    `customer_index` and `branch_index` reference positions in the input
    lists, translated to real database IDs at load time — same pattern
    used for employees.
    """
    accounts = []
    used_account_numbers = set()

    for _ in range(count):
        customer_index = random.randrange(len(customers))
        branch_index = random.randrange(len(branches))

        customer = customers[customer_index]
        branch = branches[branch_index]

        earliest_possible = max(_customer_turns_18(customer["dob"]), branch["opened_date"])
        # Guard against earliest_possible landing in the future (edge case:
        # a very recently-turned-18 customer combined with today's date)
        if earliest_possible >= date.today():
            earliest_possible = date.today() - timedelta(days=1)

        opened_date = fake.date_between(start_date=earliest_possible, end_date="today")

        while True:
            account_number = f"AC{random.randint(10**11, 10**12 - 1)}"
            if account_number not in used_account_numbers:
                used_account_numbers.add(account_number)
                break

        accounts.append({
            "customer_index": customer_index,
            "branch_index": branch_index,
            "account_number": account_number,
            "account_type": random.choices(ACCOUNT_TYPES, weights=ACCOUNT_TYPE_WEIGHTS, k=1)[0],
            "balance": round(random.uniform(500, 500000), 2),
            "currency": "INR",
            "status": random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0],
            "opened_date": opened_date,
        })

    return accounts


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches
    from data_generator.generators.customer_generator import generate_customers

    branches = generate_branches(5)
    customers = generate_customers(5)
    sample = generate_accounts(customers, branches, 5)
    for row in sample:
        print(row)
