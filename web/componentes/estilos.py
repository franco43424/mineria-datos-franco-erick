"""
Componente: estilos.py
Propósito: Elementos visuales comunes a toda la aplicación (hoja de estilos y encabezado).
"""

import os

import streamlit as st


def cargar_estilos_css(nombre_archivo="estilos.css"):
    """
    Lee una hoja de estilos CSS externa ubicada en web/static/
    y la inyecta en el DOM de la aplicación Streamlit junto con reglas de contraste.
    """
    ruta_css = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", nombre_archivo)
    css_contenido = ""
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            css_contenido = f.read()

    # Corrección de contraste para evitar letras blancas invisibles en Modo Oscuro del navegador
    css_contraste = """
    .stApp [data-testid="stMainBlockContainer"] p,
    .stApp [data-testid="stMainBlockContainer"] span,
    .stApp [data-testid="stMainBlockContainer"] label,
    .stApp [data-testid="stMainBlockContainer"] h1,
    .stApp [data-testid="stMainBlockContainer"] h2,
    .stApp [data-testid="stMainBlockContainer"] h3,
    .stApp [data-testid="stMainBlockContainer"] h4,
    .stApp [data-testid="stMainBlockContainer"] h5,
    .stTabs [data-baseweb="tab"] p {
        color: #1E293B !important;
    }
    .hero-banner h1, .hero-banner p, .hero-banner span, .hero-banner div,
    button[kind="primary"] p, button[kind="primary"] span {
        color: #FFFFFF !important;
    }
    """
    st.markdown(f"<style>{css_contenido}\n{css_contraste}</style>", unsafe_allow_html=True)


def mostrar_encabezado():
    """Dibuja el banner principal (hero) en la parte superior de la página."""
    st.markdown("""
        <div class="hero-banner">
            <div class="hero-badge">Suite Analítica • Machine Learning</div>
            <h1>Plataforma de Minería de Datos</h1>
            <p>Carga y limpieza automática de datos, Árboles de Decisión, Reglas de Asociación, Dashboard e Informes.</p>
        </div>
    """, unsafe_allow_html=True)
