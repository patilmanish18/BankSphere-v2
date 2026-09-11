"""Shared PySpark transformation utilities used across Silver ETL jobs."""

from pyspark.sql import DataFrame
import pyspark.sql.functions as F


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


if __name__ == "__main__":
    from pyspark_jobs.utils.spark_session import get_spark_session
    from pyspark_jobs.utils.schema_definitions import BRANCHES_SCHEMA

    spark = get_spark_session("transformations-test")
    df = spark.read.csv("data/raw/branches.csv", header=True, schema=BRANCHES_SCHEMA)

    print(f"Row count BEFORE dedup: {df.count()}")

    deduped = deduplicate_by_key(df, ["branch_code"])
    print(f"Row count AFTER dedup: {deduped.count()}")

    parsed_df = parse_date_col(deduped, "opened_date")
    null_count = parsed_df.filter(F.col("opened_date").isNull()).count()
    print(f"Rows with unparseable opened_date (post-dedup): {null_count}")

    spark.stop()
