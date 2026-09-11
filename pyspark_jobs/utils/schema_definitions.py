"""Explicit PySpark schemas for all 7 raw entities.

Using explicit schemas instead of inferSchema=True means:
1. Spark doesn't need to scan each file twice to guess types (faster).
2. Type mismatches in the dirty data become visible as nulls after
   parsing (which the Silver layer explicitly handles), rather than
   Spark silently deciding a whole column is StringType because a few
   rows didn't match.

All fields are read as StringType initially where the raw CSV might
contain corrupted values (e.g. dates in inconsistent formats) — proper
casting to DateType/DoubleType happens explicitly in the Silver
transformations, where we can log and quarantine rows that fail to
parse instead of Spark quietly turning them into nulls with no trace.
"""

from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType
)

BRANCHES_SCHEMA = StructType([
    StructField("branch_code", StringType(), True),
    StructField("branch_name", StringType(), True),
    StructField("ifsc_code", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("opened_date", StringType(), True),  # cast in Silver
])

EMPLOYEES_SCHEMA = StructType([
    StructField("branch_index", IntegerType(), True),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("designation", StringType(), True),
    StructField("hire_date", StringType(), True),
])

CUSTOMERS_SCHEMA = StructType([
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("dob", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("email", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("pincode", StringType(), True),
    StructField("pan_number", StringType(), True),
    StructField("kyc_status", StringType(), True),
])

ACCOUNTS_SCHEMA = StructType([
    StructField("customer_index", IntegerType(), True),
    StructField("branch_index", IntegerType(), True),
    StructField("account_number", StringType(), True),
    StructField("account_type", StringType(), True),
    StructField("balance", DoubleType(), True),
    StructField("currency", StringType(), True),
    StructField("status", StringType(), True),
    StructField("opened_date", StringType(), True),
])

CARDS_SCHEMA = StructType([
    StructField("account_index", IntegerType(), True),
    StructField("card_type", StringType(), True),
    StructField("card_number", StringType(), True),
    StructField("expiry_date", StringType(), True),
    StructField("credit_limit", DoubleType(), True),
    StructField("status", StringType(), True),
    StructField("issued_date", StringType(), True),
])

LOANS_SCHEMA = StructType([
    StructField("customer_index", IntegerType(), True),
    StructField("branch_index", IntegerType(), True),
    StructField("loan_type", StringType(), True),
    StructField("principal_amount", DoubleType(), True),
    StructField("interest_rate", DoubleType(), True),
    StructField("tenure_months", IntegerType(), True),
    StructField("emi_amount", DoubleType(), True),
    StructField("status", StringType(), True),
    StructField("disbursed_date", StringType(), True),
])

TRANSACTIONS_SCHEMA = StructType([
    StructField("account_index", IntegerType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("balance_after", DoubleType(), True),
    StructField("description", StringType(), True),
    StructField("transaction_date", StringType(), True),
])
