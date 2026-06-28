import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD, GOES_DARK

st.set_page_config(page_title="Alertas | SIBECA", page_icon="", layout="wide")
apply_goes_theme()

page_header(
    "Alertas Tempranas",
    "Identificación automática de estudiantes con riesgo académico, baja asistencia o falta de seguimiento."
)

engine = get_engine()


@st.cache_data(ttl=1800)
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
    df = df.merge(grades, left_on="id", right_on="student_id", how="left")
    df = df.merge(followups, left_on="id", right_on="student_id", how="left")

    df["expected_sessions"] = df["expected_sessions"].fillna(0)
    df["attended_sessions"] = df["attended_sessions"].fillna(0)
    df["absences"] = df["absences"].fillna(0)
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
        lambda x: (today - x).days if pd.notna(x) else 999
    )

    return df


@st.cache_data(ttl=1800)
def load_alerts():
    return pd.read_sql(
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


def calculate_alert(row):
    score = 0
    reasons = []

    if row["attendance_rate"] < 75:
        score += 30
        reasons.append("asistencia menor al 75%")

    if row["attendance_rate"] < 60:
        score += 20
        reasons.append("asistencia crítica menor al 60%")

    if row["absences"] >= 3:
        score += 15
        reasons.append("tres o más faltas registradas")

    if row["average_grade"] < 7:
        score += 25
        reasons.append("promedio académico menor a 7.0")

    if row["average_grade"] < 6:
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

    if row["attendance_rate"] < 75:
        alert_type = "Baja asistencia"
    elif row["average_grade"] < 7:
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


tab1, tab2, tab3 = st.tabs(["Alertas abiertas", "Generar alertas", "Histórico"])

with tab1:
    alerts = load_alerts()

    opened = alerts[alerts["status"] == "Abierta"] if not alerts.empty else pd.DataFrame()

    if opened.empty:
        st.info("No hay alertas abiertas.")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("Alertas abiertas", len(opened))
        col2.metric("Riesgo alto", len(opened[opened["risk_level"] == "Alto"]))
        col3.metric("Riesgo medio", len(opened[opened["risk_level"] == "Medio"]))

        risk_count = opened["risk_level"].value_counts().reset_index()
        risk_count.columns = ["Nivel", "Cantidad"]

        fig = px.bar(
            risk_count,
            x="Nivel",
            y="Cantidad",
            color="Nivel",
            title="Alertas abiertas por nivel",
            color_discrete_map={
                "Alto": "#B42318",
                "Medio": "#D97706",
                "Bajo": "#15803D"
            }
        )
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detalle de alertas abiertas")

        st.dataframe(
            opened,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Cambiar estado de alerta")

        alert_options = {
            f"{row.id} - {row.student_code} - {row.full_name} - {row.risk_level}": row.id
            for row in opened.itertuples()
        }

        selected_alert = st.selectbox("Seleccionar alerta", list(alert_options.keys()))
        new_status = st.selectbox("Nuevo estado", ["En seguimiento", "Resuelta", "Descartada"])

        if st.button("Actualizar estado"):
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
    st.subheader("Generación automática de alertas")

    st.markdown(
        """
        El motor de alertas evalúa:
        - Asistencia menor a 75%.
        - Asistencia crítica menor a 60%.
        - Promedio académico menor a 7.0.
        - Promedio académico crítico menor a 6.0.
        - Más de 15 días sin seguimiento.
        - Estado actual del estudiante marcado como en riesgo.
        """
    )

    if st.button("Generar / actualizar alertas abiertas"):
        try:
            with st.spinner("Evaluando estudiantes y generando alertas..."):
                total = generate_alerts()

            st.cache_data.clear()
            st.success(f"Alertas generadas correctamente: {total}")

        except Exception as e:
            st.error("Ocurrió un error al generar alertas.")
            st.exception(e)

    st.subheader("Vista previa de estudiantes evaluados")

    df = load_students_base()

    if not df.empty:
        results = []

        for _, row in df.iterrows():
            score, level, alert_type, message = calculate_alert(row)

            results.append(
                {
                    "student_code": row["student_code"],
                    "full_name": row["full_name"],
                    "department": row["department"],
                    "career": row["career"],
                    "attendance_rate": row["attendance_rate"],
                    "average_grade": row["average_grade"],
                    "days_without_followup": row["days_without_followup"],
                    "risk_score": score,
                    "risk_level": level,
                    "alert_type": alert_type,
                    "message": message
                }
            )

        preview = pd.DataFrame(results)

        st.dataframe(
            preview.sort_values("risk_score", ascending=False).head(30),
            use_container_width=True,
            hide_index=True
        )

with tab3:
    st.subheader("Histórico de alertas")

    alerts = load_alerts()

    if alerts.empty:
        st.info("No hay alertas registradas.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "Estado",
                ["Todos"] + sorted(alerts["status"].dropna().unique().tolist())
            )

        with col2:
            risk_filter = st.selectbox(
                "Nivel de riesgo",
                ["Todos"] + sorted(alerts["risk_level"].dropna().unique().tolist())
            )

        with col3:
            type_filter = st.selectbox(
                "Tipo de alerta",
                ["Todos"] + sorted(alerts["alert_type"].dropna().unique().tolist())
            )

        filtered = alerts.copy()

        if status_filter != "Todos":
            filtered = filtered[filtered["status"] == status_filter]

        if risk_filter != "Todos":
            filtered = filtered[filtered["risk_level"] == risk_filter]

        if type_filter != "Todos":
            filtered = filtered[filtered["alert_type"] == type_filter]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )