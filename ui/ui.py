import streamlit as st
import pandas as pd
from core.metrics import get_top_hegemonic_repo
from services.analysis_service import InterpretationResult


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


def sidebar_controls():
    with st.sidebar:
        st.header("⚙️ Controle de Ingestão")
        query = st.text_input("Query GitHub", "language:python")
        pages = st.slider("Páginas", 1, 5, 2)
        sort = st.selectbox("Ordenar por", ["stars", "forks", "updated"])
        mode = st.selectbox("Modo de Interpretação", ["Capital Digital", "Trabalho Colaborativo"])
        st.caption("A UI não processa dados — apenas solicita ao backend.")
    return query, pages, sort, mode


def render_header():
    st.title("📊 Observatório do Trabalho Digital")
    st.caption("Interface de leitura da infraestrutura do GitHub como sistema de produção simbólica e material.")


def render_overview(df: pd.DataFrame, mode: str, analysis: InterpretationResult, rate_limited: bool = False):
    labels = {
        "Capital Digital": {
            "m": "Taxa de Apropriação",
            "s": "Capital Simbólico",
            "f": "Trabalho Acumulado"
        },
        "Trabalho Colaborativo": {
            "m": "Intensidade de Uso",
            "s": "Visibilidade",
            "f": "Contribuições"
        }
    }[mode]

    st.markdown("## 📌 Visão Geral")
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
        st.metric(labels["m"], f"{df['appropriation_rate'].mean():.2%}")
        st.metric("Densidade Média", f"{df['symbolic_density'].mean():.2f}")

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


def render_empty(message: str):
    st.warning(message)
