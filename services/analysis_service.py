from dataclasses import dataclass
from typing import Optional
import pandas as pd
import numpy as np
from core.metrics import top_concentration, domination_index, segment_repositories, analyze_segments


@dataclass
class InterpretationResult:
    """
    Resultado estruturado da interpretação analítica do dataset.
    """
    hegemonic_repo: Optional[str]
    hegemonic_score: Optional[float]
    hegemony_type: str
    appropriation_level: str
    density_level: str
    density_dispersion: Optional[float]
    gini_coefficient: Optional[float]
    inequality_level: str
    top10_concentration: Optional[float]
    domination_index: Optional[float]
    domination_level: str
    sampling_bias: str
    segment_analysis: dict
    power_structure_insights: str
    summary: str


def classify_hegemony_type(stars: float, forks: float) -> str:
    """
    Classifica o tipo de hegemonia baseado na proporção forks/stars.
    Usa relação proporcional para evitar viés por repositórios grandes.
    """
    if pd.isna(stars) or pd.isna(forks) or (stars == 0 and forks == 0):
        return "Indefinida"
    if stars == 0:
        return "Técnica"

    ratio = forks / stars
    if ratio < 0.35:
        return "Simbólica"
    elif ratio > 2.5:
        return "Técnica"
    else:
        return "Híbrida"


def classify_appropriation_level(avg_appropriation: float) -> str:
    """
    Classifica o nível de apropriação baseado na taxa média.
    - 'Baixo': < 0.1
    - 'Médio': 0.1 - 0.3
    - 'Alto': > 0.3
    """
    if pd.isna(avg_appropriation):
        return "Indefinido"
    if avg_appropriation < 0.1:
        return "Baixo"
    elif avg_appropriation <= 0.3:
        return "Médio"
    else:
        return "Alto"


def classify_density_level(avg_density: float) -> str:
    """
    Classifica o nível de densidade simbólica baseado na média.
    - 'Esparsa': < 0.2
    - 'Moderada': 0.2 - 0.5
    - 'Densa': > 0.5
    """
    if pd.isna(avg_density):
        return "Indefinida"
    if avg_density < 0.2:
        return "Esparsa"
    elif avg_density <= 0.5:
        return "Moderada"
    else:
        return "Densa"


def interpret_inequality(gini_value: float) -> str:
    """
    Interpreta o coeficiente de Gini em categorias qualitativas para desigualdade de visibilidade.
    - 'Baixa': distribuição homogênea
    - 'Moderada': desigualdade presente
    - 'Alta': forte concentração
    """
    if pd.isna(gini_value):
        return "Indefinida"
    if gini_value < 0.3:
        return "Baixa"
    elif gini_value <= 0.6:
        return "Moderada"
    else:
        return "Alta"


def interpret_power_structure(gini: float, top10: float, corr: Optional[float]) -> str:
    """
    Interpreta a estrutura de poder baseada em Gini, concentração do top 10% e correlação hegemonia-visibilidade.
    """
    insights = []

    # Estrutura de concentração
    if gini > 0.7 and top10 > 0.6:
        insights.append("Estrutura altamente concentrada: uma elite dominante controla a maior parte da visibilidade.")
    elif gini > 0.5:
        insights.append("Estrutura moderadamente concentrada, com presença de polos dominantes.")
    else:
        insights.append("Estrutura relativamente distribuída, sem domínio claro.")

    # Relação hegemonia × visibilidade
    if corr is not None:
        if corr > 0.7:
            insights.append("A hegemonia é fortemente dependente da visibilidade.")
        elif corr > 0.3:
            insights.append("A hegemonia possui dependência parcial da visibilidade.")
        else:
            insights.append("A hegemonia emerge por fatores além da visibilidade.")

    return " ".join(insights)


def interpret_domination(index: float) -> str:
    """
    Classifica o Índice de Dominação em categorias interpretáveis.
    - 'Alta': index > 0.65 → sistema dominado por elite
    - 'Moderada': 0.35 ≤ index ≤ 0.65 → dominância moderada
    - 'Baixa': index < 0.35 → distribuição equilibrada
    """
    if pd.isna(index):
        return "Indefinida"
    if index > 0.65:
        return "Alta"
    elif index >= 0.35:
        return "Moderada"
    else:
        return "Baixa"


