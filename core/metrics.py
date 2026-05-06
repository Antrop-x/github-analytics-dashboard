from dataclasses import dataclass
from typing import Optional
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
# MÉTRICAS DE DESIGUALDADE
# ==============================
def gini(values: pd.Series) -> float:
    """
    Calcula o coeficiente de Gini para medir desigualdade na distribuição de valores.
    Remove valores negativos, trata soma zero e ordena para cálculo clássico.
    """
    import numpy as np

    array = np.array(values, dtype=float)
    array = array[~np.isnan(array)]
    array = array[array >= 0]

    if len(array) < 2:
        return np.nan  # Gini indefinido para amostras unitárias

    if array.sum() == 0:
        return 0.0

    array = np.sort(array)
    n = len(array)
    index = np.arange(1, n + 1)

    g = (2 * np.sum(index * array)) / (n * np.sum(array)) - (n + 1) / n

    # 🔒 CLAMP (garantia matemática)
    return max(0.0, min(1.0, float(g)))


def curva_lorenz(values: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """
    Gera pontos para a curva de Lorenz: proporção acumulada de valores vs. proporção acumulada de população.
    Retorna tuplas (x, y) para plotagem.
    """
    if values.empty:
        return np.array([0.0, 1.0]), np.array([0.0, 1.0])
    clean_values = values[values >= 0].values
    if len(clean_values) == 0:
        return np.array([0.0, 1.0]), np.array([0.0, 1.0])
    # Ordenar
    sorted_values = np.sort(clean_values)
    n = len(sorted_values)
    cumsum = np.cumsum(sorted_values)
    total = cumsum[-1]
    if total == 0:
        return np.array([0.0, 1.0]), np.array([0.0, 1.0])
    # Proporções
    x = np.linspace(0, 1, n + 1)
    y = np.concatenate([[0], cumsum / total])
    return x, y
# ==============================
# MÉTRICAS DE CONCENTRAÇÃO DE ELITE
# ==============================
def top_concentration(df: pd.DataFrame, col: str = "stars", top: float = 0.1) -> float:
    """
    Calcula a concentração de visibilidade nos top X% dos repositórios.
    """
    if df.empty or col not in df.columns:
        return 0.0
    df_sorted = df.sort_values(by=col, ascending=False)
    n = len(df_sorted)

    cutoff = max(1, int(n * top))
    top_sum = df_sorted[col].head(cutoff).sum()
    total = df_sorted[col].sum()

    return top_sum / total if total > 0 else 0.0


def domination_index(gini: float, top10: float, corr: Optional[float] = None) -> float:
    """
    Calcula índice unificado de dominação combinando:
    - Desigualdade (Gini): peso 0.4
    - Concentração de elite (Top 10%): peso 0.4
    - Correlação estrutural (hegemonia-visibilidade): peso 0.2
    
    Retorna valor entre 0.0 (equilibrado) e 1.0 (altamente dominado).
    """
    import numpy as np
    
    # Normalizar Gini [0, 1]
    gini_normalized = float(gini) if gini is not None else 0.0
    
    # Normalizar Top 10% [0, 1]
    top10_normalized = float(top10) if top10 is not None else 0.0
    
    # Normalizar correlação [0, 1]
    if corr is not None and not np.isnan(corr):
        # Correlação varia em [-1, 1], converter para [0, 1]
        corr_normalized = max(0.0, float(corr))  # Se negativa, vale 0
    else:
        corr_normalized = 0.0
    
    # Combinação ponderada
    index = (gini_normalized * 0.4) + (top10_normalized * 0.4) + (corr_normalized * 0.2)
    
    # Clamp final
    return max(0.0, min(1.0, index))


def segment_repositories(df: pd.DataFrame, col: str = "stars") -> pd.DataFrame:
    """
    Segmenta repositórios em três níveis baseado na distribuição de estrelas:
    - low: cauda longa (menor 70% dos repositórios)
    - mid: médio (próximos 20%)
    - top: elite (top 10%)
    
    Retorna DataFrame com coluna 'segment' adicionada.
    """
    if df.empty or col not in df.columns:
        return df.copy()
    
    df_segmented = df.copy()
    n = len(df_segmented)
    
    # Calcular quantis
    quantiles = df_segmented[col].quantile([0.7, 0.9])
    
    # Função de segmentação
    def assign_segment(stars):
        if stars <= quantiles[0.7]:
            return "low"
        elif stars <= quantiles[0.9]:
            return "mid"
        else:
            return "top"
    
    df_segmented["segment"] = df_segmented[col].apply(assign_segment)
    return df_segmented


def analyze_segments(df: pd.DataFrame) -> dict:
    """
    Análise estatística por segmento de repositórios.
    Retorna métricas agregadas por segmento.
    """
    if df.empty or "segment" not in df.columns:
        return {}
    
    analysis = {}
    for segment in ["low", "mid", "top"]:
        segment_data = df[df["segment"] == segment]
        if not segment_data.empty:
            analysis[segment] = {
                "count": len(segment_data),
                "mean_stars": segment_data["stars"].mean(),
                "median_stars": segment_data["stars"].median(),
                "std_stars": segment_data["stars"].std(),
                "total_stars": segment_data["stars"].sum(),
                "percentage": len(segment_data) / len(df) * 100
            }
    
    return analysis
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