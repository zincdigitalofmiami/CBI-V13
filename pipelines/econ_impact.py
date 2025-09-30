from datetime import datetime
import json
from sqlalchemy import text

from db.session import get_engine


SIGNAL_COLORS = {
    "BUY": "#1E7A46",
    "WATCH": "#C98E1D",
    "HOLD": "#A31D2A",
}


def run(volume_lbs: float = 1000000.0):
    engine = get_engine()
    now = datetime.utcnow()
    with engine.begin() as conn:
        row = conn.execute(text("SELECT ds, close FROM curated.prices_daily WHERE symbol='ZL=F' ORDER BY ds DESC LIMIT 1")).mappings().first()
        baseline = conn.execute(text("SELECT ds, y_hat FROM forecasts.price_baseline ORDER BY run_ts DESC, ds LIMIT 1")).mappings().first()
        price = float(row["close"]) if row else 0.0
        f30 = float(baseline["y_hat"]) if baseline else price
        delta = f30 - price
        # Simple rule: if forecast higher -> BUY now; if similar -> WATCH; if lower -> HOLD
        if delta > 0.01 * price:
            signal = "BUY"
            confidence = 0.7
        elif abs(delta) <= 0.01 * max(price, 1.0):
            signal = "WATCH"
            confidence = 0.5
        else:
            signal = "HOLD"
            confidence = 0.6
        dollar_impact = delta * volume_lbs / 100.0  # price is per 100 lbs (cwt) for ZL futures
        rationale = f"30d forecast vs spot suggests {signal}; Δ=${delta:.2f}/cwt on volume {volume_lbs:,.0f} lbs."
        conn.execute(text("INSERT INTO app.signals_today(ds, signal, confidence, dollar_impact, rationale) VALUES (CURRENT_DATE, :s, :c, :d, :r)"),
                     {"s": signal, "c": confidence, "d": dollar_impact, "r": rationale})
        conn.execute(text("INSERT INTO app.econ_impact(scenario, ds, delta_price, notes) VALUES ('baseline_30d', CURRENT_DATE, :dp, :n)"),
                     {"dp": delta, "n": rationale})
    print(json.dumps({"status": "ok", "stage": "econ_impact", "signal": signal, "delta": delta}))


if __name__ == "__main__":
    run()
