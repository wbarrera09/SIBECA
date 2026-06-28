import streamlit as st
from sqlalchemy import text
from connection import get_engine

def create_tables():
    engine = get_engine()

    sql = """
    CREATE TABLE IF NOT EXISTS modalities (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        student_code VARCHAR(20) UNIQUE NOT NULL,
        full_name VARCHAR(150) NOT NULL,
        age INT,
        sex VARCHAR(30),
        email VARCHAR(120),
        phone VARCHAR(30),
        department VARCHAR(80),
        municipality VARCHAR(80),
        address_reference TEXT,
        education_level VARCHAR(80),
        institution_name VARCHAR(150),
        career VARCHAR(150),
        modality_id INT REFERENCES modalities(id),
        scholarship_type VARCHAR(50),
        support_percentage NUMERIC(5,2),
        status VARCHAR(50),
        assigned_monitor VARCHAR(120),
        enrollment_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS risk_reasons (
        id SERIAL PRIMARY KEY,
        category VARCHAR(80),
        reason_name VARCHAR(150),
        active BOOLEAN DEFAULT TRUE
    );

    CREATE TABLE IF NOT EXISTS attendance_records (
        id SERIAL PRIMARY KEY,
        student_id INT REFERENCES students(id),
        session_date DATE NOT NULL,
        expected_attendance BOOLEAN DEFAULT TRUE,
        attendance_status VARCHAR(50),
        modality_id INT REFERENCES modalities(id),
        observation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS grades (
        id SERIAL PRIMARY KEY,
        student_id INT REFERENCES students(id),
        period VARCHAR(50),
        subject_name VARCHAR(120),
        grade NUMERIC(5,2),
        academic_status VARCHAR(50),
        observation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS followups (
        id SERIAL PRIMARY KEY,
        student_id INT REFERENCES students(id),
        followup_date DATE NOT NULL,
        followup_type VARCHAR(80),
        result VARCHAR(80),
        risk_reason_id INT REFERENCES risk_reasons(id),
        comment TEXT,
        next_action TEXT,
        next_action_date DATE,
        responsible_user VARCHAR(120),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS alerts (
        id SERIAL PRIMARY KEY,
        student_id INT REFERENCES students(id),
        alert_type VARCHAR(100),
        risk_level VARCHAR(50),
        risk_score NUMERIC(5,2),
        alert_message TEXT,
        status VARCHAR(50) DEFAULT 'Abierta',
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP
    );
    """

    with engine.begin() as conn:
        conn.execute(text(sql))


st.title("Crear estructura de base de datos")

if st.button("Crear tablas"):
    create_tables()
    st.success("Tablas creadas correctamente.")