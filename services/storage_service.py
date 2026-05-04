"""
Storage Service - GitHub Analytics Dashboard

Abstração para armazenamento de dados, permitindo diferentes backends:
- Mock data para desenvolvimento/testes
- Arquivos CSV locais
- Banco de dados (futuro)
- APIs externas (futuro)
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Interface abstrata para backends de armazenamento."""

    @abstractmethod
    def load_data(self, source: str) -> Optional[pd.DataFrame]:
        """Carrega dados de uma fonte específica."""
        pass

    @abstractmethod
    def save_data(self, data: pd.DataFrame, destination: str) -> bool:
        """Salva dados em um destino específico."""
        pass

    @abstractmethod
    def list_sources(self) -> List[str]:
        """Lista fontes de dados disponíveis."""
        pass


class FileStorageBackend(StorageBackend):
    """Backend que usa arquivos locais (CSV, JSON, etc.)."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(exist_ok=True)

    def load_data(self, source: str) -> Optional[pd.DataFrame]:
        """Carrega dados de arquivo CSV."""
        file_path = self.base_path / f"{source}.csv"
        if not file_path.exists():
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return None

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Dados carregados de {file_path}: {len(df)} registros")
            return df
        except Exception as e:
            logger.error(f"Erro ao carregar {file_path}: {e}")
            return None

    def save_data(self, data: pd.DataFrame, destination: str) -> bool:
        """Salva dados em arquivo CSV."""
        file_path = self.base_path / f"{destination}.csv"
        try:
            data.to_csv(file_path, index=False)
            logger.info(f"Dados salvos em {file_path}: {len(data)} registros")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar {file_path}: {e}")
            return False

    def list_sources(self) -> List[str]:
        """Lista arquivos CSV disponíveis."""
        return [f.stem for f in self.base_path.glob("*.csv")]


class MockStorageBackend(StorageBackend):
    """Backend que retorna dados mockados para desenvolvimento/testes."""

    def __init__(self):
        self.mock_data = {
            "example_history": pd.DataFrame({
                "date": ["2026-01-01", "2026-01-01", "2026-01-01", "2026-02-01", "2026-02-01", "2026-02-01"],
                "repository": ["repo1", "repo2", "repo3", "repo1", "repo2", "repo3"],
                "stars": [100, 50, 200, 120, 55, 250],
                "forks": [10, 8, 15, 12, 9, 18],
                "watchers": [5, 3, 8, 6, 3, 10]
            }),
            "history": pd.DataFrame({
                "name": ["test/repo1", "test/repo2", "test/repo3"],
                "stars": [1000, 500, 2000],
                "forks": [100, 50, 200],
                "language": ["python", "javascript", "python"],
                "url": ["https://github.com/test/repo1", "https://github.com/test/repo2", "https://github.com/test/repo3"],
                "description": ["Test repo 1", "Test repo 2", "Test repo 3"],
                "stars_safe": [1000, 500, 2000],
                "appropriation_rate": [0.1, 0.08, 0.15],
                "symbolic_density": [0.8, 0.6, 0.9],
                "snapshot_time": ["2026-05-03T10:00:00", "2026-05-03T10:00:00", "2026-05-03T10:00:00"],
                "query": ["python", "python", "python"],
                "updated": ["", "", ""]
            })
        }

    def load_data(self, source: str) -> Optional[pd.DataFrame]:
        """Retorna dados mockados."""
        data = self.mock_data.get(source)
        if data is not None:
            logger.info(f"Dados mockados carregados para '{source}': {len(data)} registros")
            return data.copy()
        logger.warning(f"Dados mockados não encontrados para '{source}'")
        return None

    def save_data(self, data: pd.DataFrame, destination: str) -> bool:
        """Simula salvamento (não persiste em mock)."""
        logger.info(f"Simulação de salvamento para '{destination}': {len(data)} registros")
        return True

    def list_sources(self) -> List[str]:
        """Lista fontes mockadas disponíveis."""
        return list(self.mock_data.keys())


class StorageService:
    """
    Serviço de armazenamento com suporte a múltiplos backends.

    Estratégia:
    1. Tenta carregar de backend primário (arquivos reais)
    2. Fallback para mock data se primário falhar
    3. Permite configuração de backend via settings
    """

    def __init__(self, settings):
        self.settings = settings
        self.primary_backend = FileStorageBackend(settings.DATA_DIR)
        self.fallback_backend = MockStorageBackend()
        self.force_mock = getattr(settings, 'FORCE_MOCK_STORAGE', False)

    def load_data(self, source: str, use_fallback: bool = True) -> Optional[pd.DataFrame]:
        """
        Carrega dados de uma fonte, com fallback opcional.

        Args:
            source: Nome da fonte de dados
            use_fallback: Se deve usar dados mockados como fallback

        Returns:
            DataFrame com dados ou None se não encontrado
        """
        # Força uso de mock se configurado
        if self.force_mock:
            return self.fallback_backend.load_data(source)

        # Tenta backend primário primeiro
        data = self.primary_backend.load_data(source)
        if data is not None:
            return data

        # Fallback para mock se solicitado
        if use_fallback:
            logger.info(f"Usando dados mockados para '{source}' (primário não disponível)")
            return self.fallback_backend.load_data(source)

        return None

    def save_data(self, data: pd.DataFrame, destination: str) -> bool:
        """
        Salva dados usando backend primário.

        Args:
            data: DataFrame a ser salvo
            destination: Nome do destino

        Returns:
            True se salvou com sucesso
        """
        if self.force_mock:
            return self.fallback_backend.save_data(data, destination)

        return self.primary_backend.save_data(data, destination)

    def get_data_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre os dados disponíveis.

        Returns:
            Dicionário com metadados dos backends
        """
        return {
            "primary_sources": self.primary_backend.list_sources(),
            "mock_sources": self.fallback_backend.list_sources(),
            "force_mock": self.force_mock,
            "data_dir": str(self.settings.DATA_DIR)
        }

    def ensure_data_availability(self, required_sources: List[str]) -> Dict[str, bool]:
        """
        Garante que fontes de dados necessárias estão disponíveis.

        Args:
            required_sources: Lista de fontes necessárias

        Returns:
            Dicionário indicando disponibilidade de cada fonte
        """
        availability = {}
        for source in required_sources:
            data = self.load_data(source, use_fallback=True)
            availability[source] = data is not None and not data.empty
        return availability