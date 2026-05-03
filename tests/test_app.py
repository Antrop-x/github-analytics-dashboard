#!/usr/bin/env python
"""
Test application imports and basic functionality.
"""

import pytest


def test_app_imports():
    """Test that the main app module imports without errors."""
    try:
        import app
        assert True
    except Exception as e:
        pytest.fail(f"App import failed: {str(e)}")


def test_core_imports():
    """Test that core modules import without errors."""
    try:
        from core.metrics import gini, domination_index, top_concentration
        assert True
    except Exception as e:
        pytest.fail(f"Core metrics import failed: {str(e)}")


def test_services_imports():
    """Test that service modules import without errors."""
    try:
        from services.analysis_service import interpret_dataset, interpret_domination
        assert True
    except Exception as e:
        pytest.fail(f"Services import failed: {str(e)}")


def test_infrastructure_imports():
    """Test that infrastructure modules import without errors."""
    try:
        import infrastructure.github_api
        import infrastructure.base_api
        assert True
    except Exception as e:
        pytest.fail(f"Infrastructure import failed: {str(e)}")


if __name__ == "__main__":
    test_app_imports()
    test_core_imports()
    test_services_imports()
    test_infrastructure_imports()
    print("SUCCESS: All app imports passed")
