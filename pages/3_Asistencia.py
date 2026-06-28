import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from datetime import date

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE

st.set_page_config(page_title="Asistencia | SIBECA", page_icon="", layout="wide")
apply_goes_theme()

page_header(
    "Control de Asistencia",
    "Registro y análisis de asistencia esperada versus asistencia real."
)

engine = get_engine()


@st.cache_data(ttl=1800)
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


@st.cache_data(ttl=1800)
def load_modalities():
    return pd.read_sql("SELECT id, name FROM modalities ORDER BY id", engine)


@st.cache_data(ttl=1800)
def load_attendance():
    return pd.read_sql(
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


students = load_students()
modalities = load_modalities()

if students.empty:
    st.warning("No hay estudiantes registrados.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Resumen", "Registrar asistencia", "Detalle"])

with tab1:
    df = load_attendance()

    if df.empty:
        st.info("Todavía no hay registros de asistencia.")
    else:
        summary = (
            df.groupby(["student_code", "full_name"])
            .agg(
                sesiones_esperadas=("expected_attendance", "sum"),
                asistencias=("attendance_status", lambda x: (x == "Asistió").sum()),
                faltas=("attendance_status", lambda x: (x == "Faltó").sum()),
                llegadas_tarde=("attendance_status", lambda x: (x == "Llegó tarde").sum()),
                justificadas=("attendance_status", lambda x: (x == "Justificado").sum()),
            )
            .reset_index()
        )

        summary["asistencia_%"] = summary.apply(
            lambda row: round((row["asistencias"] / row["sesiones_esperadas"]) * 100, 2)
            if row["sesiones_esperadas"] > 0 else 0,
            axis=1
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Registros de asistencia", f"{len(df):,}")
        col2.metric("Asistencia promedio", f"{summary['asistencia_%'].mean():.1f}%")
        col3.metric("Estudiantes bajo 75%", len(summary[summary["asistencia_%"] < 75]))
        col4.metric("Faltas registradas", int(summary["faltas"].sum()))

        status_count = df["attendance_status"].value_counts().reset_index()
        status_count.columns = ["Estado", "Cantidad"]

        fig = px.bar(
            status_count,
            x="Estado",
            y="Cantidad",
            title="Distribución de estados de asistencia",
            color_discrete_sequence=[GOES_BLUE]
        )

        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Ranking de asistencia")

        st.dataframe(
            summary.sort_values("asistencia_%"),
            use_container_width=True,
            hide_index=True
        )

with tab2:
    st.subheader("Registrar asistencia")

    student_options = {
        f"{row.student_code} - {row.full_name}": row.id
        for row in students.itertuples()
    }

    modality_options = {
        row.name: row.id
        for row in modalities.itertuples()
    }

    with st.form("attendance_form"):
        col1, col2 = st.columns(2)

        with col1:
            selected_student = st.selectbox("Estudiante", list(student_options.keys()))
            session_date = st.date_input("Fecha de sesión", value=date.today())
            expected_attendance = st.checkbox("Asistencia esperada", value=True)

        with col2:
            attendance_status = st.selectbox(
                "Estado de asistencia",
                ["Asistió", "Faltó", "Llegó tarde", "Justificado", "No aplica"]
            )
            modality_name = st.selectbox("Modalidad de la sesión", list(modality_options.keys()))
            observation = st.text_area("Observación")

        submitted = st.form_submit_button("Guardar asistencia")

        if submitted:
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
                        "observation": observation
                    }
                )

            st.cache_data.clear()
            st.success("Asistencia registrada correctamente.")

with tab3:
    st.subheader("Detalle de asistencia")

    df = load_attendance()

    if df.empty:
        st.info("No hay registros para mostrar.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "Estado",
                ["Todos"] + sorted(df["attendance_status"].dropna().unique().tolist())
            )

        with col2:
            modality_filter = st.selectbox(
                "Modalidad",
                ["Todas"] + sorted(df["modality"].dropna().unique().tolist())
            )

        with col3:
            career_filter = st.selectbox(
                "Carrera",
                ["Todas"] + sorted(df["career"].dropna().unique().tolist())
            )

        filtered = df.copy()

        if status_filter != "Todos":
            filtered = filtered[filtered["attendance_status"] == status_filter]

        if modality_filter != "Todas":
            filtered = filtered[filtered["modality"] == modality_filter]

        if career_filter != "Todas":
            filtered = filtered[filtered["career"] == career_filter]

        st.dataframe(filtered, use_container_width=True, hide_index=True)