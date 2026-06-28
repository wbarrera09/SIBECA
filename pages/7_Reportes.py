import io
from datetime import date

import streamlit as st
import pandas as pd
import plotly.express as px

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD, GOES_DARK

st.set_page_config(page_title="Reportes | SIBECA", page_icon="", layout="wide")
apply_goes_theme()

page_header(
    "Reportes",
    "Análisis de datos, filtros ejecutivos y exportación a Excel/PDF."
)

engine = get_engine()


@st.cache_data(ttl=1800)
def load_report_data():
    students = pd.read_sql(
        """
        SELECT 
            s.id,
            s.student_code,
            s.full_name,
            s.age,
            s.sex,
            s.department,
            s.municipality,
            s.education_level,
            s.institution_name,
            s.career,
            m.name AS modality,
            s.scholarship_type,
            s.support_percentage,
            s.status,
            s.assigned_monitor,
            s.enrollment_date
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
            SUM(CASE WHEN attendance_status = 'Faltó' THEN 1 ELSE 0 END) AS absences,
            MIN(session_date) AS first_session_date,
            MAX(session_date) AS last_session_date
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
            AVG(grade) AS average_grade,
            COUNT(*) AS grade_records
        FROM grades
        GROUP BY student_id
        """,
        engine
    )

    followups = pd.read_sql(
        """
        SELECT
            f.student_id,
            COUNT(*) AS followup_count,
            MAX(f.followup_date) AS last_followup_date
        FROM followups f
        GROUP BY f.student_id
        """,
        engine
    )

    df = students.merge(attendance, left_on="id", right_on="student_id", how="left")
    df = df.merge(grades, left_on="id", right_on="student_id", how="left")
    df = df.merge(followups, left_on="id", right_on="student_id", how="left")

    df["expected_sessions"] = df["expected_sessions"].fillna(0)
    df["attended_sessions"] = df["attended_sessions"].fillna(0)
    df["absences"] = df["absences"].fillna(0)
    df["average_grade"] = df["average_grade"].fillna(0)
    df["grade_records"] = df["grade_records"].fillna(0)
    df["followup_count"] = df["followup_count"].fillna(0)

    df["attendance_rate"] = df.apply(
        lambda row: round((row["attended_sessions"] / row["expected_sessions"]) * 100, 2)
        if row["expected_sessions"] > 0 else 0,
        axis=1
    )

    df["risk_score"] = df.apply(calculate_score, axis=1)
    df["risk_level"] = df["risk_score"].apply(calculate_level)

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


def calculate_level(score):
    if score >= 70:
        return "Alto"

    if score >= 40:
        return "Medio"

    return "Bajo"


def to_excel(df):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte SIBECA")

        workbook = writer.book
        worksheet = writer.sheets["Reporte SIBECA"]

        header_format = workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "fg_color": "#111e60",
                "font_color": "#FFFFFF",
                "border": 1,
            }
        )

        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)

    return output.getvalue()


def to_pdf(df):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    output = io.BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(letter),
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24
    )

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("SIBECA - Reporte Ejecutivo de Becados", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    summary_text = Paragraph(
        f"Total de registros: {len(df):,}",
        styles["Normal"]
    )
    elements.append(summary_text)
    elements.append(Spacer(1, 12))

    pdf_df = df[
        [
            "student_code",
            "full_name",
            "department",
            "career",
            "modality",
            "attendance_rate",
            "average_grade",
            "risk_score",
            "risk_level"
        ]
    ].head(35).copy()

    pdf_df.columns = [
        "Código",
        "Nombre",
        "Departamento",
        "Carrera",
        "Modalidad",
        "Asistencia %",
        "Promedio",
        "Riesgo",
        "Nivel"
    ]

    data = [pdf_df.columns.tolist()] + pdf_df.astype(str).values.tolist()

    table = Table(data, repeatRows=1)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111e60")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ]
        )
    )

    elements.append(table)
    doc.build(elements)

    return output.getvalue()


df = load_report_data()

if df.empty:
    st.warning("No hay datos para reportar.")
    st.stop()

st.subheader("Filtros del reporte")

col1, col2, col3, col4 = st.columns(4)

with col1:
    department_filter = st.selectbox(
        "Departamento",
        ["Todos"] + sorted(df["department"].dropna().unique().tolist())
    )

with col2:
    modality_filter = st.selectbox(
        "Modalidad",
        ["Todas"] + sorted(df["modality"].dropna().unique().tolist())
    )

with col3:
    risk_filter = st.selectbox(
        "Nivel de riesgo",
        ["Todos"] + sorted(df["risk_level"].dropna().unique().tolist())
    )

with col4:
    status_filter = st.selectbox(
        "Estado",
        ["Todos"] + sorted(df["status"].dropna().unique().tolist())
    )

