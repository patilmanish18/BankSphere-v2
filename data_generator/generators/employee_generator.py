"""Generates synthetic employee records, tied to existing branches."""

import random
from faker import Faker
from data_generator.config import RANDOM_SEED

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

DESIGNATIONS = [
    "Branch Manager", "Relationship Manager", "Loan Officer",
    "Teller", "Operations Executive", "Customer Service Officer",
]


def generate_employees(branches: list[dict], count: int) -> list[dict]:
    """Generate `count` synthetic employee records.

    Each employee references a branch by its position in the `branches`
    list (`branch_index`), NOT a real database branch_id — that mapping
    only exists once branches are actually inserted into Postgres, which
    happens in the loading step later. `branch_index` gets translated to
    a real `branch_id` at load time.
    """
    employees = []
    used_emails = set()

    for _ in range(count):
        branch_index = random.randrange(len(branches))
        branch = branches[branch_index]

        first_name = fake.first_name()
        last_name = fake.last_name()

        # Ensure email uniqueness (matches UNIQUE constraint in schema)
        while True:
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@banksphere.com"
            if email not in used_emails:
                used_emails.add(email)
                break

        # Hire date must be on/after the branch's opened_date — can't hire
        # someone before the branch existed.
        hire_date = fake.date_between(start_date=branch["opened_date"], end_date="today")

        employees.append({
            "branch_index": branch_index,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": fake.phone_number()[:15],
            "designation": random.choice(DESIGNATIONS),
            "hire_date": hire_date,
        })

    return employees


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches

    branches = generate_branches(5)
    sample = generate_employees(branches, 5)
    for row in sample:
        print(row)
