import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from datetime import date

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD, GOES_DARK
from utils.sidebar import apply_sidebar_theme
from utils.pagination import render_pagination

st.set_page_config(
    page_title="Seguimientos | SIBECA",
    page_icon="",
    layout="wide"
)

apply_goes_theme()
apply_sidebar_theme()

EMPTY_PLACEHOLDER = " "
ADD_NEW_OPTION = "Agregar nuevo"
CHART_HEIGHT = 360

CHART_CONFIG = {
    "displayModeBar": "hover",
    "displaylogo": False,
    "responsive": True
}

FOLLOWUP_RESULT_COLOR_MAP = {
    "Contactado": GOES_BLUE,
    "No respondió": "#B42318",
    "Pendiente": GOES_GOLD,
    "Caso escalado": "#D97706",
    "Caso cerrado": "#15803D"
}

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

        .followups-section-title {{
            color: {GOES_BLUE};
            font-family: "Segoe UI", Arial, sans-serif !important;
            font-weight: 800;
            font-size: 1.05rem;
            border-left: 5px solid {GOES_GOLD};
            padding-left: 10px;
            margin-top: 14px;
            margin-bottom: 12px;
        }}

        .followups-filter-title {{
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

        .followups-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.06);
            min-height: 92px;
            margin-bottom: 10px;
        }}

        .followups-card-blue {{
            border-top: 4px solid {GOES_BLUE};
        }}

        .followups-card-gold {{
            border-top: 4px solid {GOES_GOLD};
        }}

        .followups-card-red {{
            border-top: 4px solid #B42318;
        }}

        .followups-card-gray {{
            border-top: 4px solid #64748b;
        }}

        .followups-kpi-label {{
            color: {GOES_DARK};
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 6px;
        }}

        .followups-kpi-value {{
            color: {GOES_BLUE};
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 5px;
        }}

        .followups-kpi-help {{
            color: #64748b;
            font-size: 0.72rem;
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
        div[data-testid="stDateInput"] div,
        div[data-testid="stSelectbox"] div,
        div[data-testid="stMultiSelect"] div {{
            font-family: "Segoe UI", Arial, sans-serif !important;
            max-width: 100% !important;
        }}

        div[data-testid="stTextInput"] [data-baseweb="input"],
        div[data-testid="stTextArea"] [data-baseweb="textarea"],
        div[data-testid="stNumberInput"] [data-baseweb="input"],
        div[data-testid="stDateInput"] [data-baseweb="input"] {{
            background-color: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
            min-height: 44px !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stTextInput"] [data-baseweb="input"]:hover,
        div[data-testid="stTextArea"] [data-baseweb="textarea"]:hover,
        div[data-testid="stNumberInput"] [data-baseweb="input"]:hover,
        div[data-testid="stDateInput"] [data-baseweb="input"]:hover {{
            background-color: #ffffff !important;
            border-color: {GOES_BLUE} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
        div[data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,
        div[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
        div[data-testid="stDateInput"] [data-baseweb="input"]:focus-within {{
            background-color: #ffffff !important;
            border-color: {GOES_BLUE} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input {{
            background-color: transparent !important;
            color: {GOES_DARK} !important;
            caret-color: {GOES_BLUE} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder,
        div[data-testid="stNumberInput"] input::placeholder,
        div[data-testid="stDateInput"] input::placeholder {{
            color: #94a3b8 !important;
            opacity: 1 !important;
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
            max-height: 140px !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            align-items: flex-start !important;
            padding-top: 4px !important;
            padding-bottom: 4px !important;
            flex-wrap: wrap !important;
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

        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stButton"] button {{
            min-height: 38px !important;
            padding: 0.25rem 0.75rem !important;
            border-radius: 10px !important;
            background-color: {GOES_BLUE} !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 800 !important;
        }}

        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stButton"] button:hover {{
            background-color: {GOES_DARK} !important;
            color: #ffffff !important;
        }}

        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stButton"] button span {{
            color: #ffffff !important;
        }}

        div[class*="st-key-followups_clear_filters_button"] button {{
            min-height: 42px !important;
            height: 42px !important;
            padding: 0.25rem 0.55rem !important;
            border-radius: 10px !important;
            background-color: {GOES_BLUE} !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
            margin-top: 10px !important;
            margin-bottom: 10px !important;
            font-weight: 800 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        div[class*="st-key-followups_clear_filters_button"] button:hover {{
            background-color: {GOES_DARK} !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
        }}

        div[class*="st-key-followups_clear_filters_button"] button span,
        div[class*="st-key-followups_clear_filters_button"] button svg {{
            color: #ffffff !important;
            fill: #ffffff !important;
        }}

        .js-plotly-plot .plotly .modebar {{
            top: 20px !important;
            right: 20px !important;
            padding: 2px 4px !important;
        }}

        .js-plotly-plot .plotly .modebar-btn svg {{
            fill: #64748b !important;
        }}

        .js-plotly-plot .plotly .modebar-btn:hover svg {{
            fill: {GOES_BLUE} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

page_header(
    "Seguimientos",
    "Historial de contactos, motivos de riesgo, acciones realizadas y próximas intervenciones."
)

engine = get_engine()


@st.cache_data(ttl=1800, show_spinner=False)
def load_students():
    return pd.read_sql(
        """
        SELECT id, student_code, full_name, department, career, assigned_monitor
        FROM students
        ORDER BY full_name
        """,
        engine
    )


@st.cache_data(ttl=1800, show_spinner=False)
def load_risk_reasons():
    return pd.read_sql(
        """
        SELECT id, category, reason_name
        FROM risk_reasons
        WHERE active = TRUE
        ORDER BY category, reason_name
        """,
        engine
    )


@st.cache_data(ttl=1800, show_spinner=False)
def load_followups():
    df = pd.read_sql(
        """
        SELECT
            f.id,
            f.followup_date,
            s.student_code,
            s.full_name,
            s.department,
            s.career,
            f.followup_type,
            f.result,
            rr.category AS risk_category,
            rr.reason_name AS risk_reason,
            f.comment,
            f.next_action,
            f.next_action_date,
            f.responsible_user,
            f.created_at
        FROM followups f
        INNER JOIN students s ON f.student_id = s.id
        LEFT JOIN risk_reasons rr ON f.risk_reason_id = rr.id
        ORDER BY f.followup_date DESC, f.created_at DESC
        """,
        engine
    )

    text_columns = [
        "student_code",
        "full_name",
        "department",
        "career",
        "followup_type",
        "result",
        "risk_category",
        "risk_reason",
        "comment",
        "next_action",
        "responsible_user"
    ]

    for column in text_columns:
        df[column] = df[column].fillna("Sin dato")

    df["followup_date"] = pd.to_datetime(df["followup_date"], errors="coerce")
    df["next_action_date"] = pd.to_datetime(df["next_action_date"], errors="coerce")
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    return df


def render_section_title(title):
    st.markdown(
        f"""
        <div class="followups-section-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_filter_title(title):
    st.markdown(
        f"""
        <div class="followups-filter-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_kpi(label, value, help_text, variant):
    css_class = f"followups-card followups-card-{variant}"

    st.markdown(
        f"""
        <div class="{css_class}">
            <div class="followups-kpi-label">{label}</div>
            <div class="followups-kpi-value">{value}</div>
            <div class="followups-kpi-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def format_chart(fig, show_legend=True):
    fig.update_layout(
        height=CHART_HEIGHT,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_color=GOES_DARK,
        title_font_color=GOES_BLUE,
        title_font_size=14,
        title_x=0.5,
        title_y=0.98,
        title_xanchor="center",
        title_yanchor="top",
        legend_title_text="",
        showlegend=show_legend,
        margin=dict(l=35, r=55, t=72, b=35)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#eef0f3",
        zeroline=False,
        title_font_size=11,
        tickfont_size=10,
        automargin=True
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#eef0f3",
        zeroline=False,
        title_font_size=11,
        tickfont_size=10,
        automargin=True
    )

    for trace in fig.data:
        try:
            trace.update(cliponaxis=False)
        except ValueError:
            pass

        try:
            trace.update(textfont=dict(size=10))
        except ValueError:
            pass

    return fig


def render_chart(container, fig):
    container.plotly_chart(
        fig,
        use_container_width=True,
        config=CHART_CONFIG
    )


def get_clean_options(dataframe, column):
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


def clean_text(value):
    if pd.isna(value) or value is None:
        return ""
    return str(value)


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


def reset_followup_filters():
    st.session_state["followups_filter_student"] = None
    st.session_state["followups_filter_result"] = []
    st.session_state["followups_filter_type"] = []
    st.session_state["followups_filter_category"] = []
    st.session_state["followups_filter_department"] = []
    st.session_state["followups_filter_responsible"] = []
    st.session_state["followups_summary_detail_page_number"] = 1


students = load_students()
risk_reasons = load_risk_reasons()

if students.empty:
    st.warning("No hay estudiantes registrados.")
    st.stop()

student_options = {
    f"{row.student_code} - {row.full_name}": row.id
    for row in students.itertuples()
}

if risk_reasons.empty:
    reason_options = {}
else:
    reason_options = {
        f"{row.category} - {row.reason_name}": row.id
        for row in risk_reasons.itertuples()
    }

followups_reference_df = load_followups()

monitor_reference_options = sorted(
    set(
        get_clean_options(students, "assigned_monitor")
        + get_clean_options(followups_reference_df, "responsible_user")
    )
)

tab1, tab2 = st.tabs(
    [
        "Resumen",
        "Registrar seguimiento"
    ]
)

with tab1:
    render_section_title("Resumen de seguimientos")

    df = load_followups()

    if df.empty:
        st.info("Aún no hay seguimientos registrados.")
    else:
        student_filter_df = (
            df[
                [
                    "student_code",
                    "full_name"
                ]
            ]
            .drop_duplicates()
            .copy()
        )

        student_filter_df["student_selector"] = (
            student_filter_df["student_code"]
            + " - "
            + student_filter_df["full_name"]
        )

        student_filter_options = (
            student_filter_df
            .sort_values("student_selector")["student_selector"]
            .tolist()
        )

        with st.expander("Mostrar / ocultar filtros de búsqueda", expanded=True):
            col_filter_title, col_filter_button = st.columns([10, 1])

            with col_filter_title:
                render_filter_title("Seleccione los filtros para consultar seguimientos")

            with col_filter_button:
                st.button(
                    "",
                    icon=":material/filter_alt_off:",
                    help="Limpiar filtros",
                    use_container_width=True,
                    on_click=reset_followup_filters,
                    key="followups_clear_filters_button"
                )

            with st.container(border=True):
                col1, col2, col3 = st.columns([2.4, 1.4, 1.5])

                with col1:
                    selected_student_filter = st.selectbox(
                        "Buscar estudiante",
                        options=student_filter_options,
                        index=None,
                        placeholder=EMPTY_PLACEHOLDER,
                        key="followups_filter_student"
                    )

                with col2:
                    result_filter = st.multiselect(
                        "Resultado",
                        options=get_clean_options(df, "result"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="followups_filter_result"
                    )

                with col3:
                    type_filter = st.multiselect(
                        "Tipo de seguimiento",
                        options=get_clean_options(df, "followup_type"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="followups_filter_type"
                    )

                col4, col5, col6 = st.columns([1.6, 1.4, 1.6])

                with col4:
                    category_filter = st.multiselect(
                        "Categoría de riesgo",
                        options=get_clean_options(df, "risk_category"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="followups_filter_category"
                    )

                with col5:
                    department_filter = st.multiselect(
                        "Departamento",
                        options=get_clean_options(df, "department"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="followups_filter_department"
                    )

                with col6:
                    responsible_filter = st.multiselect(
                        "Responsable",
                        options=get_clean_options(df, "responsible_user"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="followups_filter_responsible"
                    )

        filtered = df.copy()

        if selected_student_filter:
            selected_student_code = selected_student_filter.split(" - ")[0]
            filtered = filtered[
                filtered["student_code"] == selected_student_code
            ]

        if result_filter:
            filtered = filtered[
                filtered["result"].isin(result_filter)
            ]

        if type_filter:
            filtered = filtered[
                filtered["followup_type"].isin(type_filter)
            ]

        if category_filter:
            filtered = filtered[
                filtered["risk_category"].isin(category_filter)
            ]

        if department_filter:
            filtered = filtered[
                filtered["department"].isin(department_filter)
            ]

        if responsible_filter:
            filtered = filtered[
                filtered["responsible_user"].isin(responsible_filter)
            ]

        st.caption(f"Mostrando {len(filtered):,} de {len(df):,} seguimientos.")

        if filtered.empty:
            st.warning("No hay seguimientos que coincidan con los filtros seleccionados.")
        else:
            total_followups = len(filtered)
            contacted_students = filtered["student_code"].nunique()
            escalated_cases = len(
                filtered[
                    filtered["result"] == "Caso escalado"
                ]
            )
            next_actions = int(filtered["next_action_date"].notna().sum())

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                render_kpi(
                    "Seguimientos",
                    f"{total_followups:,}",
                    "Registros filtrados",
                    "blue"
                )

            with col2:
                render_kpi(
                    "Estudiantes",
                    f"{contacted_students:,}",
                    "Estudiantes contactados",
                    "gold"
                )

            with col3:
                render_kpi(
                    "Escalados",
                    f"{escalated_cases:,}",
                    "Casos escalados",
                    "red"
                )

            with col4:
                render_kpi(
                    "Próximas acciones",
                    f"{next_actions:,}",
                    "Acciones con fecha",
                    "gray"
                )

            col_a, col_b = st.columns(2)

            reason_count = (
                filtered["risk_category"]
                .fillna("Sin motivo")
                .value_counts()
                .reset_index()
            )
            reason_count.columns = ["Categoría", "Cantidad"]

            fig_reason = px.bar(
                reason_count,
                x="Categoría",
                y="Cantidad",
                title="Seguimientos por categoría de riesgo",
                color_discrete_sequence=[GOES_BLUE],
                text="Cantidad"
            )
            fig_reason = format_chart(fig_reason, show_legend=False)
            fig_reason.update_layout(
                xaxis_title="Categoría",
                yaxis_title="Cantidad"
            )
            fig_reason.update_traces(textposition="outside")
            render_chart(col_a, fig_reason)

            result_count = filtered["result"].value_counts().reset_index()
            result_count.columns = ["Resultado", "Cantidad"]

            fig_result = px.pie(
                result_count,
                names="Resultado",
                values="Cantidad",
                title="Resultado de seguimientos",
                color="Resultado",
                color_discrete_map=FOLLOWUP_RESULT_COLOR_MAP,
                hole=0.55
            )
            fig_result = format_chart(fig_result)
            fig_result.update_traces(
                textposition="inside",
                textinfo="percent+label"
            )
            render_chart(col_b, fig_result)

            render_section_title("Registros de seguimiento")

            detail_view = filtered[
                [
                    "followup_date",
                    "student_code",
                    "full_name",
                    "department",
                    "career",
                    "followup_type",
                    "result",
                    "risk_category",
                    "risk_reason",
                    "responsible_user",
                    "next_action_date",
                    "next_action",
                    "comment"
                ]
            ].copy()

            detail_view["followup_date"] = detail_view["followup_date"].dt.strftime("%Y-%m-%d")
            detail_view["next_action_date"] = detail_view["next_action_date"].dt.strftime("%Y-%m-%d")
            detail_view["next_action_date"] = detail_view["next_action_date"].fillna("")

            detail_view = detail_view.rename(
                columns={
                    "followup_date": "Fecha",
                    "student_code": "Código",
                    "full_name": "Estudiante",
                    "department": "Departamento",
                    "career": "Carrera",
                    "followup_type": "Tipo",
                    "result": "Resultado",
                    "risk_category": "Categoría",
                    "risk_reason": "Motivo",
                    "responsible_user": "Responsable",
                    "next_action_date": "Fecha próxima acción",
                    "next_action": "Próxima acción",
                    "comment": "Comentario"
                }
            )

            total_records = len(detail_view)

            page_size, page_number, start_row, end_row = render_pagination(
                total_records=total_records,
                key_prefix="followups_summary_detail",
                label="seguimientos"
            )

            paginated_detail = detail_view.iloc[start_row:end_row]

            st.dataframe(
                paginated_detail,
                use_container_width=True,
                hide_index=True,
                height=460,
                column_config={
                    "Fecha": st.column_config.TextColumn("Fecha", width="small"),
                    "Código": st.column_config.TextColumn("Código", width="small"),
                    "Estudiante": st.column_config.TextColumn("Estudiante", width="medium"),
                    "Departamento": st.column_config.TextColumn("Departamento", width="small"),
                    "Carrera": st.column_config.TextColumn("Carrera", width="medium"),
                    "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                    "Resultado": st.column_config.TextColumn("Resultado", width="small"),
                    "Categoría": st.column_config.TextColumn("Categoría", width="medium"),
                    "Motivo": st.column_config.TextColumn("Motivo", width="medium"),
                    "Responsable": st.column_config.TextColumn("Responsable", width="small"),
                    "Fecha próxima acción": st.column_config.TextColumn("Fecha próxima acción", width="small"),
                    "Próxima acción": st.column_config.TextColumn("Próxima acción", width="large"),
                    "Comentario": st.column_config.TextColumn("Comentario", width="large")
                }
            )

with tab2:
    render_section_title("Registrar seguimiento")

    if not reason_options:
        st.warning("No hay motivos de riesgo cargados. El seguimiento se podrá guardar sin motivo principal.")

    with st.container(border=True):
        render_filter_title("Datos del seguimiento")

        col1, col2 = st.columns(2)

        with col1:
            selected_student = st.selectbox(
                "Estudiante",
                options=list(student_options.keys()),
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="followup_student"
            )

            followup_date = st.date_input(
                "Fecha de seguimiento",
                value=date.today(),
                key="followup_date"
            )

            followup_type = st.selectbox(
                "Tipo de seguimiento",
                options=[
                    "Llamada",
                    "Correo",
                    "WhatsApp",
                    "Reunión",
                    "Visita",
                    "Otro"
                ],
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="followup_type"
            )

            result = st.selectbox(
                "Resultado",
                options=[
                    "Contactado",
                    "No respondió",
                    "Pendiente",
                    "Caso escalado",
                    "Caso cerrado"
                ],
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="followup_result"
            )

        with col2:
            selected_reason = st.selectbox(
                "Motivo principal",
                options=list(reason_options.keys()) if reason_options else [],
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="followup_reason"
            )

            responsible_user = reference_value_input(
                "Responsable",
                monitor_reference_options,
                "followup_responsible"
            )

            next_action_date = st.date_input(
                "Fecha próxima acción",
                value=date.today(),
                key="followup_next_action_date"
            )

            next_action = st.text_area(
                "Próxima acción",
                key="followup_next_action"
            )

        comment = st.text_area(
            "Comentario del seguimiento",
            key="followup_comment"
        )

        submitted = st.button(
            "Guardar seguimiento",
            use_container_width=True,
            key="followup_submit"
        )

        if submitted:
            if not selected_student:
                st.error("Debes seleccionar un estudiante.")
            elif not followup_type:
                st.error("Debes seleccionar el tipo de seguimiento.")
            elif not result:
                st.error("Debes seleccionar el resultado del seguimiento.")
            elif not responsible_user.strip():
                st.error("Debes ingresar el responsable del seguimiento.")
            else:
                risk_reason_id = None

                if reason_options and selected_reason in reason_options:
                    risk_reason_id = reason_options[selected_reason]

                with engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            INSERT INTO followups (
                                student_id,
                                followup_date,
                                followup_type,
                                result,
                                risk_reason_id,
                                comment,
                                next_action,
                                next_action_date,
                                responsible_user
                            )
                            VALUES (
                                :student_id,
                                :followup_date,
                                :followup_type,
                                :result,
                                :risk_reason_id,
                                :comment,
                                :next_action,
                                :next_action_date,
                                :responsible_user
                            )
                            """
                        ),
                        {
                            "student_id": student_options[selected_student],
                            "followup_date": followup_date,
                            "followup_type": followup_type,
                            "result": result,
                            "risk_reason_id": risk_reason_id,
                            "comment": comment.strip(),
                            "next_action": next_action.strip(),
                            "next_action_date": next_action_date,
                            "responsible_user": responsible_user.strip()
                        }
                    )

                st.cache_data.clear()
                st.success("Seguimiento registrado correctamente.")