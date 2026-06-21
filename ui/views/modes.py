"""
Mode configurations and labels for UI presentation
"""

MODE_MAP = {
    "Modo Exploratório": "exploratory",
    "Modo Analítico": "analytical"
}

LABELS = {
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


def get_mode_labels(mode: str) -> dict:
    """
    Mapeia o modo de UI para rótulos apropriados.
    
    Args:
        mode: Modo de interpretação (texto exibido)
    
    Returns:
        Dicionário com labels para o modo
    """
    mode_key = MODE_MAP.get(mode, "exploratory")
    return LABELS[mode_key]
