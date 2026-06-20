"""
Legacy analysis adapter for compatibility with existing imports.
"""

from typing import Optional
import pandas as pd
from services.interpretation_service import InterpretationService


def interpret_dataset(df_metrics: pd.DataFrame, df_hegemony: pd.DataFrame, gini_value: Optional[float] = None):
    service = InterpretationService()
    return service.interpret_dataset(df_metrics, df_hegemony, gini_value)


def interpret_domination(index: float) -> str:
    service = InterpretationService()
    return service.interpret_domination(index)


def interpret_power_structure(gini: float, top10: float, corr: Optional[float] = None) -> str:
    service = InterpretationService()
    return service.interpret_power_structure(gini, top10, corr)

__all__ = [
    "interpret_dataset",
    "interpret_domination",
    "interpret_power_structure",
]
