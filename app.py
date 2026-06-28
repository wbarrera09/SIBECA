import streamlit as st
from utils.ui import apply_goes_theme, page_header, card

st.set_page_config(
    page_title="SIBECA",
    page_icon="",
    layout="wide"
)

apply_goes_theme()

page_header(
    "SIBECA",
    "Sistema Integral de Becados para monitoreo, seguimiento y alertas tempranas"
)

col1, col2, col3 = st.columns(3)

with col1:
    card(
        "Gestión de becados",
        "Registro centralizado de estudiantes, modalidad, institución, carrera, porcentaje de apoyo y estado actual."
    )

with col2:
    card(
        "Monitoreo académico",
        "Control de asistencia, notas, historial de seguimientos y motivos de riesgo."
    )

with col3:
    card(
        "Inteligencia operativa",
        "Dashboard ejecutivo, alertas tempranas, reportes filtrables y exportación a Excel/PDF."
    )

st.markdown("### Módulos disponibles")

st.markdown(
    """
    - **Dashboard:** KPIs generales, riesgo, asistencia, notas y estudiantes prioritarios.
    - **Estudiantes:** consulta y registro de estudiantes becados.
    - **Asistencia:** control de sesiones esperadas y asistencias reales.
    - **Notas:** registro y análisis del rendimiento académico.
    - **Seguimientos:** historial de contactos, motivos y próximas acciones.
    - **Alertas:** generación de alertas tempranas por riesgo.
    - **Reportes:** filtros, tablas y exportación de información.
    """
)

st.info("Usa el menú lateral para navegar entre los módulos de SIBECA.")