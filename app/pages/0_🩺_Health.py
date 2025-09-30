import os
import streamlit as st
from sqlalchemy import text

from db.session import get_engine, ping

st.set_page_config(page_title="Health", layout="centered")

st.title("System Health & Connections")

mode = "DATABASE_URL" if os.getenv("DATABASE_URL") else ("CloudSQL_IAM" if os.getenv("USE_IAM_AUTH", "false").lower() in ("1","true","yes") else "unconfigured")
st.caption(f"DB mode: {mode}")

ok = ping()
if not ok:
    st.error("Database not reachable. Check .env or environment variables.")
    st.stop()

engine = get_engine()

cols = st.columns(2)
with cols[0]:
    st.subheader("Row Counts")
    try:
        with engine.begin() as conn:
            c_prices = conn.execute(text("SELECT COUNT(*) FROM curated.prices_daily")).scalar() or 0
            c_base = conn.execute(text("SELECT COUNT(*) FROM forecasts.price_baseline")).scalar() or 0
            c_nn = conn.execute(text("SELECT COUNT(*) FROM forecasts.price_nn")).scalar() or 0
            c_sig = conn.execute(text("SELECT COUNT(*) FROM app.signals_today")).scalar() or 0
        st.write({
            "curated.prices_daily": int(c_prices),
            "forecasts.price_baseline": int(c_base),
            "forecasts.price_nn": int(c_nn),
            "app.signals_today": int(c_sig),
        })
    except Exception as e:
        st.error(f"Query error: {e}")

with cols[1]:
    st.subheader("Latest Records")
    try:
        with engine.begin() as conn:
            last_price = conn.execute(text("SELECT ds, symbol, close FROM curated.prices_daily ORDER BY ds DESC LIMIT 1")).mappings().first()
            last_base = conn.execute(text("SELECT ds, y_hat FROM forecasts.price_baseline ORDER BY run_ts DESC, ds DESC LIMIT 1")).mappings().first()
            last_sig = conn.execute(text("SELECT ds, signal, confidence FROM app.signals_today ORDER BY ds DESC LIMIT 1")).mappings().first()
        st.write({
            "curated.prices_daily": last_price or {},
            "forecasts.price_baseline": last_base or {},
            "app.signals_today": last_sig or {},
        })
    except Exception as e:
        st.error(f"Query error: {e}")

st.divider()

st.subheader("Next actions")
st.markdown("- If counts are zero, run pipelines: Admin page → Run All Stages, or `make pipelines`.")
st.markdown("- If DB not reachable, ensure DATABASE_URL is set (Neon requires ?sslmode=require) or USE_IAM_AUTH=true with Cloud SQL envs.")
