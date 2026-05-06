from config.settings import Settings
from services.pipeline_service import PipelineService
from services.interpretation_service import InterpretationService
from services.storage_service import StorageService
from services.storage_inspection_service import StorageInspectionService
from ui.ui import GitHubAnalyticsUI

settings = Settings()

pipeline_service = PipelineService(settings)
interpretation_service = InterpretationService()
storage_service = StorageService(settings)
storage_inspection_service = StorageInspectionService(storage_service)

ui = GitHubAnalyticsUI(
    pipeline_service=pipeline_service,
    interpretation_service=interpretation_service,
    storage_service=storage_service,
    storage_inspection_service=storage_inspection_service,
    settings=settings
)

ui.run()
