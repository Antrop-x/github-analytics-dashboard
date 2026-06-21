"""
Hegemony presenter - Renderização da seção de hegemonia
"""

import pandas as pd
from typing import Dict, Any
from ui.widgets import render_section_header


def render_hegemony_section(heg: Dict[str, Any]):
    """
    Renderiza seção de hegemonia.
    
    Args:
        heg: Dados de hegemonia computada
    """
    import streamlit as st
    
    render_section_header("🧠 Hegemonia Computada", 
                         description="Distribuição de poder e influência na rede")
    
    if isinstance(heg, pd.DataFrame):
        st.dataframe(heg, use_container_width=True)
    else:
        st.info("Nenhum dado de hegemonia disponível")
