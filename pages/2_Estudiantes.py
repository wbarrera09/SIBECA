import streamlit as st
import pandas as pd
from sqlalchemy import text
from html import escape

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD, GOES_DARK
from utils.sidebar import apply_sidebar_theme
from utils.pagination import render_pagination

st.set_page_config(
    page_title="Estudiantes | SIBECA",
    page_icon="",
    layout="wide"
)

apply_goes_theme()
apply_sidebar_theme()

EMPTY_PLACEHOLDER = " "


EL_SALVADOR_MUNICIPALITIES = {
    "Ahuachapán": [
        "Ahuachapán Norte",
        "Ahuachapán Centro",
        "Ahuachapán Sur"
    ],
    "Santa Ana": [
        "Santa Ana Norte",
        "Santa Ana Centro",
        "Santa Ana Este",
        "Santa Ana Oeste"
    ],
    "Sonsonate": [
        "Sonsonate Norte",
        "Sonsonate Centro",
        "Sonsonate Este",
        "Sonsonate Oeste"
    ],
    "Chalatenango": [
        "Chalatenango Norte",
        "Chalatenango Centro",
        "Chalatenango Sur"
    ],
    "La Libertad": [
        "La Libertad Norte",
        "La Libertad Centro",
        "La Libertad Oeste",
        "La Libertad Este",
        "La Libertad Costa",
        "La Libertad Sur"
    ],
    "San Salvador": [
        "San Salvador Norte",
        "San Salvador Oeste",
        "San Salvador Este",
        "San Salvador Centro",
        "San Salvador Sur"
    ],
    "Cuscatlán": [
        "Cuscatlán Norte",
        "Cuscatlán Sur"
    ],
    "La Paz": [
        "La Paz Oeste",
        "La Paz Centro",
        "La Paz Este"
    ],
    "Cabañas": [
        "Cabañas Este",
        "Cabañas Oeste"
    ],
    "San Vicente": [
        "San Vicente Norte",
        "San Vicente Sur"
    ],
    "Usulután": [
        "Usulután Norte",
        "Usulután Este",
        "Usulután Oeste"
    ],
    "San Miguel": [
        "San Miguel Norte",
        "San Miguel Centro",
        "San Miguel Oeste"
    ],
    "Morazán": [
        "Morazán Norte",
        "Morazán Sur"
    ],
    "La Unión": [
        "La Unión Norte",
        "La Unión Sur"
    ]
}

DEPARTMENT_OPTIONS = list(EL_SALVADOR_MUNICIPALITIES.keys())

ADD_NEW_OPTION = "Agregar nuevo"

