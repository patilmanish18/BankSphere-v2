"""Shared PySpark transformation utilities used across Silver ETL jobs."""

from pyspark.sql import DataFrame
import pyspark.sql.functions as F

def read_raw_csv(spark, path: str, schema):
    """Reads a raw CSV with the settings this project's data actually
    requires — critically, multiLine=true, because some generated fields
    (e.g. customer addresses) can contain embedded newlines inside
    quoted values. Without this, Spark silently splits those single
    logical rows into multiple broken ones, corrupting every column
    that comes after the multiline field. Discovered via a real bug:
    pan_number was 64.9% null before this fix was found and verified.

    Every Silver job should read raw CSVs through this function, not
    spark.read.csv directly, so this fix can't be silently forgotten
    in a future file.
    """
    return spark.read.option("multiLine", "true").csv(path, header=True, schema=schema)

def parse_date_col(df: DataFrame, col_name: str) -> DataFrame:
    """Parses a string date column that may be in any of several known
    formats (the ones this project's dirty data injector actually
    produces) into a proper DateType column.

    Each known dirty format uses a distinct delimiter, so trying them in
    sequence via coalesce is unambiguous — to_date() returns null on a
    non-matching pattern, and coalesce takes the first real match.
    Any value that matches none of these formats becomes null, which is
    the correct, visible outcome for a genuinely unparseable date —
    NOT something to silently guess at.
    """
    parsed = F.coalesce(
        F.to_date(F.col(col_name), "yyyy-MM-dd"),   # clean format
        F.to_date(F.col(col_name), "dd/MM/yyyy"),   # dirty: DD/MM/YYYY
        F.to_date(F.col(col_name), "MM-dd-yyyy"),   # dirty: MM-DD-YYYY
        F.to_date(F.col(col_name), "yyyy.MM.dd"),   # dirty: YYYY.MM.DD
    )
    return df.withColumn(col_name, parsed)

def deduplicate_by_key(df: DataFrame, key_cols: list) -> DataFrame:
    """Removes duplicate rows based on `key_cols`, keeping one row per
    unique key combination. Uses dropDuplicates rather than a window
    function here since our duplicates are exact copies (no "most
    recent wins" data to actually choose between) — dropDuplicates is
    simpler and sufficient for that case.
    """
    return df.dropDuplicates(subset=key_cols)

def mask_pii_sha256(df: DataFrame, col_name: str, salt: str = None) -> DataFrame:
    """Replaces a sensitive column's values with a salted SHA-256 hash,
    stored in a new `{col_name}_hash` column. The original column is
    dropped — this is irreversible masking, appropriate for identifiers
    like PAN numbers where downstream jobs need to group/join on a
    consistent value but never need the real number back.

    The salt should come from an environment variable in real usage
    (never hardcoded) — passed explicitly here so the caller controls
    where it comes from, rather than this function reading os.environ
    directly and hiding that dependency.
    """
    if salt is None:
        raise ValueError(
            "mask_pii_sha256 requires an explicit salt — pass one in, "
            "don't rely on a hardcoded default for anything touching real PII."
        )
    hashed = F.sha2(F.concat(F.col(col_name), F.lit(salt)), 256)
    return df.withColumn(f"{col_name}_hash", hashed).drop(col_name)


def mask_card_number(df: DataFrame, col_name: str = "card_number") -> DataFrame:
    """Masks a card number to PCI-DSS-style display format: only the
    last 4 digits visible, everything before replaced with asterisks.
    Example: 1234567812345678 -> ************5678
    """
    masked = F.concat(
        F.lit("*" * 12),
        F.substring(F.col(col_name), -4, 4)
    )
    return df.withColumn(col_name, masked)

if __name__ == "__main__":
    import os
    from pyspark_jobs.utils.spark_session import get_spark_session
    from pyspark_jobs.utils.schema_definitions import BRANCHES_SCHEMA, CUSTOMERS_SCHEMA, CARDS_SCHEMA

    spark = get_spark_session("transformations-test")

    # --- Date parsing + dedup test ---
    df = read_raw_csv(spark, "data/raw/branches.csv", BRANCHES_SCHEMA)
    print(f"Row count BEFORE dedup: {df.count()}")
    deduped = deduplicate_by_key(df, ["branch_code"])
    print(f"Row count AFTER dedup: {deduped.count()}")
    parsed_df = parse_date_col(deduped, "opened_date")
    null_count = parsed_df.filter(F.col("opened_date").isNull()).count()
    print(f"Rows with unparseable opened_date (post-dedup): {null_count}")

    # --- PAN masking test (now reading correctly via multiLine) ---
    salt = os.getenv("PII_SALT", "dev_only_test_salt")
    customers_df = read_raw_csv(spark, "data/raw/customers.csv", CUSTOMERS_SCHEMA)
    total_customers = customers_df.count()
    print(f"\nTotal customer rows (should be 5150): {total_customers}")
    masked_customers = mask_pii_sha256(customers_df, "pan_number", salt=salt)
    null_pan_hash = masked_customers.filter(F.col("pan_number_hash").isNull()).count()
    print(f"Null pan_number_hash after masking (should be 0): {null_pan_hash}")
    masked_customers.select("pan_number_hash").show(5, truncate=False)
    print(f"Original pan_number column still present: {'pan_number' in masked_customers.columns}")

    # --- Card masking test ---
    cards_df = read_raw_csv(spark, "data/raw/cards.csv", CARDS_SCHEMA)
    masked_cards = mask_card_number(cards_df)
    masked_cards.select("card_number").show(5, truncate=False)

    spark.stop()