def interpret_sampling_bias(df: pd.DataFrame) -> str:
    """
    Detecta viés de amostragem baseado na distribuição por segmentos.
    """
    if "segment" not in df.columns:
        return ""

    if df["segment"].nunique() < 3:
        return "A amostra não cobre todos os níveis do ecossistema"

    counts = df["segment"].value_counts(normalize=True)

    low = counts.get("low", 0)
    mid = counts.get("mid", 0)
    top = counts.get("top", 0)

    if low < 0.2:
        return "Sub-representação da cauda longa detectada, limitando a análise da base do ecossistema."

    if top > 0.5:
        return "Predominância de repositórios de alta visibilidade, sugerindo viés elitizado na amostra."

    if abs(low - mid) < 0.1 and abs(mid - top) < 0.1:
        return "Distribuição aproximadamente uniforme entre segmentos — possível amostragem artificial."

    return "Distribuição heterogênea com representação relativa dos três níveis do ecossistema."


def safe_interpretation(df: pd.DataFrame) -> str:
    """
    Fallback interpretativo para amostras pequenas.
    """
    if len(df) < 10:
        return "Dados insuficientes para inferência estrutural."
    return ""


def get_dispersion_description(std_value: float) -> str:
    if pd.isna(std_value):
        return "dispersão indefinida"
    if std_value < 0.08:
        return "alta concentração simbólica"
    if std_value < 0.22:
        return "difusão simbólica moderada"
    return "ampla dispersão simbólica"


def generate_summary(result: InterpretationResult) -> str:
    """
    Gera uma síntese narrativa baseada nos níveis identificados.
    """
    if result.hegemonic_repo is None:
        return "Dados insuficientes para interpretação. Verifique a qualidade dos dados de entrada."

    hegemony_desc = {
        "Simbólica": "com predominância simbólica, onde visibilidade supera reuso técnico",
        "Técnica": "com predominância técnica, onde reuso prático se impõe",
        "Híbrida": "como um nó híbrido, com acoplamento entre visibilidade e reuso",
        "Indefinida": "indefinida devido a dados incompletos"
    }.get(result.hegemony_type, "desconhecida")

    appropriation_desc = {
        "Baixo": "baixa apropriação técnica",
        "Médio": "apropriação técnica moderada",
        "Alto": "apropriação técnica elevada",
        "Indefinido": "apropriação indefinida"
    }.get(result.appropriation_level, "desconhecido")

    density_desc = {
        "Esparsa": "baixa densidade simbólica",
        "Moderada": "densidade simbólica moderada",
        "Densa": "densidade simbólica alta",
        "Indefinida": "densidade simbólica indefinida"
    }.get(result.density_level, "desconhecida")

    inequality_desc = {
        "Baixa": "baixa desigualdade na distribuição de visibilidade",
        "Moderada": "desigualdade moderada na distribuição de visibilidade",
        "Alta": "alta desigualdade na distribuição de visibilidade",
        "Indefinida": "desigualdade indefinida"
    }.get(result.inequality_level, "desconhecida")

    dispersion_value = result.density_dispersion if result.density_dispersion is not None else float('nan')
    dispersion_desc = get_dispersion_description(dispersion_value)

    gini_str = f"{result.gini_coefficient:.3f}" if result.gini_coefficient is not None else "N/A"
    dom_str = f"{result.domination_index:.3f}" if result.domination_index is not None else "N/A"
    score_str = f"{result.hegemonic_score:.2f}" if result.hegemonic_score is not None else "N/A"

    return (
        f"O repositório hegemônico '{result.hegemonic_repo}' (score: {score_str}) "
        f"tem uma hegemonia {hegemony_desc}, com {appropriation_desc} e {density_desc}. "
        f"A desigualdade de visibilidade é {inequality_desc} (Gini: {gini_str}). "
        f"O índice de dominação é {result.domination_level.lower()} ({dom_str}). "
        f"A amostra revela {dispersion_desc}. "
        f"{result.sampling_bias} "
        f"{result.power_structure_insights} "
        "Essa interpretação usa proxies heurísticos e não representa verdade objetiva."
    )


