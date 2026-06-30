import streamlit as st
import pandas as pd
import plotly.express as px
from xlsxwriter import color

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD, GOES_DARK
from utils.sidebar import apply_sidebar_theme
from utils.pagination import render_pagination

st.set_page_config(
    page_title="Dashboard | SIBECA",
    layout="wide"
)

apply_goes_theme()
apply_sidebar_theme()

CHART_HEIGHT = 360

CHART_CONFIG = {
    "displayModeBar": "hover",
    "displaylogo": False,
    "responsive": True
}

EMPTY_PLACEHOLDER = " "

GOES_PALETTE = [
    GOES_BLUE,
    GOES_GOLD,
    GOES_DARK,
    "#64748b",
    "#94a3b8",
    "#B42318",
    "#D97706",
    "#15803D"
]

RISK_COLOR_MAP = {
    "Alto": "#111e60",   # PANTONE 2748 C (Azul institucional principal)
    "Medio": "#c9a892",  # PANTONE 7604 C (Tono arena/dorado neutro)
    "Bajo": "#d2d2d2"    # Color gris claro definido para el emblema
}

def reset_filters():
    st.session_state["filter_student"] = None
    st.session_state["filter_department"] = []
    st.session_state["filter_modality"] = []
    st.session_state["filter_career"] = []
    st.session_state["filter_risk"] = []
    st.session_state["filter_status"] = []
    st.session_state["filter_scholarship"] = []
    st.session_state["filter_monitor"] = []
    st.session_state["filter_attendance"] = (0.0, 100.0)
    st.session_state["filter_grade"] = (0.0, 10.0)
    st.session_state["students_page_number"] = 1


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

        .dashboard-section-title {{
            color: {GOES_BLUE};
            font-family: "Segoe UI", Arial, sans-serif !important;
            font-weight: 800;
            font-size: 1.05rem;
            border-left: 5px solid {GOES_GOLD};
            padding-left: 10px;
            margin-top: 14px;
            margin-bottom: 10px;
        }}

        .dashboard-filter-title {{
            background: {GOES_BLUE};
            color: #ffffff;
            padding: 10px 14px;
            border-radius: 10px;
            border-left: 5px solid {GOES_GOLD};
            font-weight: 700;
            margin-bottom: 10px;
            font-size: 0.9rem;
            margin-top: 10px;
        }}

        .dashboard-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.06);
            min-height: 92px;
            margin-bottom: 10px;
        }}

        .dashboard-card-blue {{
            border-top: 4px solid {GOES_BLUE};
        }}

        .dashboard-card-gold {{
            border-top: 4px solid {GOES_GOLD};
        }}

        .dashboard-card-red {{
            border-top: 4px solid #B42318;
        }}

        .dashboard-card-orange {{
            border-top: 4px solid #D97706;
        }}

        .dashboard-card-green {{
            border-top: 4px solid #15803D;
        }}

        .dashboard-kpi-label {{
            color: {GOES_DARK};
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 6px;
        }}

        .dashboard-kpi-value {{
            color: {GOES_BLUE};
            font-size: 1.55rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 5px;
        }}

        .dashboard-kpi-help {{
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
            transition: background-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease !important;
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

        div[data-baseweb="select"] {{
            background-color: #f8fafc !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
            min-height: 44px !important;
            max-width: 100% !important;
            width: 100% !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-baseweb="select"]:hover {{
            border-color: {GOES_BLUE} !important;
            background-color: #ffffff !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-baseweb="select"]:focus-within {{
            border-color: {GOES_BLUE} !important;
            background-color: #ffffff !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            background-color: transparent !important;
            min-height: 42px !important;
            max-height: 42px !important;
            overflow: hidden !important;
            align-items: center !important;
            padding-top: 4px !important;
            padding-bottom: 4px !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            background-color: transparent !important;
            min-height: 42px !important;
            max-height: 120px !important;
            overflow-y: auto !important;
            align-items: flex-start !important;
            padding-top: 4px !important;
            padding-bottom: 4px !important;
        }}

        div[data-baseweb="select"] div {{
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-baseweb="select"] input {{
            color: {GOES_DARK} !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-baseweb="select"] input:focus {{
            box-shadow: none !important;
            outline: none !important;
        }}

        div[data-baseweb="select"] span {{
            color: #64748b !important;
        }}

        div[data-baseweb="select"] [data-baseweb="icon"] {{
            color: {GOES_DARK} !important;
        }}

/
        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {{
            background-color: {GOES_BLUE} !important;
            border: 1px solid {GOES_BLUE} !important;
            border-radius: 8px !important;
            max-width: none !important;
            width: auto !important;
            min-width: fit-content !important;
            margin-top: 2px !important;
            margin-bottom: 2px !important;
            flex-shrink: 0 !important;
            white-space: nowrap !important;
        }}

        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span {{
            color: #ffffff !important;
            max-width: none !important;
            width: auto !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
        }}

        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] svg {{
            fill: #ffffff !important;
            color: #ffffff !important;
            flex-shrink: 0 !important;
        }}

        div[data-baseweb="tag"] [role="button"] {{
            color: #ffffff !important;
        }}

        div[data-baseweb="tag"]:hover {{
            background-color: #1a2a6c !important;
            border-color: #1a2a6c !important;
        }}

        div[data-testid="stMultiSelect"] div {{
            font-family: "Segoe UI", Arial, sans-serif !important;
            max-width: 100% !important;
        }}

        div[data-testid="stSelectbox"] div {{
            font-family: "Segoe UI", Arial, sans-serif !important;
            max-width: 100% !important;
        }}

        div[data-testid="stTextInput"] div {{
            font-family: "Segoe UI", Arial, sans-serif !important;
        }}

        div[data-testid="stSlider"] div {{
            font-family: "Segoe UI", Arial, sans-serif !important;
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

                div[data-testid="stMultiSelect"] div[data-baseweb="tag"],
        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {{
            background-color: {GOES_BLUE} !important;
            border: 1px solid {GOES_BLUE} !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            max-width: 100% !important;
            width: auto !important;
            min-width: 0 !important;
            margin-top: 2px !important;
            margin-bottom: 2px !important;
            flex-shrink: 1 !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span,
        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span,
        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span[title],
        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span[title] {{
            color: #ffffff !important;
            max-width: none !important;
            width: auto !important;
            overflow: visible !important;
            text-overflow: clip !important;
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
            max-height: 150px !important;
            overflow-y: auto !important;
        }}
        
    </style>
    """,
    unsafe_allow_html=True
)

page_header(
    "Dashboard Operativo",
    "Vista general del programa de becados, indicadores clave, distribución y estudiantes prioritarios."
)

engine = get_engine()


@st.cache_data(ttl=1800, show_spinner=False)
def load_dashboard_data():
    query = """
        WITH attendance AS (
            SELECT
                student_id,
                COUNT(*) AS expected_sessions,
                SUM(CASE WHEN attendance_status = 'Asistió' THEN 1 ELSE 0 END) AS attended_sessions,
                SUM(CASE WHEN attendance_status = 'Faltó' THEN 1 ELSE 0 END) AS absences,
                SUM(CASE WHEN attendance_status = 'Llegó tarde' THEN 1 ELSE 0 END) AS late_arrivals,
                SUM(CASE WHEN attendance_status = 'Justificado' THEN 1 ELSE 0 END) AS justified_absences
            FROM attendance_records
            WHERE expected_attendance = TRUE
            GROUP BY student_id
        ),
        grades_summary AS (
            SELECT
                student_id,
                AVG(grade) AS average_grade,
                COUNT(*) AS grade_records
            FROM grades
            GROUP BY student_id
        ),
        followups_summary AS (
            SELECT
                student_id,
                COUNT(*) AS followup_count,
                MAX(followup_date) AS last_followup_date
            FROM followups
            GROUP BY student_id
        ),
        alerts_summary AS (
            SELECT
                student_id,
                COUNT(*) AS open_alerts
            FROM alerts
            WHERE status = 'Abierta'
            GROUP BY student_id
        )
        SELECT
            s.id,
            s.student_code,
            s.full_name,
            s.department,
            s.municipality,
            s.career,
            s.institution_name,
            s.scholarship_type,
            s.support_percentage,
            s.status,
            s.assigned_monitor,
            m.name AS modality,
            COALESCE(a.expected_sessions, 0) AS expected_sessions,
            COALESCE(a.attended_sessions, 0) AS attended_sessions,
            COALESCE(a.absences, 0) AS absences,
            COALESCE(a.late_arrivals, 0) AS late_arrivals,
            COALESCE(a.justified_absences, 0) AS justified_absences,
            COALESCE(g.average_grade, 0) AS average_grade,
            COALESCE(g.grade_records, 0) AS grade_records,
            COALESCE(f.followup_count, 0) AS followup_count,
            f.last_followup_date,
            COALESCE(al.open_alerts, 0) AS open_alerts
        FROM students s
        LEFT JOIN modalities m ON s.modality_id = m.id
        LEFT JOIN attendance a ON s.id = a.student_id
        LEFT JOIN grades_summary g ON s.id = g.student_id
        LEFT JOIN followups_summary f ON s.id = f.student_id
        LEFT JOIN alerts_summary al ON s.id = al.student_id
    """

    df = pd.read_sql(query, engine)

    numeric_columns = [
        "expected_sessions",
        "attended_sessions",
        "absences",
        "late_arrivals",
        "justified_absences",
        "average_grade",
        "grade_records",
        "followup_count",
        "open_alerts",
        "support_percentage"
    ]

    text_columns = [
        "student_code",
        "full_name",
        "department",
        "municipality",
        "career",
        "institution_name",
        "scholarship_type",
        "status",
        "assigned_monitor",
        "modality"
    ]

    for column in numeric_columns:
        df[column] = df[column].fillna(0)

    for column in text_columns:
        df[column] = df[column].fillna("Sin dato")

    df["attendance_rate"] = df.apply(
        lambda row: round((row["attended_sessions"] / row["expected_sessions"]) * 100, 2)
        if row["expected_sessions"] > 0 else 0,
        axis=1
    )

    df["last_followup_date"] = pd.to_datetime(df["last_followup_date"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    df["days_without_followup"] = df["last_followup_date"].apply(
        lambda value: (today - value).days if pd.notna(value) else 999
    )

    return df


def calculate_score(row):
    score = 0

    if row["attendance_rate"] < 75:
        score += 30

    if row["attendance_rate"] < 60:
        score += 20

    if row["average_grade"] < 7:
        score += 25

    if row["average_grade"] < 6:
        score += 15

    if row["days_without_followup"] > 15:
        score += 15

    if row["status"] == "En riesgo":
        score += 20

    return min(score, 100)


def calculate_risk(score):
    if score >= 70:
        return "Alto"

    if score >= 40:
        return "Medio"

    return "Bajo"


def render_section_title(title):
    st.markdown(
        f"""
        <div class="dashboard-section-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_filter_title(title):
    st.markdown(
        f"""
        <div class="dashboard-filter-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_kpi(label, value, help_text, variant):
    css_class = f"dashboard-card dashboard-card-{variant}"

    st.markdown(
        f"""
        <div class="{css_class}">
            <div class="dashboard-kpi-label">{label}</div>
            <div class="dashboard-kpi-value">{value}</div>
            <div class="dashboard-kpi-help">{help_text}</div>
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


def count_dataframe(dataframe, column, label, limit=10):
    result = dataframe[column].value_counts().reset_index()
    result.columns = [label, "Cantidad"]
    return result.head(limit)


def render_chart(container, fig):
    container.plotly_chart(
        fig,
        use_container_width=True,
        config=CHART_CONFIG
    )


df = load_dashboard_data()

if df.empty:
    st.warning("No hay datos cargados todavía.")
    st.stop()

df["risk_score"] = df.apply(calculate_score, axis=1)
df["risk_level"] = df["risk_score"].apply(calculate_risk)

student_lookup = df[
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

with st.expander("Mostrar / ocultar filtros de búsqueda", expanded=True):
    col_filter_title, col_filter_button = st.columns([10, 1])

    with col_filter_title:
        render_filter_title("Seleccione los filtros para la búsqueda de estudiantes")

    with col_filter_button:
        st.button(
            "",
            icon=":material/filter_alt_off:",
            help="Limpiar filtros",
            use_container_width=True,
            on_click=reset_filters
        )

    with st.container(border=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns([2.3, 2.1, 1.4, 1.1])

        with col_f1:
            selected_student = st.selectbox(
                "Buscar estudiante",
                options=student_options,
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="filter_student"
            )

        with col_f2:
            career_filter = st.multiselect(
                "Carrera",
                options=sorted(df["career"].unique().tolist()),
                placeholder=EMPTY_PLACEHOLDER,
                key="filter_career"
            )

        with col_f3:
            department_filter = st.multiselect(
                "Departamento",
                options=sorted(df["department"].unique().tolist()),
                placeholder=EMPTY_PLACEHOLDER,
                key="filter_department"
            )

        with col_f4:
            risk_filter = st.multiselect(
                "Riesgo",
                options=["Alto", "Medio", "Bajo"],
                placeholder=EMPTY_PLACEHOLDER,
                key="filter_risk"
            )

        col_f5, col_f6, col_f7, col_f8 = st.columns([1.4, 1.2, 1.5, 1.7])

        with col_f5:
            modality_filter = st.multiselect(
                "Modalidad",
                options=sorted(df["modality"].unique().tolist()),
                placeholder=EMPTY_PLACEHOLDER,
                key="filter_modality"
            )

        with col_f6:
            status_filter = st.multiselect(
                "Estado",
                options=sorted(df["status"].unique().tolist()),
                placeholder=EMPTY_PLACEHOLDER,
                key="filter_status"
            )

        with col_f7:
            scholarship_filter = st.multiselect(
                "Tipo de beca",
                options=sorted(df["scholarship_type"].unique().tolist()),
                placeholder=EMPTY_PLACEHOLDER,
                key="filter_scholarship"
            )

        with col_f8:
            monitor_filter = st.multiselect(
                "Monitor asignado",
                options=sorted(df["assigned_monitor"].unique().tolist()),
                placeholder=EMPTY_PLACEHOLDER,
                key="filter_monitor"
            )

    with st.expander("Filtros avanzados", expanded=False):
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            attendance_range = st.slider(
                "Rango de asistencia",
                min_value=0.0,
                max_value=100.0,
                value=(0.0, 100.0),
                step=1.0,
                key="filter_attendance"
            )

        with col_r2:
            grade_range = st.slider(
                "Rango de promedio académico",
                min_value=0.0,
                max_value=10.0,
                value=(0.0, 10.0),
                step=0.1,
                key="filter_grade"
            )

filtered_df = df.copy()

if selected_student:
    selected_student_code = selected_student.split(" - ")[0]
    filtered_df = filtered_df[
        filtered_df["student_code"] == selected_student_code
    ]

if department_filter:
    filtered_df = filtered_df[filtered_df["department"].isin(department_filter)]

if modality_filter:
    filtered_df = filtered_df[filtered_df["modality"].isin(modality_filter)]

if career_filter:
    filtered_df = filtered_df[filtered_df["career"].isin(career_filter)]

if risk_filter:
    filtered_df = filtered_df[filtered_df["risk_level"].isin(risk_filter)]

if status_filter:
    filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]

if scholarship_filter:
    filtered_df = filtered_df[filtered_df["scholarship_type"].isin(scholarship_filter)]

if monitor_filter:
    filtered_df = filtered_df[filtered_df["assigned_monitor"].isin(monitor_filter)]

filtered_df = filtered_df[
    (filtered_df["attendance_rate"] >= attendance_range[0])
    & (filtered_df["attendance_rate"] <= attendance_range[1])
]

filtered_df = filtered_df[
    (filtered_df["average_grade"] >= grade_range[0])
    & (filtered_df["average_grade"] <= grade_range[1])
]

st.caption(f"Mostrando {len(filtered_df):,} de {len(df):,} estudiantes.")

if filtered_df.empty:
    st.warning("No hay estudiantes que coincidan con los filtros seleccionados.")
    st.stop()

render_section_title("Indicadores principales")

total_students = len(filtered_df)
avg_attendance = filtered_df["attendance_rate"].mean()
avg_grade = filtered_df["average_grade"].mean()
high_risk = len(filtered_df[filtered_df["risk_level"] == "Alto"])
medium_risk = len(filtered_df[filtered_df["risk_level"] == "Medio"])
low_risk = len(filtered_df[filtered_df["risk_level"] == "Bajo"])
open_alerts = int(filtered_df["open_alerts"].sum())
without_followup = len(filtered_df[filtered_df["days_without_followup"] > 15])

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_kpi("Total de becados", f"{total_students:,}", "Estudiantes filtrados", "blue")

with col2:
    render_kpi("Asistencia promedio", f"{avg_attendance:.1f}%", "Promedio de asistencia", "gold")

with col3:
    render_kpi("Promedio académico", f"{avg_grade:.2f}", "Promedio general de notas", "blue")

with col4:
    render_kpi("Alertas abiertas", f"{open_alerts:,}", "Alertas activas", "gold")

col5, col6, col7, col8 = st.columns(4)

with col5:
    render_kpi("Riesgo alto", f"{high_risk:,}", "Casos prioritarios", "red")

with col6:
    render_kpi("Riesgo medio", f"{medium_risk:,}", "Casos en observación", "orange")

with col7:
    render_kpi("Riesgo bajo", f"{low_risk:,}", "Casos estables", "green")

with col8:
    render_kpi("Sin seguimiento", f"{without_followup:,}", "Más de 15 días", "gold")

with st.expander("Mostrar / ocultar análisis general", expanded=True):
    render_section_title("Distribución de estudiantes")

    tab_distribucion, tab_riesgo, tab_academico = st.tabs(
        [
            "Distribución",
            "Riesgo",
            "Asistencia y notas"
        ]
    )

    with tab_distribucion:
        col_a, col_b = st.columns(2)

        department_count = count_dataframe(filtered_df, "department", "Departamento", 10)

        fig_department = px.bar(
            department_count,
            x="Departamento",
            y="Cantidad",
            title="Estudiantes por departamento",
            color_discrete_sequence=[GOES_BLUE],
            text="Cantidad"
        )

        fig_department = format_chart(fig_department, show_legend=False)
        fig_department.update_layout(
            xaxis_title="Departamento",
            yaxis_title="Cantidad"
        )
        fig_department.update_xaxes(tickangle=-25)
        fig_department.update_traces(textposition="outside")
        render_chart(col_a, fig_department)

        career_count = count_dataframe(filtered_df, "career", "Carrera", 10)
        career_count = career_count.sort_values("Cantidad", ascending=True)

        fig_career = px.bar(
            career_count,
            x="Cantidad",
            y="Carrera",
            orientation="h",
            title="Estudiantes por carrera",
            color_discrete_sequence=[GOES_GOLD],
            text="Cantidad"
        )

        fig_career = format_chart(fig_career, show_legend=False)
        fig_career.update_layout(
            yaxis_title="",
            xaxis_title="Cantidad"
        )
        fig_career.update_traces(textposition="inside")
        render_chart(col_b, fig_career)

        col_c, col_d, col_e = st.columns(3)

        modality_count = count_dataframe(filtered_df, "modality", "Modalidad", 10)

        fig_modality = px.pie(
            modality_count,
            names="Modalidad",
            values="Cantidad",
            title="Estudiantes por modalidad",
            hole=0.55,
            color_discrete_sequence=[GOES_GOLD, GOES_BLUE, GOES_DARK, "#64748b"]
        )

        fig_modality = format_chart(fig_modality)
        fig_modality.update_traces(
            textposition="inside",
            textinfo="percent"
        )
        render_chart(col_c, fig_modality)

        scholarship_count = count_dataframe(filtered_df, "scholarship_type", "Tipo de beca", 10)

        scholarship_total = scholarship_count["Cantidad"].sum()

        scholarship_count["Porcentaje"] = scholarship_count["Cantidad"].apply(
            lambda value: round((value / scholarship_total) * 100, 1)
            if scholarship_total > 0 else 0
        )

        scholarship_count["Etiqueta"] = scholarship_count.apply(
            lambda row: f"{row['Cantidad']} | {row['Porcentaje']}%",
            axis=1
        )

        fig_scholarship = px.bar(
            scholarship_count.sort_values("Cantidad", ascending=True),
            x="Cantidad",
            y="Tipo de beca",
            orientation="h",
            title="Estudiantes por tipo de beca",
            color_discrete_sequence=[GOES_BLUE],
            text="Etiqueta",
            hover_data={
                "Tipo de beca": False,
                "Cantidad": True,
                "Porcentaje": True,
                "Etiqueta": False
            }
        )

        fig_scholarship = format_chart(fig_scholarship, show_legend=False)
        fig_scholarship.update_layout(
            yaxis_title="",
            xaxis_title="Cantidad"
        )
        fig_scholarship.update_traces(
            textposition="outside"
        )
        render_chart(col_d, fig_scholarship)

        status_count = count_dataframe(filtered_df, "status", "Estado", 10)

        fig_status = px.pie(
            status_count,
            names="Estado",
            values="Cantidad",
            title="Estudiantes por estado",
            color="Estado",
            color_discrete_map={
                "Activo": GOES_BLUE,
                "En riesgo": GOES_GOLD,
                "Inactivo": GOES_DARK,
                "Graduado": "#15803D",
                "Suspendido": "#B42318"
            }
        )

        fig_status = format_chart(fig_status)
        fig_status.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )
        render_chart(col_e, fig_status)

    with tab_riesgo:
        col_a, col_b, col_c = st.columns(3)

        risk_count = count_dataframe(filtered_df, "risk_level", "Nivel de riesgo", 10)

        fig_risk = px.pie(
            risk_count,
            names="Nivel de riesgo",
            values="Cantidad",
            title="Estudiantes por nivel de riesgo",
            hole=0.5,
            color="Nivel de riesgo",
            color_discrete_map=RISK_COLOR_MAP
        )

        fig_risk = format_chart(fig_risk)
        fig_risk.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )
        render_chart(col_a, fig_risk)

        risk_department = (
            filtered_df
            .groupby(["department", "risk_level"])
            .size()
            .reset_index(name="Cantidad")
            .rename(
                columns={
                    "department": "Departamento",
                    "risk_level": "Nivel de riesgo"
                }
            )
        )

        top_departments = (
            risk_department
            .groupby("Departamento")["Cantidad"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .index
            .tolist()
        )

        risk_department = risk_department[
            risk_department["Departamento"].isin(top_departments)
        ]

        fig_dept_risk = px.bar(
            risk_department,
            x="Cantidad",
            y="Departamento",
            color="Nivel de riesgo",
            orientation="h",
            title="Riesgo por departamento",
            color_discrete_map=RISK_COLOR_MAP,
            text="Cantidad"
        )

        fig_dept_risk = format_chart(fig_dept_risk)
        fig_dept_risk.update_layout(
            yaxis_title="",
            barmode="stack"
        )
        render_chart(col_b, fig_dept_risk)

        monitor_risk = (
            filtered_df
            .groupby(["assigned_monitor", "risk_level"])
            .size()
            .reset_index(name="Cantidad")
            .rename(
                columns={
                    "assigned_monitor": "Monitor",
                    "risk_level": "Nivel de riesgo"
                }
            )
        )

        top_monitors = (
            monitor_risk
            .groupby("Monitor")["Cantidad"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .index
            .tolist()
        )

        monitor_risk = monitor_risk[
            monitor_risk["Monitor"].isin(top_monitors)
        ]

        fig_monitor_risk = px.bar(
            monitor_risk,
            x="Monitor",
            y="Cantidad",
            color="Nivel de riesgo",
            title="Riesgo por monitor",
            color_discrete_map=RISK_COLOR_MAP,
            text="Cantidad"
        )

        fig_monitor_risk = format_chart(fig_monitor_risk)
        fig_monitor_risk.update_layout(
            xaxis_title="",
            yaxis_title="Cantidad",
            barmode="stack"
        )
        fig_monitor_risk.update_traces(textposition="inside")
        render_chart(col_c, fig_monitor_risk)

        with tab_academico:
         col_a, col_b = st.columns(2)

        performance_by_career = (
            filtered_df
            .groupby("career")
            .agg(
                promedio_academico=("average_grade", "mean"),
                asistencia_promedio=("attendance_rate", "mean"),
                estudiantes=("id", "count")
            )
            .reset_index()
            .rename(
                columns={
                    "career": "Carrera",
                    "promedio_academico": "Promedio académico",
                    "asistencia_promedio": "Asistencia promedio",
                    "estudiantes": "Estudiantes"
                }
            )
        )

        performance_by_career["Promedio académico"] = performance_by_career["Promedio académico"].round(2)
        performance_by_career["Asistencia promedio"] = performance_by_career["Asistencia promedio"].round(1)

        lowest_grade_careers = (
            performance_by_career
            .sort_values("Promedio académico", ascending=True)
            .head(10)
        )

        fig_lowest_grades = px.bar(
            lowest_grade_careers,
            x="Carrera",
            y="Promedio académico",
            title="Carreras con menor promedio académico",
            color_discrete_sequence=[GOES_BLUE],
            text="Promedio académico",
            hover_data={
                "Carrera": True,
                "Promedio académico": ":.2f",
                "Asistencia promedio": ":.1f",
                "Estudiantes": True
            }
        )

        fig_lowest_grades = format_chart(fig_lowest_grades, show_legend=False)
        fig_lowest_grades.update_layout(
            xaxis_title="Carrera",
            yaxis_title="Promedio académico"
        )
        fig_lowest_grades.update_xaxes(tickangle=-25)
        fig_lowest_grades.update_traces(textposition="outside")
        render_chart(col_a, fig_lowest_grades)

        lowest_attendance_careers = (
            performance_by_career
            .sort_values("Asistencia promedio", ascending=True)
            .head(10)
        )

        fig_lowest_attendance = px.bar(
            lowest_attendance_careers,
            x="Carrera",
            y="Asistencia promedio",
            title="Carreras con menor asistencia promedio",
            color_discrete_sequence=[GOES_GOLD],
            text="Asistencia promedio",
            hover_data={
                "Carrera": True,
                "Asistencia promedio": ":.1f",
                "Promedio académico": ":.2f",
                "Estudiantes": True
            }
        )

        fig_lowest_attendance = format_chart(fig_lowest_attendance, show_legend=False)
        fig_lowest_attendance.update_layout(
            xaxis_title="Carrera",
            yaxis_title="Asistencia promedio"
        )
        fig_lowest_attendance.update_xaxes(tickangle=-25)
        fig_lowest_attendance.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )
        render_chart(col_b, fig_lowest_attendance)

with st.expander("Mostrar / ocultar listado de estudiantes", expanded=True):
    render_section_title("Listado de estudiantes")

    students_view = filtered_df.sort_values(
        by=["risk_score", "attendance_rate", "average_grade"],
        ascending=[False, True, True]
    )

    students_view = students_view[
        [
            "student_code",
            "full_name",
            "department",
            "modality",
            "career",
            "attendance_rate",
            "average_grade",
            "risk_level",
            "assigned_monitor"
        ]
    ].copy()

    students_view = students_view.rename(
        columns={
            "student_code": "Código",
            "full_name": "Estudiante",
            "department": "Departamento",
            "modality": "Modalidad",
            "career": "Carrera",
            "attendance_rate": "Asistencia",
            "average_grade": "Promedio",
            "risk_level": "Riesgo",
            "assigned_monitor": "Monitor"
        }
    )

    students_view["Asistencia"] = pd.to_numeric(
        students_view["Asistencia"],
        errors="coerce"
    ).fillna(0)

    students_view["Promedio"] = pd.to_numeric(
        students_view["Promedio"],
        errors="coerce"
    ).fillna(0)

    total_records = len(students_view)

    page_size, page_number, start_row, end_row = render_pagination(
        total_records=total_records,
        key_prefix="dashboard_students",
        label="estudiantes filtrados"
    )

    paginated_students = students_view.iloc[start_row:end_row]

    st.dataframe(
        paginated_students,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Código": st.column_config.TextColumn("Código", width="small"),
            "Estudiante": st.column_config.TextColumn("Estudiante", width="medium"),
            "Departamento": st.column_config.TextColumn("Departamento", width="small"),
            "Modalidad": st.column_config.TextColumn("Modalidad", width="small"),
            "Carrera": st.column_config.TextColumn("Carrera", width="medium"),
            "Asistencia": st.column_config.ProgressColumn(
                "Asistencia",
                min_value=0,
                max_value=100,
                format="%.1f%%",
                width="small"
            ),
            "Promedio": st.column_config.NumberColumn("Promedio", format="%.2f", width="small"),
            "Riesgo": st.column_config.TextColumn("Riesgo", width="small"),
            "Monitor": st.column_config.TextColumn("Monitor", width="small")
        }
    )