"""Generates synthetic card records, tied to existing accounts."""

import random
from datetime import timedelta
from faker import Faker
from data_generator.config import RANDOM_SEED

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

CARD_TYPES = ["DEBIT", "CREDIT"]
CARD_TYPE_WEIGHTS = [0.7, 0.3]

STATUSES = ["ACTIVE", "BLOCKED", "EXPIRED"]
STATUS_WEIGHTS = [0.85, 0.10, 0.05]


def generate_cards(accounts: list[dict], count: int) -> list[dict]:
    """Generate `count` synthetic card records.

    `account_index` references a position in the input `accounts` list,
    translated to a real database ID at load time.
    """
    cards = []
    used_card_numbers = set()

    for _ in range(count):
        account_index = random.randrange(len(accounts))
        account = accounts[account_index]

        card_type = random.choices(CARD_TYPES, weights=CARD_TYPE_WEIGHTS, k=1)[0]

        # A card can't be issued before its account was opened
        issued_date = fake.date_between(start_date=account["opened_date"], end_date="today")
        expiry_date = issued_date + timedelta(days=5 * 365)  # 5-year validity

        while True:
            card_number = "".join(random.choices("0123456789", k=16))
            if card_number not in used_card_numbers:
                used_card_numbers.add(card_number)
                break

        cards.append({
            "account_index": account_index,
            "card_type": card_type,
            "card_number": card_number,
            "expiry_date": expiry_date,
            # Only CREDIT cards carry a credit_limit — DEBIT cards leave it null,
            # matching the nullable column in the schema
            "credit_limit": round(random.uniform(20000, 500000), 2) if card_type == "CREDIT" else None,
            "status": random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0],
            "issued_date": issued_date,
        })

    return cards


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches
    from data_generator.generators.customer_generator import generate_customers
    from data_generator.generators.account_generator import generate_accounts

    branches = generate_branches(5)
    customers = generate_customers(5)
    accounts = generate_accounts(customers, branches, 5)
    sample = generate_cards(accounts, 5)
    for row in sample:
        print(row)
