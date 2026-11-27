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

# Ilustración animada "CSV desordenado → tabla limpia + auditoría" (diseño de Erick Mamani)
ILUSTRACION_FLUJO = """<div class="visual-flow-wrapper">
<div>
<div class="sheet-mockup">
<div class="sheet-tab-gray">Archivo Crudo</div>
<div class="mini-grid">
<div class="cell-gray"></div><div class="cell-gray"></div><div class="cell-gray"></div><div class="cell-gray"></div>
<div class="cell-gray"></div><div class="cell-red"></div><div class="cell-gray"></div><div class="cell-amber"></div>
<div class="cell-amber"></div><div class="cell-gray"></div><div class="cell-red"></div><div class="cell-gray"></div>
<div class="cell-gray"></div><div class="cell-gray"></div><div class="cell-amber"></div><div class="cell-red"></div>
</div>
</div>
<div class="flow-caption"><strong>Un CSV desordenado</strong><br>con nulos, duplicados y outliers</div>
</div>
<div class="flow-arrow">→</div>
<div>
<div style="display:flex; gap:8px; align-items:flex-start;">
<div class="sheet-mockup" style="width:155px;">
<div class="sheet-tab-green">Datos Limpios</div>
<div class="mini-grid">
<div class="cell-green-dark"></div><div class="cell-green-dark"></div><div class="cell-green-dark"></div><div class="cell-green-dark"></div>
<div class="cell-green-soft"></div><div class="cell-green-soft"></div><div class="cell-green-soft"></div><div class="cell-green-soft"></div>
<div class="cell-green-soft"></div><div class="cell-green-soft"></div><div class="cell-green-soft"></div><div class="cell-green-soft"></div>
<div class="cell-green-soft"></div><div class="cell-green-soft"></div><div class="cell-green-soft"></div><div class="cell-green-soft"></div>
</div>
</div>
<div class="issues-card">
<strong>⚠️ Auditoría</strong>
• Duplicados<br>
• Nulos (NaN)<br>
• Outliers IQR
</div>
</div>
<div class="flow-caption"><strong>Una tabla estructurada</strong><br>+ auditoría completa de reparaciones</div>
</div>
</div>"""


def mostrar():
    """Dibuja el contenido de la pestaña."""
    # Diseño en dos columnas (Erick): ilustración "antes / después" a la izquierda y carga a la derecha
    col_izq, col_der = st.columns([1.15, 1], gap="large")

    with col_izq:
        with st.container(border=True):
            # El HTML va sin sangría para que Markdown no lo interprete como bloque de código
            st.markdown(ILUSTRACION_FLUJO, unsafe_allow_html=True)

    with col_der:
        with st.container(border=True):
            # El recuadro se estiliza por CSS (texto, ícono y bordes en web/static/estilos.css)
            archivo = st.file_uploader(
                "Subir archivo CSV",
                type=["csv"],
                label_visibility="collapsed",
                help="Límite de tamaño: 50 MB. Estructura mínima requerida: 2 columnas."
            )

            # Selector de datasets de ejemplo incluidos en datos/ejemplos (se leen tal cual, sin modificarlos)
            datasets_demo = sorted(
                f for f in os.listdir(RUTA_EJEMPLOS) if f.lower().endswith(".csv")
            ) if os.path.isdir(RUTA_EJEMPLOS) else []
            if archivo is None and datasets_demo:
                st.markdown('<div class="ejemplos-caption">...o usa uno de los datasets de ejemplo del proyecto</div>',
                            unsafe_allow_html=True)
                demo_elegido = st.selectbox(
                    "Dataset de ejemplo",
                    options=datasets_demo,
                    index=datasets_demo.index("01_clientes_tienda.csv") if "01_clientes_tienda.csv" in datasets_demo else 0,
                    label_visibility="collapsed"
                )
                if st.button("Cargar ejemplo", type="secondary", width="stretch"):
                    with open(os.path.join(RUTA_EJEMPLOS, demo_elegido), "rb") as f_demo:
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

        st.write("")
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
