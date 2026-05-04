"""
UI Sections - Seções principais da interface
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from models.ui_models import StorageInfo, OverviewMetrics, InequalityMetrics
from services.interpretation_service import AnalysisResult
from ui.components import (
    render_section_header,
    render_status_badge,
    render_progress_with_label,
    render_dataframe_card,
    render_metric_grid,
    render_metric_card,
    MetricCard
)
from core.metrics import get_top_hegemonic_repo, top_concentration


def render_overview_section(df: pd.DataFrame, mode: str, analysis: AnalysisResult, 
                           rate_limited: bool = False):
    """
    Renderiza seção de overview/resumo.
    
    Args:
        df: DataFrame de repositórios
        mode: Modo de interpretação
        analysis: Resultado da análise
        rate_limited: Se foi rate limited
    """
    from ui.ui import get_mode_labels
    
    mode_labels = get_mode_labels(mode)
    render_section_header(mode_labels['title'], description=mode_labels['description'])
    
    # Métricas principais
    name, value, rank_label = get_top_hegemonic_repo(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Repositórios", len(df))
    
    with col2:
        st.metric("⭐ Stars Médios", f"{df['stars'].mean():.1f}" if not df.empty else "0")
    
    with col3:
        st.metric("🔗 Forks Médios", f"{df['forks'].mean():.1f}" if not df.empty else "0")
    
    with col4:
        gini_val = analysis.gini if hasattr(analysis, 'gini') else None
        st.metric("📉 Gini", f"{gini_val:.3f}" if gini_val else "N/A")
    
    # Top repo
    if name:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**Top Hegemônico:** `{name}`")
        with col2:
            st.write(f"⭐ {value}")
    
    if rate_limited:
        st.warning("⚠️ Rate limited - alguns dados podem estar incompletos")


def render_data_table_section(df: pd.DataFrame):
    """
    Renderiza tabela de dados.
    
    Args:
        df: DataFrame a exibir
    """
    render_section_header("📋 Dados Brutos", description="Todos os repositórios coletados")
    
    # Colunas principais para exibição
    display_cols = ["name", "stars", "forks", "url"] if "url" in df.columns else ["name", "stars", "forks"]
    
    st.dataframe(
        df[display_cols].head(50),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Mostrando 50 de {len(df)} repositórios")


def render_hegemony_section(heg: Dict[str, Any]):
    """
    Renderiza seção de hegemonia.
    
    Args:
        heg: Dados de hegemonia computada
    """
    render_section_header("🧠 Hegemonia Computada", 
                         description="Distribuição de poder e influência na rede")
    
    if isinstance(heg, pd.DataFrame):
        st.dataframe(heg, use_container_width=True)
    else:
        st.write(heg)


def render_inequality_section(df: pd.DataFrame, analysis: AnalysisResult, 
                            debug_mode: bool = False):
    """
    Renderiza seção de desigualdade.
    
    Args:
        df: DataFrame de dados
        analysis: Resultado da análise
        debug_mode: Se está em modo debug
    """
    render_section_header("📈 Análise de Desigualdade",
                         description="Métricas e interpretação de distribuição de poder")
    
    if debug_mode:
        st.markdown("### 🔍 Modo Debug")
        st.dataframe(
            df[["name", "stars", "forks"]].head(20) if not df.empty else df,
            use_container_width=True
        )
    
    # Mostrar concentração
    if not df.empty:
        concentration = top_concentration(df["stars"])
        st.write(f"**Concentração (Top 10%):** {concentration:.2%}")
    
    # Mostrar análise
    if hasattr(analysis, 'interpretation'):
        st.info(analysis.interpretation)


def render_storage_section(storage_info: StorageInfo):
    """
    Renderiza seção de storage e infraestrutura.
    
    Args:
        storage_info: Informações de storage
    """
    render_section_header("💾 Storage e Infraestrutura", 
                         description="Estado e disponibilidade das fontes de dados")
    
    # Backend e diretório
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Backend:** {storage_info.backend}")
    with col2:
        st.write(f"**Diretório:** `{storage_info.directory}`")
    
    # Status do modo mock
    if storage_info.force_mock:
        st.warning("🔧 Modo MOCK forçado - usando dados simulados")
    elif storage_info.mock_fallback:
        st.info("🔄 Usando dados mockados como fallback")
    
    # Fontes disponíveis
    with st.expander("📊 Fontes de Dados", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Fontes Primárias:**")
            if storage_info.sources:
                for source in storage_info.sources:
                    st.write(f"• {source}")
            else:
                st.write("*Nenhuma fonte primária*")
        
        with col2:
            st.markdown("**Fontes Mock:**")
            if storage_info.mock_sources:
                for source in storage_info.mock_sources:
                    st.write(f"• {source}")
            else:
                st.write("*Nenhuma fonte mock*")
    
    # Disponibilidade das fontes
    st.markdown("**Disponibilidade:**")
    for name, available in storage_info.availability.items():
        render_status_badge(name, available)
    
    # Saúde do storage
    if storage_info.total_sources > 0:
        render_progress_with_label(
            storage_info.health_percentage / 100,
            storage_info.health_text,
            max_value=100
        )


def render_footer_section():
    """
    Renderiza rodapé com informações sobre a interface.
    """
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### ⚖️ Interpretação
        
        Stars representam **visibilidade social**  
        Forks representam **reuso técnico**
        """)
    
    with col2:
        st.markdown("""
        ### 🏗️ Arquitetura
        
        UI layer é **passiva**  
        Toda lógica em **services** e **core**
        """)
    
    with col3:
        st.markdown("""
        ### 📚 Camadas
        
        **Infrastructure** → **Services** → **UI**  
        Separação clara de responsabilidades
        """)
