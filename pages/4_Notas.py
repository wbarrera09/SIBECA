import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD, GOES_DARK
from utils.sidebar import apply_sidebar_theme
from utils.pagination import render_pagination

st.set_page_config(
    page_title="Notas | SIBECA",
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

ACADEMIC_STATUS_COLOR_MAP = {
    "Aprobado": GOES_BLUE,
    "En riesgo": GOES_GOLD,
    "Reprobado": "#B42318"
}

def reset_grades_filters():
    st.session_state["grades_detail_student"] = None
    st.session_state["grades_detail_period"] = []
    st.session_state["grades_detail_status"] = []
    st.session_state["grades_detail_department"] = []
    st.session_state["grades_detail_career"] = []
    st.session_state["grades_detail_subject"] = []
    st.session_state["grades_detail_page_number"] = 1

    
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

        .grades-section-title {{
            color: {GOES_BLUE};
            font-family: "Segoe UI", Arial, sans-serif !important;
            font-weight: 800;
            font-size: 1.05rem;
            border-left: 5px solid {GOES_GOLD};
            padding-left: 10px;
            margin-top: 14px;
            margin-bottom: 12px;
        }}

        .grades-filter-title {{
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

        .grades-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.06);
            min-height: 92px;
            margin-bottom: 10px;
        }}

        .grades-card-blue {{
            border-top: 4px solid {GOES_BLUE};
        }}

        .grades-card-gold {{
            border-top: 4px solid {GOES_GOLD};
        }}

        .grades-card-red {{
            border-top: 4px solid #B42318;
        }}

        .grades-card-gray {{
            border-top: 4px solid #64748b;
        }}

        .grades-kpi-label {{
            color: {GOES_DARK};
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 6px;
        }}

        .grades-kpi-value {{
            color: {GOES_BLUE};
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 5px;
        }}

        .grades-kpi-help {{
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

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {{
            background-color: {GOES_BLUE} !important;
            border: 1px solid {GOES_BLUE} !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            max-width: calc(100% - 42px) !important;
            margin-top: 2px !important;
            margin-bottom: 2px !important;
            flex-shrink: 1 !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span {{
            color: #ffffff !important;
            opacity: 1 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
            max-width: calc(100% - 24px) !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] svg {{
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

        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stButton"] button:hover {{
            background-color: {GOES_DARK} !important;
            color: #ffffff !important;
        }}

        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stButton"] button span {{
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


        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {{
            max-width: 100% !important;
            width: auto !important;
            min-width: 0 !important;
            flex-shrink: 1 !important;
        }}

        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span,
        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stMultiSelect"] div[data-baseweb="tag"] div,
        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stMultiSelect"] div[data-baseweb="tag"] p {{
            max-width: none !important;
            width: auto !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
        }}

        div[data-testid="stAppViewContainer"] .block-container div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
            flex-wrap: wrap !important;
            max-height: 160px !important;
        }}

                div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {{
            max-width: none !important;
            width: auto !important;
            min-width: fit-content !important;
            flex-shrink: 0 !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span[title] {{
            max-width: none !important;
            width: auto !important;
            min-width: fit-content !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span {{
            max-width: none !important;
            width: auto !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
        }}

        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
            flex-wrap: wrap !important;
            max-height: 180px !important;
            overflow-y: auto !important;
        }}


        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {{
            max-width: none !important;
            width: auto !important;
            min-width: fit-content !important;
            flex-shrink: 0 !important;
        }}

        div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span {{
            max-width: none !important;
            width: auto !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: normal !important;
            color: #ffffff !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

page_header(
    "Rendimiento Académico",
    "Registro de notas, promedios y estudiantes con bajo desempeño."
)

engine = get_engine()


@st.cache_data(ttl=1800, show_spinner=False)
def load_students():
    return pd.read_sql(
        """
        SELECT
            id,
            student_code,
            full_name,
            career
        FROM students
        ORDER BY full_name
        """,
        engine
    )


@st.cache_data(ttl=1800, show_spinner=False)
def load_grades():
    df = pd.read_sql(
        """
        SELECT
            g.id,
            s.student_code,
            s.full_name,
            s.career,
            s.department,
            g.period,
            g.subject_name,
            g.grade,
            g.academic_status,
            g.observation,
            g.created_at
        FROM grades g
        INNER JOIN students s ON g.student_id = s.id
        ORDER BY g.created_at DESC
        """,
        engine
    )

    text_columns = [
        "student_code",
        "full_name",
        "career",
        "department",
        "period",
        "subject_name",
        "academic_status",
        "observation"
    ]

    for column in text_columns:
        df[column] = df[column].fillna("Sin dato")

    df["grade"] = df["grade"].fillna(0)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    return df


def render_section_title(title):
    st.markdown(
        f"""
        <div class="grades-section-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_filter_title(title):
    st.markdown(
        f"""
        <div class="grades-filter-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_kpi(label, value, help_text, variant):
    css_class = f"grades-card grades-card-{variant}"

    st.markdown(
        f"""
        <div class="{css_class}">
            <div class="grades-kpi-label">{label}</div>
            <div class="grades-kpi-value">{value}</div>
            <div class="grades-kpi-help">{help_text}</div>
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


def clean_text(value):
    if pd.isna(value) or value is None:
        return ""
    return str(value)


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


students = load_students()
grades_reference_df = load_grades()

if students.empty:
    st.warning("No hay estudiantes registrados.")
    st.stop()

student_options = {
    f"{row.student_code} - {row.full_name}": row.id
    for row in students.itertuples()
}

period_reference_options = get_distinct_options(
    grades_reference_df,
    "period"
)

subject_reference_options = get_distinct_options(
    grades_reference_df,
    "subject_name"
)

tab1, tab2, tab3 = st.tabs(
    [
        "Resumen académico",
        "Registrar nota",
        "Detalle"
    ]
)

with tab1:
    render_section_title("Resumen académico")

    df = load_grades()

    if df.empty:
        st.info("No hay notas registradas.")
    else:
        avg_by_student = (
            df.groupby(
                [
                    "student_code",
                    "full_name",
                    "career"
                ]
            )
            .agg(
                promedio=("grade", "mean"),
                materias=("subject_name", "count")
            )
            .reset_index()
        )

        avg_by_student["promedio"] = avg_by_student["promedio"].round(2)

        total_grades = len(df)
        general_average = df["grade"].mean()
        students_below_seven = len(avg_by_student[avg_by_student["promedio"] < 7])
        minimum_grade = df["grade"].min()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_kpi(
                "Notas registradas",
                f"{total_grades:,}",
                "Total de registros",
                "blue"
            )

        with col2:
            render_kpi(
                "Promedio general",
                f"{general_average:.2f}",
                "Promedio académico",
                "gold"
            )

        with col3:
            render_kpi(
                "Bajo 7.0",
                f"{students_below_seven:,}",
                "Estudiantes en observación",
                "red"
            )

        with col4:
            render_kpi(
                "Nota mínima",
                f"{minimum_grade:.2f}",
                "Nota más baja registrada",
                "gray"
            )

        col_a, col_b = st.columns(2)

        career_avg = (
            df.groupby("career")["grade"]
            .mean()
            .round(2)
            .reset_index()
            .sort_values("grade", ascending=True)
            .rename(
                columns={
                    "career": "Carrera",
                    "grade": "Promedio"
                }
            )
        )

        fig_career = px.bar(
            career_avg,
            x="Promedio",
            y="Carrera",
            orientation="h",
            title="Promedio académico por carrera",
            color_discrete_sequence=[GOES_BLUE],
            text="Promedio"
        )

        fig_career = format_chart(fig_career, show_legend=False)
        fig_career.update_layout(
            xaxis_title="Promedio",
            yaxis_title="Carrera"
        )
        fig_career.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )
        render_chart(col_a, fig_career)

        status_count = df["academic_status"].value_counts().reset_index()
        status_count.columns = ["Estado académico", "Cantidad"]

        fig_status = px.pie(
            status_count,
            names="Estado académico",
            values="Cantidad",
            title="Distribución por estado académico",
            color="Estado académico",
            color_discrete_map=ACADEMIC_STATUS_COLOR_MAP,
            hole=0.55
        )

        fig_status = format_chart(fig_status)
        fig_status.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )
        render_chart(col_b, fig_status)

        render_section_title("Estudiantes con menor promedio")

        lowest_students = (
            avg_by_student
            .sort_values("promedio", ascending=True)
            .head(50)
            .copy()
        )

        lowest_students = lowest_students.rename(
            columns={
                "student_code": "Código",
                "full_name": "Estudiante",
                "career": "Carrera",
                "promedio": "Promedio",
                "materias": "Materias"
            }
        )

        total_records = len(lowest_students)

        page_size, page_number, start_row, end_row = render_pagination(
            total_records=total_records,
            key_prefix="grades_summary",
            label="estudiantes"
        )

        paginated_lowest_students = lowest_students.iloc[start_row:end_row]

        st.dataframe(
            paginated_lowest_students,
            use_container_width=True,
            hide_index=True,
            height=420,
            column_config={
                "Código": st.column_config.TextColumn("Código", width="small"),
                "Estudiante": st.column_config.TextColumn("Estudiante", width="medium"),
                "Carrera": st.column_config.TextColumn("Carrera", width="medium"),
                "Promedio": st.column_config.ProgressColumn(
                    "Promedio",
                    min_value=0,
                    max_value=10,
                    format="%.2f",
                    width="small"
                ),
                "Materias": st.column_config.NumberColumn("Materias", width="small")
            }
        )

with tab2:
    render_section_title("Registrar nota")

    with st.container(border=True):
        render_filter_title("Datos académicos")

        col1, col2 = st.columns(2)

        with col1:
            selected_student = st.selectbox(
                "Estudiante",
                options=list(student_options.keys()),
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="grade_student"
            )

            period = reference_value_input(
                "Periodo",
                period_reference_options,
                "grade_period",
                current_value="Ciclo 01-2026"
            )

            subject_name = reference_value_input(
                "Materia o módulo",
                subject_reference_options,
                "grade_subject"
            )

        with col2:
            grade = st.number_input(
                "Nota",
                min_value=0.0,
                max_value=10.0,
                value=7.0,
                step=0.1,
                key="grade_value"
            )

            academic_status = st.selectbox(
                "Estado académico",
                options=[
                    "Aprobado",
                    "En riesgo",
                    "Reprobado"
                ],
                index=None,
                placeholder=EMPTY_PLACEHOLDER,
                key="grade_status"
            )

            observation = st.text_area(
                "Observación",
                key="grade_observation"
            )

        submitted = st.button(
            "Guardar nota",
            use_container_width=True,
            key="grade_submit"
        )

        if submitted:
            if not selected_student:
                st.error("Debes seleccionar un estudiante.")
            elif not period.strip():
                st.error("Debes ingresar el periodo.")
            elif not subject_name.strip():
                st.error("Debes ingresar la materia o módulo.")
            else:
                final_status = academic_status

                if grade < 7:
                    final_status = "En riesgo"

                if not final_status:
                    final_status = "Aprobado"

                with engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            INSERT INTO grades (
                                student_id,
                                period,
                                subject_name,
                                grade,
                                academic_status,
                                observation
                            )
                            VALUES (
                                :student_id,
                                :period,
                                :subject_name,
                                :grade,
                                :academic_status,
                                :observation
                            )
                            """
                        ),
                        {
                            "student_id": student_options[selected_student],
                            "period": period.strip(),
                            "subject_name": subject_name.strip(),
                            "grade": grade,
                            "academic_status": final_status,
                            "observation": observation.strip()
                        }
                    )

                st.cache_data.clear()
                st.success("Nota registrada correctamente.")


with tab3:
    render_section_title("Detalle de notas")

    df = load_grades()

    if df.empty:
        st.info("No hay notas para mostrar.")
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
                render_filter_title("Seleccione los filtros para consultar notas")

            with col_filter_button:
                st.button(
                    "",
                    icon=":material/filter_alt_off:",
                    help="Limpiar filtros",
                    use_container_width=True,
                    on_click=reset_grades_filters,
                    key="grades_clear_filters_button"
                )

            with st.container(border=True):
                col1, col2, col3 = st.columns([2.4, 1.3, 1.3])

                with col1:
                    selected_student_filter = st.selectbox(
                        "Buscar estudiante",
                        options=student_filter_options,
                        index=None,
                        placeholder=EMPTY_PLACEHOLDER,
                        key="grades_detail_student"
                    )

                with col2:
                    period_filter = st.multiselect(
                        "Periodo",
                        options=sorted(df["period"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="grades_detail_period"
                    )

                with col3:
                    status_filter = st.multiselect(
                        "Estado académico",
                        options=sorted(df["academic_status"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="grades_detail_status"
                    )

                col4, col5, col6 = st.columns([2.0, 1.7, 1.3])

                with col4:
                    career_filter = st.multiselect(
                        "Carrera",
                        options=sorted(df["career"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="grades_detail_career"
                    )

                with col5:
                    subject_filter = st.multiselect(
                        "Materia / módulo",
                        options=sorted(df["subject_name"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="grades_detail_subject"
                    )

                with col6:
                    department_filter = st.multiselect(
                        "Departamento",
                        options=sorted(df["department"].dropna().unique().tolist()),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="grades_detail_department"
                    )

        filtered = df.copy()

        if selected_student_filter:
            selected_student_code = selected_student_filter.split(" - ")[0]
            filtered = filtered[
                filtered["student_code"] == selected_student_code
            ]

        if period_filter:
            filtered = filtered[
                filtered["period"].isin(period_filter)
            ]

        if career_filter:
            filtered = filtered[
                filtered["career"].isin(career_filter)
            ]

        if status_filter:
            filtered = filtered[
                filtered["academic_status"].isin(status_filter)
            ]

        if department_filter:
            filtered = filtered[
                filtered["department"].isin(department_filter)
            ]

        if subject_filter:
            filtered = filtered[
                filtered["subject_name"].isin(subject_filter)
            ]

        st.caption(f"Mostrando {len(filtered):,} de {len(df):,} notas.")

        detail_view = filtered[
            [
                "created_at",
                "student_code",
                "full_name",
                "department",
                "career",
                "period",
                "subject_name",
                "grade",
                "academic_status",
                "observation"
            ]
        ].copy()

        detail_view["created_at"] = detail_view["created_at"].dt.strftime("%Y-%m-%d")

        detail_view = detail_view.rename(
            columns={
                "created_at": "Fecha registro",
                "student_code": "Código",
                "full_name": "Estudiante",
                "department": "Departamento",
                "career": "Carrera",
                "period": "Periodo",
                "subject_name": "Materia / módulo",
                "grade": "Nota",
                "academic_status": "Estado académico",
                "observation": "Observación"
            }
        )

        total_records = len(detail_view)

        page_size, page_number, start_row, end_row = render_pagination(
            total_records=total_records,
            key_prefix="grades_detail",
            label="notas"
        )

        paginated_detail = detail_view.iloc[start_row:end_row]

        st.dataframe(
            paginated_detail,
            use_container_width=True,
            hide_index=True,
            height=460,
            column_config={
                "Fecha registro": st.column_config.TextColumn("Fecha registro", width="small"),
                "Código": st.column_config.TextColumn("Código", width="small"),
                "Estudiante": st.column_config.TextColumn("Estudiante", width="medium"),
                "Departamento": st.column_config.TextColumn("Departamento", width="small"),
                "Carrera": st.column_config.TextColumn("Carrera", width="medium"),
                "Periodo": st.column_config.TextColumn("Periodo", width="small"),
                "Materia / módulo": st.column_config.TextColumn("Materia / módulo", width="medium"),
                "Nota": st.column_config.NumberColumn(
                    "Nota",
                    min_value=0,
                    max_value=10,
                    format="%.2f",
                    width="small"
                ),
                "Estado académico": st.column_config.TextColumn("Estado académico", width="small"),
                "Observación": st.column_config.TextColumn("Observación", width="large")
            }
        )