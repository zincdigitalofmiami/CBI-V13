import streamlit as st
import pandas as pd
from sqlalchemy import text
from db.session import get_engine, ping

st.set_page_config(page_title="Sentiment & Market Intelligence", layout="wide")

st.title("Sentiment & Market Intelligence")

if not ping():
    st.warning("Database not reachable.")
else:
    engine = get_engine()
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader("Mood Gauge")
        with engine.begin() as conn:
            scores = pd.read_sql(text("SELECT ts, category, score, label, weight FROM sentiment.category_scores ORDER BY ts DESC LIMIT 200"), conn)
        if scores.empty:
            st.info("No sentiment data yet.")
        else:
            s = scores.groupby("category")["score"].mean().sort_values()
            st.bar_chart(s)
    with col2:
        st.subheader("Recent Sources")
        st.write("Click a category to expand recent sources with impact scoring (placeholder)")
