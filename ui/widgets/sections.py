"""
Section widgets - Componentes de seção reutilizáveis
"""


def render_section_header(title: str, description: str = ""):
    """
    Renderiza o cabeçalho de uma seção.
    
    Args:
        title: Título da seção
        description: Descrição opcional
    """
    import streamlit as st
    
    st.markdown(f"## {title}")
    if description:
        st.caption(description)


def render_progress_with_label(label: str, value: float, max_value: float = 100):
    """
    Renderiza uma barra de progresso com label.
    
    Args:
        label: Rótulo da barra
        value: Valor atual
        max_value: Valor máximo
    """
    import streamlit as st
    
    st.write(f"{label}: {value:.1f}%")
    st.progress(value / max_value if max_value > 0 else 0)
