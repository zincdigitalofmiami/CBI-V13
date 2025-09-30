import os
import streamlit as st
from sqlalchemy import text

from config.settings import settings
from db.session import get_engine, ping

st.set_page_config(page_title="Admin", layout="centered")

st.title("Admin Controls")

admin_token = st.text_input("Admin Token", type="password")
if st.button("Verify"):
    st.session_state["admin_ok"] = admin_token and admin_token == settings.admin_token

if not st.session_state.get("admin_ok"):
    st.info("Enter the admin token to manage pipelines and parameters.")
    st.stop()

if not ping():
    st.warning("Database not reachable.")
else:
    engine = get_engine()

    # Schema management
    st.subheader("Database Schema")
    if st.button("Apply sql/schema.sql now"):
        try:
            from pathlib import Path
            schema_path = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"
            sql_text = schema_path.read_text(encoding="utf-8")
            with engine.begin() as conn:
                conn.execute(text(sql_text))
            st.success("Schema applied successfully.")
        except Exception as e:
            st.error(f"Failed to apply schema: {e}")

    st.subheader("Refresh Cadence (hours)")
    with engine.begin() as conn:
        row = conn.execute(text("SELECT value FROM app.parameters WHERE key='refresh_hours'"))
        try:
            curr = int(row.scalar() or settings.refresh_hours)
        except Exception:
            curr = settings.refresh_hours
    new_val = st.number_input("Refresh every N hours", min_value=1, max_value=24, value=curr)
    if st.button("Update Cadence"):
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO app.parameters(key, value) VALUES ('refresh_hours', :v) ON CONFLICT (key) DO UPDATE SET value = excluded.value"),
                         {"v": str(int(new_val))})
        st.success("Updated refresh cadence.")

    st.subheader("Trigger Pipelines Now")
    if st.button("Run All Stages (ingest → features → baseline → nn → econ)"):
        try:
            import pipelines.ingest as ing
            import pipelines.features as feat
            import pipelines.models_baseline as mb
            import pipelines.models_nn as mn
            import pipelines.econ_impact as ei
            ing.main()
            feat.run()
            mb.run()
            mn.run()
            ei.run()
            st.success("Pipelines completed")
        except Exception as e:
            st.error(f"Error running pipelines: {e}")
