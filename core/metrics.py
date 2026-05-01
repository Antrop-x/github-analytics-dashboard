from dataclasses import dataclass
import pandas as pd
import numpy as np
# ==============================
# MODELO DE MÉTRICAS
# ==============================
@dataclass
class MetricsConfig:
    safe_division: bool = True


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """
    Divide séries numéricas de forma segura, preservando NaN e evitando infinito.
    """
    result = numerator / denominator
    result = result.replace([np.inf, -np.inf], np.nan)
    return result
# ==============================
# MÉTRICAS FUNDAMENTAIS
# ==============================
def compute_appropriation_rate(df: pd.DataFrame) -> pd.Series:
    """
    Proxy de reuso técnico em relação à visibilidade.
    forks / stars com tratamento de zero e NaN após a divisão.
    """
    if df.empty:
        return pd.Series(dtype=float)
    rates = safe_divide(df["forks"].astype(float), df["stars"].astype(float))
    return rates.fillna(0.0)
def compute_symbolic_density(df: pd.DataFrame) -> pd.Series:
    """
    Normalização de visibilidade relativa dentro da amostra.
    stars / max(stars)
    """
    if df.empty:
        return pd.Series(dtype=float)
    max_stars = df["stars"].max()
    if max_stars == 0:
        return pd.Series([0.0] * len(df))
    return safe_divide(df["stars"].astype(float), pd.Series(max_stars, index=df.index)).fillna(0.0)
# ==============================
# PIPELINE PRINCIPAL
# ==============================
def build_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas as métricas no dataframe de entrada.
    Camada pura: não faz I/O, não acessa API, não depende de UI.
    """
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["stars"] = df["stars"].fillna(0).astype(int)
    df["forks"] = df["forks"].fillna(0).astype(int)
    df["appropriation_rate"] = compute_appropriation_rate(df)
    df["symbolic_density"] = compute_symbolic_density(df)
    return df
# ==============================
# AGREGADOS ANALÍTICOS
# ==============================
def compute_hegemony_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Índice de hegemonia com valores absolutos e relativos.
    Inclui versão logarítmica, normalizada, ranking e percentil.
    """
    if df.empty:
        return pd.DataFrame()
    grouped = df.groupby("name", as_index=False).agg({
        "stars": "mean",
        "forks": "mean"
    })
    grouped["hegemony_index"] = grouped["stars"] + grouped["forks"]
    grouped["hegemony_index"] = grouped["hegemony_index"].fillna(0.0)
    grouped["hegemony_log"] = np.log1p(grouped["hegemony_index"])

    min_log = grouped["hegemony_log"].min()
    max_log = grouped["hegemony_log"].max()
    if max_log > min_log:
        grouped["hegemony_norm"] = (grouped["hegemony_log"] - min_log) / (max_log - min_log)
    else:
        grouped["hegemony_norm"] = 0.0

    grouped["hegemony_percentile"] = grouped["hegemony_index"].rank(pct=True, ascending=True) * 100
    grouped["hegemony_rank"] = grouped["hegemony_index"].rank(ascending=False, method="dense").astype(int)
    return grouped.sort_values("hegemony_index", ascending=False)


def get_top_hegemonic_repo(df: pd.DataFrame) -> tuple:
    """
    Retorna o repositório com maior índice de hegemonia e seu contexto relativo.
    """
    if df.empty:
        return None, None, None
    heg = compute_hegemony_index(df)
    if heg.empty:
        return None, None, None
    top_repo = heg.iloc[0]
    percentile = top_repo["hegemony_percentile"]
    rank_label = f"Top {max(1, int(np.ceil(100 - percentile)))}%"
    return top_repo["name"], top_repo["hegemony_index"], rank_label
# ==============================
# NORMALIZAÇÃO AVANÇADA
# ==============================
def normalize_zscore(series: pd.Series) -> pd.Series:
    """
    Z-score normalization para análises comparativas.
    """
    if series.empty:
        return series
    std = series.std()
    if std == 0 or np.isnan(std):
        return pd.Series([0] * len(series))
    return (series - series.mean()) / std
def enrich_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extensão analítica opcional do dataset.
    Inclui normalizações estatísticas.
    """
    if df.empty:
        return df
    df = df.copy()
    df["appropriation_z"] = normalize_zscore(safe_divide(df["forks"].astype(float), df["stars"].astype(float)).fillna(0.0))
    df["stars_z"] = normalize_zscore(df["stars"])
    df["forks_z"] = normalize_zscore(df["forks"])
    return df
# ==============================
# UTILITÁRIOS DE VALIDAÇÃO
# ==============================
def validate_input(df: pd.DataFrame) -> bool:
    """
    Valida estrutura mínima do dataset.
    """
    required_columns = {"name", "stars", "forks"}
    if df is None or df.empty:
        return False
    return required_columns.issubset(set(df.columns))