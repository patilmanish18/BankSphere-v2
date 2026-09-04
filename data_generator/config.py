"""Central configuration for synthetic data generation."""

import os

# Reproducibility — same seed means same "random" data every run,
# which makes debugging downstream Spark jobs much easier.
RANDOM_SEED = 42

# Where generated CSVs land
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw"
)

# Row counts per entity — small enough to iterate on quickly locally,
# large enough to be meaningful once Spark/DQ checks run against it.
ROW_COUNTS = {
    "branches": 50,
    "employees": 200,
    "customers": 5000,
    "accounts": 7000,
    "cards": 4000,
    "loans": 1500,
    "transactions": 25000,
}

# Fraction of rows deliberately corrupted per entity (wired in later this Day)
DIRTY_DATA_RATE = 0.03
