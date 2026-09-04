"""Generates synthetic bank branch records."""

import random
from faker import Faker
from data_generator.config import RANDOM_SEED
from data_generator.utils.location_data import INDIAN_STATES_CITIES

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)


def generate_branches(count: int) -> list[dict]:
    """Generate `count` synthetic branch records.

    Returns a list of dicts matching the `branches` table schema
    (excluding branch_id, which the database assigns via SERIAL).
    """
    branches = []
    used_ifsc = set()

    for i in range(count):
        state = random.choice(list(INDIAN_STATES_CITIES.keys()))
        city = random.choice(INDIAN_STATES_CITIES[state])

        # Ensure IFSC codes are unique (matches the UNIQUE constraint in schema)
        while True:
            ifsc = f"BSPH0{str(i).zfill(6)}"
            if ifsc not in used_ifsc:
                used_ifsc.add(ifsc)
                break

        branches.append({
            "branch_code": f"BR{str(i + 1).zfill(4)}",
            "branch_name": f"{city} {random.choice(['Main', 'Central', 'Metro', 'City'])} Branch",
            "ifsc_code": ifsc,
            "city": city,
            "state": state,
            "opened_date": fake.date_between(start_date="-15y", end_date="-1y"),
        })

    return branches


if __name__ == "__main__":
    sample = generate_branches(5)
    for row in sample:
        print(row)
