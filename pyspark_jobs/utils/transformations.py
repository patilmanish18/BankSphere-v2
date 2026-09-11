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


if __name__ == "__main__":
    from pyspark_jobs.utils.spark_session import get_spark_session
    from pyspark_jobs.utils.schema_definitions import BRANCHES_SCHEMA

    spark = get_spark_session("date-parser-test")
    df = spark.read.csv("data/raw/branches.csv", header=True, schema=BRANCHES_SCHEMA)

    print("BEFORE parsing (raw strings):")
    df.select("branch_code", "opened_date").show(20, truncate=False)

    parsed_df = parse_date_col(df, "opened_date")

    print("AFTER parsing (should all be real dates or null):")
    parsed_df.select("branch_code", "opened_date").show(20, truncate=False)

    null_count = parsed_df.filter(F.col("opened_date").isNull()).count()
    total_count = parsed_df.count()
    print(f"\nRows with unparseable opened_date: {null_count} out of {total_count}")

    spark.stop()
