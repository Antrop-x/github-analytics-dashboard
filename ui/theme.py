"""
UI Theme - Configuração de tema visual
"""

import streamlit as st
from models.ui_models import ThemeConfig


# Tema padrão - GitHub Dark
DEFAULT_THEME = ThemeConfig(
    primary_color="#58a6ff",
    secondary_color="#1f6feb",
    accent_color="#238636",
    background_color="#0d1117",
    surface_color="#161b22",
    border_color="#30363d",
    text_primary="#c9d1d9",
    text_secondary="#8b949e",
    success_color="#238636",
    warning_color="#d29922",
    error_color="#f85149"
)


def apply_theme(theme: ThemeConfig = DEFAULT_THEME):
    """
    Aplica tema customizado à interface.
    
    Args:
        theme: Configuração de tema
    """
    st.markdown(f"""
    <style>
        {theme.css_variables}
        
        /* Estilos base */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-surface); }}
        ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
        
        /* Cards principais */
        .critico-card {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            transition: border-color 0.2s ease;
        }}
        
        .critico-card:hover {{
            border-color: var(--primary);
        }}
        
        /* Badges */
        .badge-status {{
            background-color: var(--success);
            color: white;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
        }}
        
        .badge-warning {{
            background-color: var(--warning);
            color: white;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
        }}
        
        .badge-critical {{
            background-color: var(--error);
            color: white;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
        }}
        
        /* Títulos */
        h1, h2, h3 {{
            color: var(--text-primary);
        }}
        
        .section-title {{
            margin-top: 2rem;
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--primary);
            border-bottom: 2px solid var(--border);
            padding-bottom: 0.5rem;
        }}
        
        /* Métricas */
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary);
            line-height: 1;
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }}
        
        /* Dividers */
        hr {{
            border: none;
            border-top: 1px solid var(--border);
            margin: 1rem 0;
        }}
        
        /* Links */
        a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        /* Código */
        code {{
            background-color: var(--bg-surface);
            color: var(--text-primary);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            overflow-x: auto;
        }}
        
        /* Botões */
        .stButton > button {{
            background-color: var(--primary);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background-color: var(--secondary);
            border-color: var(--primary);
        }}
        
        /* Expandables */
        .streamlit-expanderHeader {{
            color: var(--text-primary);
        }}
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border);
            color: var(--text-primary);
            border-radius: 6px;
        }}
        
        /* Mensagens */
        .stInfo, .stSuccess, .stWarning, .stError {{
            border-radius: 8px;
        }}
    </style>
    """, unsafe_allow_html=True)


def get_color(color_type: str, theme: ThemeConfig = DEFAULT_THEME) -> str:
    """
    Obtém cor do tema por tipo.
    
    Args:
        color_type: Tipo de cor ('primary', 'success', 'warning', 'error', etc)
        theme: Tema atual
        
    Returns:
        Código HEX da cor
    """
    colors = {
        'primary': theme.primary_color,
        'secondary': theme.secondary_color,
        'accent': theme.accent_color,
        'bg': theme.background_color,
        'surface': theme.surface_color,
        'border': theme.border_color,
        'text': theme.text_primary,
        'text-dim': theme.text_secondary,
        'success': theme.success_color,
        'warning': theme.warning_color,
        'error': theme.error_color,
    }
    return colors.get(color_type, theme.primary_color)
