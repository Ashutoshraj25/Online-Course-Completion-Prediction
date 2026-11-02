"""SaaS Design System and UI Components for Course Analytics Dashboard.

Engineered with a clean, light-theme palette:
- Background: #F8FAFC
- Sidebar: #FFFFFF
- Cards: #FFFFFF
- Primary text: #0F172A
- Secondary text: #64748B
- Primary blue: #2563EB
- Success: #16A34A
- Danger: #DC2626
- Borders: #E2E8F0
"""

import streamlit as st


# Global Color System Constants
COLOR_BG_APP = "#F8FAFC"
COLOR_BG_SIDEBAR = "#FFFFFF"
COLOR_BG_CARD = "#FFFFFF"
COLOR_TEXT_PRIMARY = "#0F172A"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_ACCENT = "#2563EB"
COLOR_ACCENT_HOVER = "#1D4ED8"
COLOR_ACCENT_BG = "#EFF6FF"
COLOR_BORDER = "#E2E8F0"
COLOR_SUCCESS = "#16A34A"
COLOR_SUCCESS_BG = "#F0FDF4"
COLOR_DANGER = "#DC2626"
COLOR_DANGER_BG = "#FEF2F2"


def apply_custom_css() -> None:
    """Inject strict light-theme SaaS CSS styling."""
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Global Application Resets */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            color: {COLOR_TEXT_PRIMARY};
            -webkit-font-smoothing: antialiased;
        }}

        .stApp {{
            background-color: {COLOR_BG_APP} !important;
        }}

        /* Responsive Main Container (Zero Horizontal Overflow) */
        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 1.75rem !important;
            padding-right: 1.75rem !important;
            max-width: 100% !important;
            width: 100% !important;
            box-sizing: border-box !important;
            overflow-x: hidden !important;
        }}

        /* Sidebar Container */
        section[data-testid="stSidebar"] {{
            background-color: {COLOR_BG_SIDEBAR} !important;
            border-right: 1px solid {COLOR_BORDER} !important;
        }}

        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1.25rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}

        /* Sidebar Navigation Text Visibility */
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {{
            color: #334155 !important;
        }}

        /* Sidebar Radio Group */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {{
            gap: 0.35rem !important;
        }}

        /* Navigation Option Items */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
            background-color: transparent !important;
            padding: 0.55rem 0.75rem !important;
            border-radius: 8px !important;
            border: 1px solid transparent !important;
            transition: all 0.15s ease-in-out !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label p {{
            color: #334155 !important;
            font-size: 0.885rem !important;
            font-weight: 500 !important;
            margin: 0 !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
            background-color: #F8FAFC !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover p {{
            color: #0F172A !important;
        }}

        /* Active Selected Navigation Item */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {{
            background-color: {COLOR_ACCENT_BG} !important;
            border-color: #DBEAFE !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {{
            color: #1D4ED8 !important;
            font-weight: 600 !important;
        }}

        /* Hide Default Radio Circle Input */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {{
            display: none !important;
        }}

        /* Native Streamlit Bordered Container Cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 8px !important;
            border: 1px solid {COLOR_BORDER} !important;
            background-color: {COLOR_BG_CARD} !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02) !important;
        }}

        /* KPI Card Styles (Zero Leading Whitespace - Immune to Code Fences) */
        .kpi-card {{
            background-color: {COLOR_BG_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 8px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
            height: 125px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
        }}
        .kpi-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .kpi-label {{
            font-size: 0.775rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: {COLOR_TEXT_SECONDARY};
        }}
        .kpi-icon {{
            font-size: 1rem;
        }}
        .kpi-value {{
            font-size: 1.85rem;
            font-weight: 700;
            color: {COLOR_TEXT_PRIMARY};
            letter-spacing: -0.02em;
            line-height: 1.1;
            margin: 2px 0;
        }}
        .kpi-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .kpi-desc {{
            font-size: 0.785rem;
            color: {COLOR_TEXT_SECONDARY};
        }}

        /* Primary Action Buttons */
        div.stButton > button:first-child {{
            background-color: {COLOR_ACCENT} !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            border-radius: 8px !important;
            padding: 0.55rem 1.25rem !important;
            border: none !important;
            box-shadow: 0 1px 2px 0 rgba(37, 99, 235, 0.2) !important;
            transition: all 0.15s ease !important;
            width: 100% !important;
        }}

        div.stButton > button:first-child:hover {{
            background-color: {COLOR_ACCENT_HOVER} !important;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.25) !important;
        }}

        /* Form Labels & Controls */
        div[data-testid="stWidgetLabel"] label p {{
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            color: {COLOR_TEXT_PRIMARY} !important;
        }}

        div[data-baseweb="select"] > div {{
            border-radius: 8px !important;
            border-color: {COLOR_BORDER} !important;
            background-color: #FFFFFF !important;
            font-size: 0.875rem !important;
            color: {COLOR_TEXT_PRIMARY} !important;
        }}

        div[data-baseweb="input"] {{
            border-radius: 8px !important;
            border-color: {COLOR_BORDER} !important;
            background-color: #FFFFFF !important;
            font-size: 0.875rem !important;
            color: {COLOR_TEXT_PRIMARY} !important;
        }}

        /* Dataframe styling */
        div[data-testid="stDataFrame"] {{
            border-radius: 8px !important;
            border: 1px solid {COLOR_BORDER} !important;
            background-color: #FFFFFF !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_dashboard_header(title: str, subtitle: str) -> None:
    """Render a clean, modern SaaS header with crisp typography."""
    html = (
        f'<div style="margin-bottom: 1.25rem;">'
        f'<h1 style="font-size: 1.7rem; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; letter-spacing: -0.02em; margin: 0 0 0.25rem 0;">{title}</h1>'
        f'<p style="font-size: 0.925rem; color: {COLOR_TEXT_SECONDARY}; margin: 0; line-height: 1.45;">{subtitle}</p>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_kpi_card(
    label: str,
    value: str,
    description: str,
    icon: str = "📊",
    badge: str = "",
    badge_positive: bool = True,
) -> None:
    """Render an equal-height, white KPI card with zero leading indentation to prevent code fences."""
    badge_span = ""
    if badge:
        bg = COLOR_SUCCESS_BG if badge_positive else "#F1F5F9"
        text_color = COLOR_SUCCESS if badge_positive else COLOR_TEXT_SECONDARY
        badge_span = f'<span style="background-color:{bg};color:{text_color};font-size:0.725rem;font-weight:600;padding:2px 8px;border-radius:9999px;">{badge}</span>'

    card_html = (
        f'<div class="kpi-card">'
        f'<div class="kpi-header"><span class="kpi-label">{label}</span><span class="kpi-icon">{icon}</span></div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-footer"><span class="kpi-desc">{description}</span>{badge_span}</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_card_header(title: str, subtitle: str = "") -> None:
    """Render a clean card header with optional description."""
    sub_html = f'<div style="font-size: 0.8rem; color: {COLOR_TEXT_SECONDARY}; margin-top: 2px;">{subtitle}</div>' if subtitle else ""
    html = (
        f'<div style="margin-bottom: 0.65rem;">'
        f'<div style="font-size: 0.975rem; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; letter-spacing: -0.01em;">{title}</div>'
        f'{sub_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_prediction_result(
    predicted_label: str,
    probability_completion: float,
    model_name: str,
    explanation: str,
) -> None:
    """Render clean prediction outcome panel without code fence artifacts."""
    is_completed = predicted_label.lower() == "completed"
    status_bg = COLOR_SUCCESS_BG if is_completed else COLOR_DANGER_BG
    status_color = COLOR_SUCCESS if is_completed else COLOR_DANGER
    status_border = "#BBF7D0" if is_completed else "#FECACA"
    status_icon = "✓" if is_completed else "✕"

    panel_html = (
        f'<div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-radius: 8px; padding: 1.25rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {COLOR_BORDER}; padding-bottom: 1rem;">'
        f'<div><div style="font-size: 0.775rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: {COLOR_TEXT_SECONDARY}; margin-bottom: 4px;">Predicted Status</div>'
        f'<span style="display: inline-flex; align-items: center; gap: 4px; background-color: {status_bg}; color: {status_color}; border: 1px solid {status_border}; font-weight: 700; font-size: 1.1rem; padding: 4px 10px; border-radius: 9999px;">'
        f'{status_icon} {predicted_label.upper()}</span></div>'
        f'<div style="text-align: right;"><div style="font-size: 0.775rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: {COLOR_TEXT_SECONDARY}; margin-bottom: 2px;">Probability</div>'
        f'<div style="font-size: 1.85rem; font-weight: 700; color: {COLOR_TEXT_PRIMARY}; letter-spacing: -0.02em;">{probability_completion:.1%}</div></div>'
        f'</div>'
        f'<div style="margin-top: 1rem;">'
        f'<div style="font-size: 0.825rem; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; margin-bottom: 4px;">Assessment:</div>'
        f'<div style="font-size: 0.865rem; line-height: 1.55; color: {COLOR_TEXT_SECONDARY};">{explanation}</div>'
        f'</div>'
        f'<div style="margin-top: 0.85rem; padding-top: 0.75rem; border-top: 1px solid {COLOR_BORDER}; display: flex; justify-content: space-between; font-size: 0.75rem; color: {COLOR_TEXT_SECONDARY};">'
        f'<span>Evaluated by: <strong>{model_name}</strong></span>'
        f'<span>Engine: <strong>Spark MLlib</strong></span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(panel_html, unsafe_allow_html=True)
