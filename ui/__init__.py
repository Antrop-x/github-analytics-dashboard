"""
UI Package - Interface do Observatório do Trabalho Digital
"""

from ui.ui import (
    configure_page,
    apply_theme,
    get_mode_labels,
    sidebar_controls,
    render_header,
    render_overview,
    render_data_table,
    render_hegemony,
    render_reflexivity,
    render_inequality_section,
    render_empty,
)

from ui.components import (
    render_metric_card,
    render_info_card,
    render_metric_grid,
    render_dataframe_card,
    render_status_badge,
    render_progress_with_label,
    render_section_header,
    create_custom_card_html,
    render_custom_card,
)

from ui.theme import apply_theme, get_color, DEFAULT_THEME

from ui.sections import (
    render_overview_section,
    render_data_table_section,
    render_hegemony_section,
    render_inequality_section,
    render_storage_section,
    render_footer_section,
)

from ui.layout import (
    render_main_layout,
    render_empty_state,
    configure_page,
)

__all__ = [
    # ui.py
    "configure_page",
    "apply_theme",
    "get_mode_labels",
    "sidebar_controls",
    "render_header",
    "render_overview",
    "render_data_table",
    "render_hegemony",
    "render_reflexivity",
    "render_inequality_section",
    "render_empty",
    # components.py
    "render_metric_card",
    "render_info_card",
    "render_metric_grid",
    "render_dataframe_card",
    "render_status_badge",
    "render_progress_with_label",
    "render_section_header",
    "create_custom_card_html",
    "render_custom_card",
    # theme.py
    "get_color",
    "DEFAULT_THEME",
    # sections.py
    "render_overview_section",
    "render_data_table_section",
    "render_hegemony_section",
    "render_storage_section",
    "render_footer_section",
    # layout.py
    "render_main_layout",
    "render_empty_state",
]
