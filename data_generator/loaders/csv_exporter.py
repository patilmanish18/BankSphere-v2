"""Exports generated entity data to CSV files in data/raw/, after dirty
data injection has already been applied to the rows passed in."""

import os
import pandas as pd
from data_generator.config import OUTPUT_DIR


def export_to_csv(rows: list[dict], entity_name: str) -> str:
    """Writes `rows` to data/raw/<entity_name>.csv. Returns the file path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{entity_name}.csv")
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches
    from data_generator.utils.dirty_injector import (
        inject_nulls, inject_duplicates, corrupt_date_formats
    )

    branches = generate_branches(20)
    dirty = inject_nulls(branches, ["branch_name"], rate=0.15)
    dirty = inject_duplicates(dirty, rate=0.1)
    dirty = corrupt_date_formats(dirty, ["opened_date"], rate=0.2)

    path = export_to_csv(dirty, "branches")
    print(f"Exported {len(dirty)} rows to {path}")
