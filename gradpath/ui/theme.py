from __future__ import annotations

from typing import Any

# UI/UX Pro Max Design Intelligence System
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --gp-bg: #f8fafc;
        --gp-panel: #ffffff;
        --gp-text-main: #0f172a;
        --gp-text-muted: #64748b;
        --gp-border: #e2e8f0;
        --gp-primary: #2563eb;
        --gp-primary-hover: #1d4ed8;
        --gp-primary-light: #eff6ff;
        --gp-accent: #0d9488;
        --gp-accent-light: #ccfbf1;
        --gp-success: #16a34a;
        --gp-success-light: #f0fdf4;
        --gp-warning: #d97706;
        --gp-warning-light: #fffbeb;
        --gp-risk: #dc2626;
        --gp-risk-light: #fef2f2;
        --gp-glass-bg: rgba(255, 255, 255, 0.85);
        --gp-glass-border: rgba(226, 232, 240, 0.8);
        --gp-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --gp-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
        --gp-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
        --gp-radius: 12px;
    }

    .stApp {
        background-color: var(--gp-bg);
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        color: var(--gp-text-main);
    }

    .stMainBlockContainer {
        max-width: 1440px;
        padding: 2.5rem 3rem;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: var(--gp-text-main) !important;
    }

    .gp-main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: var(--gp-shadow-lg);
        position: relative;
        overflow: hidden;
    }

    .gp-main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, rgba(13, 148, 136, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .gp-main-title {
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff !important;
    }

    .gp-main-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* KPI Glassmorphic Cards */
    .gp-kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.25rem;
        margin-bottom: 2rem;
    }

    .gp-kpi-card {
        background: var(--gp-glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--gp-glass-border);
        border-radius: var(--gp-radius);
        padding: 1.25rem 1.5rem;
        box-shadow: var(--gp-shadow-sm);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .gp-kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--gp-shadow-md);
    }

    .gp-kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--gp-text-muted);
        margin-bottom: 0.5rem;
    }

    .gp-kpi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--gp-text-main);
        line-height: 1.1;
    }

    .gp-kpi-sub {
        font-size: 0.8rem;
        color: var(--gp-text-muted);
        margin-top: 0.35rem;
    }

    /* Category & Fit Badges */
    .gp-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.025em;
    }

    .gp-badge-reach {
        background-color: var(--gp-risk-light);
        color: var(--gp-risk);
        border: 1px solid rgba(220, 38, 38, 0.2);
    }

    .gp-badge-target {
        background-color: var(--gp-primary-light);
        color: var(--gp-primary);
        border: 1px solid rgba(37, 99, 235, 0.2);
    }

    .gp-badge-safety {
        background-color: var(--gp-success-light);
        color: var(--gp-success);
        border: 1px solid rgba(22, 163, 74, 0.2);
    }

    .gp-badge-warning {
        background-color: var(--gp-warning-light);
        color: var(--gp-warning);
        border: 1px solid rgba(217, 119, 6, 0.2);
    }

    /* Card Panels */
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
        font-weight: 600;
        color: var(--gp-text-main);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Sidebar Styling & Crisp Dark Font inside White Bars */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }

    /* Sidebar Labels & Captions */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] caption,
    section[data-testid="stSidebar"] .stMarkdown small {
        color: #94a3b8 !important;
    }

    /* White Input Bars on Sidebar: White Background + High Contrast Dark Text (#0f172a) */
    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #0f172a !important;
        fill: #0f172a !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] input {
        color: #0f172a !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] div {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #0f172a !important;
    }

    /* Multi-select Tags inside White Bars */
    section[data-testid="stSidebar"] span[data-baseweb="tag"] {
        background-color: #e2e8f0 !important;
        border-radius: 6px !important;
    }

    section[data-testid="stSidebar"] span[data-baseweb="tag"] * {
        color: #0f172a !important;
    }

    /* Dropdown Menu Popover styling (white background + dark text) */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }

    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] div {
        color: #0f172a !important;
        background-color: #ffffff !important;
    }

    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] div:hover {
        background-color: #f1f5f9 !important;
        color: #2563eb !important;
    }

    /* Sidebar Clear Filters button */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        width: 100%;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
    }

    /* Form Controls & Main Area Inputs */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: var(--gp-text-main) !important;
    }

    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25) !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
        transform: translateY(-1px);
    }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        color: var(--gp-text-muted);
        padding: 8px 16px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: var(--gp-primary) !important;
        box-shadow: var(--gp-shadow-sm);
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
    if "reach" in cat_lower:
        cls = "gp-badge-reach"
    elif "safety" in cat_lower or "likely" in cat_lower:
        cls = "gp-badge-safety"
    elif "target" in cat_lower:
        cls = "gp-badge-target"
    else:
        cls = "gp-badge-warning"
    return f'<span class="gp-badge {cls}">{category}</span>'
