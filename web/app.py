"""
Módulo: app.py
Propósito: Punto de entrada de la aplicación web (capa de presentación, Streamlit).

Este archivo solo arma la página: configura Streamlit, aplica los estilos, crea las pestañas
y delega el contenido de cada una a su vista en web/vistas/. Todo el procesamiento y análisis
de datos ocurre en la capa /analisis.

Ejecutar desde la raíz del proyecto:
    streamlit run web/app.py
"""

import os
import sys

# Permitir que Python encuentre el paquete 'analisis' (está en la raíz del proyecto, un nivel arriba de /web)
RUTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if RUTA_RAIZ not in sys.path:
    sys.path.append(RUTA_RAIZ)

import streamlit as st

from componentes.estilos import cargar_estilos_css, mostrar_encabezado
from componentes.barra_lateral import mostrar_barra_lateral
from vistas import carga, limpieza, arbol, historial, asociacion, dashboard, informe

# Configuración principal de la página (diseño ancho y barra lateral expandida)
st.set_page_config(
    page_title="Plataforma de Minería de Datos",
    layout="wide",
    initial_sidebar_state="expanded"
)

cargar_estilos_css()

# Se reserva el espacio de la barra lateral ahora, pero se dibuja al final,
# cuando las pestañas ya actualizaron el estado de la sesión
contenedor_sidebar = st.sidebar.empty()

mostrar_encabezado()

# Pestañas en el orden del flujo de trabajo de Orange: Datos → Preprocesamiento → Modelos → Visualización → Informe
PESTANAS = [
    ("1. Carga y Validación (RF1)", carga),
    ("2. Preprocesamiento y Limpieza (RF2)", limpieza),
    ("3. Árbol de Decisión (RF3)", arbol),
    ("4. Historial y Comparativa (RF3)", historial),
    ("5. Reglas de Asociación (RF4)", asociacion),
    ("6. Dashboard (RF6)", dashboard),
    ("7. Informe (RF5)", informe),
]

for pestana, (_, vista) in zip(st.tabs([nombre for nombre, _ in PESTANAS]), PESTANAS):
    with pestana:
        vista.mostrar()

mostrar_barra_lateral(contenedor_sidebar)
