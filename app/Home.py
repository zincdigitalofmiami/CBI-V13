import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import text

from db.session import get_engine, ping

st.set_page_config(page_title="Procurement Command Center", layout="wide")

DARK_CSS = """
<style>
    .stApp { background: #0e1117; color: #e1e3e8; }
    .metric-card { background: rgba(255,255,255,0.05); padding: 16px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); backdrop-filter: blur(6px); }
    .signal { font-size: 36px; font-weight: 700; letter-spacing: 1px; }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

st.title("U.S. Oil Solution Intelligence")

ok = False
try:
    ok = ping()
except Exception:
    ok = False

if not ok:
    st.warning("Database not reachable. Set DATABASE_URL and apply sql/schema.sql.")
else:
    engine = get_engine()
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("Price & Forecast")
        with engine.begin() as conn:
            px = pd.read_sql(text("SELECT ds, close FROM curated.prices_daily WHERE symbol='ZL=F' ORDER BY ds"), conn)
            fb = pd.read_sql(text("SELECT ds, y_hat, y_lo, y_hi FROM forecasts.price_baseline ORDER BY ds"), conn)
        fig = go.Figure()
        if not px.empty:
            fig.add_trace(go.Scatter(x=px["ds"], y=px["close"], mode="lines", name="ZL=F Close", line=dict(color="#6ea3f7", width=2)))
        if not fb.empty:
            fig.add_trace(go.Scatter(x=fb["ds"], y=fb["y_hat"], mode="lines", name="Baseline 30-365d", line=dict(color="#C98E1D", dash="dash")))
            fig.add_trace(go.Scatter(x=fb["ds"], y=fb["y_lo"], mode="lines", name="Lo", line=dict(color="#444", width=1)))
            fig.add_trace(go.Scatter(x=fb["ds"], y=fb["y_hi"], mode="lines", name="Hi", line=dict(color="#444", width=1), fill='tonexty', fillcolor='rgba(201,142,29,0.1)'))
        fig.update_layout(template="plotly_dark", height=420, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Signal")
        with engine.begin() as conn:
            sig = conn.execute(text("SELECT ds, signal, confidence, dollar_impact, rationale FROM app.signals_today ORDER BY ds DESC LIMIT 1")).mappings().first()
        if sig:
            color = {"BUY": "#1E7A46", "WATCH": "#C98E1D", "HOLD": "#A31D2A"}.get(sig["signal"], "#888")
            st.markdown(f"<div class='metric-card'><div class='signal' style='color:{color}'>{sig['signal']}</div>Confidence: {sig['confidence']:.0%}<br/>Impact: ${sig['dollar_impact']:,.0f}<br/><small>{sig['rationale']}</small></div>", unsafe_allow_html=True)
        else:
            st.info("No signal yet. Run pipelines.")
    with col3:
        st.subheader("Parameters")
        with engine.begin() as conn:
            params = dict(conn.execute(text("SELECT key, value FROM app.parameters")).all())
        st.json(params or {"refresh_hours": os.getenv("REFRESH_HOURS", "8")})

st.sidebar.title("Navigation")
st.sidebar.write("Use the pages sidebar to explore Sentiment and Strategy Lab.")
