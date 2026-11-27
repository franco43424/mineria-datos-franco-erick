"""
Componente: estilos.py
Propósito: Elementos visuales comunes a toda la aplicación.
Diseño editorial (paleta verde, tipografías Instrument Serif y Plus Jakarta Sans,
barra superior, hero enmarcado y stepper de pestañas) creado por Erick Mamani.
"""

import os
import base64

import streamlit as st

RUTA_STATIC = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
RUTA_ASSETS = os.path.join(RUTA_STATIC, "assets")

# Paleta de colores del diseño, reutilizada por los gráficos de Plotly en las vistas
PALETA = ["#165B33", "#10B981", "#D97706", "#0EA5E9", "#DC2626", "#7C3AED"]
ESCALA_CONTINUA = "Greens"


def _imagen_base64(nombre_archivo):
    """Lee una imagen de web/static/assets y la devuelve en Base64 (o None si no existe)."""
    ruta = os.path.join(RUTA_ASSETS, nombre_archivo)
    if not os.path.exists(ruta):
        return None
    with open(ruta, "rb") as archivo:
        return base64.b64encode(archivo.read()).decode()


@st.cache_data(show_spinner=False)
def _css_completo(fecha_modificacion_css):
    """
    Arma el CSS (hoja de estilos externa + imágenes en Base64 + reglas de contraste) y lo guarda
    en caché, para no volver a leer y convertir las imágenes en cada clic.
    El parámetro es la fecha de modificación del .css: si alguien edita el archivo, la caché se renueva.
    """
    css_contenido = ""
    ruta_css = os.path.join(RUTA_STATIC, "estilos.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            css_contenido = f.read()

    css_imagenes = ""

    # 1. Ícono animado para el recuadro de subida de archivos
    icono = _imagen_base64("icono_limpieza.png")
    if icono:
        css_imagenes += f"""
        section[data-testid="stFileUploaderDropzone"]::before {{
            background-image: url("data:image/png;base64,{icono}") !important;
            width: 64px !important;
            height: 64px !important;
        }}
        """

    # 2. Imagen de fondo de toda la página, con un velo claro para mantener la legibilidad
    fondo = _imagen_base64("fondo.jpg")
    if fondo:
        css_imagenes += f"""
        .stApp {{
            background-image: linear-gradient(rgba(250, 250, 249, 0.84), rgba(250, 250, 249, 0.88)),
                              url("data:image/jpeg;base64,{fondo}") !important;
            background-size: cover !important;
            background-position: center center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        """

    # Protección de contraste en modo claro editorial
    css_contraste = """
    .stApp [data-testid="stMainBlockContainer"] p,
    .stApp [data-testid="stMainBlockContainer"] span,
    .stApp [data-testid="stMainBlockContainer"] label {
        color: #1C1917;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p,
    button[kind="primary"] p,
    button[kind="primary"] span,
    .nav-pill-btn,
    .sheet-tab-green {
        color: #FFFFFF !important;
    }
    button[kind="secondary"] p,
    button[kind="secondary"] span {
        color: #165B33 !important;
    }
    """
    return f"<style>{css_contenido}\n{css_imagenes}\n{css_contraste}</style>"


def cargar_estilos_css():
    """Inyecta la hoja de estilos y los fondos personalizados en la página."""
    ruta_css = os.path.join(RUTA_STATIC, "estilos.css")
    fecha = os.path.getmtime(ruta_css) if os.path.exists(ruta_css) else 0
    st.markdown(_css_completo(fecha), unsafe_allow_html=True)


def mostrar_encabezado():
    """Dibuja la barra superior y el hero editorial enmarcado."""
    st.markdown(
"""<div class="top-navbar">
<div class="nav-links">
<span>Validación CSV</span>
<span>Limpieza</span>
<span>Árboles de Decisión</span>
<span>Asociación</span>
<span>Dashboard</span>
<span>Informe</span>
</div>
<div class="nav-pill-btn">Franco &amp; Erick</div>
</div>
<div class="editorial-hero">
<div class="editorial-kicker">MINERÍA DE DATOS Y APRENDIZAJE AUTOMÁTICO</div>
<div class="editorial-title">Limpieza y análisis predictivo para CSV</div>
<div class="editorial-desc">
Sube un archivo CSV en bruto. Aplicamos validación estructural, imputación de valores nulos,
detección de anomalías (IQR), Árboles de Decisión y Reglas de Asociación, con dashboard e informe final en un solo flujo interactivo.
</div>
</div>""",
        unsafe_allow_html=True
    )
