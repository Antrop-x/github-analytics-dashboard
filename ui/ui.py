import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, Union
from core.metrics import get_top_hegemonic_repo
from services.interpretation_service import AnalysisResult
from services.storage_inspection_service import StorageInspectionService
from models.ui_models import StorageInfo
import plotly.graph_objects as go
import plotly.express as px
from core.metrics import top_concentration, analyze_segments


def configure_page():
    """Configura página do Streamlit"""
    st.set_page_config(
        page_title="Observatório do Trabalho Digital",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def apply_theme():
    """Aplica tema customizado à interface"""
    from ui.theme import apply_theme as apply_theme_impl
    apply_theme_impl()



def get_mode_labels(mode: str) -> dict:
    """
    Mapeia o modo de UI para chaves de backend e retorna labels apropriados.
    """
    mode_map = {
        "Modo Exploratório": "exploratory",
        "Modo Analítico": "analytical"
    }
    
    mode_key = mode_map.get(mode, "exploratory")
    
    labels = {
        "exploratory": {
            "title": "📊 Visão Exploratória",
            "description": "Análise inicial dos dados coletados. Foco em descoberta e padrões gerais.",
            "metrics_focus": "Métricas básicas de distribuição",
            "interpretation_style": "Descritivo e acessível",
            "appropriation_label": "Taxa de Reuso",
            "density_label": "Visibilidade Média"
        },
        "analytical": {
            "title": "🔬 Análise Profunda",
            "description": "Análise estatística rigorosa com métricas avançadas e interpretações estruturais.",
            "metrics_focus": "Índices de desigualdade e dominação",
            "interpretation_style": "Técnico e detalhado",
            "appropriation_label": "Taxa de Apropriação Técnica",
            "density_label": "Densidade Simbólica"
        }
    }
    
    return labels[mode_key]


def sidebar_controls():
    with st.sidebar:
        st.header("⚙️ Controle de Ingestão")
        query = st.text_input("Query GitHub", "language:python")
        pages = st.slider("Páginas", 1, 5, 2)
        sort = st.selectbox("Ordenar por", ["stars", "forks", "updated"])
        mode = st.selectbox("Modo de Interpretação", ["Modo Exploratório", "Modo Analítico"])
        debug_mode = st.checkbox("Modo Debug Analítico", value=False)
        st.caption("A UI não processa dados — apenas solicita ao backend.")
    return query, pages, sort, mode, debug_mode


def render_header():
    st.title("📊 Observatório do Trabalho Digital")
    st.caption("Interface de leitura da infraestrutura do GitHub como sistema de produção simbólica e material.")
    
    # Badge de status de processamento no topo
    st.markdown("""
    <div style="position: fixed; top: 10px; right: 10px; z-index: 1000;">
        <span style="background-color: #238636; color: white; padding: 4px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 700;">
            ✅ Coleta total realizada sem interrupções por rate limit
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_overview(df: pd.DataFrame, mode: str, analysis: AnalysisResult, rate_limited: bool = False):
    mode_labels = get_mode_labels(mode)
    
    st.markdown(f"## {mode_labels['title']} ⓘ")
    with st.popover("Sobre esta análise"):
        st.markdown("""
        **Baseado em heurísticas computacionais:** Esta análise combina visibilidade social (stars) 
        com reuso técnico (forks) para identificar padrões de distribuição de poder na rede.
        """)
    st.markdown(mode_labels['description'])
    
    # Cartão de status de processamento
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Registros Processados", len(df))
    
    with col2:
        total_stars = df["stars"].sum() if not df.empty else 0
        st.metric("⭐ Total de Stars", f"{total_stars:,.0f}")
    
    with col3:
        total_forks = df["forks"].sum() if not df.empty else 0
        st.metric("🔗 Total de Forks", f"{total_forks:,.0f}")
    
    with col4:
        if rate_limited:
            st.metric("⚠️ Rate Limited", "Sim")
        else:
            st.metric("✅ Taxa Limite", "Normal")
    
    col1, col2 = st.columns(2)
    name, value, rank_label = get_top_hegemonic_repo(df)

    # Detectar se é uma Awesome-List/Curadoria
    awesome_keywords = ["awesome", "curated", "list"]
    is_awesome = False
    awesome_icon = ""
    if name:
        name_lower = name.lower()
        for kw in awesome_keywords:
            if kw in name_lower:
                is_awesome = True
                break
    if is_awesome:
        awesome_icon = "<span style='font-size:1.2em;' title='Curadoria/Awesome-List'>📚</span> "

    with col1:
        st.markdown(f"""
        <div class="critico-card">
            <span class="badge-status">Hegemonia Detectada</span>
            <h2 style="color:white; margin:10px 0;">{awesome_icon}{name}</h2>
            <p style="color:#8b949e;">Índice de Hegemonia: {value:.2f}</p>
            <p style="color:#8b949e;">{rank_label}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.metric(mode_labels["appropriation_label"], f"{df['appropriation_rate'].mean():.2%}")
        st.metric(mode_labels["density_label"], f"{df['symbolic_density'].mean():.2f}")

    # Glossário Dinâmico
    with st.expander("📚 Glossário de Conceitos"):
        st.markdown("""
        **Capital Digital:** Acúmulo de visibilidade e influência na rede GitHub, medido por stars e forks.
        
        **Hegemonia Computada:** Concentração de poder simbólico em repositórios específicos, calculada 
        através de algoritmos que combinam métricas de popularidade e impacto técnico.
        
        **Coeficiente de Gini:** Medida de desigualdade na distribuição de recursos (0 = igualdade perfeita, 1 = desigualdade máxima).
        """)

    # Exibir análise interpretativa
    st.markdown("## 🧠 Interpretação Analítica ⓘ")
    with st.popover("Sobre as interpretações"):
        st.markdown("""
        **Baseado em heurísticas:** As interpretações são geradas por algoritmos que analisam 
        distribuições estatísticas e padrões de concentração, não representando verdades absolutas.
        """)
    st.info(analysis.interpretation['summary'])
    st.caption("⚠️ As interpretações são baseadas em heurísticas computacionais e não representam verdades absolutas.")


def render_data_table(df: pd.DataFrame):
    st.markdown("## 📊 Repositórios")
    st.dataframe(
        df[["name", "stars", "forks", "appropriation_rate", "symbolic_density"]],
        width='stretch'
    )


def render_hegemony(heg: pd.DataFrame):
    st.markdown("## 🧠 Hegemonia Computada ⓘ")
    with st.popover("Sobre hegemonia computada"):
        st.markdown("""
        **Baseado em algoritmos de concentração:** Esta tabela identifica repositórios com 
        maior influência combinada de visibilidade e reuso técnico na rede.
        """)
    
    if heg is not None and not heg.empty:
        # Preparar colunas configuráveis
        column_config = {}
        
        # Adicionar coluna de progresso para hegemony_index se existir
        if "hegemony_index" in heg.columns:
            max_hegemony = float(heg["hegemony_index"].max()) if heg["hegemony_index"].max() > 0 else 1.0
            column_config["hegemony_index"] = st.column_config.ProgressColumn(
                "Índice de Hegemonia",
                help="Grau de dominação do repositório na rede (0.0 a 1.0)",
                format="%.3f",
                min_value=0.0,
                max_value=max_hegemony
            )
        
        # Adicionar coluna de progresso para hegemony_norm se existir
        if "hegemony_norm" in heg.columns:
            column_config["hegemony_norm"] = st.column_config.ProgressColumn(
                "Hegemonia Normalizada",
                help="Índice de hegemonia normalizado (0.0 a 1.0)",
                format="%.3f",
                min_value=0.0,
                max_value=1.0
            )
        
        # Aplicar Styler para background gradient opcional
        styled_heg = heg.style.background_gradient(
            subset=[col for col in heg.columns if col in ["hegemony_index", "hegemony_norm", "stars", "forks"]],
            cmap="RdYlGn_r",
            vmin=0
        ).format(precision=2)
        
        st.dataframe(
            styled_heg,
            column_config=column_config if column_config else None,
            width='stretch',
            hide_index=False
        )
    else:
        st.info("Dados de hegemonia não disponíveis")


def render_reflexivity(storage_info: Union[StorageInfo, Dict[str, Any]]):
    """
    Renderiza informações do storage layer de forma puramente passiva.

    Args:
        storage_info: Dados StorageInfo ou dict prontos para renderização
    """
    # Converter dict para StorageInfo se necessário (compatibilidade)
    if isinstance(storage_info, dict):
        storage_info = StorageInfo(**storage_info)
    
    # Abas para separar informações técnicas
    tab1, tab2 = st.tabs(["📊 Dashboard", "⚙️ Configurações & Metadados"])
    
    with tab1:
        st.markdown("## ⚖️ Interpretação")
        st.info(
            "Stars representam visibilidade social; forks representam reuso técnico. "
            "A interface não interpreta valor absoluto, apenas distribuições relativas."
        )
        st.caption(
            "UI layer: responsável apenas pela visualização. "
            "Toda lógica reside em infrastructure, services e core."
        )
        
        # Indicador de saúde do storage visível no dashboard
        if storage_info.total_sources > 0:
            health_percentage = storage_info.health_percentage
            health_text = storage_info.health_text
            st.progress(health_percentage / 100, text=health_text)
    
    with tab2:
        st.markdown("## 💾 Storage Layer (Detalhes Técnicos)")
        
        # Backend e diretório
        st.write(f"**Backend:** {storage_info.backend}")
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

        # Disponibilidade das fontes principais
        st.markdown("**Disponibilidade:**")
        availability = storage_info.availability or {}
        if availability:
            for name, available in availability.items():
                status_icon = "✅" if available else "❌"
                status_text = "Disponível" if available else "Indisponível"
                st.write(f"{status_icon} **{name}**: {status_text}")
        else:
            st.write("*Sem informações de disponibilidade*")

    # Informações sobre storage
    with st.expander("💾 Storage Layer"):
        # Backend e diretório
        st.write(f"**Backend:** {storage_info.backend}")
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

        # Disponibilidade das fontes principais
        st.markdown("**Disponibilidade:**")
        availability = storage_info.availability or {}
        if availability:
            for name, available in availability.items():
                status_icon = "✅" if available else "❌"
                status_text = "Disponível" if available else "Indisponível"
                st.write(f"{status_icon} **{name}**: {status_text}")
        else:
            st.write("*Sem informações de disponibilidade*")

        # Métricas de saúde do storage com barra formatada corretamente
        if storage_info.total_sources > 0:
            health_percentage = storage_info.health_percentage
            health_text = storage_info.health_text
            st.progress(health_percentage / 100, text=health_text)




def render_inequality_section(df: pd.DataFrame, analysis: AnalysisResult, debug_mode: bool = False):
    st.markdown("## 📈 Análise de Desigualdade ⓘ")
    with st.popover("Sobre a análise de desigualdade"):
        st.markdown("""
        **Baseado em distribuição de poder:** Esta seção analisa como recursos (stars, forks) 
        estão distribuídos entre repositórios, identificando concentrações e desigualdades.
        """)
    
    # Modo debug: mostrar distribuição bruta
    if debug_mode:
        st.markdown("### 🔍 Distribuição Bruta (Debug)")
        st.dataframe(df[["name", "stars", "forks"]].head(20), width='stretch')
        fig_hist = px.histogram(df, x="stars", title="Histograma de Estrelas (Bruto)")
        st.plotly_chart(fig_hist, width='stretch')
    
    # Mostrar tamanho da amostra (OBRIGATÓRIO)
    n_total = len(df)
    st.metric("Tamanho da Amostra (N)", n_total)
    
    # Indicador de confiança baseado no contrato
    confidence_score = analysis.confidence
    st.progress(confidence_score, text=f"Confiança Analítica: {confidence_score:.1%}")
    
    # Alertas visuais baseados nos metadados
    if analysis.metadata.get('sample_size', 0) < 30:
        st.warning("⚠️ Amostra pequena - Interpretações limitadas")
    if "viés" in analysis.interpretation.get('sampling_bias', '').lower() or "elitizado" in analysis.interpretation.get('sampling_bias', '').lower():
        st.warning("⚠️ Viés de coleta detectado")
    
    # N por segmento com cores semânticas
    segment_analysis = analysis.interpretation.get('segment_analysis', {})
    if segment_analysis:
        seg_cols = st.columns(3)
        low_count = segment_analysis.get("low_count", 0)
        mid_count = segment_analysis.get("mid_count", 0)
        top_count = segment_analysis.get("top_count", 0)
        
        with seg_cols[0]:
            color = "#58a6ff" if low_count > 0 else "#8b949e"  # Azul para equilíbrio, cinza para zero
            st.markdown(f"<div style='color: {color}; font-weight: bold;'>N Low: {low_count}</div>", unsafe_allow_html=True)
        with seg_cols[1]:
            color = "#58a6ff" if mid_count > 0 else "#8b949e"
            st.markdown(f"<div style='color: {color}; font-weight: bold;'>N Mid: {mid_count}</div>", unsafe_allow_html=True)
        with seg_cols[2]:
            color = "#f85149" if top_count > 0 else "#8b949e"  # Vermelho para alta concentração
            st.markdown(f"<div style='color: {color}; font-weight: bold;'>N Top: {top_count}</div>", unsafe_allow_html=True)
    
    # Métricas principais em linha
    col1, col2, col3 = st.columns(3)
    with col1:
        gini = analysis.interpretation.get('gini_coefficient')
        if gini is not None:
            st.metric("Coeficiente de Gini", f"{gini:.3f}")
            # Nota de RH sobre barreiras de entrada
            if gini > 0.6:
                st.caption("🔎 Um Gini alto pode indicar barreiras de entrada para novos talentos ou projetos menores.")
    with col2:
        top10 = analysis.interpretation.get('top10_concentration')
        if top10 is not None:
            st.metric("Top 10% concentração", f"{top10:.2%}")
    with col3:
        dom_index = analysis.interpretation.get('domination_index')
        if dom_index is not None:
            st.metric("Índice de Dominação", f"{dom_index:.3f}")

    # Classificações
    inequality_level = analysis.interpretation.get('inequality_level', 'Indefinida')
    domination_level = analysis.interpretation.get('domination_level', 'Indefinida')
    if analysis.interpretation.get('gini_coefficient') is not None:
        st.info(f"⚖️ Desigualdade: **{inequality_level}** | 🏛️ Dominação: **{domination_level}**")

    # Gráfico da Curva de Lorenz e Interpretação Analítica lado a lado
    if not df.empty and "stars" in df.columns:
        col_lorenz, col_interp = st.columns([1, 1])
        with col_lorenz:
            st.markdown("### Curva de Lorenz")
            from core.metrics import curva_lorenz
            x_lorenz, y_lorenz = curva_lorenz(df["stars"])
            fig_lorenz = go.Figure()
            fig_lorenz.add_trace(go.Scatter(x=x_lorenz, y=y_lorenz, mode='lines', name='Distribuição Real'))
            fig_lorenz.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Igualdade Perfeita', line=dict(dash='dash')))
            fig_lorenz.update_layout(
                title="Curva de Lorenz - Distribuição de Visibilidade",
                xaxis_title="Percentual Acumulado de Repositórios",
                yaxis_title="Percentual Acumulado de Estrelas",
                legend_title_text="Legenda"
            )
            st.plotly_chart(fig_lorenz, use_container_width=True)
        with col_interp:
            st.markdown("### Interpretação Analítica")
            st.info(analysis.interpretation['summary'])

        # Gráfico de Pareto e Log-Log abaixo
        col_pareto, col_loglog = st.columns([1, 1])
        with col_pareto:
            st.markdown("### Gráfico de Pareto")
            df_sorted = df.sort_values("stars", ascending=False).head(20)  # Top 20 para legibilidade
            fig_pareto = go.Figure()
            fig_pareto.add_trace(go.Bar(x=df_sorted["name"], y=df_sorted["stars"], name="Estrelas"))
            cumulative = df_sorted["stars"].cumsum() / df_sorted["stars"].sum() * 100
            fig_pareto.add_trace(go.Scatter(x=df_sorted["name"], y=cumulative, mode='lines+markers', name='Acumulado (%)', yaxis='y2'))
            fig_pareto.update_layout(
                title="Gráfico de Pareto - Concentração de Estrelas",
                xaxis_title="Repositórios",
                yaxis=dict(title="Estrelas"),
                yaxis2=dict(title="Percentual Acumulado de Estrelas", overlaying='y', side='right'),
                legend_title_text="Legenda",
                showlegend=True
            )
            st.plotly_chart(fig_pareto, use_container_width=True)
        with col_loglog:
            st.markdown("""
            <div style='display: flex; align-items: center; gap: 0.5em;'>
                <span style='background: #f85149; color: white; padding: 2px 10px; border-radius: 8px; font-size: 1em; font-weight: bold;'>Destaque</span>
                <span style='font-size:1.2em;'>📈</span>
                <span style='font-size:1em; color:#f85149; font-weight:bold;'>Distribuição Log-Log</span>
            </div>
            <span style='font-size:0.95em; color:#8b949e;'>Esta visualização aplica uma transformação logarítmica a ambos os eixos para avaliar a proporcionalidade na distribuição de visibilidade. Ela permite testar visualmente a aderência dos dados a modelos de escala livre (como a Lei de Zipf ou distribuições de Pareto), facilitando a identificação do coeficiente de decaimento da atenção na cauda do ecossistema.</span>
            """, unsafe_allow_html=True)
            ranks = range(1, len(df) + 1)
            fig_loglog = px.scatter(x=ranks, y=df["stars"].sort_values(ascending=False), log_x=True, log_y=True)
            fig_loglog.update_layout(title="Distribuição Log-Log - Ranking vs. Estrelas", xaxis_title="Ranking", yaxis_title="Estrelas", plot_bgcolor="#fff0f0")
            st.plotly_chart(fig_loglog, use_container_width=True)

        # Novo gráfico: Queda de Visibilidade por Ranking
        st.markdown("### Queda de Visibilidade por Ranking")
        plot_rank_decay(df)


def render_empty(message: str):
    st.warning(message)


def plot_rank_decay(df: pd.DataFrame):
    """
    Mostra a queda de visibilidade por ranking (tipo curva de elite).
    """
    import plotly.express as px
    import numpy as np

    if df.empty or "stars" not in df.columns:
        return

    df_sorted = df.sort_values(by="stars", ascending=False).copy()
    df_sorted["rank"] = np.arange(1, len(df_sorted) + 1)

    fig = px.line(
        df_sorted.head(50),
        x="rank",
        y="stars",
        title="Queda de Visibilidade por Ranking"
    )

    st.plotly_chart(fig, width='stretch')


class GitHubAnalyticsUI:
    """
    Classe principal da UI - renderização pura, sem lógica de negócio.
    
    Recebe apenas AnalysisResult como contrato entre camadas.
    Não interpreta, não calcula, não infere - apenas renderiza.
    """
    
    def __init__(
        self,
        pipeline_service,
        interpretation_service,
        storage_service=None,
        storage_inspection_service=None,
        settings=None
    ):
        """
        Inicializa a UI com dependências injetadas.
        
        Args:
            pipeline_service: Serviço de pipeline para coleta de dados
            interpretation_service: Serviço de interpretação
            storage_service: Serviço de armazenamento (fallback)
            storage_inspection_service: Serviço de inspeção de storage
            settings: Configurações da aplicação
        """
        self.pipeline_service = pipeline_service
        self.interpretation_service = interpretation_service
        self.storage_service = storage_service
        self.storage_inspection_service = storage_inspection_service
        self.settings = settings
    
    def run(self):
        """Executa a aplicação Streamlit."""
        configure_page()
        apply_theme()
        
        # Controles da sidebar
        query, pages, sort, mode, debug_mode = sidebar_controls()
        render_header()
        
        # Status visual durante a coleta
        with st.status("🔄 Coletando dados do ecossistema GitHub...", expanded=True) as status:
            st.write("📡 Buscando repositórios...")
            
            # Coletar dados via pipeline service
            result = self.pipeline_service.ingest_repositories(
                query=query, 
                pages=pages, 
                sort=sort, 
                use_cache=True
            )
            
            st.write("✅ Repositórios coletados com sucesso")
            st.write("🔨 Normalizando e validando dados...")
            
            df = result["data"]
            heg = result["hegemony"]
            rate_limited = result["rate_limited"]
            
            if df.empty:
                status.update(label="❌ Nenhum dado disponível", state="error", expanded=False)
                render_empty("Sem dados disponíveis para este recorte.")
                st.stop()
            
            st.write("📊 Calculando métricas...")
            
            # Calcular Gini
            from core.metrics import gini
            gini_value = gini(df["stars"]) if not df.empty else None
            
            st.write("🧠 Gerando interpretações analíticas...")
            
            # Criar AnalysisResult via interpretation service
            analysis = self.interpretation_service.create_analysis_result(df, heg, gini_value)
            
            st.write("💾 Carregando informações de storage...")
            
            # Capturar informações de storage para renderização
            storage_info = self._load_storage_info()
            
            status.update(label="✅ Ingestão completa! Renderizando dashboard...", state="complete", expanded=False)
        
        # Renderizar usando apenas o contrato AnalysisResult
        self._render_dashboard(df, heg, mode, analysis, rate_limited, debug_mode, storage_info)
    
    def _load_storage_info(self) -> StorageInfo:
        if self.storage_inspection_service is not None:
            return self.storage_inspection_service.inspect()
        if self.storage_service is not None:
            return StorageInspectionService(self.storage_service).inspect()
        raise RuntimeError("Storage inspection service is not available")

    def _render_dashboard(self, df: pd.DataFrame, heg: pd.DataFrame, mode: str, analysis: AnalysisResult, 
                         rate_limited: bool, debug_mode: bool, storage_info: StorageInfo):
        """
        Renderiza o dashboard completo usando apenas AnalysisResult.
        
        Args:
            df: DataFrame com dados brutos (apenas para exibição)
            mode: Modo de visualização
            analysis: Contrato estruturado com métricas, interpretação e confiança
            rate_limited: Flag de rate limit
            debug_mode: Flag de modo debug
        """
        render_overview(df, mode, analysis, rate_limited)
        render_data_table(df)
        render_hegemony(heg)
        render_inequality_section(df, analysis, debug_mode)
        render_reflexivity(storage_info)
