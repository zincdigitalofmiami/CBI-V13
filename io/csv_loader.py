from __future__ import annotations

from typing import Optional
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def load_csv_to_table(engine: Engine, csv_path: str, table: str, schema: Optional[str] = None, if_exists: str = "append") -> int:
    """
    Load a CSV into Postgres using pandas.to_sql with dtype inference.
    Args:
        engine: SQLAlchemy engine
        csv_path: path to CSV file
        table: table name without schema
        schema: schema name (optional)
        if_exists: 'append' | 'replace' | 'fail'
    Returns:
        rows inserted
    """
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]
    df.to_sql(table, engine, schema=schema, if_exists=if_exists, index=False, method="multi", chunksize=1000)
    with engine.connect() as conn:
        full_table = f"{schema}.{table}" if schema else table
        res = conn.execute(text(f"SELECT COUNT(*) FROM {full_table}"))
        total = res.scalar() or 0
    return int(total)
