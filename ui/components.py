"""
UI Components - Componentes reutilizáveis do Streamlit
"""

import streamlit as st
import pandas as pd
from typing import Optional, Any
from models.ui_models import MetricCard, InfoCard, ThemeConfig


def render_metric_card(metric: MetricCard):
    """
    Renderiza um card de métrica de forma padronizada.
    
    Args:
        metric: Dados da métrica
    """
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


def render_metric_grid(metrics: list[MetricCard], columns: int = 3):
    """
    Renderiza uma grade de métricas.
    
    Args:
        metrics: Lista de métricas
        columns: Número de colunas
    """
    cols = st.columns(columns)
    for idx, metric in enumerate(metrics):
        with cols[idx % columns]:
            render_metric_card(metric)


def render_dataframe_card(title: str, df: pd.DataFrame, icon: str = "📊", **kwargs):
    """
    Renderiza uma tabela em formato de card.
    
    Args:
        title: Título do card
        df: DataFrame a renderizar
        icon: Ícone para o título
        **kwargs: Argumentos adicionais para st.dataframe
    """
    st.markdown(f"## {icon} {title}")
    st.dataframe(df, use_container_width=True, **kwargs)


def render_status_badge(label: str, value: bool):
    """
    Renderiza um badge de status.
    
    Args:
        label: Texto do label
        value: True para ✅, False para ❌
    """
    icon = "✅" if value else "❌"
    status = "Disponível" if value else "Indisponível"
    st.write(f"{icon} **{label}**: {status}")


def render_progress_with_label(value: float, label: str, max_value: float = 1.0):
    """
    Renderiza uma barra de progresso com label formatado.
    
    Args:
        value: Valor atual (0-1)
        label: Template de label com {value} e {percent}
        max_value: Valor máximo para cálculo de percentual
    """
    percent = (value / max_value * 100) if max_value > 0 else 0
    text = label.format(value=value, percent=percent)
    st.progress(value, text=text)


def render_section_header(title: str, icon: str = "📊", description: str = ""):
    """
    Renderiza cabeçalho de uma seção.
    
    Args:
        title: Título da seção
        icon: Ícone
        description: Descrição opcional
    """
    st.markdown(f"## {icon} {title}")
    if description:
        st.markdown(description)
        st.divider()


def create_custom_card_html(title: str, content: str, icon: str = "📊", 
                           bg_color: str = "#0d1117", border_color: str = "#30363d") -> str:
    """
    Cria HTML personalizado para um card.
    
    Args:
        title: Título do card
        content: Conteúdo HTML
        icon: Ícone
        bg_color: Cor de fundo
        border_color: Cor da borda
        
    Returns:
        HTML do card
    """
    return f"""
    <div style="
        background-color: {bg_color};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    ">
        <h4 style="margin-top: 0;">{icon} {title}</h4>
        <div>{content}</div>
    </div>
    """


def render_custom_card(title: str, content: str, icon: str = "📊"):
    """
    Renderiza um card customizado com HTML.
    
    Args:
        title: Título
        content: Conteúdo
        icon: Ícone
    """
    html = create_custom_card_html(title, content, icon)
    st.markdown(html, unsafe_allow_html=True)
