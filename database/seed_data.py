import random
from datetime import date, timedelta

import streamlit as st
from faker import Faker
from sqlalchemy import text

from connection import get_engine

fake = Faker("es_ES")

departments = [
    "San Salvador", "La Libertad", "Santa Ana", "San Miguel",
    "Usulután", "Sonsonate", "Ahuachapán", "La Paz",
    "Cuscatlán", "Chalatenango", "Morazán", "La Unión",
    "Cabañas", "San Vicente"
]

careers = [
    "Ingeniería en Sistemas",
    "Administración de Empresas",
    "Contaduría Pública",
    "Enfermería",
    "Psicología",
    "Mercadeo",
    "Diseño Gráfico",
    "Técnico en Software"
]

institutions = [
    "Universidad Nacional",
    "Universidad Tecnológica",
    "Instituto Técnico",
    "Colegio Nacional",
    "Universidad Privada"
]

risk_reasons = [
    ("Económico", "No puede cubrir transporte"),
    ("Económico", "Necesita trabajar"),
    ("Económico", "Gastos familiares imprevistos"),
    ("Económico", "No puede cubrir alimentación o materiales"),
    ("Académico", "Bajo rendimiento"),
    ("Académico", "Dificultad con materias"),
    ("Académico", "Reprobación recurrente"),
    ("Académico", "Falta de hábitos de estudio"),
    ("Asistencia", "Faltas recurrentes"),
    ("Asistencia", "Llegadas tarde"),
    ("Asistencia", "Abandono de clases"),
    ("Laboral", "Comenzó a trabajar"),
    ("Laboral", "Cambio de horario laboral"),
    ("Laboral", "Cansancio por doble jornada"),
    ("Transporte", "Costo de pasaje"),
    ("Transporte", "Rutas complicadas"),
    ("Transporte", "Lejanía del centro educativo"),
    ("Modalidad", "No se adapta a modalidad virtual"),
    ("Modalidad", "No se adapta a modalidad presencial"),
    ("Modalidad", "Problemas de conexión"),
    ("Modalidad", "Falta de equipo tecnológico"),
    ("Familiar", "Responsabilidades en casa"),
    ("Familiar", "Cuido de familiares"),
    ("Familiar", "Falta de apoyo familiar"),
    ("Motivacional", "Falta de interés"),
    ("Motivacional", "Dudas sobre la carrera"),
    ("Motivacional", "Baja participación"),
    ("Horario", "Choque de horarios"),
    ("Horario", "Horarios muy extensos"),
    ("Administrativo", "Documentación pendiente"),
    ("Administrativo", "Problemas con matrícula")
]


def clear_demo_data(conn):
    """
    Limpia las tablas principales y reinicia los IDs.
    Esto evita datos duplicados si ejecutas la carga varias veces.
    """
    conn.execute(
        text("""
            TRUNCATE TABLE
                alerts,
                followups,
                grades,
                attendance_records,
                students,
                risk_reasons,
                modalities
            RESTART IDENTITY CASCADE;
        """)
    )


def seed_catalogs(conn):
    """
    Carga catálogos base: modalidades y motivos de riesgo.
    """

    modalities = ["Presencial", "Virtual", "Semi-presencial"]

    for modality in modalities:
        conn.execute(
            text("""
                INSERT INTO modalities (name)
                VALUES (:name)
                ON CONFLICT (name) DO NOTHING;
            """),
            {"name": modality}
        )

    for category, reason in risk_reasons:
        conn.execute(
            text("""
                INSERT INTO risk_reasons (category, reason_name, active)
                SELECT :category, :reason_name, TRUE
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM risk_reasons
                    WHERE category = :category
                    AND reason_name = :reason_name
                );
            """),
            {
                "category": category,
                "reason_name": reason
            }
        )


def get_modality_ids(conn):
    """
    Obtiene los IDs reales de modalidades desde la base.
    Así evitamos asumir que siempre serán 1, 2 y 3.
    """

    rows = conn.execute(
        text("SELECT id FROM modalities ORDER BY id;")
    ).fetchall()

    modality_ids = [row[0] for row in rows]

    if not modality_ids:
        raise Exception("No existen modalidades cargadas en la tabla modalities.")

    return modality_ids


