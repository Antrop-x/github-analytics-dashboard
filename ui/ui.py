import streamlit as st
import pandas as pd
from core.metrics import get_top_hegemonic_repo
from services.analysis_service import InterpretationResult
import plotly.graph_objects as go
import plotly.express as px
from core.metrics import top_concentration, analyze_segments


def configure_page():
    st.set_page_config(page_title="Observatório do Trabalho Digital", layout="wide")


def apply_theme():
    st.markdown("""
    <style>
        :root { --accent: #58a6ff; --bg-card: #0d1117; --border: #30363d; --text-dim: #8b949e; }
        .critico-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        .badge-status {
            background-color: #238636;
            color: white;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 0.7rem;
            font-weight: 700;
        }
        .section-title {
            margin-top: 2rem;
            font-size: 1.2rem;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)


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


def render_overview(df: pd.DataFrame, mode: str, analysis: InterpretationResult, rate_limited: bool = False):
    mode_labels = get_mode_labels(mode)
    
    st.markdown(f"## {mode_labels['title']}")
    st.markdown(mode_labels['description'])
    
    col1, col2 = st.columns(2)
    name, value, rank_label = get_top_hegemonic_repo(df)

    with col1:
        st.markdown(f"""
        <div class="critico-card">
            <span class="badge-status">Hegemonia Detectada</span>
            <h2 style="color:white; margin:10px 0;">{name}</h2>
            <p style="color:#8b949e;">Índice de Hegemonia: {value:.2f}</p>
            <p style="color:#8b949e;">{rank_label}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.metric(mode_labels["appropriation_label"], f"{df['appropriation_rate'].mean():.2%}")
        st.metric(mode_labels["density_label"], f"{df['symbolic_density'].mean():.2f}")

    # Aviso de rate limit / estado do pipeline
    if rate_limited:
        st.warning(
            "⚠️ Coleta parcial devido ao limite da API do GitHub. "
            "Os dados podem não representar toda a amostra."
        )
    else:
        st.success("Coleta total realizada sem interrupções por rate limit.")

    # Exibir análise interpretativa
    st.markdown("## 🧠 Interpretação Analítica")
    st.info(analysis.summary)
    st.caption("⚠️ As interpretações são baseadas em heurísticas computacionais e não representam verdades absolutas.")


def render_data_table(df: pd.DataFrame):
    st.markdown("## 📊 Repositórios")
    st.dataframe(
        df[["name", "stars", "forks", "appropriation_rate", "symbolic_density"]],
        width="stretch"
    )


def render_hegemony(heg: pd.DataFrame):
    st.markdown("## 🧠 Hegemonia Computada")
    st.dataframe(heg, width="stretch")


def render_reflexivity():
    st.markdown("## ⚖️ Interpretação")
    st.info(
        "Stars representam visibilidade social; forks representam reuso técnico. "
        "A interface não interpreta valor absoluto, apenas distribuições relativas."
    )
    st.caption(
        "UI layer: responsável apenas pela visualização. "
        "Toda lógica reside em infrastructure, services e core."
    )


def render_inequality_section(df: pd.DataFrame, analysis: InterpretationResult, debug_mode: bool = False):
    st.markdown("## 📈 Análise de Desigualdade")
    
    # Modo debug: mostrar distribuição bruta
    if debug_mode:
        st.markdown("### 🔍 Distribuição Bruta (Debug)")
        st.dataframe(df[["name", "stars", "forks"]].head(20), use_container_width=True)
        fig_hist = px.histogram(df, x="stars", title="Histograma de Estrelas (Bruto)")
        st.plotly_chart(fig_hist, width="stretch")
    
    # Mostrar tamanho da amostra (OBRIGATÓRIO)
    n_total = len(df)
    st.metric("Tamanho da Amostra (N)", n_total)
    
    # Indicador de confiança
    confidence_score = min(1, n_total / 100)
    st.progress(confidence_score, text=f"Confiança Analítica: {confidence_score:.1%}")
    
    # Alertas visuais
    if n_total < 30:
        st.warning("⚠️ Amostra pequena - Interpretações limitadas")
    if "viés" in analysis.sampling_bias.lower() or "elitizado" in analysis.sampling_bias.lower():
        st.warning("⚠️ Viés de coleta detectado")
    
    # N por segmento
    if analysis.segment_analysis:
        seg_cols = st.columns(3)
        with seg_cols[0]:
            st.metric("N Low", analysis.segment_analysis.get("low_count", 0))
        with seg_cols[1]:
            st.metric("N Mid", analysis.segment_analysis.get("mid_count", 0))
        with seg_cols[2]:
            st.metric("N Top", analysis.segment_analysis.get("top_count", 0))
    
    # Métricas principais em linha
    col1, col2, col3 = st.columns(3)
    with col1:
        if analysis.gini_coefficient is not None:
            st.metric("Coeficiente de Gini", f"{analysis.gini_coefficient:.3f}")
    with col2:
        if analysis.top10_concentration is not None:
            st.metric("Top 10% concentração", f"{analysis.top10_concentration:.2%}")
    with col3:
        if analysis.domination_index is not None:
            st.metric("Índice de Dominação", f"{analysis.domination_index:.3f}")
    
    # Classificações
    if analysis.gini_coefficient is not None:
        st.info(f"⚖️ Desigualdade: **{analysis.inequality_level}** | 🏛️ Dominação: **{analysis.domination_level}**")
    
    # Texto analítico
    st.markdown("### Interpretação")
    st.info(analysis.summary)
    
    # Gráficos
    if not df.empty and "stars" in df.columns:
        # Curva de Lorenz
        st.markdown("### Curva de Lorenz")
        from core.metrics import curva_lorenz
        x_lorenz, y_lorenz = curva_lorenz(df["stars"])
        fig_lorenz = go.Figure()
        fig_lorenz.add_trace(go.Scatter(x=x_lorenz, y=y_lorenz, mode='lines', name='Distribuição Real'))
        fig_lorenz.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Igualdade Perfeita', line=dict(dash='dash')))
        fig_lorenz.update_layout(title="Curva de Lorenz - Distribuição de Visibilidade", xaxis_title="Proporção da População", yaxis_title="Proporção das Estrelas")
        st.plotly_chart(fig_lorenz, width="stretch")
        
        # Gráfico de Pareto
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
            yaxis2=dict(title="Percentual Acumulado", overlaying='y', side='right'),
            showlegend=True
        )
        st.plotly_chart(fig_pareto, width="stretch")
        
        # Gráfico Log-Log
        st.markdown("### Distribuição Log-Log")
        ranks = range(1, len(df) + 1)
        fig_loglog = px.scatter(x=ranks, y=df["stars"].sort_values(ascending=False), log_x=True, log_y=True)
        fig_loglog.update_layout(title="Distribuição Log-Log - Ranking vs. Estrelas", xaxis_title="Ranking", yaxis_title="Estrelas")
        st.plotly_chart(fig_loglog, width="stretch")
        
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

    st.plotly_chart(fig, width="stretch")
