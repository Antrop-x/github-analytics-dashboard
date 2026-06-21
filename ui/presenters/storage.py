"""
Storage presenter - Renderização da seção de storage
"""

from models.ui_models import StorageInfo
from ui.widgets import render_section_header


def render_storage_section(storage_info: StorageInfo):
    """
    Renderiza seção de storage.
    
    Args:
        storage_info: Informações de storage
    """
    import streamlit as st
    
    render_section_header("💾 Status de Storage", 
                         description="Saúde e disponibilidade de dados")
    
    if storage_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Backend", storage_info.backend)
        
        with col2:
            st.metric("Saúde", f"{storage_info.health_percentage:.1f}%")
        
        with col3:
            st.metric("Disponibilidade", f"{storage_info.available_sources}/{storage_info.total_sources}")
