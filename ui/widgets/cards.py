"""
Card widgets - Componentes de card reutilizáveis
"""

from models.ui_models import MetricCard, InfoCard


def render_metric_card(metric: MetricCard):
    """
    Renderiza um card de métrica de forma padronizada.
    
    Args:
        metric: Dados da métrica
    """
    import streamlit as st
    
    status_color = {
        'good': '#238636',
        'warning': '#d29922',
        'critical': '#f85149'
    }
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.write(f"## {metric.icon}")
    
    with col2:
        st.write(f"**{metric.label}**")
        st.write(f"**{metric.format_value()}** {metric.unit}")
        if metric.context:
            st.caption(metric.context)
    
    if metric.status:
        color = status_color.get(metric.status, '#58a6ff')
        st.markdown(f"<hr style='border: 1px solid {color};'/>", unsafe_allow_html=True)


def render_info_card(card: InfoCard):
    """
    Renderiza um card informativo.
    
    Args:
        card: Dados do card
    """
    import streamlit as st
    
    card_type_styles = {
        'info': {'color': '#58a6ff', 'icon': 'ℹ️'},
        'warning': {'color': '#d29922', 'icon': '⚠️'},
        'success': {'color': '#238636', 'icon': '✅'},
        'error': {'color': '#f85149', 'icon': '❌'}
    }
    
    style = card_type_styles.get(card.card_type, card_type_styles['info'])
    
    if card.expandable:
        with st.expander(f"{style['icon']} {card.title}", expanded=card.expanded):
            st.write(card.content)
    else:
        st.markdown(f"**{card.title}**")
        st.write(card.content)
