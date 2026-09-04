"""Utilities for deliberately corrupting clean generated data before CSV
export, simulating what a real messy data export often looks like."""

import copy
import random
from datetime import date, datetime

# Alternate date string formats a messy real-world export might contain
DATE_FORMAT_VARIANTS = ["%d/%m/%Y", "%m-%d-%Y", "%Y.%m.%d"]


def inject_nulls(rows: list[dict], nullable_fields: list[str], rate: float) -> list[dict]:
    """Randomly blank out values in `nullable_fields` for `rate` fraction
    of rows. Only touches fields explicitly passed in — never touches
    primary/foreign keys, since a null ID would make a row unattributable
    rather than just messy.
    """
    rows = copy.deepcopy(rows)
    for row in rows:
        if random.random() < rate:
            field = random.choice(nullable_fields)
            if field in row:
                row[field] = None
    return rows


def inject_duplicates(rows: list[dict], rate: float) -> list[dict]:
    """Duplicates `rate` fraction of rows, appended to the end — simulates
    a re-export or retry that accidentally re-sent already-seen records.
    """
    rows = copy.deepcopy(rows)
    n_duplicates = int(len(rows) * rate)
    duplicates = [copy.deepcopy(random.choice(rows)) for _ in range(n_duplicates)]
    return rows + duplicates


def corrupt_date_formats(rows: list[dict], date_fields: list[str], rate: float) -> list[dict]:
    """For `rate` fraction of rows, reformats a date field into one of
    several alternate string formats — simulates inconsistent date
    formatting across export batches, a very common real-world issue.
    Leaves the value as an actual date object for untouched rows (CSV
    writing will stringify it consistently); only touched rows get an
    already-stringified, differently-formatted value.
    """
    rows = copy.deepcopy(rows)
    for row in rows:
        if random.random() < rate:
            field = random.choice(date_fields)
            value = row.get(field)
            if isinstance(value, (date, datetime)):
                fmt = random.choice(DATE_FORMAT_VARIANTS)
                row[field] = value.strftime(fmt)
    return rows


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches

    branches = generate_branches(20)
    dirty = inject_nulls(branches, ["branch_name"], rate=0.2)
    dirty = inject_duplicates(dirty, rate=0.1)
    dirty = corrupt_date_formats(dirty, ["opened_date"], rate=0.3)

    null_count = sum(1 for r in dirty if r["branch_name"] is None)
    string_date_count = sum(1 for r in dirty if isinstance(r["opened_date"], str))

    print(f"Total rows: {len(dirty)} (started with {len(branches)})")
    print(f"Rows with null branch_name: {null_count}")
    print(f"Rows with string-formatted opened_date: {string_date_count}")
    print("\nSample rows:")
    for row in dirty[:5]:
        print(row)
