"""Generates synthetic loan records, tied to existing customers and branches."""

import random
from faker import Faker
from data_generator.config import RANDOM_SEED

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

LOAN_TYPES = ["HOME", "PERSONAL", "AUTO", "EDUCATION"]

LOAN_RANGES = {
    "HOME": (1_500_000, 8_000_000),
    "PERSONAL": (50_000, 1_000_000),
    "AUTO": (200_000, 1_500_000),
    "EDUCATION": (100_000, 2_500_000),
}

INTEREST_RATE_RANGES = {
    "HOME": (7.5, 9.5),
    "PERSONAL": (10.5, 16.0),
    "AUTO": (8.5, 12.0),
    "EDUCATION": (8.0, 11.5),
}

TENURE_MONTHS_RANGES = {
    "HOME": (120, 360),
    "PERSONAL": (12, 60),
    "AUTO": (24, 84),
    "EDUCATION": (36, 180),
}

STATUSES = ["ACTIVE", "CLOSED", "DEFAULTED"]
STATUS_WEIGHTS = [0.75, 0.20, 0.05]


def _calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Standard reducing-balance EMI formula:
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    where r is the MONTHLY interest rate (annual_rate / 12 / 100).
    """
    monthly_rate = annual_rate / 12 / 100
    numerator = principal * monthly_rate * (1 + monthly_rate) ** tenure_months
    denominator = (1 + monthly_rate) ** tenure_months - 1
    return round(numerator / denominator, 2)


def generate_loans(customers: list[dict], branches: list[dict], count: int) -> list[dict]:
    """Generate `count` synthetic loan records with a real amortization-based EMI."""
    loans = []

    for _ in range(count):
        customer_index = random.randrange(len(customers))
        branch_index = random.randrange(len(branches))
        loan_type = random.choice(LOAN_TYPES)

        principal = round(random.uniform(*LOAN_RANGES[loan_type]), 2)
        interest_rate = round(random.uniform(*INTEREST_RATE_RANGES[loan_type]), 2)
        tenure_months = random.randint(*TENURE_MONTHS_RANGES[loan_type])
        emi_amount = _calculate_emi(principal, interest_rate, tenure_months)

        disbursed_date = fake.date_between(start_date="-10y", end_date="today")

        loans.append({
            "customer_index": customer_index,
            "branch_index": branch_index,
            "loan_type": loan_type,
            "principal_amount": principal,
            "interest_rate": interest_rate,
            "tenure_months": tenure_months,
            "emi_amount": emi_amount,
            "status": random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0],
            "disbursed_date": disbursed_date,
        })

    return loans


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches
    from data_generator.generators.customer_generator import generate_customers

    branches = generate_branches(5)
    customers = generate_customers(5)
    sample = generate_loans(customers, branches, 5)
    for row in sample:
        print(row)
