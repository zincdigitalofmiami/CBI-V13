#!/usr/bin/env python3
"""
Apply the Postgres schema from sql/schema.sql using the configured DB connection.
Works with either DATABASE_URL or USE_IAM_AUTH (Cloud SQL connector) via db.session.get_engine().
"""
from pathlib import Path
from sqlalchemy import text
from db.session import get_engine


def apply_schema():
    engine = get_engine()
    schema_path = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"
    sql_text = schema_path.read_text(encoding="utf-8")

    # Execute as a single script; Postgres understands multiple statements
    with engine.begin() as conn:
        conn.execute(text(sql_text))


def main():
    apply_schema()
    print("schema_applied")


if __name__ == "__main__":
    main()
