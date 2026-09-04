"""PostgreSQL connection handling, credentials read from .env."""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Returns a new psycopg2 connection using credentials from .env.

    Caller is responsible for closing it (or using it as a context
    manager via `with get_connection() as conn:`).
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user, version();")
    result = cur.fetchone()
    print("Connected successfully:")
    print(f"  Database: {result[0]}")
    print(f"  User: {result[1]}")
    print(f"  Version: {result[2]}")
    cur.close()
    conn.close()
