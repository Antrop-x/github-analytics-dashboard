"""
Storage Inspection Service - GitHub Analytics Dashboard

Serviço dedicado para inspeção e relatório do estado do storage.
Isola lógica de inspeção da UI, retornando dados prontos para renderização.
"""

from typing import Dict, Any
from services.storage_service import StorageService
from models.ui_models import StorageInfo


class StorageInspectionService:
    """
    Serviço de inspeção do storage - prepara dados para UI.

    Responsabilidades:
    - Coletar informações do storage service
    - Formatar dados para apresentação
    - Calcular métricas de disponibilidade
    - Preparar estrutura pronta para renderização
    """

    def __init__(self, storage_service: StorageService):
        """
        Inicializa o serviço de inspeção.

        Args:
            storage_service: Instância do StorageService a ser inspecionada
        """
        self.storage_service = storage_service

    def inspect(self) -> StorageInfo:
        """
        Inspeciona o estado atual do storage e retorna dados formatados para UI.

        Returns:
            StorageInfo com informações prontas para renderização
        """
        # Obter informações básicas do storage
        storage_info = self.storage_service.get_data_info()

        # Verificar disponibilidade das fontes principais
        required_sources = ["example_history", "history"]
        availability = self.storage_service.ensure_data_availability(required_sources)

        # Preparar dados para UI usando dataclass
        return StorageInfo(
            backend=self._get_backend_description(storage_info),
            directory=storage_info.get("data_dir", "N/A"),
            sources=storage_info.get("primary_sources", []),
            mock_sources=storage_info.get("mock_sources", []),
            availability=availability,
            force_mock=storage_info.get("force_mock", False),
            total_sources=len(storage_info.get("primary_sources", [])),
            available_sources=sum(availability.values()),
            mock_fallback=any(not available for available in availability.values())
        )

    def _get_backend_description(self, storage_info: Dict[str, Any]) -> str:
        """
        Retorna descrição amigável do backend atual.

        Args:
            storage_info: Informações do storage

        Returns:
            String descritiva do backend
        """
        if storage_info.get("force_mock"):
            return "Mock Data (Forçado)"

        primary_sources = storage_info.get("primary_sources", [])
        if primary_sources:
            return f"Arquivos locais ({len(primary_sources)} fontes)"

        return "Mock Data (Fallback)"

    def get_storage_health(self) -> Dict[str, Any]:
        """
        Retorna status de saúde do storage para monitoramento.

        Returns:
            Métricas de saúde do storage
        """
        inspection = self.inspect()

        return {
            "healthy": inspection.available_sources > 0,
            "total_sources": inspection.total_sources,
            "available_sources": inspection.available_sources,
            "using_mock_fallback": inspection.mock_fallback,
            "force_mock_mode": inspection.force_mock
        }
