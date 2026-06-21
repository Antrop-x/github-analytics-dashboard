"""
UI Sections - Adaptador de compatibilidade que delega para presenters
NOTA: Este módulo é mantido apenas para compatibilidade retroativa.
Use ui.presenters diretamente em novo código.
"""

from ui.presenters import (
    render_overview_section,
    render_data_table_section,
    render_hegemony_section,
    render_inequality_section,
    render_storage_section,
    render_footer_section
)

__all__ = [
    "render_overview_section",
    "render_data_table_section",
    "render_hegemony_section",
    "render_inequality_section",
    "render_storage_section",
    "render_footer_section"
]
