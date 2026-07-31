from __future__ import annotations

from typing import Any

# UI/UX Pro Max Design Intelligence System
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --gp-bg: #f8fafc;
        --gp-panel: #ffffff;
        --gp-panel-muted: #f1f5f9;
        --gp-text-main: #0f172a;
        --gp-text-muted: #64748b;
        --gp-text-light: #94a3b8;
        --gp-border: #e2e8f0;
        --gp-border-hover: #cbd5e1;
        --gp-primary: #2563eb;
        --gp-primary-hover: #1d4ed8;
        --gp-primary-light: #eff6ff;
        --gp-accent: #0d9488;
        --gp-accent-hover: #0f766e;
        --gp-accent-light: #f0fdfa;
        --gp-success: #16a34a;
        --gp-success-light: #f0fdf4;
        --gp-warning: #d97706;
        --gp-warning-light: #fffbeb;
        --gp-risk: #dc2626;
        --gp-risk-light: #fef2f2;
        --gp-glass-bg: rgba(255, 255, 255, 0.88);
        --gp-glass-border: rgba(226, 232, 240, 0.85);
        --gp-shadow-sm: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
        --gp-shadow-md: 0 4px 12px -2px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
        --gp-shadow-lg: 0 12px 24px -4px rgba(15, 23, 42, 0.12), 0 4px 8px -2px rgba(15, 23, 42, 0.04);
        --gp-radius: 14px;
        --gp-radius-sm: 8px;
        --gp-radius-pill: 9999px;
    }

    /* Global Canvas & Fonts */
    .stApp {
        background-color: var(--gp-bg);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--gp-text-main);
        -webkit-font-smoothing: antialiased;
    }

    .stMainBlockContainer {
        max-width: 1440px;
        padding: 2.5rem 3rem;
    }

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp p, .stApp li, .stApp label,
    .stApp div[data-testid="stMarkdownContainer"] {
        color: var(--gp-text-main);
    }

    .stApp div[data-testid="stCaptionContainer"],
    .stApp small {
        color: var(--gp-text-muted);
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', 'Space Grotesk', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: var(--gp-text-main) !important;
    }

    h1 { font-size: 1.85rem !important; }
    h2 { font-size: 1.45rem !important; }
    h3 { font-size: 1.2rem !important; }

    /* Header Banner */
    .gp-main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f172a 100%);
        color: #ffffff;
        padding: 2.25rem 2.75rem;
        border-radius: 18px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.2), 0 8px 10px -6px rgba(15, 23, 42, 0.1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .gp-main-header::before {
        content: '';
        position: absolute;
        top: -60%;
        right: -10%;
        width: 380px;
        height: 380px;
        background: radial-gradient(circle, rgba(37, 99, 235, 0.35) 0%, rgba(13, 148, 136, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .gp-main-header::after {
        content: '';
        position: absolute;
        bottom: -50%;
        left: 25%;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(13, 148, 136, 0.25) 0%, rgba(0, 0, 0, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .gp-main-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.35rem;
        font-weight: 800;
        margin: 0;
        color: #ffffff !important;
        letter-spacing: -0.025em;
    }

    .gp-main-subtitle {
        color: #94a3b8;
        font-size: 0.975rem;
        margin-top: 0.5rem;
        font-weight: 450;
        letter-spacing: 0.01em;
    }

    /* KPI Glassmorphic Cards */
    .gp-kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.25rem;
        margin-bottom: 2rem;
    }

    .gp-kpi-card {
        background: var(--gp-glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--gp-glass-border);
        border-radius: var(--gp-radius);
        padding: 1.25rem 1.5rem;
        box-shadow: var(--gp-shadow-sm);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }

    .gp-kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--gp-shadow-md);
        border-color: rgba(37, 99, 235, 0.3);
    }

    .gp-kpi-label {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--gp-text-muted);
        margin-bottom: 0.4rem;
    }

    .gp-kpi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.15rem;
        font-weight: 700;
        color: var(--gp-text-main);
        line-height: 1.1;
    }

    .gp-kpi-sub {
        font-size: 0.825rem;
        color: var(--gp-text-muted);
        margin-top: 0.4rem;
        font-weight: 500;
    }

    div[data-testid="stMetric"] {
        background: var(--gp-glass-bg) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid var(--gp-glass-border) !important;
        border-radius: var(--gp-radius) !important;
        padding: 1rem 1.25rem !important;
        box-shadow: var(--gp-shadow-sm) !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--gp-shadow-md) !important;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: var(--gp-text-muted) !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: var(--gp-text-main) !important;
    }

    /* Category & Fit Badges */
    .gp-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.8rem;
        border-radius: var(--gp-radius-pill);
        font-size: 0.775rem;
        font-weight: 700;
        letter-spacing: 0.025em;
        line-height: 1;
        transition: all 0.15s ease;
    }

    .gp-badge-reach {
        background-color: var(--gp-risk-light);
        color: var(--gp-risk);
        border: 1px solid rgba(220, 38, 38, 0.3);
    }

    .gp-badge-target {
        background-color: var(--gp-primary-light);
        color: var(--gp-primary);
        border: 1px solid rgba(37, 99, 235, 0.3);
    }

    .gp-badge-safety {
        background-color: var(--gp-success-light);
        color: var(--gp-success);
        border: 1px solid rgba(22, 163, 74, 0.3);
    }

    .gp-badge-warning {
        background-color: var(--gp-warning-light);
        color: var(--gp-warning);
        border: 1px solid rgba(217, 119, 6, 0.3);
    }

    .gp-pill {
        display: inline-block;
        border: 1px solid var(--gp-border);
        border-radius: var(--gp-radius-pill);
        padding: 0.2rem 0.75rem;
        margin: 2px 4px 2px 0;
        font-size: 0.825rem;
        font-weight: 500;
        background: #f1f5f9;
        color: var(--gp-text-main);
    }

    .gp-strong { color: var(--gp-success) !important; font-weight: 700 !important; }
    .gp-good { color: var(--gp-accent) !important; font-weight: 700 !important; }
    .gp-review { color: var(--gp-warning) !important; font-weight: 700 !important; }
    .gp-risk { color: var(--gp-risk) !important; font-weight: 700 !important; }
    .gp-muted { color: var(--gp-text-muted) !important; }

    /* Card Panels & Containers */
    .gp-card {
        background: var(--gp-panel);
        border: 1px solid var(--gp-border);
        border-radius: var(--gp-radius-sm);
        padding: 1rem 1.25rem;
        margin-bottom: 0.85rem;
        box-shadow: var(--gp-shadow-sm);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .gp-card:hover {
        border-color: var(--gp-border-hover);
        box-shadow: var(--gp-shadow-md);
    }

    .gp-panel-card {
        background: #ffffff;
        border: 1px solid var(--gp-border);
        border-radius: var(--gp-radius);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--gp-shadow-sm);
    }

    .gp-panel-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--gp-text-main);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .gp-section {
        background: #ffffff;
        border: 1px solid var(--gp-border);
        border-radius: var(--gp-radius);
        padding: 1.35rem 1.65rem;
        margin: 1.15rem 0;
        box-shadow: var(--gp-shadow-sm);
    }

    .gp-section-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--gp-text-main);
        margin-bottom: 0.25rem;
        letter-spacing: -0.01em;
    }

    .gp-section-caption {
        color: var(--gp-text-muted);
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }

    .gp-workflow {
        background: var(--gp-accent-light);
        border: 1px solid rgba(13, 148, 136, 0.3);
        border-radius: var(--gp-radius-sm);
        color: var(--gp-text-main);
        padding: 0.85rem 1.25rem;
        margin: 1rem 0;
        font-weight: 600;
        font-size: 0.925rem;
    }

    .gp-workflow span {
        color: var(--gp-accent);
    }

    /* Sidebar Styling & Crisp Dark Text inside White Inputs */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] caption,
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] small {
        color: #94a3b8 !important;
        opacity: 1 !important;
    }

    /* High Contrast White Inputs inside Dark Sidebar */
    section[data-testid="stSidebar"] div[data-baseweb="select"],
    section[data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: var(--gp-radius-sm) !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] *,
    section[data-testid="stSidebar"] div[data-baseweb="input"] * {
        color: #0f172a !important;
        fill: #0f172a !important;
        caret-color: #0f172a !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] input,
    section[data-testid="stSidebar"] div[data-baseweb="input"] input {
        color: #0f172a !important;
        background-color: transparent !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] div {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] span[data-baseweb="tag"],
    section[data-testid="stSidebar"] div[data-baseweb="tag"] {
        background-color: #e2e8f0 !important;
        border-radius: 6px !important;
    }

    section[data-testid="stSidebar"] span[data-baseweb="tag"] *,
    section[data-testid="stSidebar"] div[data-baseweb="tag"] * {
        color: #0f172a !important;
    }

    /* Dropdown Popover Menus (white background + dark text) */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: var(--gp-shadow-lg) !important;
        border-radius: var(--gp-radius-sm) !important;
    }

    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] div,
    div[data-baseweb="menu"] li {
        color: #0f172a !important;
        background-color: #ffffff !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] div:hover,
    div[data-baseweb="menu"] li:hover {
        background-color: #eff6ff !important;
        color: #2563eb !important;
    }

    /* Sidebar Clear Filters button */
    section[data-testid="stSidebar"] .stButton > button,
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: var(--gp-radius-sm) !important;
        width: 100%;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover,
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }

    /* Form Controls & Main Area Inputs */
    .stTextInput input, .stSelectbox select, .stTextArea textarea, .stNumberInput input,
    div[data-baseweb="input"] input, div[data-baseweb="select"] > div {
        border-radius: var(--gp-radius-sm) !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: var(--gp-text-main) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, div[data-baseweb="input"]:focus-within {
        border-color: var(--gp-primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* Main Area Buttons */
    .stButton > button,
    div[data-testid="stFormSubmitButton"] button,
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stFileUploader"] button {
        border-radius: var(--gp-radius-sm) !important;
        font-weight: 600 !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        color: var(--gp-text-main) !important;
        box-shadow: var(--gp-shadow-sm) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] button:hover,
    div[data-testid="stDownloadButton"] button:hover,
    div[data-testid="stFileUploader"] button:hover {
        border-color: var(--gp-primary) !important;
        background-color: #eff6ff !important;
        color: var(--gp-primary) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--gp-shadow-md) !important;
    }

    .stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:disabled,
    div[data-testid="stFormSubmitButton"] button:disabled {
        background-color: #f1f5f9 !important;
        border-color: #e2e8f0 !important;
        color: #94a3b8 !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* Streamlit Tabs Navigation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: #f1f5f9 !important;
        padding: 6px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: var(--gp-radius-sm) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: var(--gp-text-muted) !important;
        padding: 8px 16px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--gp-text-main) !important;
        background-color: rgba(255, 255, 255, 0.6) !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: var(--gp-primary) !important;
        box-shadow: var(--gp-shadow-sm) !important;
        font-weight: 700 !important;
    }

    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span {
        color: var(--gp-primary) !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Form & Container Borders */
    div[data-testid="stForm"],
    div[data-testid="stContainer"][data-border="true"] {
        border: 1px solid var(--gp-border) !important;
        border-radius: var(--gp-radius) !important;
        box-shadow: var(--gp-shadow-sm) !important;
        background-color: #ffffff !important;
        padding: 1.25rem 1.5rem !important;
    }

    /* Slider styling */
    .stSlider [data-baseweb="slider"] {
        padding-top: 8px;
    }
</style>
"""


def render_kpi_card(label: str, value: Any, subtext: str = "", badge_class: str = "") -> str:
    """Returns HTML for a glassmorphic KPI summary card."""
    badge_html = f'<span class="gp-badge {badge_class}">{badge_class.replace("gp-badge-", "").upper()}</span>' if badge_class else ""
    return f"""
    <div class="gp-kpi-card">
        <div class="gp-kpi-label">{label}</div>
        <div class="gp-kpi-value">{value}</div>
        {f'<div class="gp-kpi-sub">{subtext}</div>' if subtext else ''}
        {badge_html}
    </div>
    """


def render_category_badge(category: str) -> str:
    """Returns an HTML badge for Reach/Target/Safety categories."""
    cat_lower = category.lower()
    if "reach" in cat_lower or "衝刺" in cat_lower:
        cls = "gp-badge-reach"
    elif "safety" in cat_lower or "likely" in cat_lower or "保底" in cat_lower:
        cls = "gp-badge-safety"
    elif "target" in cat_lower or "核心" in cat_lower:
        cls = "gp-badge-target"
    else:
        cls = "gp-badge-warning"
    return f'<span class="gp-badge {cls}">{category}</span>'