col5, col6 = st.columns(2)

with col5:
    career_filter = st.selectbox(
        "Carrera",
        ["Todas"] + sorted(df["career"].dropna().unique().tolist())
    )

with col6:
    scholarship_filter = st.selectbox(
        "Tipo de beca",
        ["Todas"] + sorted(df["scholarship_type"].dropna().unique().tolist())
    )

filtered = df.copy()

if department_filter != "Todos":
    filtered = filtered[filtered["department"] == department_filter]

if modality_filter != "Todas":
    filtered = filtered[filtered["modality"] == modality_filter]

if risk_filter != "Todos":
    filtered = filtered[filtered["risk_level"] == risk_filter]

if status_filter != "Todos":
    filtered = filtered[filtered["status"] == status_filter]

if career_filter != "Todas":
    filtered = filtered[filtered["career"] == career_filter]

if scholarship_filter != "Todas":
    filtered = filtered[filtered["scholarship_type"] == scholarship_filter]

st.divider()

col_a, col_b, col_c, col_d = st.columns(4)

col_a.metric("Registros filtrados", f"{len(filtered):,}")
col_b.metric("Asistencia promedio", f"{filtered['attendance_rate'].mean():.1f}%")
col_c.metric("Promedio académico", f"{filtered['average_grade'].mean():.2f}")
col_d.metric("Riesgo alto", len(filtered[filtered["risk_level"] == "Alto"]))

st.divider()

col_chart1, col_chart2 = st.columns(2)

risk_count = filtered["risk_level"].value_counts().reset_index()
risk_count.columns = ["Nivel de riesgo", "Cantidad"]

fig_risk = px.bar(
    risk_count,
    x="Nivel de riesgo",
    y="Cantidad",
    title="Distribución por nivel de riesgo",
    color="Nivel de riesgo",
    color_discrete_map={
        "Alto": "#B42318",
        "Medio": "#D97706",
        "Bajo": "#15803D"
    }
)

fig_risk.update_layout(paper_bgcolor="white", plot_bgcolor="white")
col_chart1.plotly_chart(fig_risk, use_container_width=True)

modality_count = filtered["modality"].value_counts().reset_index()
modality_count.columns = ["Modalidad", "Cantidad"]

fig_modality = px.pie(
    modality_count,
    names="Modalidad",
    values="Cantidad",
    title="Distribución por modalidad",
    color_discrete_sequence=[GOES_BLUE, GOES_GOLD, GOES_DARK]
)

fig_modality.update_layout(paper_bgcolor="white")
col_chart2.plotly_chart(fig_modality, use_container_width=True)

col_chart3, col_chart4 = st.columns(2)

dept_count = (
    filtered.groupby("department")
    .size()
    .reset_index(name="Cantidad")
    .sort_values("Cantidad", ascending=False)
    .head(10)
)

fig_dept = px.bar(
    dept_count,
    x="Cantidad",
    y="department",
    orientation="h",
    title="Top departamentos",
    color_discrete_sequence=[GOES_BLUE]
)

fig_dept.update_layout(paper_bgcolor="white", plot_bgcolor="white", yaxis_title="Departamento")
col_chart3.plotly_chart(fig_dept, use_container_width=True)

career_count = (
    filtered.groupby("career")
    .size()
    .reset_index(name="Cantidad")
    .sort_values("Cantidad", ascending=False)
    .head(10)
)

fig_career = px.bar(
    career_count,
    x="Cantidad",
    y="career",
    orientation="h",
    title="Top carreras",
    color_discrete_sequence=[GOES_GOLD]
)

fig_career.update_layout(paper_bgcolor="white", plot_bgcolor="white", yaxis_title="Carrera")
col_chart4.plotly_chart(fig_career, use_container_width=True)

st.subheader("Tabla de reporte")

report_columns = [
    "student_code",
    "full_name",
    "age",
    "sex",
    "department",
    "municipality",
    "education_level",
    "institution_name",
    "career",
    "modality",
    "scholarship_type",
    "support_percentage",
    "status",
    "assigned_monitor",
    "attendance_rate",
    "average_grade",
    "risk_score",
    "risk_level",
    "followup_count",
    "last_followup_date"
]

st.dataframe(
    filtered[report_columns],
    use_container_width=True,
    hide_index=True
)

st.subheader("Exportar reporte")

excel_file = to_excel(filtered[report_columns])
pdf_file = to_pdf(filtered[report_columns])

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    st.download_button(
        label="Descargar Excel",
        data=excel_file,
        file_name="reporte_sibeca.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col_exp2:
    st.download_button(
        label="Descargar PDF",
        data=pdf_file,
        file_name="reporte_sibeca.pdf",
        mime="application/pdf"
    )