st.markdown(
    f"""
    <style>
        .block-container {{
            padding-top: 1.5rem;
            padding-left: 1.8rem;
            padding-right: 1.8rem;
            max-width: 1500px;
        }}

        body, .stApp, div, p, label, input, textarea, button {{
            font-family: "Segoe UI", Arial, sans-serif !important;
        }}

        h1, h2, h3 {{
            font-family: "Segoe UI", Arial, sans-serif !important;
        }}

        .goes-header h1 {{
            font-family: "Segoe UI", Arial, sans-serif !important;
        }}

        .goes-header {{
            background: {GOES_BLUE} !important;
            border-left: 8px solid {GOES_GOLD} !important;
            box-shadow: 0 8px 24px rgba(17, 30, 96, 0.16) !important;
        }}

        .students-section-title {{
            color: {GOES_BLUE};
            font-family: "Segoe UI", Arial, sans-serif !important;
            font-weight: 800;
            font-size: 1.05rem;
            border-left: 5px solid {GOES_GOLD};
            padding-left: 10px;
            margin-top: 14px;
            margin-bottom: 12px;
        }}

        .students-filter-title {{
            background: {GOES_BLUE};
            color: #ffffff;
            padding: 10px 14px;
            border-radius: 10px;
            border-left: 5px solid {GOES_GOLD};
            font-weight: 700;
            margin-top: 10px;
            margin-bottom: 10px;
            font-size: 0.9rem;
        }}

        .students-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.06);
            min-height: 92px;
            margin-bottom: 10px;
        }}

        .students-card-blue {{
            border-top: 4px solid {GOES_BLUE};
        }}

        .students-card-gold {{
            border-top: 4px solid {GOES_GOLD};
        }}

        .students-card-gray {{
            border-top: 4px solid #64748b;
        }}

        .students-kpi-label {{
            color: {GOES_DARK};
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 6px;
        }}

        .students-kpi-value {{
            color: {GOES_BLUE};
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 5px;
        }}

        .students-kpi-help {{
            color: #64748b;
            font-size: 0.72rem;
        }}

        .student-profile-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.06);
            margin-bottom: 12px;
        }}

        .student-profile-name {{
            color: {GOES_BLUE};
            font-weight: 900;
            font-size: 1.35rem;
            line-height: 1.2;
            margin-bottom: 4px;
        }}

        .student-profile-subtitle {{
            color: #64748b;
            font-size: 0.86rem;
            margin-bottom: 12px;
        }}

        .student-badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            background: {GOES_BLUE};
            color: #ffffff;
            font-size: 0.75rem;
            font-weight: 800;
            margin-right: 6px;
            margin-bottom: 6px;
        }}

        .student-badge-gold {{
            background: {GOES_GOLD};
            color: {GOES_DARK};
        }}

        .student-badge-gray {{
            background: #e2e8f0;
            color: {GOES_DARK};
        }}

        .student-detail-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px 16px;
            margin-top: 8px;
        }}

        .student-detail-item {{
            border-bottom: 1px solid #eef0f3;
            padding-bottom: 8px;
        }}

        .student-detail-label {{
            color: #64748b;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-bottom: 2px;
        }}

        .student-detail-value {{
            color: {GOES_DARK};
            font-size: 0.92rem;
            font-weight: 600;
            word-break: break-word;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            overflow: visible !important;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.06);
            position: relative !important;
        }}

        div[data-testid="stDataFrame"] div[data-testid="stElementToolbar"] {{
            opacity: 1 !important;
            visibility: visible !important;
            z-index: 9999 !important;
        }}

        div[data-testid="stDataFrame"] [role="columnheader"] {{
            background-color: {GOES_BLUE} !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 0.78rem !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: #d9dee7 !important;
            border-radius: 14px !important;
            background: transparent !important;
        }}

        div[data-testid="stExpander"] {{
            background: #ffffff !important;
            border: 1px solid #d9dee7;
            border-radius: 14px;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.05);
            overflow: hidden;
        }}

        div[data-testid="stExpander"] summary {{
            background-color: #ffffff !important;
            color: {GOES_BLUE} !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
            min-height: 42px;
            padding-top: 10px !important;
            padding-bottom: 10px !important;
            display: flex !important;
            align-items: center !important;
            transition: background-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease !important;
        }}

        div[data-testid="stExpander"] details[open] > summary {{
            background-color: #ffffff !important;
            color: {GOES_BLUE} !important;
            border-bottom: 1px solid #d9dee7 !important;
        }}

        div[data-testid="stExpander"] summary:hover,
        div[data-testid="stExpander"] details[open] > summary:hover {{
            background-color: #f8fafc !important;
            box-shadow: inset 4px 0 0 {GOES_GOLD} !important;
        }}

        div[data-testid="stExpander"] summary p {{
            margin: 0 !important;
            color: {GOES_BLUE} !important;
        }}

        div[data-testid="stExpander"] summary svg {{
            display: none !important;
        }}

        div[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {{
            display: none !important;
        }}

        div[data-testid="stExpander"] summary::before {{
            content: "▼";
            color: {GOES_BLUE};
            font-size: 0.72rem;
            margin-right: 8px;
        }}

        div[data-testid="stTextInput"] div,
        div[data-testid="stTextArea"] div,
        div[data-testid="stNumberInput"] div,
        div[data-testid="stSelectbox"] div,
        div[data-testid="stMultiSelect"] div {{
            font-family: "Segoe UI", Arial, sans-serif !important;
            max-width: 100% !important;
        }}

        div[data-testid="stTextInput"] [data-baseweb="input"],
        div[data-testid="stTextArea"] [data-baseweb="textarea"],
        div[data-testid="stNumberInput"] [data-baseweb="input"] {{
            background-color: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
            min-height: 44px !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stTextInput"] [data-baseweb="input"]:hover,
        div[data-testid="stTextArea"] [data-baseweb="textarea"]:hover,
        div[data-testid="stNumberInput"] [data-baseweb="input"]:hover {{
            background-color: #ffffff !important;
            border-color: {GOES_BLUE} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
        div[data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,
        div[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within {{
            background-color: #ffffff !important;
            border-color: {GOES_BLUE} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input {{
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

        div[data-testid="stNumberInput"] button {{
            background-color: #f8fafc !important;
            color: {GOES_DARK} !important;
            border-color: #cbd5e1 !important;
            box-shadow: none !important;
        }}

        div[data-testid="stNumberInput"] button:hover {{
            background-color: #ffffff !important;
            color: {GOES_BLUE} !important;
            border-color: {GOES_BLUE} !important;
        }}

        div[data-testid="stNumberInput"] button svg {{
            fill: {GOES_DARK} !important;
            color: {GOES_DARK} !important;
        }}

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

        div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"]:hover {{
            background-color: #ffffff !important;
            border-color: {GOES_BLUE} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"]:focus-within {{
            background-color: #ffffff !important;
            border-color: {GOES_BLUE} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            min-height: 42px !important;
            max-height: 42px !important;
            overflow: hidden !important;
            align-items: center !important;
            padding-top: 4px !important;
            padding-bottom: 4px !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            min-height: 42px !important;
            max-height: 120px !important;
            overflow-y: auto !important;
            align-items: flex-start !important;
            padding-top: 4px !important;
            padding-bottom: 4px !important;
        }}

        div[data-testid="stSelectbox"] div[data-baseweb="select"] input,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] input {{
            color: {GOES_DARK} !important;
            background-color: transparent !important;
            box-shadow: none !important;
            outline: none !important;
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

        div[data-baseweb="tag"] {{
            background-color: {GOES_BLUE} !important;
            border: 1px solid {GOES_BLUE} !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            max-width: 180px !important;
            margin-top: 2px !important;
            margin-bottom: 2px !important;
            flex-shrink: 0 !important;
        }}

        div[data-baseweb="tag"] span {{
            color: #ffffff !important;
            opacity: 1 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
            max-width: 145px !important;
        }}

        div[data-baseweb="tag"] svg {{
            fill: #ffffff !important;
            color: #ffffff !important;
            flex-shrink: 0 !important;
        }}

        div[data-testid="stButton"] button {{
            min-height: 42px !important;
            padding: 0.25rem 0.55rem !important;
            border-radius: 10px !important;
            background-color: {GOES_BLUE} !important;
            color: #ffffff !important;
            border: none !important;
            margin-top: 10px;
            margin-bottom: 10px;
        }}

        div[data-testid="stButton"] button:hover {{
            background-color: {GOES_DARK} !important;
            color: #ffffff !important;
        }}

        div[data-testid="stButton"] button span {{
            color: #ffffff !important;
        }}

        div[data-testid="stFormSubmitButton"] button {{
            background-color: {GOES_BLUE} !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: 800 !important;
        }}

        div[data-testid="stFormSubmitButton"] button:hover {{
            background-color: {GOES_DARK} !important;
            color: #ffffff !important;
        }}

        input:-webkit-autofill,
        input:-webkit-autofill:hover,
        input:-webkit-autofill:focus {{
            -webkit-text-fill-color: {GOES_DARK} !important;
            box-shadow: 0 0 0px 1000px #f8fafc inset !important;
            transition: background-color 5000s ease-in-out 0s !important;
        }}


        div[class*="st-key-students_list_pager_controls"] {{
            margin-top: 4px !important;
            margin-bottom: 10px !important;
        }}

        div[class*="st-key-students_list_pager_prev"] button,
        div[class*="st-key-students_list_pager_next"] button {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: {GOES_BLUE} !important;
            min-height: 34px !important;
            height: 34px !important;
            width: 34px !important;
            padding: 0 !important;
            border-radius: 8px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 900 !important;
        }}

        div[class*="st-key-students_list_pager_prev"] button:hover,
        div[class*="st-key-students_list_pager_next"] button:hover {{
            background: #f1f5f9 !important;
            color: {GOES_BLUE} !important;
            border: none !important;
            box-shadow: none !important;
        }}

        div[class*="st-key-students_list_pager_prev"] button:disabled,
        div[class*="st-key-students_list_pager_next"] button:disabled {{
            background: transparent !important;
            color: #cbd5e1 !important;
            opacity: 1 !important;
        }}

        div[class*="st-key-students_list_pager_prev"] button p,
        div[class*="st-key-students_list_pager_next"] button p,
        div[class*="st-key-students_list_pager_prev"] button span,
        div[class*="st-key-students_list_pager_next"] button span {{
            color: inherit !important;
            font-size: 1.35rem !important;
            font-weight: 900 !important;
            line-height: 1 !important;
            margin: 0 !important;
        }}

        .students-pager-label {{
            height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            font-weight: 800;
            color: {GOES_BLUE};
            white-space: nowrap;
            line-height: 1;
        }}

        .students-pager-info {{
            height: 34px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            font-size: 0.82rem;
            color: #64748b;
            white-space: nowrap;
            line-height: 1;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"],
        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {{
            background-color: {GOES_BLUE} !important;
            border: 1px solid {GOES_BLUE} !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            max-width: 100% !important;
            min-width: 0 !important;
            width: auto !important;
            display: inline-flex !important;
            align-items: center !important;
            overflow: hidden !important;
            white-space: nowrap !important;
            margin-top: 2px !important;
            margin-bottom: 2px !important;
            flex-shrink: 1 !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span,
        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span,
        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span[title],
        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span[title] {{
            color: #ffffff !important;
            opacity: 1 !important;
            display: block !important;
            max-width: 100% !important;
            min-width: 0 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] svg,
        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] svg {{
            fill: #ffffff !important;
            color: #ffffff !important;
            flex-shrink: 0 !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
            flex-wrap: wrap !important;
            max-height: 130px !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }}

    </style>
    """,
    unsafe_allow_html=True
)

