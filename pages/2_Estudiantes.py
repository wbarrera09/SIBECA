import streamlit as st
import pandas as pd
from sqlalchemy import text

from database.connection import get_engine
from utils.ui import apply_goes_theme, page_header

st.set_page_config(
    page_title="Estudiantes | SIBECA",
    page_icon="",
    layout="wide"
)

apply_goes_theme()

page_header(
    "Gestión de Estudiantes",
    "Registro, consulta y administración de estudiantes becados."
)

engine = get_engine()


@st.cache_data(ttl=1800)
def load_modalities():
    return pd.read_sql(
        "SELECT id, name FROM modalities ORDER BY id",
        engine
    )


@st.cache_data(ttl=1800)
def load_students():
    return pd.read_sql(
        """
        SELECT 
            s.id,
            s.student_code,
            s.full_name,
            s.age,
            s.sex,
            s.email,
            s.phone,
            s.department,
            s.municipality,
            s.address_reference,
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
        ORDER BY s.id DESC
        """,
        engine
    )


modalities = load_modalities()

if modalities.empty:
    st.warning("No hay modalidades cargadas.")
    st.stop()

tab1, tab2, tab3 = st.tabs(
    [
        "Listado",
        "Nuevo estudiante",
        "Ficha rápida"
    ]
)

with tab1:
    st.subheader("Listado de estudiantes")

    df = load_students()

    if df.empty:
        st.info("No hay estudiantes registrados.")
    else:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            search = st.text_input(
                "Buscar",
                placeholder="Nombre, código o carrera"
            )

        with col2:
            department_filter = st.selectbox(
                "Departamento",
                ["Todos"] + sorted(df["department"].dropna().unique().tolist())
            )

        with col3:
            modality_filter = st.selectbox(
                "Modalidad",
                ["Todas"] + sorted(df["modality"].dropna().unique().tolist())
            )

        with col4:
            status_filter = st.selectbox(
                "Estado",
                ["Todos"] + sorted(df["status"].dropna().unique().tolist())
            )

        filtered = df.copy()

        if search:
            filtered = filtered[
                filtered["full_name"].str.contains(search, case=False, na=False)
                | filtered["student_code"].str.contains(search, case=False, na=False)
                | filtered["career"].str.contains(search, case=False, na=False)
            ]

        if department_filter != "Todos":
            filtered = filtered[filtered["department"] == department_filter]

        if modality_filter != "Todas":
            filtered = filtered[filtered["modality"] == modality_filter]

        if status_filter != "Todos":
            filtered = filtered[filtered["status"] == status_filter]

        st.caption(f"Registros encontrados: {len(filtered):,}")

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

with tab2:
    st.subheader("Registrar nuevo estudiante")

    modality_options = dict(zip(modalities["name"], modalities["id"]))

    with st.form("student_form"):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Nombre completo")
            age = st.number_input(
                "Edad",
                min_value=10,
                max_value=80,
                value=18
            )
            sex = st.selectbox(
                "Sexo",
                [
                    "Masculino",
                    "Femenino",
                    "Otro",
                    "Prefiere no decir"
                ]
            )
            email = st.text_input("Correo")
            phone = st.text_input("Teléfono")
            department = st.text_input("Departamento")
            municipality = st.text_input("Municipio")
            address_reference = st.text_area("Dirección o referencia")

        with col2:
            education_level = st.selectbox(
                "Nivel de escolaridad",
                [
                    "Bachillerato",
                    "Técnico",
                    "Universitario"
                ]
            )
            institution_name = st.text_input(
                "Universidad / Colegio / Institución"
            )
            career = st.text_input("Carrera")
            modality_name = st.selectbox(
                "Modalidad",
                list(modality_options.keys())
            )
            scholarship_type = st.selectbox(
                "Tipo de beca",
                [
                    "Total",
                    "Parcial"
                ]
            )
            support_percentage = st.number_input(
                "Porcentaje de apoyo económico",
                min_value=0,
                max_value=100,
                value=100
            )
            status = st.selectbox(
                "Estado",
                [
                    "Activo",
                    "En riesgo",
                    "Suspendido",
                    "Retirado",
                    "Graduado"
                ]
            )
            assigned_monitor = st.text_input("Monitor asignado")

        submitted = st.form_submit_button("Guardar estudiante")

        if submitted:
            if not full_name:
                st.error("El nombre completo es obligatorio.")
            else:
                with engine.begin() as conn:
                    next_id = conn.execute(
                        text("SELECT COALESCE(MAX(id), 0) + 1 FROM students")
                    ).scalar()

                    student_code = f"BEC-{next_id:04d}"

                    conn.execute(
                        text(
                            """
                            INSERT INTO students (
                                student_code,
                                full_name,
                                age,
                                sex,
                                email,
                                phone,
                                department,
                                municipality,
                                address_reference,
                                education_level,
                                institution_name,
                                career,
                                modality_id,
                                scholarship_type,
                                support_percentage,
                                status,
                                assigned_monitor,
                                enrollment_date
                            )
                            VALUES (
                                :student_code,
                                :full_name,
                                :age,
                                :sex,
                                :email,
                                :phone,
                                :department,
                                :municipality,
                                :address_reference,
                                :education_level,
                                :institution_name,
                                :career,
                                :modality_id,
                                :scholarship_type,
                                :support_percentage,
                                :status,
                                :assigned_monitor,
                                CURRENT_DATE
                            )
                            """
                        ),
                        {
                            "student_code": student_code,
                            "full_name": full_name,
                            "age": age,
                            "sex": sex,
                            "email": email,
                            "phone": phone,
                            "department": department,
                            "municipality": municipality,
                            "address_reference": address_reference,
                            "education_level": education_level,
                            "institution_name": institution_name,
                            "career": career,
                            "modality_id": modality_options[modality_name],
                            "scholarship_type": scholarship_type,
                            "support_percentage": support_percentage,
                            "status": status,
                            "assigned_monitor": assigned_monitor
                        }
                    )

                st.cache_data.clear()
                st.success(
                    f"Estudiante guardado correctamente con código {student_code}"
                )

with tab3:
    st.subheader("Ficha rápida del estudiante")

    df = load_students()

    if df.empty:
        st.info("No hay estudiantes registrados.")
    else:
        selected = st.selectbox(
            "Seleccionar estudiante",
            df["student_code"] + " - " + df["full_name"]
        )

        code = selected.split(" - ")[0]
        student = df[df["student_code"] == code].iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric("Código", student["student_code"])
        col2.metric("Estado", student["status"])
        col3.metric("Apoyo económico", f"{student['support_percentage']}%")

        st.markdown("### Datos generales")

        st.write(
            {
                "Nombre": student["full_name"],
                "Edad": int(student["age"]) if pd.notna(student["age"]) else "",
                "Sexo": student["sex"],
                "Correo": student["email"],
                "Teléfono": student["phone"],
                "Departamento": student["department"],
                "Municipio": student["municipality"],
                "Carrera": student["career"],
                "Institución": student["institution_name"],
                "Modalidad": student["modality"],
                "Tipo de beca": student["scholarship_type"],
                "Monitor asignado": student["assigned_monitor"],
            }
        )