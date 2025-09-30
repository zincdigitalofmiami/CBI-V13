import argparse
from datetime import datetime
import json

import yfinance as yf
from sqlalchemy import text

from db.session import get_engine
from config.settings import settings


def upsert_parameter(engine, key: str, value: str):
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO app.parameters(key, value) VALUES (:k, :v) ON CONFLICT (key) DO UPDATE SET value = excluded.value"), {"k": key, "v": value})


def ingest_yahoo(symbol: str = "ZL=F"):
    engine = get_engine()
    # Ensure schemas/tables exist (assumes sql/schema.sql applied out-of-band)
    data = yf.download(symbol, period="5y", interval="1d", progress=False)
    data = data.reset_index().rename(columns={
        "Date": "ds",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })
    data["symbol"] = symbol
    with engine.begin() as conn:
        # write to curated.prices_daily
        for _, row in data.iterrows():
            conn.execute(
                text(
                    """
                    INSERT INTO curated.prices_daily(ds, symbol, open, high, low, close, volume)
                    VALUES (:ds, :symbol, :open, :high, :low, :close, :volume)
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "ds": row["ds"].date(),
                    "symbol": row["symbol"],
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]) if row["volume"] == row["volume"] else None,
                },
            )
    # Update refresh hours parameter if missing
    upsert_parameter(engine, "refresh_hours", str(settings.refresh_hours))


def main():
    parser = argparse.ArgumentParser(description="Ingest data into Neon Postgres")
    parser.add_argument("--symbol", default="ZL=F")
    args = parser.parse_args()
    ingest_yahoo(args.symbol)
    print(json.dumps({"status": "ok", "ts": datetime.utcnow().isoformat()}))


if __name__ == "__main__":
    main()
