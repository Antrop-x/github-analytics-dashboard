import streamlit as st

from services.pipeline_service import ingest_repositories
from core.metrics import gini
from ui.ui import (
    configure_page,
    apply_theme,
    sidebar_controls,
    render_header,
    render_overview,
    render_data_table,
    render_hegemony,
    render_reflexivity,
    render_inequality_section,
    render_empty,
)

configure_page()
apply_theme()

query, pages, sort, mode, debug_mode = sidebar_controls()
render_header()

result = ingest_repositories(query=query, pages=pages, sort=sort, use_cache=True)
df = result["data"]
heg = result["hegemony"]
rate_limited = result["rate_limited"]

if df.empty:
    render_empty("Sem dados disponíveis para este recorte.")
    st.stop()

# Calcular Gini
gini_value = gini(df["stars"]) if not df.empty else None

# Interpretar com desigualdade
from services.analysis_service import interpret_dataset
analysis = interpret_dataset(df, heg, gini_value)

render_overview(df, mode, analysis, rate_limited)
render_data_table(df)
render_hegemony(heg)
render_inequality_section(df, analysis, debug_mode)
render_reflexivity()
