import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD, GOES_DARK
from utils.sidebar import apply_sidebar_theme
from utils.pagination import render_pagination

st.set_page_config(
    page_title="Alertas | SIBECA",
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

RISK_COLOR_MAP = {
    "Alto": "#B42318",
    "Medio": GOES_GOLD,
    "Bajo": "#64748b"
}

ALERT_STATUS_COLOR_MAP = {
    "Abierta": "#B42318",
    "En seguimiento": GOES_GOLD,
    "Resuelta": "#15803D",
    "Descartada": "#64748b"
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

        .alerts-section-title {{
            color: {GOES_BLUE};
            font-family: "Segoe UI", Arial, sans-serif !important;
            font-weight: 800;
            font-size: 1.05rem;
            border-left: 5px solid {GOES_GOLD};
            padding-left: 10px;
            margin-top: 14px;
            margin-bottom: 12px;
        }}

        .alerts-filter-title {{
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

        .alerts-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.06);
            min-height: 92px;
            margin-bottom: 10px;
        }}

        .alerts-card-blue {{
            border-top: 4px solid {GOES_BLUE};
        }}

        .alerts-card-gold {{
            border-top: 4px solid {GOES_GOLD};
        }}

        .alerts-card-red {{
            border-top: 4px solid #B42318;
        }}

        .alerts-card-gray {{
            border-top: 4px solid #64748b;
        }}

        .alerts-kpi-label {{
            color: {GOES_DARK};
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 6px;
        }}

        .alerts-kpi-value {{
            color: {GOES_BLUE};
            font-size: 1.45rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 5px;
        }}

        .alerts-kpi-help {{
            color: #64748b;
            font-size: 0.72rem;
        }}

        .alerts-info-box {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-left: 5px solid {GOES_GOLD};
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 4px 12px rgba(17, 30, 96, 0.06);
            color: {GOES_DARK};
            margin-bottom: 14px;
        }}

        .alerts-info-box-title {{
            color: {GOES_BLUE};
            font-weight: 900;
            font-size: 1rem;
            margin-bottom: 8px;
        }}

        .alerts-info-box ul {{
            margin-top: 6px;
            margin-bottom: 0;
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

        div[class*="st-key-alerts_clear_open_filters_button"] button,
        div[class*="st-key-alerts_clear_history_filters_button"] button {{
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

        div[class*="st-key-alerts_clear_open_filters_button"] button:hover,
        div[class*="st-key-alerts_clear_history_filters_button"] button:hover {{
            background-color: {GOES_DARK} !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
        }}

        div[class*="st-key-alerts_clear_open_filters_button"] button span,
        div[class*="st-key-alerts_clear_open_filters_button"] button svg,
        div[class*="st-key-alerts_clear_history_filters_button"] button span,
        div[class*="st-key-alerts_clear_history_filters_button"] button svg {{
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
    "Alertas Tempranas",
    "Identificación automática de estudiantes con riesgo académico, baja asistencia o falta de seguimiento."
)

engine = get_engine()


@st.cache_data(ttl=1800, show_spinner=False)
def load_students_base():
    students = pd.read_sql(
        """
        SELECT 
            s.id,
            s.student_code,
            s.full_name,
            s.department,
            s.career,
            s.status,
            s.assigned_monitor,
            m.name AS modality
        FROM students s
        LEFT JOIN modalities m ON s.modality_id = m.id
        """,
        engine
    )

    attendance = pd.read_sql(
        """
        SELECT
            student_id,
            COUNT(*) AS expected_sessions,
            SUM(CASE WHEN attendance_status = 'Asistió' THEN 1 ELSE 0 END) AS attended_sessions,
            SUM(CASE WHEN attendance_status = 'Faltó' THEN 1 ELSE 0 END) AS absences
        FROM attendance_records
        WHERE expected_attendance = TRUE
        GROUP BY student_id
        """,
        engine
    )

    grades = pd.read_sql(
        """
        SELECT
            student_id,
            COUNT(*) AS grade_count,
            AVG(grade) AS average_grade
        FROM grades
        GROUP BY student_id
        """,
        engine
    )

    followups = pd.read_sql(
        """
        SELECT
            student_id,
            MAX(followup_date) AS last_followup_date,
            COUNT(*) AS followup_count
        FROM followups
        GROUP BY student_id
        """,
        engine
    )

    df = students.merge(attendance, left_on="id", right_on="student_id", how="left")
    df = df.drop(columns=["student_id"], errors="ignore")
    df = df.merge(grades, left_on="id", right_on="student_id", how="left")
    df = df.drop(columns=["student_id"], errors="ignore")
    df = df.merge(followups, left_on="id", right_on="student_id", how="left")
    df = df.drop(columns=["student_id"], errors="ignore")

    text_columns = [
        "student_code",
        "full_name",
        "department",
        "career",
        "status",
        "assigned_monitor",
        "modality"
    ]

    for column in text_columns:
        df[column] = df[column].fillna("Sin dato")

    df["expected_sessions"] = df["expected_sessions"].fillna(0)
    df["attended_sessions"] = df["attended_sessions"].fillna(0)
    df["absences"] = df["absences"].fillna(0)
    df["grade_count"] = df["grade_count"].fillna(0)
    df["average_grade"] = df["average_grade"].fillna(0)
    df["followup_count"] = df["followup_count"].fillna(0)

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


@st.cache_data(ttl=1800, show_spinner=False)
def load_alerts():
    df = pd.read_sql(
        """
        SELECT
            a.id,
            a.generated_at,
            s.student_code,
            s.full_name,
            s.department,
            s.career,
            a.alert_type,
            a.risk_level,
            a.risk_score,
            a.alert_message,
            a.status,
            a.resolved_at
        FROM alerts a
        INNER JOIN students s ON a.student_id = s.id
        ORDER BY a.generated_at DESC
        """,
        engine
    )

    text_columns = [
        "student_code",
        "full_name",
        "department",
        "career",
        "alert_type",
        "risk_level",
        "alert_message",
        "status"
    ]

    for column in text_columns:
        df[column] = df[column].fillna("Sin dato")

    df["risk_score"] = df["risk_score"].fillna(0)
    df["generated_at"] = pd.to_datetime(df["generated_at"], errors="coerce")
    df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce")

    return df


def calculate_alert(row):
    score = 0
    reasons = []

    has_attendance = row["expected_sessions"] > 0
    has_grades = row["grade_count"] > 0

    if has_attendance and row["attendance_rate"] < 75:
        score += 30
        reasons.append("asistencia menor al 75%")

    if has_attendance and row["attendance_rate"] < 60:
        score += 20
        reasons.append("asistencia crítica menor al 60%")

    if has_attendance and row["absences"] >= 3:
        score += 15
        reasons.append("tres o más faltas registradas")

    if has_grades and row["average_grade"] < 7:
        score += 25
        reasons.append("promedio académico menor a 7.0")

    if has_grades and row["average_grade"] < 6:
        score += 15
        reasons.append("promedio académico crítico menor a 6.0")

    if row["days_without_followup"] > 15:
        score += 15
        reasons.append("más de 15 días sin seguimiento")

    if row["status"] == "En riesgo":
        score += 20
        reasons.append("estado actual marcado como en riesgo")

    score = min(score, 100)

    if score >= 70:
        level = "Alto"
    elif score >= 40:
        level = "Medio"
    else:
        level = "Bajo"

    if reasons:
        message = "El estudiante presenta " + ", ".join(reasons) + "."
    else:
        message = "Sin señales críticas detectadas."

    if has_attendance and row["attendance_rate"] < 75:
        alert_type = "Baja asistencia"
    elif has_grades and row["average_grade"] < 7:
        alert_type = "Bajo rendimiento"
    elif row["days_without_followup"] > 15:
        alert_type = "Sin seguimiento"
    else:
        alert_type = "Riesgo general"

    return score, level, alert_type, message


def generate_alerts():
    df = load_students_base()
    generated = 0

    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM alerts WHERE status = 'Abierta';")
        )

        for _, row in df.iterrows():
            score, level, alert_type, message = calculate_alert(row)

            if level in ["Alto", "Medio"]:
                conn.execute(
                    text(
                        """
                        INSERT INTO alerts (
                            student_id,
                            alert_type,
                            risk_level,
                            risk_score,
                            alert_message,
                            status
                        )
                        VALUES (
                            :student_id,
                            :alert_type,
                            :risk_level,
                            :risk_score,
                            :alert_message,
                            'Abierta'
                        )
                        """
                    ),
                    {
                        "student_id": int(row["id"]),
                        "alert_type": alert_type,
                        "risk_level": level,
                        "risk_score": score,
                        "alert_message": message
                    }
                )

                generated += 1

    return generated


def render_section_title(title):
    st.markdown(
        f"""
        <div class="alerts-section-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_filter_title(title):
    st.markdown(
        f"""
        <div class="alerts-filter-title">{title}</div>
        """,
        unsafe_allow_html=True
    )


def render_kpi(label, value, help_text, variant):
    css_class = f"alerts-card alerts-card-{variant}"

    st.markdown(
        f"""
        <div class="{css_class}">
            <div class="alerts-kpi-label">{label}</div>
            <div class="alerts-kpi-value">{value}</div>
            <div class="alerts-kpi-help">{help_text}</div>
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


def build_student_filter_options(dataframe):
    if dataframe.empty:
        return []

    student_filter_df = (
        dataframe[
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

    return (
        student_filter_df
        .sort_values("student_selector")["student_selector"]
        .tolist()
    )


def reset_open_alert_filters():
    st.session_state["alerts_open_student"] = None
    st.session_state["alerts_open_risk"] = []
    st.session_state["alerts_open_type"] = []
    st.session_state["alerts_open_department"] = []
    st.session_state["alerts_open_page_number"] = 1


def reset_history_alert_filters():
    st.session_state["alerts_history_student"] = None
    st.session_state["alerts_history_status"] = []
    st.session_state["alerts_history_risk"] = []
    st.session_state["alerts_history_type"] = []
    st.session_state["alerts_history_department"] = []
    st.session_state["alerts_history_page_number"] = 1


def prepare_alert_table(dataframe):
    detail_view = dataframe[
        [
            "generated_at",
            "student_code",
            "full_name",
            "department",
            "career",
            "alert_type",
            "risk_level",
            "risk_score",
            "alert_message",
            "status",
            "resolved_at"
        ]
    ].copy()

    detail_view["generated_at"] = detail_view["generated_at"].dt.strftime("%Y-%m-%d")
    detail_view["resolved_at"] = detail_view["resolved_at"].dt.strftime("%Y-%m-%d")
    detail_view["resolved_at"] = detail_view["resolved_at"].fillna("")

    return detail_view.rename(
        columns={
            "generated_at": "Fecha generación",
            "student_code": "Código",
            "full_name": "Estudiante",
            "department": "Departamento",
            "career": "Carrera",
            "alert_type": "Tipo de alerta",
            "risk_level": "Nivel",
            "risk_score": "Score",
            "alert_message": "Mensaje",
            "status": "Estado",
            "resolved_at": "Fecha cierre"
        }
    )


tab1, tab2, tab3 = st.tabs(
    [
        "Alertas abiertas",
        "Generar alertas",
        "Histórico"
    ]
)

with tab1:
    render_section_title("Alertas abiertas")

    alerts = load_alerts()
    opened = alerts[alerts["status"] == "Abierta"].copy() if not alerts.empty else pd.DataFrame()

    if opened.empty:
        st.info("No hay alertas abiertas.")
    else:
        student_filter_options = build_student_filter_options(opened)

        with st.expander("Mostrar / ocultar filtros de búsqueda", expanded=True):
            col_filter_title, col_filter_button = st.columns([10, 1])

            with col_filter_title:
                render_filter_title("Seleccione los filtros para consultar alertas abiertas")

            with col_filter_button:
                st.button(
                    "",
                    icon=":material/filter_alt_off:",
                    help="Limpiar filtros",
                    use_container_width=True,
                    on_click=reset_open_alert_filters,
                    key="alerts_clear_open_filters_button"
                )

            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([2.4, 1.2, 1.5, 1.4])

                with col1:
                    selected_student_filter = st.selectbox(
                        "Buscar estudiante",
                        options=student_filter_options,
                        index=None,
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_open_student"
                    )

                with col2:
                    risk_filter = st.multiselect(
                        "Nivel de riesgo",
                        options=get_clean_options(opened, "risk_level"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_open_risk"
                    )

                with col3:
                    type_filter = st.multiselect(
                        "Tipo de alerta",
                        options=get_clean_options(opened, "alert_type"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_open_type"
                    )

                with col4:
                    department_filter = st.multiselect(
                        "Departamento",
                        options=get_clean_options(opened, "department"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_open_department"
                    )

        filtered_opened = opened.copy()

        if selected_student_filter:
            selected_student_code = selected_student_filter.split(" - ")[0]
            filtered_opened = filtered_opened[
                filtered_opened["student_code"] == selected_student_code
            ]

        if risk_filter:
            filtered_opened = filtered_opened[
                filtered_opened["risk_level"].isin(risk_filter)
            ]

        if type_filter:
            filtered_opened = filtered_opened[
                filtered_opened["alert_type"].isin(type_filter)
            ]

        if department_filter:
            filtered_opened = filtered_opened[
                filtered_opened["department"].isin(department_filter)
            ]

        st.caption(f"Mostrando {len(filtered_opened):,} de {len(opened):,} alertas abiertas.")

        if filtered_opened.empty:
            st.warning("No hay alertas abiertas que coincidan con los filtros seleccionados.")
        else:
            avg_score = filtered_opened["risk_score"].mean()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                render_kpi(
                    "Alertas abiertas",
                    f"{len(filtered_opened):,}",
                    "Alertas filtradas",
                    "blue"
                )

            with col2:
                render_kpi(
                    "Riesgo alto",
                    f"{len(filtered_opened[filtered_opened['risk_level'] == 'Alto']):,}",
                    "Alertas críticas",
                    "red"
                )

            with col3:
                render_kpi(
                    "Riesgo medio",
                    f"{len(filtered_opened[filtered_opened['risk_level'] == 'Medio']):,}",
                    "Alertas preventivas",
                    "gold"
                )

            with col4:
                render_kpi(
                    "Score promedio",
                    f"{avg_score:.1f}",
                    "Promedio de riesgo",
                    "gray"
                )

            col_a, col_b = st.columns(2)

            risk_count = filtered_opened["risk_level"].value_counts().reset_index()
            risk_count.columns = ["Nivel", "Cantidad"]

            fig_risk = px.bar(
                risk_count,
                x="Nivel",
                y="Cantidad",
                color="Nivel",
                title="Alertas abiertas por nivel",
                color_discrete_map=RISK_COLOR_MAP,
                text="Cantidad"
            )
            fig_risk = format_chart(fig_risk, show_legend=False)
            fig_risk.update_layout(
                xaxis_title="Nivel",
                yaxis_title="Cantidad"
            )
            fig_risk.update_traces(textposition="outside")
            render_chart(col_a, fig_risk)

            type_count = filtered_opened["alert_type"].value_counts().reset_index()
            type_count.columns = ["Tipo", "Cantidad"]

            fig_type = px.bar(
                type_count,
                x="Cantidad",
                y="Tipo",
                orientation="h",
                title="Alertas abiertas por tipo",
                color_discrete_sequence=[GOES_BLUE],
                text="Cantidad"
            )
            fig_type = format_chart(fig_type, show_legend=False)
            fig_type.update_layout(
                xaxis_title="Cantidad",
                yaxis_title="Tipo"
            )
            fig_type.update_traces(textposition="outside")
            render_chart(col_b, fig_type)

            render_section_title("Detalle de alertas abiertas")

            detail_view = prepare_alert_table(filtered_opened)
            total_records = len(detail_view)

            page_size, page_number, start_row, end_row = render_pagination(
                total_records=total_records,
                key_prefix="alerts_open",
                label="alertas"
            )

            paginated_detail = detail_view.iloc[start_row:end_row]

            st.dataframe(
                paginated_detail,
                use_container_width=True,
                hide_index=True,
                height=460,
                column_config={
                    "Fecha generación": st.column_config.TextColumn("Fecha generación", width="small"),
                    "Código": st.column_config.TextColumn("Código", width="small"),
                    "Estudiante": st.column_config.TextColumn("Estudiante", width="medium"),
                    "Departamento": st.column_config.TextColumn("Departamento", width="small"),
                    "Carrera": st.column_config.TextColumn("Carrera", width="medium"),
                    "Tipo de alerta": st.column_config.TextColumn("Tipo de alerta", width="medium"),
                    "Nivel": st.column_config.TextColumn("Nivel", width="small"),
                    "Score": st.column_config.ProgressColumn(
                        "Score",
                        min_value=0,
                        max_value=100,
                        format="%.0f",
                        width="small"
                    ),
                    "Mensaje": st.column_config.TextColumn("Mensaje", width="large"),
                    "Estado": st.column_config.TextColumn("Estado", width="small"),
                    "Fecha cierre": st.column_config.TextColumn("Fecha cierre", width="small")
                }
            )

            with st.expander("Cambiar estado de una alerta", expanded=False):
                render_filter_title("Actualización de estado")

                alert_options = {
                    f"{row.id} - {row.student_code} - {row.full_name} - {row.risk_level}": row.id
                    for row in filtered_opened.itertuples()
                }

                col_status_1, col_status_2 = st.columns([2.6, 1.4])

                with col_status_1:
                    selected_alert = st.selectbox(
                        "Seleccionar alerta",
                        options=list(alert_options.keys()),
                        index=None,
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_open_selected_alert"
                    )

                with col_status_2:
                    new_status = st.selectbox(
                        "Nuevo estado",
                        options=[
                            "En seguimiento",
                            "Resuelta",
                            "Descartada"
                        ],
                        index=None,
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_open_new_status"
                    )

                if st.button(
                    "Actualizar estado",
                    use_container_width=True,
                    key="alerts_update_status"
                ):
                    if not selected_alert:
                        st.error("Debes seleccionar una alerta.")
                    elif not new_status:
                        st.error("Debes seleccionar el nuevo estado.")
                    else:
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    UPDATE alerts
                                    SET status = :status,
                                        resolved_at = CASE 
                                            WHEN :status IN ('Resuelta', 'Descartada') THEN CURRENT_TIMESTAMP
                                            ELSE resolved_at
                                        END
                                    WHERE id = :alert_id
                                    """
                                ),
                                {
                                    "status": new_status,
                                    "alert_id": alert_options[selected_alert]
                                }
                            )

                        st.cache_data.clear()
                        st.success("Estado actualizado correctamente.")
                        st.rerun()

with tab2:
    render_section_title("Generación automática de alertas")

    st.markdown(
        """
        <div class="alerts-info-box">
            <div class="alerts-info-box-title">Motor de alertas</div>
            El motor evalúa únicamente asistencia cuando existen sesiones esperadas y evalúa notas únicamente cuando existen calificaciones registradas.
            <ul>
                <li>Asistencia menor a 75%.</li>
                <li>Asistencia crítica menor a 60%.</li>
                <li>Tres o más faltas registradas.</li>
                <li>Promedio académico menor a 7.0.</li>
                <li>Promedio académico crítico menor a 6.0.</li>
                <li>Más de 15 días sin seguimiento.</li>
                <li>Estado actual del estudiante marcado como en riesgo.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Generar / actualizar alertas abiertas",
        use_container_width=True,
        key="alerts_generate_button"
    ):
        try:
            with st.spinner("Evaluando estudiantes y generando alertas..."):
                total = generate_alerts()

            st.cache_data.clear()
            st.success(f"Alertas generadas correctamente: {total}")

        except Exception as error:
            st.error("Ocurrió un error al generar alertas.")
            st.exception(error)

    render_section_title("Vista previa de estudiantes evaluados")

    df = load_students_base()

    if df.empty:
        st.info("No hay estudiantes para evaluar.")
    else:
        results = []

        for _, row in df.iterrows():
            score, level, alert_type, message = calculate_alert(row)

            results.append(
                {
                    "student_code": row["student_code"],
                    "full_name": row["full_name"],
                    "department": row["department"],
                    "career": row["career"],
                    "expected_sessions": row["expected_sessions"],
                    "attendance_rate": row["attendance_rate"],
                    "grade_count": row["grade_count"],
                    "average_grade": row["average_grade"],
                    "days_without_followup": row["days_without_followup"],
                    "risk_score": score,
                    "risk_level": level,
                    "alert_type": alert_type,
                    "message": message
                }
            )

        preview = pd.DataFrame(results)
        preview = preview.sort_values("risk_score", ascending=False)

        preview_view = preview.rename(
            columns={
                "student_code": "Código",
                "full_name": "Estudiante",
                "department": "Departamento",
                "career": "Carrera",
                "expected_sessions": "Sesiones esperadas",
                "attendance_rate": "Asistencia",
                "grade_count": "Notas registradas",
                "average_grade": "Promedio",
                "days_without_followup": "Días sin seguimiento",
                "risk_score": "Score",
                "risk_level": "Nivel",
                "alert_type": "Tipo de alerta",
                "message": "Mensaje"
            }
        )

        total_records = len(preview_view)

        page_size, page_number, start_row, end_row = render_pagination(
            total_records=total_records,
            key_prefix="alerts_preview",
            label="estudiantes"
        )

        paginated_preview = preview_view.iloc[start_row:end_row]

        st.dataframe(
            paginated_preview,
            use_container_width=True,
            hide_index=True,
            height=460,
            column_config={
                "Código": st.column_config.TextColumn("Código", width="small"),
                "Estudiante": st.column_config.TextColumn("Estudiante", width="medium"),
                "Departamento": st.column_config.TextColumn("Departamento", width="small"),
                "Carrera": st.column_config.TextColumn("Carrera", width="medium"),
                "Sesiones esperadas": st.column_config.NumberColumn("Sesiones esperadas", width="small"),
                "Asistencia": st.column_config.ProgressColumn(
                    "Asistencia",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%",
                    width="small"
                ),
                "Notas registradas": st.column_config.NumberColumn("Notas registradas", width="small"),
                "Promedio": st.column_config.NumberColumn(
                    "Promedio",
                    min_value=0,
                    max_value=10,
                    format="%.2f",
                    width="small"
                ),
                "Días sin seguimiento": st.column_config.NumberColumn("Días sin seguimiento", width="small"),
                "Score": st.column_config.ProgressColumn(
                    "Score",
                    min_value=0,
                    max_value=100,
                    format="%.0f",
                    width="small"
                ),
                "Nivel": st.column_config.TextColumn("Nivel", width="small"),
                "Tipo de alerta": st.column_config.TextColumn("Tipo de alerta", width="medium"),
                "Mensaje": st.column_config.TextColumn("Mensaje", width="large")
            }
        )

with tab3:
    render_section_title("Histórico de alertas")

    alerts = load_alerts()

    if alerts.empty:
        st.info("No hay alertas registradas.")
    else:
        student_filter_options = build_student_filter_options(alerts)

        with st.expander("Mostrar / ocultar filtros de búsqueda", expanded=True):
            col_filter_title, col_filter_button = st.columns([10, 1])

            with col_filter_title:
                render_filter_title("Seleccione los filtros para consultar histórico de alertas")

            with col_filter_button:
                st.button(
                    "",
                    icon=":material/filter_alt_off:",
                    help="Limpiar filtros",
                    use_container_width=True,
                    on_click=reset_history_alert_filters,
                    key="alerts_clear_history_filters_button"
                )

            with st.container(border=True):
                col1, col2, col3 = st.columns([2.4, 1.3, 1.3])

                with col1:
                    selected_student_filter = st.selectbox(
                        "Buscar estudiante",
                        options=student_filter_options,
                        index=None,
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_history_student"
                    )

                with col2:
                    status_filter = st.multiselect(
                        "Estado",
                        options=get_clean_options(alerts, "status"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_history_status"
                    )

                with col3:
                    risk_filter = st.multiselect(
                        "Nivel de riesgo",
                        options=get_clean_options(alerts, "risk_level"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_history_risk"
                    )

                col4, col5 = st.columns([1.7, 1.3])

                with col4:
                    type_filter = st.multiselect(
                        "Tipo de alerta",
                        options=get_clean_options(alerts, "alert_type"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_history_type"
                    )

                with col5:
                    department_filter = st.multiselect(
                        "Departamento",
                        options=get_clean_options(alerts, "department"),
                        placeholder=EMPTY_PLACEHOLDER,
                        key="alerts_history_department"
                    )

        filtered = alerts.copy()

        if selected_student_filter:
            selected_student_code = selected_student_filter.split(" - ")[0]
            filtered = filtered[
                filtered["student_code"] == selected_student_code
            ]

        if status_filter:
            filtered = filtered[
                filtered["status"].isin(status_filter)
            ]

        if risk_filter:
            filtered = filtered[
                filtered["risk_level"].isin(risk_filter)
            ]

        if type_filter:
            filtered = filtered[
                filtered["alert_type"].isin(type_filter)
            ]

        if department_filter:
            filtered = filtered[
                filtered["department"].isin(department_filter)
            ]

        st.caption(f"Mostrando {len(filtered):,} de {len(alerts):,} alertas.")

        if filtered.empty:
            st.warning("No hay alertas que coincidan con los filtros seleccionados.")
        else:
            detail_view = prepare_alert_table(filtered)
            total_records = len(detail_view)

            page_size, page_number, start_row, end_row = render_pagination(
                total_records=total_records,
                key_prefix="alerts_history",
                label="alertas"
            )

            paginated_detail = detail_view.iloc[start_row:end_row]

            st.dataframe(
                paginated_detail,
                use_container_width=True,
                hide_index=True,
                height=460,
                column_config={
                    "Fecha generación": st.column_config.TextColumn("Fecha generación", width="small"),
                    "Código": st.column_config.TextColumn("Código", width="small"),
                    "Estudiante": st.column_config.TextColumn("Estudiante", width="medium"),
                    "Departamento": st.column_config.TextColumn("Departamento", width="small"),
                    "Carrera": st.column_config.TextColumn("Carrera", width="medium"),
                    "Tipo de alerta": st.column_config.TextColumn("Tipo de alerta", width="medium"),
                    "Nivel": st.column_config.TextColumn("Nivel", width="small"),
                    "Score": st.column_config.ProgressColumn(
                        "Score",
                        min_value=0,
                        max_value=100,
                        format="%.0f",
                        width="small"
                    ),
                    "Mensaje": st.column_config.TextColumn("Mensaje", width="large"),
                    "Estado": st.column_config.TextColumn("Estado", width="small"),
                    "Fecha cierre": st.column_config.TextColumn("Fecha cierre", width="small")
                }
            )
