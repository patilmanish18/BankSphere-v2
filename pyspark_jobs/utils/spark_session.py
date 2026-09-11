"""Reusable Spark session factory — every ETL job should create its
session through this function rather than calling SparkSession.builder
directly, so configuration stays in one place.
"""

from pyspark.sql import SparkSession


def get_spark_session(app_name: str) -> SparkSession:
    """Returns a local SparkSession configured for this project's scale.

    Notes on the settings below:
    - `local[*]` uses all available CPU cores — fine for a laptop-scale
      project like this, would be a real cluster master URL in production.
    - `spark.sql.shuffle.partitions` defaults to 200, which is tuned for
      large clusters. On a few thousand rows locally, 200 tiny partitions
      just adds overhead — 8 is far more sensible at this data volume.
    - Log level is set to WARN so job output isn't buried under Spark's
      own INFO-level chatter.
    """
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.session.timeZone", "Asia/Kolkata")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


if __name__ == "__main__":
    spark = get_spark_session("spark-session-test")
    print(f"Spark version: {spark.version}")
    print(f"App name: {spark.sparkContext.appName}")
    print(f"Master: {spark.sparkContext.master}")
    print(f"Shuffle partitions config: {spark.conf.get('spark.sql.shuffle.partitions')}")
    spark.stop()
    print("Session stopped cleanly.")
