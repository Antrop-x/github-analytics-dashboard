"""
Inequality presenter - Renderização da seção de desigualdade
"""

import pandas as pd
from typing import Any
from ui.widgets import render_section_header


def render_inequality_section(df: pd.DataFrame, analysis: Any, debug_mode: bool = False):
    """
    Renderiza seção de desigualdade.
    
    Args:
        df: DataFrame de repositórios
        analysis: Resultado da análise
        debug_mode: Se está em modo debug
    """
    import streamlit as st
    
    render_section_header("📊 Distribuição de Desigualdade", 
                         description="Métricas de concentração e dominação")
    
    if hasattr(analysis, 'gini'):
        st.metric("📉 Coeficiente de Gini", f"{analysis.gini:.3f}")
    
    if debug_mode and hasattr(analysis, 'interpretation'):
        st.info(f"Interpretação: {analysis.interpretation.get('summary', 'N/A')}")
