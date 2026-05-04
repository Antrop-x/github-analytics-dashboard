#!/usr/bin/env python3
"""
GitHub Analytics Dashboard - Entrypoint Principal

Este arquivo é o ponto de entrada único da aplicação, responsável por:
- Inicializar configurações
- Injetar dependências
- Iniciar a UI
"""

import sys
import logging
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from config.settings import Settings
from services.pipeline_service import PipelineService
from services.interpretation_service import InterpretationService
from services.storage_service import StorageService
from ui.ui import GitHubAnalyticsUI


def main():
    """Função principal da aplicação."""
    try:
        # Inicializar configurações
        settings = Settings()

        # Configurar logging
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            format=settings.log_format
        )

        logger = logging.getLogger(__name__)
        logger.info("Iniciando GitHub Analytics Dashboard...")

        # Inicializar serviços
        pipeline_service = PipelineService(settings)
        interpretation_service = InterpretationService()
        storage_service = StorageService(settings)

        # Iniciar UI
        ui = GitHubAnalyticsUI(
            pipeline_service=pipeline_service,
            interpretation_service=interpretation_service,
            storage_service=storage_service,
            settings=settings
        )

        # Executar aplicação
        ui.run()

    except Exception as e:
        logging.error(f"Erro fatal na aplicação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()