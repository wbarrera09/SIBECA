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
    page_title="Asistencia | SIBECA",
    page_icon="",
    layout="wide"
)

apply_goes_theme()
apply_sidebar_theme()

EMPTY_PLACEHOLDER = " "

CHART_HEIGHT = 360

CHART_CONFIG = {
    "displayModeBar": "hover",
    "displaylogo": False,
    "responsive": True
}

ATTENDANCE_COLOR_MAP = {
    "Asistió": GOES_BLUE,
    "Faltó": "#B42318",
    "Llegó tarde": GOES_GOLD,
    "Justificado": "#64748b",
    "No aplica": "#d2d2d2"
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

        .attendance-section-title {{
            color: {GOES_BLUE};
            font-family: "Segoe UI", Arial, sans-serif !important;
            font-weight: 800;
            font-size: 1.05rem;
            border-left: 5px solid {GOES_GOLD};
            padding-left: 10px;
            margin-top: 14px;
            margin-bottom: 12px;
        }}

        .attendance-filter-title {{
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

        .attendance-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.06);
            min-height: 92px;
            margin-bottom: 10px;
        }}

        .attendance-card-blue {{
            border-top: 4px solid {GOES_BLUE};
        }}

        .attendance-card-gold {{
            border-top: 4px solid {GOES_GOLD};
        }}

        .attendance-card-red {{
            border-top: 4px solid #B42318;
        }}

        .attendance-card-gray {{
            border-top: 4px solid #64748b;
        }}

        .attendance-kpi-label {{
            color: {GOES_DARK};
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 6px;
        }}

        .attendance-kpi-value {{
            color: {GOES_BLUE};
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 5px;
        }}

        .attendance-kpi-help {{
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

        div[class*="st-key-attendance_clear_filters_button"] button {{
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

        div[class*="st-key-attendance_clear_filters_button"] button:hover {{
            background-color: {GOES_DARK} !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
        }}

        div[class*="st-key-attendance_clear_filters_button"] button span {{
            color: #ffffff !important;
        }}

        div[class*="st-key-attendance_clear_filters_button"] button svg {{
            color: #ffffff !important;
            fill: #ffffff !important;
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
    "Control de Asistencia",
    "Registro y análisis de asistencia esperada versus asistencia real."
)

engine = get_engine()


@st.cache_data(ttl=1800, show_spinner=False)
def load_students():
    return pd.read_sql(
        """
        SELECT 
            s.id,
            s.student_code,
            s.full_name,
            m.name AS modality
        FROM students s
        LEFT JOIN modalities m ON s.modality_id = m.id
        ORDER BY s.full_name
        """,
        engine
    )


@st.cache_data(ttl=1800, show_spinner=False)
def load_modalities():
    return pd.read_sql(
        """
        SELECT id, name
        FROM modalities
        ORDER BY id
        """,
        engine
    )


@st.cache_data(ttl=1800, show_spinner=False)
def load_attendance():
    df = pd.read_sql(
        """
        SELECT
            ar.id,
            ar.session_date,
            s.student_code,
            s.full_name,
            s.department,
            s.career,
            m.name AS modality,
            ar.expected_attendance,
            ar.attendance_status,
            ar.observation
        FROM attendance_records ar
        INNER JOIN students s ON ar.student_id = s.id
        LEFT JOIN modalities m ON ar.modality_id = m.id
        ORDER BY ar.session_date DESC, s.full_name
        """,
        engine
    )

    text_columns = [
        "student_code",
        "full_name",
        "department",
        "career",
        "modality",
        "attendance_status",
        "observation"
    ]

    for column in text_columns:
        df[column] = df[column].fillna("Sin dato")

    df["session_date"] = pd.to_datetime(df["session_date"], errors="coerce")

    return df


def render_section_title(title):
    st.markdown(
        f"""
        <div class="attendance-section-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_filter_title(title):
    st.markdown(
        f"""
        <div class="attendance-filter-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_kpi(label, value, help_text, variant):
    css_class = f"attendance-card attendance-card-{variant}"

    st.markdown(
        f"""
        <div class="{css_class}">
            <div class="attendance-kpi-label">{label}</div>
            <div class="attendance-kpi-value">{value}</div>
            <div class="attendance-kpi-help">{help_text}</div>
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


def reset_attendance_filters():
    st.session_state["attendance_summary_student"] = None
    st.session_state["attendance_summary_status"] = []
    st.session_state["attendance_summary_modality"] = []
    st.session_state["attendance_summary_career"] = []
    st.session_state["attendance_summary_department"] = []
    st.session_state["attendance_summary_expected"] = []
    st.session_state["attendance_summary_detail_page_number"] = 1


students = load_students()
modalities = load_modalities()

if students.empty:
    st.warning("No hay estudiantes registrados.")
    st.stop()

if modalities.empty:
    st.warning("No hay modalidades cargadas.")
    st.stop()

student_options = {
    f"{row.student_code} - {row.full_name}": row.id
    for row in students.itertuples()
}

modality_options = {
    row.name: row.id
    for row in modalities.itertuples()
}

tab1, tab2 = st.tabs(
    [
        "Resumen",
        "Registrar asistencia"
    ]
)

with tab1:
    render_section_title("Resumen de asistencia")

    df = load_attendance()

    if df.empty:
        st.info("Todavía no hay registros de asistencia.")
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
                render_filter_title("Seleccione los filtros para consultar asistencia")

            with col_filter_button:
                st.button(
                    "",
                    icon=":material/filter_alt_off:",
                    help="Limpiar filtros",
                    use_container_width=True,
                    on_click=reset_attendance_filters,
                    key="attendance_clear_filters_button"
                )

            with st.container(border=True):
                col1, col2, col3 = st.columns([2.4, 1.3, 1.3])

                with col1:
                    selected_student_filter = st.selectbox(
                        "Buscar estudiante",
                        options=student_filter_options,
                        index=None,
                        placeholder=EMPTY_PLACEHOLDER,
                        key="attendance_summary_student"
                    )

                with col2:
                    status_filter = st.multiselect(
                        "Estado",
                        options=sorted(df["attendance_status"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="attendance_summary_status"
                    )

                with col3:
                    modality_filter = st.multiselect(
                        "Modalidad",
                        options=sorted(df["modality"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="attendance_summary_modality"
                    )

                col4, col5, col6 = st.columns([2.0, 1.4, 1.2])

                with col4:
                    career_filter = st.multiselect(
                        "Carrera",
                        options=sorted(df["career"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="attendance_summary_career"
                    )

                with col5:
                    department_filter = st.multiselect(
                        "Departamento",
                        options=sorted(df["department"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="attendance_summary_department"
                    )

                with col6:
                    expected_filter = st.multiselect(
                        "Esperada",
                        options=[
                            "Sí",
                            "No"
                        ],
                        placeholder=EMPTY_PLACEHOLDER,
                        key="attendance_summary_expected"
                    )

        filtered = df.copy()

        if selected_student_filter:
            selected_student_code = selected_student_filter.split(" - ")[0]
            filtered = filtered[
                filtered["student_code"] == selected_student_code
            ]

        if status_filter:
            filtered = filtered[
                filtered["attendance_status"].isin(status_filter)
            ]

        if modality_filter:
            filtered = filtered[
                filtered["modality"].isin(modality_filter)
            ]

        if career_filter:
            filtered = filtered[
                filtered["career"].isin(career_filter)
            ]

        if department_filter:
            filtered = filtered[
                filtered["department"].isin(department_filter)
            ]

        if expected_filter:
            expected_values = [
                True if value == "Sí" else False
                for value in expected_filter
            ]

            filtered = filtered[
                filtered["expected_attendance"].isin(expected_values)
            ]

        st.caption(f"Mostrando {len(filtered):,} de {len(df):,} registros.")

        if filtered.empty:
            st.warning("No hay registros que coincidan con los filtros seleccionados.")
        else:
            summary = (
                filtered.groupby(
                    [
                        "student_code",
                        "full_name",
                        "career"
                    ]
                )
                .agg(
                    sesiones_esperadas=("expected_attendance", "sum"),
                    asistencias=("attendance_status", lambda x: (x == "Asistió").sum()),
                    faltas=("attendance_status", lambda x: (x == "Faltó").sum()),
                    llegadas_tarde=("attendance_status", lambda x: (x == "Llegó tarde").sum()),
                    justificadas=("attendance_status", lambda x: (x == "Justificado").sum())
                )
                .reset_index()
            )

            summary["asistencia_%"] = summary.apply(
                lambda row: round((row["asistencias"] / row["sesiones_esperadas"]) * 100, 2)
                if row["sesiones_esperadas"] > 0 else 0,
                axis=1
            )

            valid_summary = summary[
                summary["sesiones_esperadas"] > 0
            ].copy()

            total_attendance_records = len(filtered)

            if valid_summary.empty:
                avg_attendance = 0
                low_attendance = 0
            else:
                avg_attendance = valid_summary["asistencia_%"].mean()
                low_attendance = len(
                    valid_summary[
                        valid_summary["asistencia_%"] < 75
                    ]
                )

            total_absences = int(summary["faltas"].sum())

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                render_kpi(
                    "Registros",
                    f"{total_attendance_records:,}",
                    "Registros filtrados",
                    "blue"
                )

            with col2:
                render_kpi(
                    "Asistencia promedio",
                    f"{avg_attendance:.1f}%",
                    "Promedio general",
                    "gold"
                )

            with col3:
                render_kpi(
                    "Bajo 75%",
                    f"{low_attendance:,}",
                    "Estudiantes con baja asistencia",
                    "red"
                )

            with col4:
                render_kpi(
                    "Faltas",
                    f"{total_absences:,}",
                    "Faltas registradas",
                    "gray"
                )

            col_a, col_b = st.columns(2)

            status_count = filtered["attendance_status"].value_counts().reset_index()
            status_count.columns = ["Estado", "Cantidad"]

            fig_status = px.bar(
                status_count,
                x="Estado",
                y="Cantidad",
                title="Distribución de estados de asistencia",
                color="Estado",
                color_discrete_map=ATTENDANCE_COLOR_MAP,
                text="Cantidad"
            )

            fig_status = format_chart(fig_status, show_legend=False)
            fig_status.update_layout(
                xaxis_title="Estado",
                yaxis_title="Cantidad"
            )
            fig_status.update_traces(textposition="outside")
            render_chart(col_a, fig_status)

            lowest_attendance = (
                valid_summary
                .sort_values("asistencia_%", ascending=True)
                .head(10)
            )

            if lowest_attendance.empty:
                col_b.info("No hay sesiones esperadas para calcular menor asistencia.")
            else:
                fig_lowest = px.bar(
                    lowest_attendance,
                    x="asistencia_%",
                    y="full_name",
                    orientation="h",
                    title="Estudiantes con menor asistencia",
                    color_discrete_sequence=[GOES_BLUE],
                    text="asistencia_%"
                )

                fig_lowest = format_chart(fig_lowest, show_legend=False)
                fig_lowest.update_layout(
                    xaxis_title="Asistencia",
                    yaxis_title="Estudiante"
                )
                fig_lowest.update_traces(
                    texttemplate="%{text:.1f}%",
                    textposition="outside"
                )
                render_chart(col_b, fig_lowest)

            render_section_title("Registros de asistencia")

            detail_view = filtered[
                [
                    "session_date",
                    "student_code",
                    "full_name",
                    "department",
                    "career",
                    "modality",
                    "expected_attendance",
                    "attendance_status",
                    "observation"
                ]
            ].copy()

            detail_view["session_date"] = detail_view["session_date"].dt.strftime("%Y-%m-%d")

            detail_view["expected_attendance"] = detail_view["expected_attendance"].apply(
                lambda value: "Sí" if bool(value) else "No"
            )

            detail_view = detail_view.rename(
                columns={
                    "session_date": "Fecha",
                    "student_code": "Código",
                    "full_name": "Estudiante",
                    "department": "Departamento",
                    "career": "Carrera",
                    "modality": "Modalidad",
                    "expected_attendance": "Esperada",
                    "attendance_status": "Estado",
                    "observation": "Observación"
                }
            )

            total_records = len(detail_view)

            page_size, page_number, start_row, end_row = render_pagination(
                total_records=total_records,
                key_prefix="attendance_summary_detail",
                label="registros"
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
                    "Modalidad": st.column_config.TextColumn("Modalidad", width="small"),
                    "Esperada": st.column_config.TextColumn("Esperada", width="small"),
                    "Estado": st.column_config.TextColumn("Estado", width="small"),
                    "Observación": st.column_config.TextColumn("Observación", width="large")
                }
            )

with tab2:
    render_section_title("Registrar asistencia")

    with st.container(border=True):
        render_filter_title("Datos de la sesión")

        col1, col2 = st.columns(2)

        with col1:
            selected_student = st.selectbox(
                "Estudiante",
                options=list(student_options.keys()),
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="attendance_student"
            )

            session_date = st.date_input(
                "Fecha de sesión",
                value=date.today(),
                key="attendance_session_date"
            )

            expected_attendance = st.checkbox(
                "Asistencia esperada",
                value=True,
                key="attendance_expected"
            )

        with col2:
            attendance_status = st.selectbox(
                "Estado de asistencia",
                options=[
                    "Asistió",
                    "Faltó",
                    "Llegó tarde",
                    "Justificado",
                    "No aplica"
                ],
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="attendance_status"
            )

            modality_name = st.selectbox(
                "Modalidad de la sesión",
                options=list(modality_options.keys()),
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="attendance_modality"
            )

            observation = st.text_area(
                "Observación",
                key="attendance_observation"
            )

        submitted = st.button(
            "Guardar asistencia",
            use_container_width=True,
            key="attendance_submit"
        )

        if submitted:
            if not selected_student:
                st.error("Debes seleccionar un estudiante.")
            elif not attendance_status:
                st.error("Debes seleccionar el estado de asistencia.")
            elif not modality_name:
                st.error("Debes seleccionar la modalidad de la sesión.")
            else:
                with engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            INSERT INTO attendance_records (
                                student_id,
                                session_date,
                                expected_attendance,
                                attendance_status,
                                modality_id,
                                observation
                            )
                            VALUES (
                                :student_id,
                                :session_date,
                                :expected_attendance,
                                :attendance_status,
                                :modality_id,
                                :observation
                            )
                            """
                        ),
                        {
                            "student_id": student_options[selected_student],
                            "session_date": session_date,
                            "expected_attendance": expected_attendance,
                            "attendance_status": attendance_status,
                            "modality_id": modality_options[modality_name],
                            "observation": observation.strip()
                        }
                    )

                st.cache_data.clear()
                st.success("Asistencia registrada correctamente.")