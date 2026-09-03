# Architecture

## Overview

BankSphere follows a Medallion Architecture: data moves through three
progressively cleaner layers before it's ready for reporting.                                                                                  


## Layers

**Raw**
Synthetically generated banking data (branches, employees, customers,
accounts, cards, loans, transactions), written as-is including intentional
data quality problems: nulls, duplicate rows, inconsistent date formats.
This mimics what a real source system export usually looks like.

**Silver**
PySpark jobs clean, deduplicate, and validate the Raw data. Sensitive fields
(PAN numbers, card numbers) are masked here. Records that fail validation
are routed to a quarantine area instead of silently dropped, so nothing
disappears without a trace.

**Gold**
Aggregated, analysis-ready marts built from Silver: customer summaries,
branch performance, monthly transaction trends, and loan portfolio health.
This is the layer a BI tool or analyst would actually query.

## Orchestration

Apache Airflow runs the full pipeline as a DAG: generate → Silver → data
quality gate → Gold → data quality gate → upload to S3.

## Storage

- **Local:** Parquet files under `data/raw`, `data/silver`, `data/gold`
  during processing (Spark reads/writes locally for speed).
- **Cloud:** Finalized Silver and Gold outputs sync to a single AWS S3
  bucket via a scoped IAM user (S3 access limited to that one bucket).

## Data quality

Every layer transition is checked against explicit rules (not-null,
uniqueness, allowed values, range checks) before downstream jobs are
allowed to run. Results are logged, not just pass/fail printed to console.

## Status

This document will be expanded with diagrams and per-entity detail as each
layer is actually built (see commit history for current progress).
