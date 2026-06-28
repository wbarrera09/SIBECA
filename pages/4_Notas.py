import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE

st.set_page_config(page_title="Notas | SIBECA", page_icon="", layout="wide")
apply_goes_theme()

page_header(
    "Rendimiento Académico",
    "Registro de notas, promedios y estudiantes con bajo desempeño."
)

engine = get_engine()


@st.cache_data(ttl=1800)
def load_students():
    return pd.read_sql(
        """
        SELECT id, student_code, full_name, career
        FROM students
        ORDER BY full_name
        """,
        engine
    )


@st.cache_data(ttl=1800)
def load_grades():
    return pd.read_sql(
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


students = load_students()

if students.empty:
    st.warning("No hay estudiantes registrados.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Resumen académico", "Registrar nota", "Detalle"])

with tab1:
    df = load_grades()

    if df.empty:
        st.info("No hay notas registradas.")
    else:
        avg_by_student = (
            df.groupby(["student_code", "full_name", "career"])
            .agg(promedio=("grade", "mean"), materias=("subject_name", "count"))
            .reset_index()
        )

        avg_by_student["promedio"] = avg_by_student["promedio"].round(2)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Notas registradas", f"{len(df):,}")
        col2.metric("Promedio general", f"{df['grade'].mean():.2f}")
        col3.metric("Estudiantes bajo 7.0", len(avg_by_student[avg_by_student["promedio"] < 7]))
        col4.metric("Nota mínima", f"{df['grade'].min():.2f}")

        career_avg = (
            df.groupby("career")["grade"]
            .mean()
            .round(2)
            .reset_index()
            .sort_values("grade")
        )

        fig = px.bar(
            career_avg,
            x="grade",
            y="career",
            orientation="h",
            title="Promedio académico por carrera",
            color_discrete_sequence=[GOES_BLUE]
        )

        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Promedio",
            yaxis_title="Carrera"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Estudiantes con menor promedio")

        st.dataframe(
            avg_by_student.sort_values("promedio").head(20),
            use_container_width=True,
            hide_index=True
        )

with tab2:
    st.subheader("Registrar nota")

    student_options = {
        f"{row.student_code} - {row.full_name}": row.id
        for row in students.itertuples()
    }

    with st.form("grade_form"):
        col1, col2 = st.columns(2)

        with col1:
            selected_student = st.selectbox("Estudiante", list(student_options.keys()))
            period = st.text_input("Periodo", value="Ciclo 01-2026")
            subject_name = st.text_input("Materia o módulo")

        with col2:
            grade = st.number_input("Nota", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
            academic_status = st.selectbox("Estado académico", ["Aprobado", "En riesgo", "Reprobado"])
            observation = st.text_area("Observación")

        submitted = st.form_submit_button("Guardar nota")

        if submitted:
            if not subject_name:
                st.error("Debes ingresar la materia o módulo.")
            else:
                if grade < 7:
                    academic_status = "En riesgo"

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
                            "period": period,
                            "subject_name": subject_name,
                            "grade": grade,
                            "academic_status": academic_status,
                            "observation": observation
                        }
                    )

                st.cache_data.clear()
                st.success("Nota registrada correctamente.")

with tab3:
    st.subheader("Detalle de notas")

    df = load_grades()

    if df.empty:
        st.info("No hay notas para mostrar.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            period_filter = st.selectbox(
                "Periodo",
                ["Todos"] + sorted(df["period"].dropna().unique().tolist())
            )

        with col2:
            career_filter = st.selectbox(
                "Carrera",
                ["Todas"] + sorted(df["career"].dropna().unique().tolist())
            )

        with col3:
            status_filter = st.selectbox(
                "Estado académico",
                ["Todos"] + sorted(df["academic_status"].dropna().unique().tolist())
            )

        filtered = df.copy()

        if period_filter != "Todos":
            filtered = filtered[filtered["period"] == period_filter]

        if career_filter != "Todas":
            filtered = filtered[filtered["career"] == career_filter]

        if status_filter != "Todos":
            filtered = filtered[filtered["academic_status"] == status_filter]

        st.dataframe(filtered, use_container_width=True, hide_index=True)