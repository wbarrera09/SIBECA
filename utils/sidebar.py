import streamlit as st

from utils.ui import GOES_BLUE, GOES_GOLD


def apply_sidebar_theme():
    st.markdown(
        f"""
        <style>
            section[data-testid="stSidebar"] {{
                background-color: {GOES_BLUE} !important;
                border-right: 1px solid {GOES_GOLD} !important;
            }}

            section[data-testid="stSidebar"] > div {{
                background-color: {GOES_BLUE} !important;
            }}

            div[data-testid="stSidebarContent"] {{
                background-color: {GOES_BLUE} !important;
            }}

            section[data-testid="stSidebar"] * {{
                color: #ffffff !important;
            }}

            section[data-testid="stSidebar"] a {{
                color: #ffffff !important;
                text-decoration: none !important;
            }}

            section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
                background-color: {GOES_BLUE} !important;
            }}

            section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {{
                background-color: {GOES_BLUE} !important;
            }}

            section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {{
                background-color: transparent !important;
            }}

            section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {{
                background-color: transparent !important;
                border-radius: 0 !important;
            }}

            section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li:hover {{
                background-color: transparent !important;
            }}

            section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a {{
                border-radius: 8px !important;
            }}

            section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a:hover {{
                background-color: rgba(255, 255, 255, 0.10) !important;
            }}

            section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li [aria-current="page"] {{
                background-color: rgba(255, 255, 255, 0.18) !important;
                border-radius: 8px !important;
                font-weight: 800 !important;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )