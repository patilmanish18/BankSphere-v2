# BankSphere

A banking data engineering pipeline built to practice production-style data
engineering patterns: Medallion Architecture (Raw → Silver → Gold), data
quality checks, orchestration, containerization, and cloud storage.

This is a personal learning project using synthetically generated banking
data (customers, accounts, transactions, loans, cards) — not real financial
data or a production system.

## Problem

Raw operational data is rarely analysis-ready: it has duplicates, bad date
formats, and unmasked sensitive fields (like PAN numbers). BankSphere takes
messy synthetic banking data and moves it through cleaning, validation, and
aggregation stages until it's ready for reporting — the same shape as a real
data platform team's ETL work, at a scale one person can build in a week.

## Tech stack

- **Language:** Python 3.11
- **Database:** PostgreSQL 16
- **Processing:** Apache Spark (PySpark 3.5)
- **Orchestration:** Apache Airflow
- **Containerization:** Docker / Docker Compose
- **Cloud storage:** AWS S3 (boto3)
- **Testing:** Pytest
- **CI/CD:** GitHub Actions

## Status

🚧 Work in progress — built incrementally, day by day. See commit history
for progress; this README will be filled in with setup instructions and
architecture details as each layer is completed.

## License

MIT — see [LICENSE](LICENSE).
