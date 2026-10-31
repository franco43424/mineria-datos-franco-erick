import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from analisis.validador import validar_y_cargar_csv
from analisis.limpieza import limpiar_dataset_automatico

st.set_page_config(page_title="Minería de Datos - Franco & Erick", layout="wide")

st.title("Plataforma de Administración de Minería de Datos")
st.caption("Desarrollado por Franco Fajardo y Erick | Flujo tipo Orange Data Mining")

st.divider()

# --- SECCIÓN RF1: CARGA Y VALIDACIÓN DE DATOS ---
st.header("1. Carga y Validación de Datos (RF1)")

archivo = st.file_uploader("Selecciona un archivo CSV para analizar", type=["csv"])

if archivo is not None:
    exito, mensaje, df, meta = validar_y_cargar_csv(archivo)
    
    if not exito:
        st.error(mensaje)
    else:
        st.success(mensaje)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Tamaño", meta["tamano_kb"])
        col2.metric("Codificación", meta["codificacion"])
        col3.metric("Separador", meta["separador"])
        col4.metric("Filas Originales", meta["filas"])
        col5.metric("Columnas", meta["columnas"])
        
        with st.expander("Ver vista previa del Dataset original (Sin limpiar)", expanded=False):
            st.dataframe(df, use_container_width=True)
        
        st.session_state["df_original"] = df
        st.session_state["nombre_dataset"] = meta["nombre"]

        st.divider()

        # --- SECCIÓN RF2: LIMPIEZA AUTOMÁTICA ---
        st.header("2. Limpieza Automática de Datos (RF2)")
        
        # Opciones configurables pero con valores automáticos por defecto
        c_opt1, c_opt2 = st.columns(2)
        metodo_nulos = c_opt1.selectbox(
            "Tratamiento de valores nulos:",
            options=["imputar", "eliminar"],
            format_func=lambda x: "Imputar automáticamente (Mediana / Moda)" if x == "imputar" else "Eliminar filas con nulos"
        )
        metodo_outliers = c_opt2.selectbox(
            "Tratamiento de valores atípicos (Outliers - IQR):",
            options=["mediana", "acotar", "eliminar"],
            format_func=lambda x: {
                "mediana": "Reemplazar por la Mediana normal",
                "acotar": "Acotar a límites estadísticos (IQR)",
                "eliminar": "Eliminar filas con outliers"
            }[x]
        )

        # Se ejecuta automáticamente al cargar el archivo
        df_limpio, resumen = limpiar_dataset_automatico(df, metodo_nulos, metodo_outliers)
        st.session_state["df_limpio"] = df_limpio
        st.session_state["resumen_limpieza"] = resumen

        # Métricas del resumen de limpieza
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Filas Finales Limpias", resumen["filas_finales"], delta=resumen["filas_finales"] - resumen["filas_iniciales"])
        m2.metric("Duplicados Eliminados", resumen["duplicados_eliminados"])
        m3.metric("Columnas con Nulos Tratados", len(resumen["nulos_tratados"]))
        m4.metric("Columnas con Outliers Tratados", len(resumen["outliers_tratados"]))

        # Detalle de qué se modificó exactamente (exigido en RF2)
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.subheader("Detalle de transformaciones aplicadas")
            st.write("**Columnas normalizadas:**", resumen["columnas_renombradas"] if resumen["columnas_renombradas"] else "Ya estaban normalizadas")
            st.write("**Nulos tratados por columna:**", resumen["nulos_tratados"] if resumen["nulos_tratados"] else "Sin valores nulos")
            st.write("**Outliers detectados (IQR):**", resumen["outliers_tratados"] if resumen["outliers_tratados"] else "Sin valores atípicos")
            if resumen["tipos_corregidos"]:
                st.write("**Tipos de datos corregidos:**", resumen["tipos_corregidos"])

        with col_res2:
            st.subheader("Vista previa del Dataset Limpio")
            st.dataframe(df_limpio, use_container_width=True)