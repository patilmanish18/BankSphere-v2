"""Generates synthetic customer records."""

import random
import string
from faker import Faker
from data_generator.config import RANDOM_SEED
from data_generator.utils.location_data import INDIAN_STATES_CITIES

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

KYC_STATUSES = ["VERIFIED", "PENDING", "REJECTED"]
KYC_WEIGHTS = [0.85, 0.12, 0.03]


def _generate_pan(used_pans: set) -> str:
    """Generates a realistic Indian PAN number: 5 letters, 4 digits, 1 letter."""
    while True:
        pan = (
            "".join(random.choices(string.ascii_uppercase, k=5))
            + "".join(random.choices(string.digits, k=4))
            + random.choice(string.ascii_uppercase)
        )
        if pan not in used_pans:
            used_pans.add(pan)
            return pan


def generate_customers(count: int) -> list[dict]:
    """Generate `count` synthetic customer records."""
    customers = []
    used_emails = set()
    used_pans = set()

    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=75)

        while True:
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 9999)}@example.com"
            if email not in used_emails:
                used_emails.add(email)
                break

        state = random.choice(list(INDIAN_STATES_CITIES.keys()))
        city = random.choice(INDIAN_STATES_CITIES[state])

        customers.append({
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
            "gender": random.choice(["M", "F", "Other"]),
            "email": email,
            "phone": fake.phone_number()[:15],
            "address": fake.street_address(),
            "city": city,
            "state": state,
            "pincode": fake.postcode(),
            "pan_number": _generate_pan(used_pans),
            "kyc_status": random.choices(KYC_STATUSES, weights=KYC_WEIGHTS, k=1)[0],
        })

    return customers


if __name__ == "__main__":
    sample = generate_customers(5)
    for row in sample:
        print(row)
