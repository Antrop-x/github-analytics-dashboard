import streamlit as st

from services.pipeline_service import ingest_repositories
from ui.ui import (
    configure_page,
    apply_theme,
    sidebar_controls,
    render_header,
    render_overview,
    render_data_table,
    render_hegemony,
    render_reflexivity,
    render_empty,
)

configure_page()
apply_theme()

query, pages, sort, mode = sidebar_controls()
render_header()

result = ingest_repositories(query=query, pages=pages, sort=sort, use_cache=True)
df = result["data"]
heg = result["hegemony"]
analysis = result["analysis"]
rate_limited = result["rate_limited"]

if df.empty:
    render_empty("Sem dados disponíveis para este recorte.")
    st.stop()

render_overview(df, mode, analysis, rate_limited)
render_data_table(df)
render_hegemony(heg)
render_reflexivity()
