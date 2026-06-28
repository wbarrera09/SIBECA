import streamlit as st
import pandas as pd
import plotly.express as px

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD, GOES_DARK

st.set_page_config(
    page_title="Dashboard | SIBECA",
    page_icon="",
    layout="wide"
)

apply_goes_theme()

page_header(
    "Dashboard Ejecutivo",
    "Vista general del programa de becados, indicadores clave y estudiantes prioritarios."
)

engine = get_engine()


@st.cache_data(ttl=1800)
def load_dashboard_data():
    students = pd.read_sql(
        """
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
            SUM(CASE WHEN attendance_status = 'Asistió' THEN 1 ELSE 0 END) AS attended_sessions
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
            AVG(grade) AS average_grade
        FROM grades
        GROUP BY student_id
        """,
        engine
    )

    df = students.merge(
        attendance,
        left_on="id",
        right_on="student_id",
        how="left"
    )

    df = df.merge(
        grades,
        left_on="id",
        right_on="student_id",
        how="left"
    )

    df["expected_sessions"] = df["expected_sessions"].fillna(0)
    df["attended_sessions"] = df["attended_sessions"].fillna(0)
    df["average_grade"] = df["average_grade"].fillna(0)

    df["attendance_rate"] = df.apply(
        lambda row: round(
            (row["attended_sessions"] / row["expected_sessions"]) * 100,
            2
        ) if row["expected_sessions"] > 0 else 0,
        axis=1
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

    if row["status"] == "En riesgo":
        score += 20

    return min(score, 100)


def calculate_risk(score):
    if score >= 70:
        return "Alto"

    if score >= 40:
        return "Medio"

    return "Bajo"


df = load_dashboard_data()

if df.empty:
    st.warning("No hay datos cargados todavía.")
    st.stop()

df["risk_score"] = df.apply(calculate_score, axis=1)
df["risk_level"] = df["risk_score"].apply(calculate_risk)

total_students = len(df)
avg_attendance = df["attendance_rate"].mean()
avg_grade = df["average_grade"].mean()
high_risk = len(df[df["risk_level"] == "Alto"])
medium_risk = len(df[df["risk_level"] == "Medio"])

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total becados", f"{total_students:,}")
col2.metric("Asistencia promedio", f"{avg_attendance:.1f}%")
col3.metric("Promedio académico", f"{avg_grade:.2f}")
col4.metric("Riesgo alto", high_risk)
col5.metric("Riesgo medio", medium_risk)

st.divider()

col_a, col_b = st.columns(2)

risk_count = df["risk_level"].value_counts().reset_index()
risk_count.columns = ["Nivel de riesgo", "Cantidad"]

fig_risk = px.bar(
    risk_count,
    x="Nivel de riesgo",
    y="Cantidad",
    title="Estudiantes por nivel de riesgo",
    color="Nivel de riesgo",
    color_discrete_map={
        "Alto": "#B42318",
        "Medio": "#D97706",
        "Bajo": "#15803D"
    }
)

fig_risk.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    title_font_color=GOES_BLUE,
    font_color=GOES_DARK
)

col_a.plotly_chart(fig_risk, use_container_width=True)

modality_count = df["modality"].value_counts().reset_index()
modality_count.columns = ["Modalidad", "Cantidad"]

fig_modality = px.pie(
    modality_count,
    names="Modalidad",
    values="Cantidad",
    title="Distribución por modalidad",
    color_discrete_sequence=[GOES_BLUE, GOES_GOLD, GOES_DARK]
)

fig_modality.update_layout(
    paper_bgcolor="white",
    title_font_color=GOES_BLUE,
    font_color=GOES_DARK
)

col_b.plotly_chart(fig_modality, use_container_width=True)

col_c, col_d = st.columns(2)

dept_risk = (
    df[df["risk_level"].isin(["Alto", "Medio"])]
    .groupby("department")
    .size()
    .reset_index(name="Cantidad")
    .sort_values("Cantidad", ascending=False)
    .head(10)
)

fig_dept = px.bar(
    dept_risk,
    x="Cantidad",
    y="department",
    orientation="h",
    title="Top departamentos con mayor riesgo",
    color_discrete_sequence=[GOES_BLUE]
)

fig_dept.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    title_font_color=GOES_BLUE,
    font_color=GOES_DARK,
    yaxis_title="Departamento"
)

col_c.plotly_chart(fig_dept, use_container_width=True)

career_risk = (
    df[df["risk_level"].isin(["Alto", "Medio"])]
    .groupby("career")
    .size()
    .reset_index(name="Cantidad")
    .sort_values("Cantidad", ascending=False)
    .head(10)
)

fig_career = px.bar(
    career_risk,
    x="Cantidad",
    y="career",
    orientation="h",
    title="Carreras con mayor cantidad de casos en riesgo",
    color_discrete_sequence=[GOES_GOLD]
)

fig_career.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    title_font_color=GOES_BLUE,
    font_color=GOES_DARK,
    yaxis_title="Carrera"
)

col_d.plotly_chart(fig_career, use_container_width=True)

st.subheader("Estudiantes prioritarios")

priority = df.sort_values(
    by=["risk_score", "attendance_rate", "average_grade"],
    ascending=[False, True, True]
)

st.dataframe(
    priority[
        [
            "student_code",
            "full_name",
            "department",
            "career",
            "modality",
            "attendance_rate",
            "average_grade",
            "risk_score",
            "risk_level",
            "assigned_monitor"
        ]
    ].head(25),
    use_container_width=True,
    hide_index=True
)