page_header(
    "Gestión de Estudiantes",
    "Registro, consulta, actualización y administración de estudiantes becados."
)

engine = get_engine()


@st.cache_data(ttl=1800, show_spinner=False)
def load_modalities():
    return pd.read_sql(
        "SELECT id, name FROM modalities ORDER BY id",
        engine
    )


@st.cache_data(ttl=1800, show_spinner=False)
def load_students():
    return pd.read_sql(
        """
        SELECT 
            s.id,
            s.student_code,
            s.full_name,
            s.age,
            s.sex,
            s.email,
            s.phone,
            s.department,
            s.municipality,
            s.address_reference,
            s.education_level,
            s.institution_name,
            s.career,
            s.modality_id,
            m.name AS modality,
            s.scholarship_type,
            s.support_percentage,
            s.status,
            s.assigned_monitor,
            s.enrollment_date
        FROM students s
        LEFT JOIN modalities m ON s.modality_id = m.id
        ORDER BY s.id DESC
        """,
        engine
    )


def render_section_title(title):
    st.markdown(
        f"""
        <div class="students-section-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_filter_title(title):
    st.markdown(
        f"""
        <div class="students-filter-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_kpi(label, value, help_text, variant):
    css_class = f"students-card students-card-{variant}"

    st.markdown(
        f"""
        <div class="{css_class}">
            <div class="students-kpi-label">{label}</div>
            <div class="students-kpi-value">{value}</div>
            <div class="students-kpi-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def safe_text(value):
    if pd.isna(value) or value is None:
        return ""
    return escape(str(value))


def clean_text(value):
    if pd.isna(value) or value is None:
        return ""
    return str(value)


def clean_int(value, default=0):
    if pd.isna(value) or value is None:
        return default
    return int(value)


def clean_percentage(value, default=0):
    if pd.isna(value) or value is None:
        return default
    return int(value)


def get_option_index(options, value, default_index=0):
    if value in options:
        return options.index(value)
    return default_index


def get_distinct_options(dataframe, column):
    if dataframe.empty or column not in dataframe.columns:
        return []

    values = (
        dataframe[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[
        (values != "")
        & (values.str.lower() != "sin dato")
        & (values.str.lower() != "none")
        & (values.str.lower() != "nan")
    ]

    return sorted(values.drop_duplicates().tolist())


def reference_value_input(label, existing_options, key_prefix, current_value=""):
    current_value = clean_text(current_value).strip()

    options = [
        option
        for option in existing_options
        if option and option.strip()
    ]

    options = sorted(set(options))

    select_options = [ADD_NEW_OPTION] + options

    if current_value in options:
        default_index = select_options.index(current_value)
        default_new_value = ""
    else:
        default_index = 0
        default_new_value = current_value

    selected_value = st.selectbox(
        label,
        options=select_options,
        index=default_index,
        key=f"{key_prefix}_select"
    )

    if selected_value == ADD_NEW_OPTION:
        return st.text_input(
            f"{label} nuevo",
            value=default_new_value,
            key=f"{key_prefix}_new"
        ).strip()

    return selected_value.strip()


def get_current_department(value):
    value = clean_text(value).strip()

    if value in DEPARTMENT_OPTIONS:
        return value

    return DEPARTMENT_OPTIONS[0]


def get_current_municipality(department, value):
    value = clean_text(value).strip()
    municipality_options = EL_SALVADOR_MUNICIPALITIES.get(department, [])

    if value in municipality_options:
        return value

    if municipality_options:
        return municipality_options[0]

    return ""


def clear_student_cache():
    st.cache_data.clear()

def reset_student_filters():
    st.session_state["students_filter_student"] = None
    st.session_state["students_filter_department"] = []
    st.session_state["students_filter_modality"] = []
    st.session_state["students_filter_status"] = []
    st.session_state["students_filter_scholarship"] = []
    st.session_state["students_filter_career"] = []
    st.session_state["students_filter_monitor"] = []
    st.session_state["students_filter_support"] = (0, 100)
    st.session_state["students_list_page_number"] = 1


def create_student(payload):
    with engine.begin() as conn:
        next_id = conn.execute(
            text("SELECT COALESCE(MAX(id), 0) + 1 FROM students")
        ).scalar()

        student_code = f"BEC-{next_id:04d}"

        conn.execute(
            text(
                """
                INSERT INTO students (
                    student_code,
                    full_name,
                    age,
                    sex,
                    email,
                    phone,
                    department,
                    municipality,
                    address_reference,
                    education_level,
                    institution_name,
                    career,
                    modality_id,
                    scholarship_type,
                    support_percentage,
                    status,
                    assigned_monitor,
                    enrollment_date
                )
                VALUES (
                    :student_code,
                    :full_name,
                    :age,
                    :sex,
                    :email,
                    :phone,
                    :department,
                    :municipality,
                    :address_reference,
                    :education_level,
                    :institution_name,
                    :career,
                    :modality_id,
                    :scholarship_type,
                    :support_percentage,
                    :status,
                    :assigned_monitor,
                    CURRENT_DATE
                )
                """
            ),
            {
                **payload,
                "student_code": student_code
            }
        )

    return student_code


def update_student(student_id, payload):
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE students
                SET
                    full_name = :full_name,
                    age = :age,
                    sex = :sex,
                    email = :email,
                    phone = :phone,
                    department = :department,
                    municipality = :municipality,
                    address_reference = :address_reference,
                    education_level = :education_level,
                    institution_name = :institution_name,
                    career = :career,
                    modality_id = :modality_id,
                    scholarship_type = :scholarship_type,
                    support_percentage = :support_percentage,
                    status = :status,
                    assigned_monitor = :assigned_monitor
                WHERE id = :student_id
                """
            ),
            {
                **payload,
                "student_id": int(student_id)
            }
        )


