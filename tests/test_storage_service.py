"""
Testes para Storage Service - GitHub Analytics Dashboard
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
from services.storage_service import StorageService, FileStorageBackend, MockStorageBackend


class MockSettings:
    """Mock settings para testes."""
    def __init__(self, data_dir: Path):
        self.DATA_DIR = data_dir

    def get(self, key: str, default=None):
        return getattr(self, key, default)


@pytest.fixture
def temp_data_dir():
    """Diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_settings(temp_data_dir):
    """Settings mockados para testes."""
    return MockSettings(temp_data_dir)


@pytest.fixture
def sample_dataframe():
    """DataFrame de exemplo para testes."""
    return pd.DataFrame({
        'name': ['repo1', 'repo2', 'repo3'],
        'stars': [100, 200, 300],
        'forks': [10, 20, 30]
    })


class TestFileStorageBackend:
    """Testes para FileStorageBackend."""

    def test_load_data_file_exists(self, temp_data_dir, sample_dataframe):
        """Testa carregamento de arquivo existente."""
        # Criar arquivo de teste
        test_file = temp_data_dir / "test_data.csv"
        sample_dataframe.to_csv(test_file, index=False)

        backend = FileStorageBackend(temp_data_dir)
        result = backend.load_data("test_data")

        assert result is not None
        assert len(result) == 3
        assert result['name'].tolist() == ['repo1', 'repo2', 'repo3']

    def test_load_data_file_not_exists(self, temp_data_dir):
        """Testa carregamento de arquivo inexistente."""
        backend = FileStorageBackend(temp_data_dir)
        result = backend.load_data("nonexistent")

        assert result is None

    def test_save_data(self, temp_data_dir, sample_dataframe):
        """Testa salvamento de dados."""
        backend = FileStorageBackend(temp_data_dir)
        success = backend.save_data(sample_dataframe, "saved_data")

        assert success
        assert (temp_data_dir / "saved_data.csv").exists()

        # Verificar conteúdo salvo
        loaded = pd.read_csv(temp_data_dir / "saved_data.csv")
        assert len(loaded) == 3

    def test_list_sources(self, temp_data_dir, sample_dataframe):
        """Testa listagem de fontes disponíveis."""
        # Criar alguns arquivos
        (temp_data_dir / "data1.csv").write_text("test")
        (temp_data_dir / "data2.csv").write_text("test")
        (temp_data_dir / "not_csv.txt").write_text("test")

        backend = FileStorageBackend(temp_data_dir)
        sources = backend.list_sources()

        assert "data1" in sources
        assert "data2" in sources
        assert "not_csv" not in sources


class TestMockStorageBackend:
    """Testes para MockStorageBackend."""

    def test_load_data_existing_source(self):
        """Testa carregamento de fonte mockada existente."""
        backend = MockStorageBackend()
        result = backend.load_data("example_history")

        assert result is not None
        assert len(result) == 6  # Dados mockados têm 6 linhas
        assert 'repository' in result.columns

    def test_load_data_nonexistent_source(self):
        """Testa carregamento de fonte mockada inexistente."""
        backend = MockStorageBackend()
        result = backend.load_data("nonexistent")

        assert result is None

    def test_save_data(self, sample_dataframe):
        """Testa salvamento (simulado) em mock."""
        backend = MockStorageBackend()
        success = backend.save_data(sample_dataframe, "test")

        assert success  # Mock sempre retorna True

    def test_list_sources(self):
        """Testa listagem de fontes mockadas."""
        backend = MockStorageBackend()
        sources = backend.list_sources()

        assert "example_history" in sources
        assert "history" in sources


class TestStorageService:
    """Testes para StorageService."""

    def test_load_data_primary_backend(self, mock_settings, sample_dataframe):
        """Testa carregamento usando backend primário."""
        # Criar arquivo no backend primário
        test_file = mock_settings.DATA_DIR / "primary_data.csv"
        sample_dataframe.to_csv(test_file, index=False)

        service = StorageService(mock_settings)
        result = service.load_data("primary_data")

        assert result is not None
        assert len(result) == 3

    def test_load_data_fallback_to_mock(self, mock_settings):
        """Testa fallback para dados mockados."""
        service = StorageService(mock_settings)
        result = service.load_data("example_history", use_fallback=True)

        assert result is not None
        assert 'repository' in result.columns

    def test_load_data_no_fallback(self, mock_settings):
        """Testa carregamento sem fallback."""
        service = StorageService(mock_settings)
        result = service.load_data("nonexistent", use_fallback=False)

        assert result is None

    def test_save_data(self, mock_settings, sample_dataframe):
        """Testa salvamento de dados."""
        service = StorageService(mock_settings)
        success = service.save_data(sample_dataframe, "test_save")

        assert success
        assert (mock_settings.DATA_DIR / "test_save.csv").exists()

    def test_get_data_info(self, mock_settings, sample_dataframe):
        """Testa obtenção de informações sobre dados."""
        # Criar arquivo de teste
        (mock_settings.DATA_DIR / "info_test.csv").write_text("test")

        service = StorageService(mock_settings)
        info = service.get_data_info()

        assert 'primary_sources' in info
        assert 'mock_sources' in info
        assert 'data_dir' in info
        assert 'info_test' in info['primary_sources']

    def test_ensure_data_availability(self, mock_settings):
        """Testa verificação de disponibilidade de dados."""
        service = StorageService(mock_settings)
        availability = service.ensure_data_availability(["example_history", "nonexistent"])

        assert availability["example_history"] is True  # Mock disponível
        assert availability["nonexistent"] is False

    def test_force_mock_mode(self, mock_settings):
        """Testa modo forçado de mock."""
        mock_settings.FORCE_MOCK_STORAGE = True
        service = StorageService(mock_settings)

        # Mesmo com arquivo real, deve usar mock
        (mock_settings.DATA_DIR / "real_data.csv").write_text("name,stars\nrepo,100")
        result = service.load_data("example_history")  # Usar fonte que existe no mock

        # Deve retornar dados mockados
        assert result is not None
        assert 'repository' in result.columns  # Coluna dos dados mockados