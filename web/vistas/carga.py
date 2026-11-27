"""
Vista 1 - Carga y Validación (RF1).
Permite subir un CSV o elegir un ejemplo de datos/ejemplos/, lo valida con analisis.validador
y guarda el DataFrame en la sesión para las demás pestañas.
"""

import os
import io

import streamlit as st

from analisis.config import RUTA_EJEMPLOS
from analisis.validador import validar_y_cargar_csv


def mostrar():
    """Dibuja el contenido de la pestaña."""
    st.markdown('<div class="section-title">Importación y diagnóstico del dataset</div>', unsafe_allow_html=True)
    st.write(
        "Importa el archivo de origen en formato **.CSV**. El sistema detectará automáticamente "
        "la codificación de caracteres, el delimitador de columnas y validará la integridad estructural."
    )

    # Componente de carga de archivos con dropzone estilizado
    archivo = st.file_uploader(
        "Selecciona o arrastra un archivo CSV dentro del recuadro",
        type=["csv"],
        help="Límite de tamaño: 50 MB. Estructura mínima requerida: 2 columnas."
    )

    # Selector de datasets de ejemplo incluidos en datos/ejemplos (se leen tal cual, sin modificarlos)
    ruta_datasets = RUTA_EJEMPLOS
    datasets_demo = sorted(f for f in os.listdir(ruta_datasets) if f.lower().endswith(".csv")) if os.path.isdir(ruta_datasets) else []
    if archivo is None and datasets_demo:
        c_demo1, c_demo2 = st.columns([3, 1])
        demo_elegido = c_demo1.selectbox(
            "...o utiliza uno de los datasets de ejemplo incluidos en el proyecto:",
            options=datasets_demo,
            index=datasets_demo.index("01_clientes_tienda.csv") if "01_clientes_tienda.csv" in datasets_demo else 0
        )
        c_demo2.write("")
        if c_demo2.button("Cargar ejemplo", type="secondary", width="stretch"):
            with open(os.path.join(ruta_datasets, demo_elegido), "rb") as f_demo:
                contenido_demo = f_demo.read()
            archivo_memoria = io.BytesIO(contenido_demo)
            archivo_memoria.name = demo_elegido
            archivo_memoria.size = len(contenido_demo)
            archivo = archivo_memoria

    if archivo is not None:
        # Invocación al módulo validador del backend
        exito, mensaje, df, meta = validar_y_cargar_csv(archivo)
        if not exito:
            st.error(mensaje)
        else:
            # Control para disparar la notificación flotante (Toast) solo cuando se carga un archivo nuevo
            if st.session_state.get("nombre_dataset") != meta["nombre"]:
                st.toast(f"Dataset '{meta['nombre']}' validado correctamente.", icon="✔️")
                # Al cambiar de dataset se descartan los resultados calculados con el anterior
                for clave in ["ultimo_arbol", "resultado_reglas", "informe_html"]:
                    st.session_state.pop(clave, None)
                
            # Almacenamiento en el estado de la sesión para persistencia entre pestañas
            st.session_state["df_original"] = df
            st.session_state["meta_dataset"] = meta
            st.session_state["nombre_dataset"] = meta["nombre"]

    # Renderizar resultados si ya existe un dataset cargado en sesión
    if "df_original" in st.session_state and "meta_dataset" in st.session_state:
        df_mostrar_raw = st.session_state["df_original"]
        meta = st.session_state["meta_dataset"]

        st.markdown('<div class="section-title">Diagnóstico técnico del archivo</div>', unsafe_allow_html=True)
        # Visualización de metadatos mediante tarjetas de métricas con relieve
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Peso en disco", meta["tamano_kb"], help="Tamaño físico del archivo.")
        col2.metric("Codificación", meta["codificacion"], help="Estándar de caracteres detectado.")
        col3.metric("Delimitador", meta["separador"], help="Carácter separador de campos identificado.")
        col4.metric("Registros (Filas)", meta["filas"], help="Total de observaciones en el dataset.")
        col5.metric("Variables (Columnas)", meta["columnas"], help="Total de atributos por registro.")

        st.markdown('<div class="section-title">Exploración de datos crudos (Raw Data)</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.caption("Vista previa sin alteraciones. Los valores faltantes se visualizan como 'None' y serán tratados en la siguiente etapa.")
            st.dataframe(df_mostrar_raw, width="stretch")
    elif archivo is None:
        st.info("Sube un archivo CSV en el panel superior para habilitar las herramientas de preprocesamiento y modelado.")
