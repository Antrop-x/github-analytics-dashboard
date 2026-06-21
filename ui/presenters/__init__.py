"""
Presenters - Lógica de apresentação das seções
"""

from ui.presenters.overview import render_overview_section
from ui.presenters.data_table import render_data_table_section
from ui.presenters.hegemony import render_hegemony_section
from ui.presenters.inequality import render_inequality_section
from ui.presenters.storage import render_storage_section
from ui.presenters.footer import render_footer_section

__all__ = [
    "render_overview_section",
    "render_data_table_section",
    "render_hegemony_section",
    "render_inequality_section",
    "render_storage_section",
    "render_footer_section"
]
