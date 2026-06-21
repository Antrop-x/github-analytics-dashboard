"""
Grid widgets - Componentes de grade reutilizáveis
"""

from models.ui_models import MetricCard
from ui.widgets.cards import render_metric_card


def render_metric_grid(metrics: list, columns: int = 3):
    """
    Renderiza uma grade de métricas.
    
    Args:
        metrics: Lista de métricas
        columns: Número de colunas
    """
    import streamlit as st
    
    cols = st.columns(columns)
    for idx, metric in enumerate(metrics):
        with cols[idx % columns]:
            render_metric_card(metric)
