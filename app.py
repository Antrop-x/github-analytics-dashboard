import streamlit as st

from services.pipeline_service import ingest_repositories
from services.storage_service import StorageService
from services.storage_inspection_service import StorageInspectionService
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
from config.settings import Settings

configure_page()
apply_theme()

settings = Settings()
storage_service = StorageService(settings)
inspection_service = StorageInspectionService(storage_service)

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

# Criar AnalysisResult via interpretation service
from services.interpretation_service import InterpretationService
interpretation_service = InterpretationService()
analysis = interpretation_service.create_analysis_result(df, heg, gini_value)

# Preparar dados de storage para UI
storage_info = inspection_service.inspect()

render_overview(df, mode, analysis, rate_limited)
render_data_table(df)
render_hegemony(heg)
render_inequality_section(df, analysis, debug_mode)
render_reflexivity(storage_info)
