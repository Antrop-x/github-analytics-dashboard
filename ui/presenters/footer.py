"""
Footer presenter - Renderização do rodapé
"""

from ui.widgets import render_section_header


def render_footer_section():
    """
    Renderiza rodapé da aplicação.
    """
    import streamlit as st
    
    st.divider()
    st.caption("© 2024 GitHub Analytics Dashboard - Observatório do Trabalho Digital")
    st.caption("Dados coletados em tempo real da API do GitHub com cache de 5 minutos")
