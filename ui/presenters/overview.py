"""
Overview presenter - Renderização da seção de overview
"""

import pandas as pd
from typing import Any
from core.metrics import get_top_hegemonic_repo
from ui.views import get_mode_labels
from ui.widgets import render_section_header


def render_overview_section(df: pd.DataFrame, mode: str, analysis: Any, 
                           rate_limited: bool = False):
    """
    Renderiza seção de overview/resumo.
    
    Args:
        df: DataFrame de repositórios
        mode: Modo de interpretação
        analysis: Resultado da análise
        rate_limited: Se foi rate limited
    """
    import streamlit as st
    
    mode_labels = get_mode_labels(mode)
    render_section_header(mode_labels['title'], description=mode_labels['description'])
    
    # Métricas principais
    name, value, rank_label = get_top_hegemonic_repo(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Repositórios", len(df))
    
    with col2:
        st.metric("⭐ Stars Médios", f"{df['stars'].mean():.1f}" if not df.empty else "0")
    
    with col3:
        st.metric("🔗 Forks Médios", f"{df['forks'].mean():.1f}" if not df.empty else "0")
    
    with col4:
        gini_val = analysis.gini if hasattr(analysis, 'gini') else None
        st.metric("📉 Gini", f"{gini_val:.3f}" if gini_val else "N/A")
    
    # Top repo
    if name:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**Top Hegemônico:** `{name}`")
        with col2:
            st.write(f"⭐ {value}")
    
    if rate_limited:
        st.warning("⚠️ Rate limited - alguns dados podem estar incompletos")