modalities = load_modalities()

if modalities.empty:
    st.warning("No hay modalidades cargadas.")
    st.stop()

students_df = load_students()

if students_df.empty:
    student_options = []
else:
    student_lookup = students_df[
        [
            "student_code",
            "full_name"
        ]
    ].drop_duplicates().copy()

    student_lookup["student_selector"] = (
        student_lookup["student_code"]
        + " - "
        + student_lookup["full_name"]
    )

    student_lookup = student_lookup.sort_values("student_selector")
    student_options = student_lookup["student_selector"].tolist()

institution_options = get_distinct_options(students_df, "institution_name")
career_reference_options = get_distinct_options(students_df, "career")
monitor_reference_options = get_distinct_options(students_df, "assigned_monitor")

modality_options = dict(zip(modalities["name"], modalities["id"]))
modality_names = list(modality_options.keys())

sex_options = [
    "Masculino",
    "Femenino",
    "Otro",
    "Prefiere no decir"
]

education_options = [
    "Bachillerato",
    "Técnico",
    "Universitario"
]

scholarship_options = [
    "Total",
    "Parcial"
]

status_options = [
    "Activo",
    "En riesgo",
    "Suspendido",
    "Retirado",
    "Graduado"
]

tab1, tab2, tab3 = st.tabs(
    [
        "Listado",
        "Nuevo estudiante",
        "Ficha y edición"
    ]
)

