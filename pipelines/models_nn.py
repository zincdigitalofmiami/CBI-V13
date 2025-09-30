from datetime import datetime, timedelta
import json
import uuid
import pandas as pd
from sqlalchemy import text

from db.session import get_engine

MODEL_NAME = "nn_lstm_placeholder"
MODEL_VERSION = "0.1.0"


def run():
    engine = get_engine()
    run_id = str(uuid.uuid4())
    started = datetime.utcnow()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO models.runs(run_id, started_at, model, params_json, status) VALUES (:rid, :st, :m, '{}'::jsonb, 'running')"), {"rid": run_id, "st": started, "m": MODEL_NAME})
        df = pd.read_sql(text("SELECT ds, close FROM curated.prices_daily WHERE symbol = 'ZL=F' ORDER BY ds"), conn)
    if df.empty:
        status = "no_data"
        finished = datetime.utcnow()
        with engine.begin() as conn:
            conn.execute(text("UPDATE models.runs SET finished_at=:fin, status=:st WHERE run_id=:rid"), {"fin": finished, "st": status, "rid": run_id})
        print(json.dumps({"status": status, "stage": "models_nn", "run_id": run_id}))
        return

    # Placeholder: copy baseline horizon logic but mark as NN
    df = df.tail(60)
    y_last = float(df["close"].iloc[-1])
    std = float(df["close"].pct_change().std() or 0) * y_last
    horizons = [7, 30, 90, 365]
    with engine.begin() as conn:
        for h in horizons:
            ds = df["ds"].iloc[-1] + timedelta(days=h)
            y_hat = y_last
            y_lo = y_last - 1.5 * std
            y_hi = y_last + 1.5 * std
            conn.execute(text("INSERT INTO forecasts.price_nn(run_ts, ds, horizon_days, y_hat, y_lo, y_hi, model_version) VALUES (:rt, :ds, :h, :y, :yl, :yh, :v)"),
                         {"rt": started, "ds": ds, "h": h, "y": y_hat, "yl": y_lo, "yh": y_hi, "v": MODEL_VERSION})
            # simple explanation stub
            conn.execute(text("INSERT INTO app.explanations(run_id, ds, top_features_json, reason_text) VALUES (:rid, :ds, '{}'::jsonb, :rt)"),
                         {"rid": run_id, "ds": ds, "rt": "Placeholder NN rationale based on recent trends."})
    finished = datetime.utcnow()
    with engine.begin() as conn:
        conn.execute(text("UPDATE models.runs SET finished_at=:fin, status='ok' WHERE run_id=:rid"), {"fin": finished, "rid": run_id})
    print(json.dumps({"status": "ok", "stage": "models_nn", "run_id": run_id}))


if __name__ == "__main__":
    run()
