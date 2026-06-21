"""
UI Layout - Orchestração do layout principal
"""

import streamlit as st
import pandas as pd
from typing import Any
from models.ui_models import StorageInfo
from ui.theme import apply_theme
from ui.presenters import (
    render_overview_section,
    render_data_table_section,
    render_hegemony_section,
    render_inequality_section,
    render_storage_section,
    render_footer_section
)


def render_main_layout(
    df: pd.DataFrame,
    heg: pd.DataFrame,
    analysis: Any,
    storage_info: StorageInfo,
    mode: str,
    debug_mode: bool = False,
    rate_limited: bool = False
):
    """
    Renderiza o layout principal da aplicação.
    
    Args:
        df: DataFrame de repositórios
        heg: Dados de hegemonia
        analysis: Resultado da análise
        storage_info: Informações de storage
        mode: Modo de interpretação
        debug_mode: Se está em modo debug
        rate_limited: Se foi rate limited
    """
    # Aplicar tema
    apply_theme()
    
    # Header
    st.title("📊 Observatório do Trabalho Digital")
    st.caption("Interface de leitura da infraestrutura do GitHub como sistema de produção simbólica e material.")
    st.divider( )
    
    # Seções principais
    render_overview_section(df, mode, analysis, rate_limited)
    st.divider()
    
    render_data_table_section(df)
    st.divider()
    
    render_hegemony_section(heg)
    st.divider()
    
    render_inequality_section(df, analysis, debug_mode)
    st.divider()
    
    render_storage_section(storage_info)
    st.divider()
    
    render_footer_section()


def render_empty_state(message: str):
    """
    Renderiza estado vazio.
    
    Args:
        message: Mensagem a exibir
    """
    apply_theme()
    st.title("📊 Observatório do Trabalho Digital")
    st.warning(f"ℹ️ {message}")
    st.info("Ajuste os parâmetros na barra lateral e tente novamente.")


def configure_page():
    """Configura a página do Streamlit"""
    st.set_page_config(
        page_title="Observatório do Trabalho Digital",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
