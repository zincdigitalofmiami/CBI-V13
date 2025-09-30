from datetime import datetime
import json
import pandas as pd
from sqlalchemy import text

from db.session import get_engine


def compute_technical(prices: pd.DataFrame) -> pd.DataFrame:
    df = prices.sort_values("ds").copy()
    df["rsi"] = 50.0  # placeholder
    df["ma7"] = df["close"].rolling(7).mean()
    df["ma30"] = df["close"].rolling(30).mean()
    df["ma90"] = df["close"].rolling(90).mean()
    df["vol_z"] = (df["volume"] - df["volume"].rolling(60).mean()) / (df["volume"].rolling(60).std() + 1e-9)
    return df[["ds", "symbol", "rsi", "ma7", "ma30", "ma90", "vol_z"]].dropna()


def run():
    engine = get_engine()
    with engine.begin() as conn:
        prices = pd.read_sql(text("SELECT ds, symbol, close, volume FROM curated.prices_daily WHERE symbol = 'ZL=F' ORDER BY ds"), conn)
    tech = compute_technical(prices)
    with engine.begin() as conn:
        for _, r in tech.iterrows():
            conn.execute(
                text(
                    """
                    INSERT INTO features.technical(ds, symbol, rsi, ma7, ma30, ma90, vol_z)
                    VALUES (:ds, :symbol, :rsi, :ma7, :ma30, :ma90, :vol_z)
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "ds": r["ds"].date() if hasattr(r["ds"], "date") else r["ds"],
                    "symbol": r["symbol"],
                    "rsi": float(r["rsi"]),
                    "ma7": float(r["ma7"]),
                    "ma30": float(r["ma30"]),
                    "ma90": float(r["ma90"]),
                    "vol_z": float(r["vol_z"]),
                },
            )
    print(json.dumps({"status": "ok", "stage": "features", "ts": datetime.utcnow().isoformat()}))


if __name__ == "__main__":
    run()
