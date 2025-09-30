import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.session import get_engine, ping

st.set_page_config(page_title="Strategy — Chris's Business Intelligence", layout="wide")

st.title("Strategy")
st.caption("Timing, contract mix, market structure, and performance — plan the next moves. This page provides tools and intelligence; the BUY/WATCH/HOLD signal comes from the Command Center.")

if not ping():
    st.warning("Database not reachable. Set DATABASE_URL or Cloud SQL IAM envs and apply sql/schema.sql.")
    st.stop()

engine = get_engine()

# Top Section: Procurement Best Practices & Timing
st.header("Procurement Best Practices & Timing")
left, right = st.columns([3, 2])
with left:
    st.subheader("Optimal Procurement Windows")
    st.caption("Calendar and seasonal patterns — placeholders until data is wired.")
    try:
        with engine.begin() as conn:
            perf = pd.read_sql(text("SELECT ds, realized_cost, benchmark_cost FROM strategy.performance ORDER BY ds"), conn)
    except Exception as e:
        perf = pd.DataFrame()
    if perf.empty:
        st.info("No performance data yet. Populate strategy.performance to enable historical timing overlays.")
    else:
        st.line_chart(perf.set_index("ds"))

with right:
    st.subheader("Contract Strategy Optimizer")
    st.caption("Current recommendations and comparisons — placeholder UI.")
    qty = st.slider("Planned buy (lbs)", 10000, 1000000, 250000, step=10000)
    fwd = st.slider("Forward cover (%)", 0, 100, 40, step=5)
    st.write({"planned_lbs": qty, "forward_pct": fwd, "note": "Logic to be powered by forecasts + basis history."})

st.divider()

# Middle Section: Industry Intelligence (four columns)
st.header("Industry Intelligence")
f1, f2, f3, f4 = st.columns(4)
with f1:
    st.subheader("Key Players")
    st.write("- Sysco, Restaurant Depot, US Foods (placeholders)\n- Processors: ADM, Bunge, Cargill")
with f2:
    st.subheader("Pricing Trends")
    try:
        with engine.begin() as conn:
            tech = pd.read_sql(text("SELECT ds, ma30 AS trend, vol_z FROM features.technical WHERE symbol='ZL=F' ORDER BY ds DESC LIMIT 180"), conn)
    except Exception:
        tech = pd.DataFrame()
    if tech.empty:
        st.info("No technical features yet. Run pipelines/features.py to populate features.technical.")
    else:
        st.line_chart(tech.set_index("ds"))
with f3:
    st.subheader("Recent Developments")
    try:
        with engine.begin() as conn:
            news = pd.read_sql(text("SELECT ts, category, title FROM raw.news ORDER BY ts DESC LIMIT 20"), conn)
    except Exception:
        news = pd.DataFrame()
    if news.empty:
        st.info("No news ingested yet. Add to raw.news or wire a feed.")
    else:
        st.dataframe(news, hide_index=True, use_container_width=True)
with f4:
    st.subheader("Market Structure")
    try:
        with engine.begin() as conn:
            sd = pd.read_sql(text("SELECT ds, production, stocks, use FROM curated.supply_demand WHERE region='US' ORDER BY ds DESC LIMIT 60"), conn)
    except Exception:
        sd = pd.DataFrame()
    if sd.empty:
        st.info("Supply/Demand not available yet. Populate curated.supply_demand.")
    else:
        st.area_chart(sd.set_index("ds"))

st.divider()

# Bottom Section: Deep Dive Analytics (tabs)
st.header("Deep Dive Analytics")
T1, T2, T3, T4 = st.tabs(["U.S. Production & Storage", "Global Supply & Demand", "Soy Complex Value Chain", "Food & Industrial Demand"])
with T1:
    st.caption("Interactive US map placeholder. Data tables shown until geo layer is wired.")
    try:
        with engine.begin() as conn:
            crush = pd.read_sql(text("SELECT ds, realized_cost, benchmark_cost, savings_cum FROM strategy.performance ORDER BY ds"), conn)
    except Exception:
        crush = pd.DataFrame()
    if crush.empty:
        st.info("Populate strategy.performance for storage/utilization analytics.")
    else:
        st.line_chart(crush.set_index("ds")[["realized_cost", "benchmark_cost"]])
with T2:
    try:
        with engine.begin() as conn:
            world = pd.read_sql(text("SELECT ds, region, production, use, stocks FROM curated.supply_demand ORDER BY ds DESC LIMIT 300"), conn)
    except Exception:
        world = pd.DataFrame()
    if world.empty:
        st.info("Populate curated.supply_demand for global S&D.")
    else:
        st.dataframe(world, hide_index=True, use_container_width=True)
with T3:
    st.info("Flowchart placeholder — will compute crush margins and value splits.")
with T4:
    st.info("Demand analytics placeholder — restaurant sales, competing oils share.")

st.sidebar.header("Strategy Tools")
st.sidebar.write("Quick calculators (placeholders):")
sc_days = st.sidebar.slider("Storage days", 0, 120, 30)
sc_rate = st.sidebar.number_input("$/lb/day", min_value=0.0, value=0.0005, step=0.0001, format="%.4f")
st.sidebar.write({"storage_days": sc_days, "rate_per_lb_day": sc_rate, "est_cost": sc_days * sc_rate})

st.sidebar.subheader("Performance")
try:
    with engine.begin() as conn:
        bt = pd.read_sql(text("SELECT strategy, metric, value FROM strategy.backtests ORDER BY strategy"), conn)
except Exception:
    bt = pd.DataFrame()
if bt.empty:
    st.sidebar.info("No backtests yet. Populate strategy.backtests.")
else:
    st.sidebar.dataframe(bt, hide_index=True, use_container_width=True)