with tab1:
    render_section_title("Listado de estudiantes")

    if students_df.empty:
        st.info("No hay estudiantes registrados.")
    else:
        total_students = len(students_df)
        active_students = len(students_df[students_df["status"] == "Activo"])
        risk_students = len(students_df[students_df["status"] == "En riesgo"])
        avg_support = students_df["support_percentage"].fillna(0).mean()

        col_kpi_1, col_kpi_2, col_kpi_3, col_kpi_4 = st.columns(4)

        with col_kpi_1:
            render_kpi("Total estudiantes", f"{total_students:,}", "Registros existentes", "blue")

        with col_kpi_2:
            render_kpi("Activos", f"{active_students:,}", "Estudiantes activos", "gold")

        with col_kpi_3:
            render_kpi("En riesgo", f"{risk_students:,}", "Requieren seguimiento", "gray")

        with col_kpi_4:
            render_kpi("Apoyo promedio", f"{avg_support:.1f}%", "Promedio de apoyo", "blue")

        with st.expander("Mostrar / ocultar filtros de búsqueda", expanded=True):
            col_filter_title, col_filter_button = st.columns([10, 1])

            with col_filter_title:
                render_filter_title("Seleccione los filtros para consultar estudiantes")

            with col_filter_button:
                st.button(
                    "",
                    icon=":material/filter_alt_off:",
                    help="Limpiar filtros",
                    use_container_width=True,
                    on_click=reset_student_filters
                )

            with st.container(border=True):
                col_f1, col_f2, col_f3, col_f4 = st.columns([2.4, 2.0, 1.3, 1.1])

                with col_f1:
                    selected_student = st.selectbox(
                        "Buscar estudiante",
                        options=student_options,
                        index=None,
                        placeholder=EMPTY_PLACEHOLDER,
                        key="students_filter_student"
                    )

                with col_f2:
                    career_filter = st.multiselect(
                        "Carrera",
                        options=sorted(students_df["career"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="students_filter_career"
                    )

                with col_f3:
                    department_filter = st.multiselect(
                        "Departamento",
                        options=sorted(students_df["department"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="students_filter_department"
                    )

                with col_f4:
                    status_filter = st.multiselect(
                        "Estado",
                        options=sorted(students_df["status"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="students_filter_status"
                    )

                col_f5, col_f6, col_f7 = st.columns([1.3, 1.4, 2.1])

                with col_f5:
                    modality_filter = st.multiselect(
                        "Modalidad",
                        options=sorted(students_df["modality"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="students_filter_modality"
                    )

                with col_f6:
                    scholarship_filter = st.multiselect(
                        "Tipo de beca",
                        options=sorted(students_df["scholarship_type"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="students_filter_scholarship"
                    )

                with col_f7:
                    monitor_filter = st.multiselect(
                        "Monitor asignado",
                        options=sorted(students_df["assigned_monitor"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="students_filter_monitor"
                    )

            with st.expander("Filtros avanzados", expanded=False):
                support_range = st.slider(
                    "Apoyo económico",
                    min_value=0,
                    max_value=100,
                    value=(0, 100),
                    step=5,
                    key="students_filter_support"
                )
        filtered = students_df.copy()

        if selected_student:
            selected_student_code = selected_student.split(" - ")[0]
            filtered = filtered[
                filtered["student_code"] == selected_student_code
            ]

        if department_filter:
            filtered = filtered[filtered["department"].isin(department_filter)]

        if modality_filter:
            filtered = filtered[filtered["modality"].isin(modality_filter)]

        if status_filter:
            filtered = filtered[filtered["status"].isin(status_filter)]

        if scholarship_filter:
            filtered = filtered[filtered["scholarship_type"].isin(scholarship_filter)]

        if career_filter:
            filtered = filtered[filtered["career"].isin(career_filter)]

        if monitor_filter:
            filtered = filtered[filtered["assigned_monitor"].isin(monitor_filter)]

        filtered = filtered[
            (filtered["support_percentage"].fillna(0) >= support_range[0])
            & (filtered["support_percentage"].fillna(0) <= support_range[1])
        ]

        st.caption(f"Mostrando {len(filtered):,} de {len(students_df):,} estudiantes.")

        table_view = filtered[
            [
                "student_code",
                "full_name",
                "department",
                "municipality",
                "career",
                "modality",
                "scholarship_type",
                "support_percentage",
                "status",
                "assigned_monitor",
                "email",
                "phone"
            ]
        ].copy()

        table_view = table_view.rename(
            columns={
                "student_code": "Código",
                "full_name": "Estudiante",
                "department": "Departamento",
                "municipality": "Municipio",
                "career": "Carrera",
                "modality": "Modalidad",
                "scholarship_type": "Tipo de beca",
                "support_percentage": "Apoyo",
                "status": "Estado",
                "assigned_monitor": "Monitor",
                "email": "Correo",
                "phone": "Teléfono"
            }
        )

        total_records = len(table_view)

        page_size, page_number, start_row, end_row = render_pagination(
            total_records=total_records,
            key_prefix="students_list",
            label="estudiantes"
        )

        paginated_table = table_view.iloc[start_row:end_row]

        
        st.dataframe(
            paginated_table,
            use_container_width=True,
            hide_index=True,
            height=460,
            column_config={
                "Código": st.column_config.TextColumn("Código", width="small"),
                "Estudiante": st.column_config.TextColumn("Estudiante", width="medium"),
                "Departamento": st.column_config.TextColumn("Departamento", width="small"),
                "Municipio": st.column_config.TextColumn("Municipio", width="small"),
                "Carrera": st.column_config.TextColumn("Carrera", width="medium"),
                "Modalidad": st.column_config.TextColumn("Modalidad", width="small"),
                "Tipo de beca": st.column_config.TextColumn("Tipo de beca", width="small"),
                "Apoyo": st.column_config.ProgressColumn(
                    "Apoyo",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                    width="small"
                ),
                "Estado": st.column_config.TextColumn("Estado", width="small"),
                "Monitor": st.column_config.TextColumn("Monitor", width="small"),
                "Correo": st.column_config.TextColumn("Correo", width="medium"),
                "Teléfono": st.column_config.TextColumn("Teléfono", width="small")
            }
        )

with tab2:
    render_section_title("Registrar nuevo estudiante")

    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            render_filter_title("Datos personales")

            full_name = st.text_input(
                "Nombre completo",
                key="new_student_full_name"
            )
            age = st.number_input(
                "Edad",
                min_value=10,
                max_value=80,
                value=18,
                key="new_student_age"
            )
            sex = st.selectbox(
                "Sexo",
                sex_options,
                key="new_student_sex"
            )
            email = st.text_input(
                "Correo",
                key="new_student_email"
            )
            phone = st.text_input(
                "Teléfono",
                key="new_student_phone"
            )
            department = st.selectbox(
                "Departamento",
                options=DEPARTMENT_OPTIONS,
                key="new_student_department"
            )
            municipality = st.selectbox(
                "Municipio",
                options=EL_SALVADOR_MUNICIPALITIES.get(department, []),
                key=f"new_student_municipality_{department}"
            )
            address_reference = st.text_area(
                "Dirección o referencia",
                key="new_student_address_reference"
            )

        with col2:
            render_filter_title("Datos académicos y beca")

            education_level = st.selectbox(
                "Nivel de escolaridad",
                education_options,
                key="new_student_education_level"
            )
            institution_name = reference_value_input(
                "Universidad / Colegio / Institución",
                institution_options,
                "new_student_institution"
            )
            career = reference_value_input(
                "Carrera / curso",
                career_reference_options,
                "new_student_career"
            )
            modality_name = st.selectbox(
                "Modalidad",
                modality_names,
                key="new_student_modality"
            )
            scholarship_type = st.selectbox(
                "Tipo de beca",
                scholarship_options,
                key="new_student_scholarship_type"
            )
            support_percentage = st.number_input(
                "Porcentaje de apoyo económico",
                min_value=0,
                max_value=100,
                value=100,
                key="new_student_support_percentage"
            )
            status = st.selectbox(
                "Estado",
                status_options,
                key="new_student_status"
            )
            assigned_monitor = reference_value_input(
                "Monitor asignado",
                monitor_reference_options,
                "new_student_monitor"
            )

        submitted = st.button(
            "Guardar estudiante",
            use_container_width=True,
            key="new_student_submit"
        )

        if submitted:
            if not full_name.strip():
                st.error("El nombre completo es obligatorio.")
            elif not institution_name.strip():
                st.error("La institución es obligatoria.")
            elif not career.strip():
                st.error("La carrera o curso es obligatorio.")
            elif not assigned_monitor.strip():
                st.error("El monitor asignado es obligatorio.")
            else:
                payload = {
                    "full_name": full_name.strip(),
                    "age": int(age),
                    "sex": sex,
                    "email": email.strip(),
                    "phone": phone.strip(),
                    "department": department,
                    "municipality": municipality,
                    "address_reference": address_reference.strip(),
                    "education_level": education_level,
                    "institution_name": institution_name.strip(),
                    "career": career.strip(),
                    "modality_id": modality_options[modality_name],
                    "scholarship_type": scholarship_type,
                    "support_percentage": int(support_percentage),
                    "status": status,
                    "assigned_monitor": assigned_monitor.strip()
                }

                student_code = create_student(payload)
                clear_student_cache()
                st.success(f"Estudiante guardado correctamente con código {student_code}")

with tab3:
    render_section_title("Ficha y edición del estudiante")

    if st.session_state.get('update_success', False):
        st.success("Información del estudiante actualizada correctamente.")
        st.session_state['update_success'] = False

    if students_df.empty:
        st.info("No hay estudiantes registrados.")
    else:
        selected = st.selectbox(
            "Seleccionar estudiante",
            options=student_options,
            index=None,
            placeholder=EMPTY_PLACEHOLDER,
            key="selected_student_profile"
        )

        if not selected:
            st.info("Seleccioná un estudiante para consultar o actualizar su información.")
        else:
            code = selected.split(" - ")[0]
            student = students_df[students_df["student_code"] == code].iloc[0]
            student_id = int(student["id"])

            col_profile, col_edit = st.columns([1.1, 1.4])

            with col_profile:
                st.markdown(
                    f"""
                    <div class="student-profile-card">
                        <div class="student-profile-name">{safe_text(student["full_name"])}</div>
                        <div class="student-profile-subtitle">{safe_text(student["student_code"])} · {safe_text(student["career"])}</div>
                        <span class="student-badge">{safe_text(student["status"])}</span>
                        <span class="student-badge student-badge-gold">{safe_text(student["scholarship_type"])}</span>
                        <span class="student-badge student-badge-gray">{safe_text(student["modality"])}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col_m1, col_m2, col_m3 = st.columns(3)

                with col_m1:
                    render_kpi("Código", safe_text(student["student_code"]), "Identificador", "blue")

                with col_m2:
                    render_kpi("Apoyo", f"{clean_percentage(student['support_percentage'])}%", "Apoyo económico", "gold")

                with col_m3:
                    render_kpi("Estado", safe_text(student["status"]), "Situación actual", "gray")

                render_section_title("Datos generales")

                st.markdown(
                    f"""
                    <div class="student-profile-card">
                        <div class="student-detail-grid">
                            <div class="student-detail-item">
                                <div class="student-detail-label">Correo</div>
                                <div class="student-detail-value">{safe_text(student["email"])}</div>
                            </div>
                            <div class="student-detail-item">
                                <div class="student-detail-label">Teléfono</div>
                                <div class="student-detail-value">{safe_text(student["phone"])}</div>
                            </div>
                            <div class="student-detail-item">
                                <div class="student-detail-label">Edad</div>
                                <div class="student-detail-value">{safe_text(student["age"])}</div>
                            </div>
                            <div class="student-detail-item">
                                <div class="student-detail-label">Sexo</div>
                                <div class="student-detail-value">{safe_text(student["sex"])}</div>
                            </div>
                            <div class="student-detail-item">
                                <div class="student-detail-label">Departamento</div>
                                <div class="student-detail-value">{safe_text(student["department"])}</div>
                            </div>
                            <div class="student-detail-item">
                                <div class="student-detail-label">Municipio</div>
                                <div class="student-detail-value">{safe_text(student["municipality"])}</div>
                            </div>
                            <div class="student-detail-item">
                                <div class="student-detail-label">Institución</div>
                                <div class="student-detail-value">{safe_text(student["institution_name"])}</div>
                            </div>
                            <div class="student-detail-item">
                                <div class="student-detail-label">Monitor</div>
                                <div class="student-detail-value">{safe_text(student["assigned_monitor"])}</div>
                            </div>
                            <div class="student-detail-item">
                                <div class="student-detail-label">Nivel académico</div>
                                <div class="student-detail-value">{safe_text(student["education_level"])}</div>
                            </div>
                            <div class="student-detail-item">
                                <div class="student-detail-label">Fecha ingreso</div>
                                <div class="student-detail-value">{safe_text(student["enrollment_date"])}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                render_section_title("Dirección o referencia")

                st.markdown(
                    f"""
                    <div class="student-profile-card">
                        <div class="student-detail-value">{safe_text(student["address_reference"])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_edit:
                render_section_title("Actualizar información")

                selected_modality_name = clean_text(student["modality"])

                if selected_modality_name not in modality_names:
                    selected_modality_name = modality_names[0]

                current_department = get_current_department(student["department"])
                current_municipality = get_current_municipality(
                    current_department,
                    student["municipality"]
                )

                with st.container(border=True):
                    col_e1, col_e2 = st.columns(2)

                    with col_e1:
                        edit_full_name = st.text_input(
                            "Nombre completo",
                            value=clean_text(student["full_name"]),
                            key=f"edit_full_name_{student_id}"
                        )
                        edit_age = st.number_input(
                            "Edad",
                            min_value=10,
                            max_value=80,
                            value=clean_int(student["age"], 18),
                            key=f"edit_age_{student_id}"
                        )
                        edit_sex = st.selectbox(
                            "Sexo",
                            sex_options,
                            index=get_option_index(sex_options, clean_text(student["sex"])),
                            key=f"edit_sex_{student_id}"
                        )
                        edit_email = st.text_input(
                            "Correo",
                            value=clean_text(student["email"]),
                            key=f"edit_email_{student_id}"
                        )
                        edit_phone = st.text_input(
                            "Teléfono",
                            value=clean_text(student["phone"]),
                            key=f"edit_phone_{student_id}"
                        )
                        edit_department = st.selectbox(
                            "Departamento",
                            options=DEPARTMENT_OPTIONS,
                            index=get_option_index(DEPARTMENT_OPTIONS, current_department),
                            key=f"edit_department_{student_id}"
                        )
                        edit_municipality_options = EL_SALVADOR_MUNICIPALITIES.get(
                            edit_department,
                            []
                        )
                        edit_municipality_default = get_current_municipality(
                            edit_department,
                            student["municipality"]
                        )
                        edit_municipality = st.selectbox(
                            "Municipio",
                            options=edit_municipality_options,
                            index=get_option_index(edit_municipality_options, edit_municipality_default),
                            key=f"edit_municipality_{student_id}_{edit_department}"
                        )
                        edit_address_reference = st.text_area(
                            "Dirección o referencia",
                            value=clean_text(student["address_reference"]),
                            key=f"edit_address_reference_{student_id}"
                        )

                    with col_e2:
                        edit_education_level = st.selectbox(
                            "Nivel de escolaridad",
                            education_options,
                            index=get_option_index(education_options, clean_text(student["education_level"])),
                            key=f"edit_education_level_{student_id}"
                        )
                        edit_institution_name = reference_value_input(
                            "Universidad / Colegio / Institución",
                            institution_options,
                            f"edit_institution_{student_id}",
                            student["institution_name"]
                        )
                        edit_career = reference_value_input(
                            "Carrera / curso",
                            career_reference_options,
                            f"edit_career_{student_id}",
                            student["career"]
                        )
                        edit_modality_name = st.selectbox(
                            "Modalidad",
                            modality_names,
                            index=get_option_index(modality_names, selected_modality_name),
                            key=f"edit_modality_{student_id}"
                        )
                        edit_scholarship_type = st.selectbox(
                            "Tipo de beca",
                            scholarship_options,
                            index=get_option_index(scholarship_options, clean_text(student["scholarship_type"])),
                            key=f"edit_scholarship_type_{student_id}"
                        )
                        edit_support_percentage = st.number_input(
                            "Porcentaje de apoyo económico",
                            min_value=0,
                            max_value=100,
                            value=clean_percentage(student["support_percentage"], 100),
                            key=f"edit_support_percentage_{student_id}"
                        )
                        edit_status = st.selectbox(
                            "Estado",
                            status_options,
                            index=get_option_index(status_options, clean_text(student["status"])),
                            key=f"edit_status_{student_id}"
                        )
                        edit_assigned_monitor = reference_value_input(
                            "Monitor asignado",
                            monitor_reference_options,
                            f"edit_monitor_{student_id}",
                            student["assigned_monitor"]
                        )

                    update_submitted = st.button(
                        "Actualizar estudiante",
                        use_container_width=True,
                        key=f"edit_submit_{student_id}"
                    )

                    if update_submitted:
                        if not edit_full_name.strip():
                            st.error("El nombre completo es obligatorio.")
                        elif not edit_institution_name.strip():
                            st.error("La institución es obligatoria.")
                        elif not edit_career.strip():
                            st.error("La carrera o curso es obligatorio.")
                        elif not edit_assigned_monitor.strip():
                            st.error("El monitor asignado es obligatorio.")
                        else:
                            payload = {
                                "full_name": edit_full_name.strip(),
                                "age": int(edit_age),
                                "sex": edit_sex,
                                "email": edit_email.strip(),
                                "phone": edit_phone.strip(),
                                "department": edit_department,
                                "municipality": edit_municipality,
                                "address_reference": edit_address_reference.strip(),
                                "education_level": edit_education_level,
                                "institution_name": edit_institution_name.strip(),
                                "career": edit_career.strip(),
                                "modality_id": modality_options[edit_modality_name],
                                "scholarship_type": edit_scholarship_type,
                                "support_percentage": int(edit_support_percentage),
                                "status": edit_status,
                                "assigned_monitor": edit_assigned_monitor.strip()
                            }

                            update_student(student["id"], payload)
                            clear_student_cache()
                            
                            st.session_state["show_update_success"] = True
                            st.rerun()

                if st.session_state.get("show_update_success", False):
                    st.success("Información del estudiante actualizada correctamente.")
                    st.session_state["show_update_success"] = False