def interpret_dataset(df_metrics: pd.DataFrame, df_hegemony: pd.DataFrame, gini_value: Optional[float] = None) -> InterpretationResult:
    """
    Função principal de interpretação: valida entradas, extrai métricas,
    aplica classificações e gera síntese.
    """
    # Validação de entrada
    if df_metrics is None or df_metrics.empty or df_hegemony is None or df_hegemony.empty:
        return InterpretationResult(
            hegemonic_repo=None,
            hegemonic_score=None,
            hegemony_type="Indefinida",
            appropriation_level="Indefinido",
            density_level="Indefinida",
            density_dispersion=None,
            gini_coefficient=None,
            inequality_level="Indefinida",
            top10_concentration=None,
            domination_index=None,
            domination_level="Indefinida",
            sampling_bias="",
            segment_analysis={},
            power_structure_insights="",
            summary="Dados insuficientes para interpretação. Verifique a qualidade dos dados de entrada."
        )

    # Bloquear análise com N pequeno
    if len(df_metrics) < 30:
        return InterpretationResult(
            hegemonic_repo=None,
            hegemonic_score=None,
            hegemony_type="Indefinida",
            appropriation_level="Indefinido",
            density_level="Indefinida",
            density_dispersion=None,
            gini_coefficient=None,
            inequality_level="Indefinida",
            top10_concentration=None,
            domination_index=None,
            domination_level="Indefinida",
            sampling_bias="Amostra estatisticamente insuficiente",
            segment_analysis={},
            power_structure_insights="",
            summary="Amostra estatisticamente insuficiente"
        )

    # Extração do repositório dominante
    if df_hegemony.empty:
        hegemonic_repo = None
        hegemonic_score = None
        hegemony_type = "Indefinida"
    else:
        top_heg = df_hegemony.iloc[0]
        hegemonic_repo = top_heg["name"]
        hegemonic_score = top_heg["hegemony_index"]
        hegemony_type = classify_hegemony_type(top_heg["stars"], top_heg["forks"])

    # Cálculo de métricas agregadas
    avg_appropriation = df_metrics["appropriation_rate"].mean()
    avg_density = df_metrics["symbolic_density"].mean()
    density_std = df_metrics["symbolic_density"].std(ddof=0)

    # Aplicação de classificações
    appropriation_level = classify_appropriation_level(avg_appropriation)
    density_level = classify_density_level(avg_density)

    # Interpretação de desigualdade
    inequality_level = interpret_inequality(gini_value) if gini_value is not None else "Indefinida"

    # Concentração do top 10%
    top10_concentration = top_concentration(df_metrics, col="stars", top=0.1) if not df_metrics.empty else None

    # Correlação hegemonia × visibilidade (usando log-transformação para dados heavy-tailed)
    corr = None
    corr_linear = None
    if not df_hegemony.empty and not df_metrics.empty and len(df_hegemony) > 1:
        try:
            # Correlação linear (original)
            if "hegemony_index" in df_hegemony.columns and len(df_hegemony) > 1:
                corr_linear = df_hegemony["hegemony_index"].corr(df_hegemony["stars"])
            
            # Correlação log-transformada (mais robusta para dados assimétricos)
            log_hegemony = np.log1p(df_hegemony["hegemony_index"].values)
            log_stars = np.log1p(df_hegemony["stars"].values)
            corr = float(np.corrcoef(log_hegemony, log_stars)[0, 1])
            if np.isnan(corr):
                corr = None
        except:
            corr = None

    # Interpretação da estrutura de poder
    power_structure_insights = interpret_power_structure(gini_value or 0.0, top10_concentration or 0.0, corr)

    # Cálculo do Índice de Dominação
    dom_index = domination_index(gini_value or 0.0, top10_concentration or 0.0, corr)
    dom_level = interpret_domination(dom_index)

    # Segmentação e análise de viés
    df_segmented = segment_repositories(df_metrics, col="stars")
    segment_analysis = analyze_segments(df_segmented)
    sampling_bias = interpret_sampling_bias(df_segmented)

    # Criação do resultado preliminar
    result = InterpretationResult(
        hegemonic_repo=hegemonic_repo,
        hegemonic_score=hegemonic_score,
        hegemony_type=hegemony_type,
        appropriation_level=appropriation_level,
        density_level=density_level,
        density_dispersion=density_std,
        gini_coefficient=gini_value,
        inequality_level=inequality_level,
        top10_concentration=top10_concentration,
        domination_index=dom_index,
        domination_level=dom_level,
        sampling_bias=sampling_bias,
        segment_analysis=segment_analysis,
        power_structure_insights=power_structure_insights,
        summary=""  # Será preenchido abaixo
    )

    # Geração da síntese
    safe_msg = safe_interpretation(df_metrics)
    if safe_msg:
        result.summary = safe_msg
    else:
        result.summary = generate_summary(result)

    return result