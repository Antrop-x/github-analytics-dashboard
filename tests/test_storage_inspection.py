"""
Tests for Storage Inspection Service
"""

import pytest
from unittest.mock import Mock, MagicMock
from services.storage_inspection_service import StorageInspectionService
from models.ui_models import StorageInfo


class TestStorageInspectionService:
    """Test StorageInspectionService"""

    @pytest.fixture
    def mock_storage_service(self):
        """Create mock storage service"""
        mock_service = Mock()
        mock_service.get_data_info.return_value = {
            "data_dir": "/test/data",
            "primary_sources": ["source1", "source2"],
            "mock_sources": ["mock1"],
            "force_mock": False
        }
        mock_service.ensure_data_availability.return_value = {
            "source1": True,
            "source2": True
        }
        return mock_service

    @pytest.fixture
    def inspection_service(self, mock_storage_service):
        """Create inspection service with mock storage"""
        return StorageInspectionService(mock_storage_service)

    def test_inspect_returns_storage_info(self, inspection_service):
        """Test that inspect returns StorageInfo instance"""
        result = inspection_service.inspect()
        assert isinstance(result, StorageInfo)

    def test_inspect_data_mapping(self, inspection_service, mock_storage_service):
        """Test that inspect correctly maps data"""
        result = inspection_service.inspect()

        assert result.backend == "Arquivos locais (2 fontes)"
        assert result.directory == "/test/data"
        assert result.sources == ["source1", "source2"]
        assert result.mock_sources == ["mock1"]
        assert result.availability == {"source1": True, "source2": True}
        assert result.force_mock == False
        assert result.total_sources == 2
        assert result.available_sources == 2
        assert result.mock_fallback == False

    def test_get_backend_description_normal(self, inspection_service):
        """Test backend description for normal mode"""
        storage_info = {
            "force_mock": False,
            "primary_sources": ["src1", "src2"]
        }
        result = inspection_service._get_backend_description(storage_info)
        assert result == "Arquivos locais (2 fontes)"

    def test_get_backend_description_force_mock(self, inspection_service):
        """Test backend description for force mock mode"""
        storage_info = {
            "force_mock": True,
            "primary_sources": ["src1"]
        }
        result = inspection_service._get_backend_description(storage_info)
        assert result == "Mock Data (Forçado)"

    def test_get_backend_description_fallback(self, inspection_service):
        """Test backend description for fallback mode"""
        storage_info = {
            "force_mock": False,
            "primary_sources": []
        }
        result = inspection_service._get_backend_description(storage_info)
        assert result == "Mock Data (Fallback)"

    def test_get_storage_health(self, inspection_service):
        """Test get_storage_health method"""
        result = inspection_service.get_storage_health()

        expected_keys = [
            "healthy", "total_sources", "available_sources",
            "using_mock_fallback", "force_mock_mode"
        ]

        for key in expected_keys:
            assert key in result

        assert result["healthy"] == True
        assert result["total_sources"] == 2
        assert result["available_sources"] == 2
        assert result["using_mock_fallback"] == False
        assert result["force_mock_mode"] == False


class TestStorageInfoIntegration:
    """Integration tests for StorageInfo with real service"""

    def test_storage_info_properties(self):
        """Test StorageInfo computed properties"""
        info = StorageInfo(
            backend="Test",
            directory="/test",
            total_sources=4,
            available_sources=3
        )

        assert info.health_percentage == 75.0
        assert info.health_text == "Saúde do storage: 75.0%"

    def test_storage_info_zero_sources(self):
        """Test StorageInfo with zero sources"""
        info = StorageInfo(
            backend="Test",
            directory="/test",
            total_sources=0,
            available_sources=0
        )

        assert info.health_percentage == 0.0
        assert info.health_text == "Saúde do storage: 0.0%"


if __name__ == "__main__":
    pytest.main([__file__])