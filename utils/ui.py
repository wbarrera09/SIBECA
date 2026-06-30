import streamlit as st


GOES_BLUE = "#111e60"
GOES_GOLD = "#c9a892"
GOES_DARK = "#313945"
GOES_GRAY = "#f4f5f7"
GOES_LIGHT_GRAY = "#e9ecef"
GOES_WHITE = "#ffffff"

RISK_COLORS = {
    "Alto": "#B42318",
    "Medio": "#D97706",
    "Bajo": "#15803D",
}


def apply_goes_theme():
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {GOES_GRAY};
                color: {GOES_DARK};
                font-family: "Segoe UI", Arial, sans-serif;
            }}

            h1, h2, h3 {{
                color: {GOES_BLUE};
                font-family: Georgia, "Times New Roman", serif;
                font-weight: 700;
            }}

            h1 {{
                font-size: 2.3rem;
                margin-bottom: 0.4rem;
            }}

            h2 {{
                font-size: 1.6rem;
            }}

            h3 {{
                font-size: 1.2rem;
            }}

            .block-container {{
                padding-top: 2rem;
                padding-bottom: 3rem;
            }}

            [data-testid="stSidebar"] {{
                background-color: {GOES_BLUE};
            }}

            [data-testid="stSidebar"] * {{
                color: white !important;
            }}

            [data-testid="stMetric"] {{
                background-color: {GOES_WHITE};
                border-left: 5px solid {GOES_BLUE};
                padding: 18px;
                border-radius: 14px;
                box-shadow: 0 4px 14px rgba(17, 30, 96, 0.08);
            }}

            div[data-testid="stMetricValue"] {{
                color: {GOES_BLUE};
                font-weight: 800;
            }}

            .goes-card {{
                background: {GOES_WHITE};
                padding: 20px 22px;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 6px 18px rgba(17, 30, 96, 0.08);
                margin-bottom: 18px;
            }}

            .goes-header {{
                background: {GOES_BLUE};
                color: white;
                padding: 24px 28px;
                border-radius: 18px;
                margin-bottom: 24px;
                border-left: 8px solid {GOES_GOLD};
                box-shadow: 0 8px 24px rgba(17, 30, 96, 0.16);
            }}

            .goes-header h1 {{
                color: white;
                margin: 0;
            }}

            .goes-header p {{
                color: #e5e7eb;
                margin-top: 6px;
                margin-bottom: 0;
                font-size: 1rem;
            }}

            .badge-blue {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 999px;
                background-color: {GOES_BLUE};
                color: white;
                font-size: 0.78rem;
                font-weight: 600;
            }}

            .badge-gold {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 999px;
                background-color: {GOES_GOLD};
                color: {GOES_DARK};
                font-size: 0.78rem;
                font-weight: 700;
            }}

            .stButton > button {{
                background-color: {GOES_BLUE};
                color: white;
                border-radius: 10px;
                border: none;
                padding: 0.55rem 1rem;
                font-weight: 700;
            }}

            .stButton > button:hover {{
                background-color: {GOES_DARK};
                color: white;
                border: none;
            }}

            .stDownloadButton > button {{
                background-color: {GOES_GOLD};
                color: {GOES_DARK};
                border-radius: 10px;
                border: none;
                font-weight: 700;
            }}

            .stDownloadButton > button:hover {{
                background-color: #b99479;
                color: {GOES_DARK};
                border: none;
            }}

            div[data-testid="stDataFrame"] {{
                background-color: white;
                border-radius: 14px;
                padding: 6px;
            }}

        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stForm"],
        div[data-testid="stExpander"],
        div[data-testid="stDataFrame"] {{
            background-color: #ffffff !important;
        }}

        div[data-testid="stTextInput"] [data-baseweb="input"],
        div[data-testid="stTextArea"] [data-baseweb="textarea"],
        div[data-testid="stNumberInput"] [data-baseweb="input"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] {{
            background-color: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
            min-height: 44px !important;
            color: {GOES_DARK} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] input,
        div[data-testid="stMultiSelect"] input {{
            background-color: transparent !important;
            color: {GOES_DARK} !important;
            caret-color: {GOES_BLUE} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder,
        div[data-testid="stNumberInput"] input::placeholder {{
            color: #94a3b8 !important;
            opacity: 1 !important;
        }}

        div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] span {{
            color: #64748b !important;
        }}

        div[data-testid="stSelectbox"] div[data-baseweb="select"] [data-baseweb="icon"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] [data-baseweb="icon"] {{
            color: {GOES_DARK} !important;
            fill: {GOES_DARK} !important;
        }}

        div[data-testid="stNumberInput"] button {{
            background-color: #f8fafc !important;
            color: {GOES_DARK} !important;
            border-color: #cbd5e1 !important;
            box-shadow: none !important;
        }}

        div[data-testid="stNumberInput"] button svg {{
            fill: {GOES_DARK} !important;
            color: {GOES_DARK} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="goes-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def card(title: str, body: str):
    st.markdown(
        f"""
        <div class="goes-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def risk_badge(level: str) -> str:
    color = RISK_COLORS.get(level, GOES_DARK)

    return (
        f"<span style='background:{color}; color:white; padding:4px 10px; "
        f"border-radius:999px; font-weight:700;'>{level}</span>"
    )