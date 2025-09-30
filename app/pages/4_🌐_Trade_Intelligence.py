import json
from datetime import datetime

import pandas as pd
import streamlit as st
from sqlalchemy import text

from db.session import get_engine, ping

st.set_page_config(page_title="Trade Intelligence — Geopolitics & Trump Effect", layout="wide")
st.title("Trade Intelligence")
st.caption("Policy, geopolitics, FX, and the 'Trump Effect' — context for procurement decisions. Signals remain model-driven on the Command Center.")

if not ping():
    st.error("Database not reachable. Check DATABASE_URL or Cloud SQL IAM settings.")
    st.stop()

engine = get_engine()

# Helper to run a query safely
def safe_read(sql: str, params: dict | None = None) -> pd.DataFrame:
    try:
        with engine.begin() as conn:
            return pd.DataFrame(conn.execute(text(sql), params or {}).mappings())
    except Exception as e:
        # Missing tables/views should not break the page
        st.info(f"No data yet for: {sql.splitlines()[0][:70]}…\nReason: {e}")
        return pd.DataFrame()

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Trump Effect — Social/Policy Shock Monitor")
    st.caption("Classified social posts and news items related to tariffs/policy. Shows relevance, sentiment, and estimated impact.")

    q_trump = """
    SELECT ts, author, trade_relevance, sentiment, impact_est,
           COALESCE(entities::text, '') AS entities
    FROM sentiment.social_impact
    WHERE (author ILIKE 'Donald Trump%' OR author ILIKE 'Trump%' OR entities::text ILIKE '%Trump%')
    ORDER BY ts DESC
    LIMIT 50
    """
    df_trump = safe_read(q_trump)
    if not df_trump.empty:
        st.dataframe(df_trump, use_container_width=True, hide_index=True)
    else:
        st.warning("No 'Trump Effect' items found yet. Populate sentiment.social_impact via your features pipeline.")

    st.divider()
    st.subheader("Policy Timeline — Upcoming Events")
    st.caption("Votes, speeches, implementation deadlines likely to move soybean oil markets.")
    q_timeline = """
    SELECT event_ts, label, category, url, importance
    FROM curated.trade_timeline
    WHERE event_ts >= now() - interval '30 days'
    ORDER BY event_ts ASC
    LIMIT 200
    """
    df_timeline = safe_read(q_timeline)
    if not df_timeline.empty:
        st.dataframe(df_timeline, use_container_width=True, hide_index=True)
    else:
        st.info("No upcoming timeline entries yet. Insert into curated.trade_timeline.")

    st.divider()
    st.subheader("Congress Watch — Bills & Probabilities")
    q_congress = """
    SELECT bill_id, chamber, title, scheduled_date, topic, prob_pass, url
    FROM curated.congress_votes
    ORDER BY scheduled_date NULLS LAST, prob_pass DESC
    LIMIT 200
    """
    df_congress = safe_read(q_congress)
    if not df_congress.empty:
        st.dataframe(df_congress, use_container_width=True, hide_index=True)
    else:
        st.info("No congressional items yet. Seed curated.congress_votes from ProPublica Congress API.")

with col2:
    st.subheader("Tariff/Policy Heatmap")
    st.caption("Implied probabilities and proposed rates for trade policies affecting soy complex.")
    q_probs = """
    SELECT as_of, country, commodity, prob, proposed_rate, rationale
    FROM curated.trade_policy_probs
    WHERE as_of >= (now() - interval '90 days')::date
    ORDER BY as_of DESC, prob DESC
    LIMIT 200
    """
    df_probs = safe_read(q_probs)
    if not df_probs.empty:
        st.dataframe(df_probs, use_container_width=True, hide_index=True)
    else:
        st.info("No policy probability rows yet. Upsert into curated.trade_policy_probs.")

    st.divider()
    st.subheader("Country Snapshots")
    st.caption("Key status metrics per country/section.")
    q_country = """
    SELECT as_of, country, section, metric, value, score
    FROM curated.country_intel
    WHERE as_of >= (now() - interval '120 days')::date
    ORDER BY as_of DESC, country, section
    LIMIT 300
    """
    df_country = safe_read(q_country)
    if not df_country.empty:
        # Pivot latest by country-section if not too big
        latest_date = df_country['as_of'].max()
        df_latest = df_country[df_country['as_of'] == latest_date]
        st.write(f"Latest as of {latest_date}")
        st.dataframe(df_latest, use_container_width=True, hide_index=True)
    else:
        st.info("No country intelligence yet. Insert into curated.country_intel.")

    st.divider()
    st.subheader("FX & Macro (BRL, DXY, WTI)")
    q_fx = """
    SELECT ds, brl_usd, dxy, wti, rates10y
    FROM features.fx_trade
    ORDER BY ds DESC
    LIMIT 60
    """
    df_fx = safe_read(q_fx)
    if not df_fx.empty:
        st.line_chart(df_fx.set_index('ds'))
    else:
        st.info("No fx_trade view data yet. Populate features.macro and raw.fx.")

st.divider()

st.subheader("How this page is used")
st.markdown(
    "- Context only: BUY/WATCH/HOLD remains model-driven on the Command Center.\n"
    "- Use the timeline and Congress watch to anticipate volatility windows.\n"
    "- 'Trump Effect' highlights high-relevance social/policy shocks with estimated impact.\n"
)
