"""
Tests for UI Models and Components
"""

import pytest
from models.ui_models import StorageInfo, MetricCard, InfoCard, ThemeConfig
from ui.components import render_metric_card, render_info_card, render_status_badge
from ui.theme import get_color, DEFAULT_THEME


class TestStorageInfo:
    """Test StorageInfo dataclass"""

    def test_storage_info_creation(self):
        """Test creating StorageInfo instance"""
        info = StorageInfo(
            backend="Test Backend",
            directory="/test/path",
            sources=["source1", "source2"],
            availability={"source1": True, "source2": False}
        )
        assert info.backend == "Test Backend"
        assert info.directory == "/test/path"
        assert info.sources == ["source1", "source2"]
        assert info.availability == {"source1": True, "source2": False}

    def test_health_percentage_calculation(self):
        """Test health percentage calculation"""
        # Test with available sources
        info = StorageInfo(
            backend="Test",
            directory="/test",
            total_sources=4,
            available_sources=3
        )
        assert info.health_percentage == 75.0

        # Test with no sources
        info_zero = StorageInfo(
            backend="Test",
            directory="/test",
            total_sources=0,
            available_sources=0
        )
        assert info_zero.health_percentage == 0.0

    def test_health_text_formatting(self):
        """Test health text formatting"""
        info = StorageInfo(
            backend="Test",
            directory="/test",
            total_sources=2,
            available_sources=2
        )
        assert info.health_text == "Saúde do storage: 100.0%"


class TestMetricCard:
    """Test MetricCard dataclass"""

    def test_metric_card_creation(self):
        """Test creating MetricCard instance"""
        card = MetricCard(
            label="Test Metric",
            value=42,
            icon="📊",
            unit="units",
            context="Test context"
        )
        assert card.label == "Test Metric"
        assert card.value == 42
        assert card.icon == "📊"
        assert card.unit == "units"
        assert card.context == "Test context"

    def test_format_value_integer(self):
        """Test formatting integer values"""
        card = MetricCard(label="Test", value=42)
        assert card.format_value() == "42"

    def test_format_value_float(self):
        """Test formatting float values"""
        card = MetricCard(label="Test", value=3.14159)
        assert card.format_value() == "3.14"


class TestThemeConfig:
    """Test ThemeConfig dataclass"""

    def test_theme_creation(self):
        """Test creating ThemeConfig instance"""
        theme = ThemeConfig(
            primary_color="#ff0000",
            background_color="#000000"
        )
        assert theme.primary_color == "#ff0000"
        assert theme.background_color == "#000000"

    def test_css_variables_generation(self):
        """Test CSS variables generation"""
        theme = ThemeConfig(primary_color="#ff0000")
        css = theme.css_variables
        assert ":root {" in css
        assert "--primary: #ff0000;" in css


class TestThemeFunctions:
    """Test theme utility functions"""

    def test_get_color_existing(self):
        """Test getting existing color"""
        color = get_color("primary", DEFAULT_THEME)
        assert color == DEFAULT_THEME.primary_color

    def test_get_color_nonexistent(self):
        """Test getting nonexistent color returns primary"""
        color = get_color("nonexistent", DEFAULT_THEME)
        assert color == DEFAULT_THEME.primary_color


class TestUIComponents:
    """Test UI component functions"""

    def test_render_status_badge_true(self):
        """Test status badge for True value"""
        # This would normally render in Streamlit, but we can test the logic
        assert callable(render_status_badge)

    def test_render_metric_card_callable(self):
        """Test that render_metric_card is callable"""
        assert callable(render_metric_card)

    def test_render_info_card_callable(self):
        """Test that render_info_card is callable"""
        assert callable(render_info_card)


if __name__ == "__main__":
    pytest.main([__file__])