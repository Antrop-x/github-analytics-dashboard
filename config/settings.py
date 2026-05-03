"""
Centralized configuration management for GitHub Analytics Dashboard.
"""
import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings with environment variable support."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    ASSETS_DIR = PROJECT_ROOT / "assets"

    # GitHub API Configuration
    GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com/search/repositories")
    GITHUB_API_TIMEOUT = int(os.getenv("GITHUB_API_TIMEOUT", "10"))
    GITHUB_API_PER_PAGE = int(os.getenv("GITHUB_API_PER_PAGE", "30"))

    # Streamlit Configuration
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", "localhost")

    # GitHub Token
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    # Application Configuration
    APP_TITLE = os.getenv("APP_TITLE", "GitHub Analytics Dashboard")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

    # Application Configuration
    APP_TITLE = os.getenv("APP_TITLE", "GitHub Analytics Dashboard")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

    # Data Configuration
    DEFAULT_DATA_FILE = DATA_DIR / "example_history.csv"
    HISTORY_DATA_FILE = DATA_DIR / "history.csv"

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Test Configuration
    TEST_DATA_SIZE = int(os.getenv("TEST_DATA_SIZE", "100"))

    @classmethod
    def get_github_token(cls) -> Optional[str]:
        """Retorna o token do GitHub usando fallback seguro."""
        token = os.getenv("GITHUB_TOKEN")
        if token:
            return token

        try:
            import streamlit as st
            token = st.secrets.get("GITHUB_TOKEN")
            if token:
                return token
        except Exception:
            pass

        return None

    @classmethod
    def get_github_headers(cls) -> dict:
        """Get GitHub API headers with optional token."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"{cls.APP_TITLE}/{cls.APP_VERSION}"
        }

        token = cls.get_github_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.ASSETS_DIR.mkdir(exist_ok=True)

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"


# Global settings instance
settings = Settings()