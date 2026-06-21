"""
Data table presenter - Renderização da tabela de dados
"""

import pandas as pd
from ui.widgets import render_section_header


def render_data_table_section(df: pd.DataFrame):
    """
    Renderiza tabela de dados.
    
    Args:
        df: DataFrame a exibir
    """
    import streamlit as st
    
    render_section_header("📋 Dados Brutos", description="Todos os repositórios coletados")
    
    # Colunas principais para exibição
    display_cols = ["name", "stars", "forks", "url"] if "url" in df.columns else ["name", "stars", "forks"]
    
    st.dataframe(
        df[display_cols].head(50),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Mostrando 50 de {len(df)} repositórios")
