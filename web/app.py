import sys
import os

# Agrega la carpeta raíz del proyecto al camino de búsqueda de Python
# para que desde 'web/' podamos importar archivos de 'analisis/'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from analisis.limpieza import probar_conexion

st.set_page_config(page_title="Minería de Datos - Franco & Erick", layout="wide")

st.title("Software de Administración de Minería de Datos")
st.caption("Desarrollado por Franco Fajardo y Erick | Flujo tipo Orange Data Mining")

# Llamamos a la capa de análisis
mensaje = probar_conexion()
st.success(mensaje)