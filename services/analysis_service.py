from dataclasses import dataclass
from typing import Optional
import pandas as pd


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

    dispersion_value = result.density_dispersion if result.density_dispersion is not None else float('nan')
    dispersion_desc = get_dispersion_description(dispersion_value)

    return (
        f"O repositório hegemônico '{result.hegemonic_repo}' (score: {result.hegemonic_score:.2f}) "
        f"tem uma hegemonia {hegemony_desc}, com {appropriation_desc} e {density_desc}. "
        f"A amostra revela {dispersion_desc}. "
        "Essa interpretação usa proxies heurísticos e não representa verdade objetiva."
    )


def interpret_dataset(df_metrics: pd.DataFrame, df_hegemony: pd.DataFrame) -> InterpretationResult:
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
            summary="Dados insuficientes para interpretação. Verifique a qualidade dos dados de entrada."
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

    # Criação do resultado preliminar
    result = InterpretationResult(
        hegemonic_repo=hegemonic_repo,
        hegemonic_score=hegemonic_score,
        hegemony_type=hegemony_type,
        appropriation_level=appropriation_level,
        density_level=density_level,
        density_dispersion=density_std,
        summary=""  # Será preenchido abaixo
    )

    # Geração da síntese
    result.summary = generate_summary(result)

    return result