"""
Dashboard Application Service - GitHub Analytics Dashboard

Camada de aplicação que orquestra pipeline, interpretação e inspeção de storage.
A UI deve depender apenas desta classe para obter dados prontos para renderização.
"""

from typing import Any
import pandas as pd
from core.metrics import gini
from services.pipeline_service import PipelineService
from services.interpretation_service import InterpretationService
from services.storage_inspection_service import StorageInspectionService
from models.ui_models import DashboardContract


class DashboardApplicationService:
    """
    Serviço de aplicação que agrupa dependências de domínio e infraestrutura
    para fornecer um contrato único ao UI.
    """

    def __init__(
        self,
        pipeline_service: PipelineService,
        interpretation_service: InterpretationService,
        storage_inspection_service: StorageInspectionService
    ):
        self.pipeline_service = pipeline_service
        self.interpretation_service = interpretation_service
        self.storage_inspection_service = storage_inspection_service

    def prepare_dashboard(
        self,
        query: str,
        pages: int,
        sort: str = "stars",
        use_cache: bool = True
    ) -> DashboardContract:
        """Orquestra dados e contratos prontos para o dashboard."""
        result = self.pipeline_service.ingest_repositories(
            query=query,
            pages=pages,
            sort=sort,
            use_cache=use_cache
        )

        df = result.get("data", pd.DataFrame())
        heg = result.get("hegemony", pd.DataFrame())
        rate_limited = result.get("rate_limited", False)

        gini_value = None
        if not df.empty and "stars" in df.columns:
            gini_value = gini(df["stars"])

        analysis = self.interpretation_service.create_analysis_result(df, heg, gini_value)
        storage_info = self.storage_inspection_service.inspect()

        return DashboardContract(
            data=df,
            hegemony=heg,
            analysis=analysis,
            storage_info=storage_info,
            rate_limited=rate_limited,
            status=result.get("status", "success"),
            records=result.get("records", len(df))
        )

    def get_storage_info(self):
        return self.storage_inspection_service.inspect()
