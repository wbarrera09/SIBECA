import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from datetime import date

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD

st.set_page_config(page_title="Seguimientos | SIBECA", page_icon="", layout="wide")
apply_goes_theme()

page_header(
    "Seguimientos",
    "Historial de contactos, motivos de riesgo, acciones realizadas y próximas intervenciones."
)

engine = get_engine()


@st.cache_data(ttl=1800)
def load_students():
    return pd.read_sql(
        """
        SELECT id, student_code, full_name, department, career
        FROM students
        ORDER BY full_name
        """,
        engine
    )


@st.cache_data(ttl=1800)
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


@st.cache_data(ttl=1800)
def load_followups():
    return pd.read_sql(
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


students = load_students()
risk_reasons = load_risk_reasons()

if students.empty:
    st.warning("No hay estudiantes registrados.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Resumen", "Nuevo seguimiento", "Historial"])

with tab1:
    df = load_followups()

    if df.empty:
        st.info("Aún no hay seguimientos registrados.")
    else:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Seguimientos registrados", f"{len(df):,}")
        col2.metric("Estudiantes contactados", f"{df['student_code'].nunique():,}")
        col3.metric("Casos escalados", len(df[df["result"] == "Caso escalado"]))
        col4.metric("Próximas acciones", df["next_action_date"].notna().sum())

        col_a, col_b = st.columns(2)

        reason_count = (
            df["risk_category"]
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
            color_discrete_sequence=[GOES_BLUE]
        )
        fig_reason.update_layout(paper_bgcolor="white", plot_bgcolor="white")
        col_a.plotly_chart(fig_reason, use_container_width=True)

        result_count = df["result"].value_counts().reset_index()
        result_count.columns = ["Resultado", "Cantidad"]

        fig_result = px.pie(
            result_count,
            names="Resultado",
            values="Cantidad",
            title="Resultado de seguimientos",
            color_discrete_sequence=[GOES_BLUE, GOES_GOLD, "#313945", "#D97706"]
        )
        fig_result.update_layout(paper_bgcolor="white")
        col_b.plotly_chart(fig_result, use_container_width=True)

        st.subheader("Últimos seguimientos")

        st.dataframe(
            df.head(20),
            use_container_width=True,
            hide_index=True
        )

with tab2:
    st.subheader("Registrar nuevo seguimiento")

    student_options = {
        f"{row.student_code} - {row.full_name}": row.id
        for row in students.itertuples()
    }

    if risk_reasons.empty:
        st.warning("No hay motivos de riesgo cargados.")
        reason_options = {}
    else:
        reason_options = {
            f"{row.category} - {row.reason_name}": row.id
            for row in risk_reasons.itertuples()
        }

    with st.form("followup_form"):
        col1, col2 = st.columns(2)

        with col1:
            selected_student = st.selectbox("Estudiante", list(student_options.keys()))
            followup_date = st.date_input("Fecha de seguimiento", value=date.today())
            followup_type = st.selectbox(
                "Tipo de seguimiento",
                ["Llamada", "Correo", "WhatsApp", "Reunión", "Visita", "Otro"]
            )
            result = st.selectbox(
                "Resultado",
                ["Contactado", "No respondió", "Pendiente", "Caso escalado", "Caso cerrado"]
            )

        with col2:
            selected_reason = st.selectbox(
                "Motivo principal",
                list(reason_options.keys()) if reason_options else ["Sin motivo"]
            )
            responsible_user = st.text_input("Responsable", value="Monitor A")
            next_action_date = st.date_input("Fecha próxima acción", value=date.today())
            next_action = st.text_area("Próxima acción")

        comment = st.text_area("Comentario del seguimiento")

        submitted = st.form_submit_button("Guardar seguimiento")

        if submitted:
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
                        "comment": comment,
                        "next_action": next_action,
                        "next_action_date": next_action_date,
                        "responsible_user": responsible_user
                    }
                )

            st.cache_data.clear()
            st.success("Seguimiento registrado correctamente.")

with tab3:
    st.subheader("Historial de seguimientos")

    df = load_followups()

    if df.empty:
        st.info("No hay seguimientos para mostrar.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            result_filter = st.selectbox(
                "Resultado",
                ["Todos"] + sorted(df["result"].dropna().unique().tolist())
            )

        with col2:
            category_filter = st.selectbox(
                "Categoría de riesgo",
                ["Todas"] + sorted(df["risk_category"].dropna().unique().tolist())
            )

        with col3:
            department_filter = st.selectbox(
                "Departamento",
                ["Todos"] + sorted(df["department"].dropna().unique().tolist())
            )

        filtered = df.copy()

        if result_filter != "Todos":
            filtered = filtered[filtered["result"] == result_filter]

        if category_filter != "Todas":
            filtered = filtered[filtered["risk_category"] == category_filter]

        if department_filter != "Todos":
            filtered = filtered[filtered["department"] == department_filter]

        st.caption(f"Registros encontrados: {len(filtered):,}")

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )