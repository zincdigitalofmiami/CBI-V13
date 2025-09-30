from datetime import datetime, timedelta
import json
import uuid
import pandas as pd
from sqlalchemy import text

from db.session import get_engine


MODEL_NAME = "baseline_arima_placeholder"
MODEL_VERSION = "0.1.0"


def run():
    engine = get_engine()
    run_id = str(uuid.uuid4())
    started = datetime.utcnow()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO models.runs(run_id, started_at, model, params_json, status) VALUES (:rid, :st, :m, '{}'::jsonb, 'running')"), {"rid": run_id, "st": started, "m": MODEL_NAME})
        df = pd.read_sql(text("SELECT ds, close FROM curated.prices_daily WHERE symbol = 'ZL=F' ORDER BY ds"), conn)
    if df.empty:
        horizons = [7, 30, 90, 365]
        now = datetime.utcnow().date()
        with engine.begin() as conn:
            for h in horizons:
                conn.execute(text("INSERT INTO forecasts.price_baseline(run_ts, ds, horizon_days, y_hat, y_lo, y_hi, model_version) VALUES (:rt, :ds, :h, :y, :yl, :yh, :v)"),
                             {"rt": started, "ds": now + timedelta(days=h), "h": h, "y": 0.0, "yl": -1.0, "yh": 1.0, "v": MODEL_VERSION})
        status = "no_data"
    else:
        df = df.tail(60)
        y_last = float(df["close"].iloc[-1])
        std = float(df["close"].pct_change().std() or 0) * y_last
        horizons = [7, 30, 90, 365]
        with engine.begin() as conn:
            for h in horizons:
                ds = df["ds"].iloc[-1] + timedelta(days=h)
                y_hat = y_last
                y_lo = y_last - 2 * std
                y_hi = y_last + 2 * std
                conn.execute(text("INSERT INTO forecasts.price_baseline(run_ts, ds, horizon_days, y_hat, y_lo, y_hi, model_version) VALUES (:rt, :ds, :h, :y, :yl, :yh, :v)"),
                             {"rt": started, "ds": ds, "h": h, "y": y_hat, "yl": y_lo, "yh": y_hi, "v": MODEL_VERSION})
        status = "ok"
    finished = datetime.utcnow()
    with engine.begin() as conn:
        conn.execute(text("UPDATE models.runs SET finished_at=:fin, status=:st WHERE run_id=:rid"), {"fin": finished, "st": status, "rid": run_id})
    print(json.dumps({"status": status, "stage": "models_baseline", "run_id": run_id}))


if __name__ == "__main__":
    run()
