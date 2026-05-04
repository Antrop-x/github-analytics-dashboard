"""
UI Models - Dataclasses para tipagem de dados trafegados entre camadas
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class StorageInfo:
    """Informações de storage para renderização na UI"""
    backend: str
    directory: str
    sources: List[str] = field(default_factory=list)
    mock_sources: List[str] = field(default_factory=list)
    availability: Dict[str, bool] = field(default_factory=dict)
    force_mock: bool = False
    total_sources: int = 0
    available_sources: int = 0
    mock_fallback: bool = False

    @property
    def health_percentage(self) -> float:
        """Calcula percentual de saúde do storage"""
        if self.total_sources == 0:
            return 0.0
        return (self.available_sources / self.total_sources) * 100

    @property
    def health_text(self) -> str:
        """Texto formatado de saúde do storage"""
        return f"Saúde do storage: {self.health_percentage:.1f}%"


@dataclass
class MetricCard:
    """Componente visual de métrica"""
    label: str
    value: Any
    icon: str = "📊"
    unit: str = ""
    context: str = ""
    status: Optional[str] = None  # 'good', 'warning', 'critical'

    def format_value(self) -> str:
        """Formata o valor para exibição"""
        if isinstance(self.value, float):
            return f"{self.value:.2f}"
        return str(self.value)


@dataclass
class InfoCard:
    """Card informativo genérico"""
    title: str
    content: str
    icon: str = "ℹ️"
    card_type: str = "info"  # 'info', 'warning', 'success', 'error'
    expandable: bool = False
    expanded: bool = False


@dataclass
class OverviewMetrics:
    """Métricas para overview/resumo"""
    total_repos: int
    avg_stars: float
    avg_forks: float
    median_stars: float
    median_forks: float
    gini_coefficient: Optional[float] = None
    top_repo_name: Optional[str] = None
    top_repo_stars: Optional[int] = None
    using_mock_data: bool = False
    rate_limited: bool = False


@dataclass
class HegemonyData:
    """Dados de hegemonia computada"""
    data: Dict[str, Any]
    total_records: int = 0
    top_hegemon: Optional[str] = None
    concentration_ratio: float = 0.0


@dataclass
class InequalityMetrics:
    """Métricas de desigualdade"""
    gini_coefficient: float
    concentration_ratio: float
    top_10_percent_share: float
    bottom_50_percent_share: float
    interpretation: str = ""


@dataclass
class ThemeConfig:
    """Configuração de tema visual"""
    primary_color: str = "#58a6ff"
    secondary_color: str = "#1f6feb"
    accent_color: str = "#238636"
    background_color: str = "#0d1117"
    surface_color: str = "#161b22"
    border_color: str = "#30363d"
    text_primary: str = "#c9d1d9"
    text_secondary: str = "#8b949e"
    success_color: str = "#238636"
    warning_color: str = "#d29922"
    error_color: str = "#f85149"

    @property
    def css_variables(self) -> str:
        """Retorna variáveis CSS para aplicar tema"""
        return f"""
        :root {{
            --primary: {self.primary_color};
            --secondary: {self.secondary_color};
            --accent: {self.accent_color};
            --bg-main: {self.background_color};
            --bg-surface: {self.surface_color};
            --border: {self.border_color};
            --text-primary: {self.text_primary};
            --text-secondary: {self.text_secondary};
            --success: {self.success_color};
            --warning: {self.warning_color};
            --error: {self.error_color};
        }}
        """
