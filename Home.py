import base64
from pathlib import Path
from textwrap import dedent

import streamlit as st

from utils.ui import apply_goes_theme, page_header, GOES_BLUE, GOES_GOLD, GOES_DARK
from utils.sidebar import apply_sidebar_theme


st.set_page_config(
    page_title="SIBECA | Home",
    page_icon="",
    layout="wide"
)


def image_to_data_uri(image_path):
    path = Path(image_path)

    if not path.exists():
        return ""

    suffix = path.suffix.lower()

    if suffix == ".png":
        mime_type = "image/png"
    elif suffix in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"
    else:
        mime_type = "image/jpeg"

    with open(path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    return f"data:{mime_type};base64,{encoded_image}"


def get_initials(full_name):
    parts = full_name.strip().split()

    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()

    if len(parts) == 1:
        return parts[0][0].upper()

    return "DEV"


def render_developer_card(name, role, image_path, variant_class=""):
    image_uri = image_to_data_uri(image_path)
    initials = get_initials(name)

    if image_uri:
        photo_html = (
            f'<div class="developer-photo-frame">'
            f'<img class="developer-photo" src="{image_uri}" alt="{name}">'
            f'</div>'
        )
    else:
        photo_html = f'<div class="developer-photo-placeholder">{initials}</div>'

    st.markdown(
        f"""
<div class="developer-card {variant_class}">
    {photo_html}
    <div>
        <div class="developer-name">{name}</div>
        <div class="developer-label">{role}</div>
    </div>
</div>
        """,
        unsafe_allow_html=True
    )


apply_goes_theme()
apply_sidebar_theme()

st.markdown(
    dedent(
        f"""
        <style>
            .block-container {{
                padding-top: 1.5rem;
                padding-left: 2rem;
                padding-right: 2rem;
                max-width: 1200px;
            }}

            body, .stApp, div, p, label, input, textarea, button {{
                font-family: "Segoe UI", Arial, sans-serif !important;
            }}

            .goes-header {{
                background: {GOES_BLUE} !important;
                border-left: 8px solid {GOES_GOLD} !important;
                box-shadow: 0 8px 22px rgba(17, 30, 96, 0.12) !important;
            }}

            .home-title {{
                color: {GOES_BLUE};
                font-size: 1.18rem;
                font-weight: 900;
                margin-bottom: 10px;
            }}

            .home-text {{
                color: {GOES_DARK};
                font-size: 0.94rem;
                line-height: 1.6;
                margin-bottom: 18px;
            }}

            .home-card {{
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-left: 7px solid {GOES_GOLD};
                border-radius: 14px;
                padding: 20px 22px;
                box-shadow: 0 5px 16px rgba(17, 30, 96, 0.06);
                margin-bottom: 18px;
            }}

            .home-card-title {{
                color: {GOES_BLUE};
                font-size: 1.02rem;
                font-weight: 900;
                margin-bottom: 12px;
            }}

            .module-list {{
                color: #475569;
                font-size: 0.88rem;
                line-height: 1.65;
            }}

            .module-list ul {{
                margin: 0;
                padding-left: 20px;
            }}

            .module-list li {{
                margin-bottom: 7px;
            }}

            .module-list strong {{
                color: {GOES_BLUE};
            }}

            .developer-card {{
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-top: 4px solid {GOES_BLUE};
                border-radius: 14px;
                padding: 18px;
                box-shadow: 0 4px 12px rgba(17, 30, 96, 0.05);
                min-height: 130px;
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 10px;
            }}

            .developer-card-gold {{
                border-top: 4px solid {GOES_GOLD};
            }}

            .developer-photo-frame {{
                width: 82px;
                height: 82px;
                border-radius: 50%;
                overflow: hidden;
                border: 3px solid #f1f5f9;
                flex-shrink: 0;
                background: #f8fafc;
            }}

            .developer-photo {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                object-position: center center;
                transform: scale(1.18) translateY(3px);
                display: block;
            }}

            .developer-photo-placeholder {{
                width: 82px;
                height: 82px;
                border-radius: 50%;
                background: #f1f5f9;
                color: {GOES_BLUE};
                border: 3px solid #e5e7eb;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.1rem;
                font-weight: 900;
                flex-shrink: 0;
            }}

            .developer-label {{
                color: #64748b;
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.3px;
                margin-bottom: 7px;
            }}

            .developer-name {{
                color: {GOES_BLUE};
                font-size: 1rem;
                font-weight: 900;
                line-height: 1.35;
            }}

            .footer-note {{
                color: #64748b;
                font-size: 0.84rem;
                line-height: 1.45;
                border-top: 1px solid #e5e7eb;
                margin-top: 22px;
                padding-top: 14px;
            }}
        </style>
        """
    ),
    unsafe_allow_html=True
)

page_header(
    "SIBECA",
    "Sistema Integral de Becados"
)

st.markdown(
    """
<div class="home-title">¿Qué es SIBECA?</div>
<div class="home-text">
SIBECA es un sistema diseñado para centralizar la información de estudiantes becados
y facilitar el seguimiento de su desempeño académico, asistencia, historial de contactos
y posibles señales de riesgo. Su objetivo es apoyar la gestión operativa y la toma de
decisiones mediante información ordenada, consultable y actualizada.
</div>
    """,
    unsafe_allow_html=True
)

modules_html = (
    '<div class="home-card">'
    '<div class="home-card-title">Módulos del sistema</div>'
    '<div class="module-list">'
    '<ul>'
    '<li><strong>Dashboard:</strong> presenta indicadores generales, resumen de riesgo, asistencia, notas y estudiantes prioritarios.</li>'
    '<li><strong>Estudiantes:</strong> permite registrar, consultar y administrar la información principal de los estudiantes becados.</li>'
    '<li><strong>Asistencia:</strong> permite registrar sesiones esperadas, asistencias, faltas, llegadas tarde y justificaciones.</li>'
    '<li><strong>Notas:</strong> permite registrar y analizar el rendimiento académico por periodo, materia o módulo.</li>'
    '<li><strong>Seguimientos:</strong> permite documentar contactos, motivos de riesgo, responsables y próximas acciones.</li>'
    '<li><strong>Alertas:</strong> permite generar y revisar alertas tempranas por bajo rendimiento, baja asistencia o falta de seguimiento.</li>'
    '</ul>'
    '</div>'
    '</div>'
)

st.markdown(
    modules_html,
    unsafe_allow_html=True
)

st.markdown(
    """
<div class="home-title">Desarrolladores</div>
    """,
    unsafe_allow_html=True
)

dev_col1, dev_col2 = st.columns(2)

with dev_col1:
    render_developer_card(
        name="William Enrique Barrera Cordero",
        role="Full Stack Developer & Project Manager",
        image_path="assets/developers/william_barrera.jpg"
    )

with dev_col2:
    render_developer_card(
        name="William Fernando Mendez Granados",
        role="Backend Developer & Data Analyst",
        image_path="assets/developers/william_mendez.jpg",
        variant_class="developer-card-gold"
    )

st.markdown(
    """
<div class="footer-note">
Usa el menú lateral para navegar entre los módulos disponibles del sistema.
</div>
    """,
    unsafe_allow_html=True
)