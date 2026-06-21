"""
DataFrame widgets - Componentes de tabela reutilizáveis
"""

import pandas as pd


def render_dataframe_card(title: str, df: pd.DataFrame, icon: str = "📊", **kwargs):
    """
    Renderiza uma tabela em formato de card.
    
    Args:
        title: Título do card
        df: DataFrame a renderizar
        icon: Ícone para o título
        **kwargs: Argumentos adicionais para st.dataframe
    """
    import streamlit as st
    
    st.markdown(f"## {icon} {title}")
    st.dataframe(df, use_container_width=True, **kwargs)


def render_status_badge(label: str, value: bool):
    """
    Renderiza um badge de status.
    
    Args:
        label: Texto do label
        value: True para ✅, False para ❌
    """
    import streamlit as st
    
    icon = "✅" if value else "❌"
    st.write(f"{icon} {label}")