def seed_students(conn, total=1000):
    """
    Carga estudiantes ficticios.
    """

    modality_ids = get_modality_ids(conn)

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(1, total + 1):
        student_code = f"BEC-{i:04d}"

        conn.execute(
            text("""
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
                    :enrollment_date
                )
                ON CONFLICT (student_code) DO NOTHING;
            """),
            {
                "student_code": student_code,
                "full_name": fake.name(),
                "age": random.randint(15, 30),
                "sex": random.choice(["Masculino", "Femenino"]),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "department": random.choice(departments),
                "municipality": random.choice([
                    "San Salvador", "Santa Tecla", "Soyapango", "Mejicanos",
                    "Apopa", "Santa Ana", "San Miguel", "Sonsonate",
                    "Usulután", "Zacatecoluca", "Cojutepeque", "Chalatenango"
                ]),
                "address_reference": fake.address(),
                "education_level": random.choice([
                    "Bachillerato",
                    "Técnico",
                    "Universitario"
                ]),
                "institution_name": random.choice(institutions),
                "career": random.choice(careers),
                "modality_id": random.choice(modality_ids),
                "scholarship_type": random.choice(["Total", "Parcial"]),
                "support_percentage": random.choice([25, 50, 75, 100]),
                "status": random.choice([
                    "Activo",
                    "Activo",
                    "Activo",
                    "En riesgo"
                ]),
                "assigned_monitor": random.choice([
                    "Monitor A",
                    "Monitor B",
                    "Monitor C"
                ]),
                "enrollment_date": date(2026, 1, 15)
            }
        )

        if i % 50 == 0 or i == total:
            progress_bar.progress(i / total)
            status_text.text(f"Cargando estudiantes: {i} de {total}")

    progress_bar.progress(1.0)
    status_text.text("Estudiantes cargados correctamente.")


def seed_attendance_and_grades(conn):
    """
    Carga asistencias y notas para cada estudiante.
    """

    students = conn.execute(
        text("SELECT id FROM students ORDER BY id;")
    ).fetchall()

    if not students:
        raise Exception("No hay estudiantes cargados. Primero debes cargar estudiantes.")

    modality_ids = get_modality_ids(conn)

    total = len(students)
    progress_bar = st.progress(0)
    status_text = st.empty()

    subjects = [
        "Matemática",
        "Comunicación",
        "Especialidad"
    ]

    for index, student in enumerate(students, start=1):
        student_id = student[0]

        # 12 registros de asistencia por estudiante
        for week in range(1, 13):
            session_date = date(2026, 1, 1) + timedelta(days=week * 7)

            attendance_status = random.choices(
                ["Asistió", "Faltó", "Llegó tarde", "Justificado"],
                weights=[70, 15, 10, 5]
            )[0]

            conn.execute(
                text("""
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
                        TRUE,
                        :attendance_status,
                        :modality_id,
                        :observation
                    );
                """),
                {
                    "student_id": student_id,
                    "session_date": session_date,
                    "attendance_status": attendance_status,
                    "modality_id": random.choice(modality_ids),
                    "observation": ""
                }
            )

        # 3 notas por estudiante
        for subject in subjects:
            grade = round(random.uniform(5.0, 10.0), 2)

            conn.execute(
                text("""
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
                    );
                """),
                {
                    "student_id": student_id,
                    "period": "Ciclo 01-2026",
                    "subject_name": subject,
                    "grade": grade,
                    "academic_status": "Aprobado" if grade >= 7 else "En riesgo",
                    "observation": ""
                }
            )

        if index % 50 == 0 or index == total:
            progress_bar.progress(index / total)
            status_text.text(f"Cargando asistencia y notas: {index} de {total}")

    progress_bar.progress(1.0)
    status_text.text("Asistencias y notas cargadas correctamente.")


def run_seed(total_students=1000, clean_before_load=True):
    """
    Ejecuta la carga completa de datos demo.
    """

    engine = get_engine()

    with engine.begin() as conn:
        if clean_before_load:
            st.info("Limpiando datos anteriores...")
            clear_demo_data(conn)

        st.info("Cargando catálogos...")
        seed_catalogs(conn)

        st.info("Cargando estudiantes...")
        seed_students(conn, total=total_students)

        st.info("Cargando asistencias y notas...")
        seed_attendance_and_grades(conn)


st.title("Cargar datos de prueba")

st.warning(
    "Este proceso puede tardar un poco porque carga estudiantes, asistencias y notas."
)

total_students = st.number_input(
    "Cantidad de estudiantes a cargar",
    min_value=10,
    max_value=1000,
    value=1000,
    step=10
)

clean_before_load = st.checkbox(
    "Limpiar datos anteriores antes de cargar",
    value=True
)

if st.button("Cargar datos de prueba"):
    try:
        with st.spinner("Cargando datos de prueba en Supabase..."):
            run_seed(
                total_students=total_students,
                clean_before_load=clean_before_load
            )

        st.success("Datos de prueba cargados correctamente.")

        st.info(
            f"""
            Carga finalizada:
            - Estudiantes cargados: {total_students}
            - Registros de asistencia estimados: {total_students * 12}
            - Registros de notas estimados: {total_students * 3}
            """
        )

    except Exception as e:
        st.error("Ocurrió un error al cargar los datos.")
        st.exception(e)