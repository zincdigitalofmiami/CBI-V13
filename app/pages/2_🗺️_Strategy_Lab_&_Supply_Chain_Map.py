import streamlit as st
import pandas as pd
import pydeck as pdk
from sqlalchemy import text
from db.session import get_engine, ping

st.set_page_config(page_title="Strategy Lab & Supply Chain Map", layout="wide")

st.title("Strategy Lab & Supply Chain Map")

if not ping():
    st.warning("Database not reachable.")
else:
    engine = get_engine()
    with engine.begin() as conn:
        nodes = pd.read_sql(text("SELECT id, name, type, lat, lon FROM geo.nodes"), conn)
        edges = pd.read_sql(text("SELECT src_id, dst_id, kind, weight FROM geo.edges"), conn)
    if nodes.empty:
        st.info("No geo data yet. Populate geo.nodes and geo.edges.")
    else:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=nodes,
            get_position='[lon, lat]',
            get_color='[110, 163, 247, 200]',
            get_radius=40000,
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=float(nodes["lat"].mean()), longitude=float(nodes["lon"].mean()), zoom=2)
        st.pydeck_chart(pdk.Deck(map_style=None, initial_view_state=view_state, layers=[layer]))

    st.subheader("Pre-built Scenarios")
    st.write("Brazil drought, China buying, mandate +10%, tariffs (placeholder controls)")
