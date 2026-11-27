"""
Módulo: app.py
Propósito: Interfaz Gráfica de Usuario (Frontend) creada con Streamlit.
Actúa como la capa de presentación del proyecto, permitiendo a los usuarios interactuar 
con los procesos de minería de datos (ingesta, limpieza, modelado y evaluación) 
de forma visual, interactiva y sin necesidad de escribir código.
"""

import sys
import os
import io
import base64
import importlib

# Asegurar que el intérprete de Python encuentre el paquete 'analisis' ubicando la raíz del proyecto
RUTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if RUTA_RAIZ not in sys.path:
    sys.path.append(RUTA_RAIZ)

import streamlit as st
import pandas as pd
import plotly.express as px

# Importación y recarga forzada de los módulos de lógica de negocio (Backend)
# Evita que Streamlit retenga versiones antiguas en caché de memoria
import analisis.validador
import analisis.limpieza
import analisis.arbol_decision
importlib.reload(analisis.validador)
importlib.reload(analisis.limpieza)
importlib.reload(analisis.arbol_decision)

from analisis.validador import validar_y_cargar_csv
from analisis.limpieza import limpiar_dataset_automatico
from analisis.arbol_decision import (
    entrenar_arbol_decision,
    guardar_modelo,
    listar_modelos_guardados,
    eliminar_modelo_guardado
)

# Configuración principal de la página web
st.set_page_config(
    page_title="Plataforma de Minería de Datos",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def cargar_estilos_css(nombre_archivo="estilos.css"):
    """
    Lee una hoja de estilos CSS externa ubicada en el mismo directorio que app.py,
    convierte las imágenes locales a Base64 e inyecta los estilos y fondos personalizados.
    """
    ruta_css = os.path.join(os.path.dirname(__file__), nombre_archivo)
    css_contenido = ""
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            css_contenido = f.read()

    css_imagenes = ""

    # 1. Ícono animado de limpieza para el recuadro de subida de archivos (web/assets/17364836.png)
    ruta_icono = os.path.join(os.path.dirname(__file__), "assets", "17364836.png")
    if os.path.exists(ruta_icono):
        with open(ruta_icono, "rb") as img_file:
            icono_base64 = base64.b64encode(img_file.read()).decode()

        css_imagenes += f"""
        section[data-testid="stFileUploaderDropzone"]::before {{
            background-image: url("data:image/png;base64,{icono_base64}") !important;
            width: 64px !important;
            height: 64px !important;
        }}
        """

    # 2. Imagen de fondo para toda la página (web/assets/images.png) con velo suave para legibilidad
    ruta_fondo = os.path.join(os.path.dirname(__file__), "assets", "images.png")
    if os.path.exists(ruta_fondo):
        with open(ruta_fondo, "rb") as bg_file:
            fondo_base64 = base64.b64encode(bg_file.read()).decode()

        css_imagenes += f"""
        .stApp {{
            background-image: linear-gradient(rgba(250, 250, 249, 0.84), rgba(250, 250, 249, 0.88)),
                              url("data:image/png;base64,{fondo_base64}") !important;
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
    st.markdown(f"<style>{css_contenido}\n{css_imagenes}\n{css_contraste}</style>", unsafe_allow_html=True)

# Aplicar los estilos visuales desde el archivo externo
cargar_estilos_css()

# Reservamos el contenedor de la barra lateral para actualizarlo al final del script
contenedor_sidebar = st.sidebar.empty()

# ==========================================
# BARRA DE NAVEGACIÓN SUPERIOR Y ENCABEZADO
# ==========================================
st.markdown(
"""<div class="top-navbar">
<div class="nav-links">
<span>Validación CSV</span>
<span>Limpieza Estadística</span>
<span>Árboles de Decisión</span>
<span>Comparativa</span>
</div>
<div class="nav-pill-btn">Franco &amp; Erick</div>
</div>
<div class="editorial-hero">
<div class="editorial-kicker">MINERÍA DE DATOS Y APRENDIZAJE AUTOMÁTICO</div>
<div class="editorial-title">Limpieza y análisis predictivo para CSV</div>
<div class="editorial-desc">
Sube un archivo CSV en bruto. Aplicamos validación estructural, imputación de valores nulos, 
detección de anomalías (IQR) y entrenamiento de Árboles de Decisión en un solo flujo interactivo.
</div>
</div>""",
    unsafe_allow_html=True
)

# Definición de pestañas interactivas tipo Stepper
tab1, tab2, tab3, tab4 = st.tabs([
    "① Carga y Validación (RF1)",
    "② Limpieza Automática (RF2)",
    "③ Árbol de Decisión (RF3)",
    "④ Historial y Comparativa"
])

# ==========================================
# PESTAÑA 1: CARGA Y VALIDACIÓN (Ingesta de Datos)
# ==========================================
with tab1:
    col_izq, col_der = st.columns([1.15, 1], gap="large")

    with col_izq:
        with st.container(border=True):
            # Se coloca sin sangría interna para evitar que Markdown lo interprete como bloque de código
            st.markdown(
"""<div class="visual-flow-wrapper">
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
</div>""",
                unsafe_allow_html=True
            )

    with col_der:
        with st.container(border=True):
            # Componente de carga de archivos estilizado vía CSS para replicar el dropzone editorial
            archivo = st.file_uploader(
                "Subir archivo CSV",
                type=["csv"],
                label_visibility="collapsed"
            )

            # Botón auxiliar para cargar directamente el dataset de prueba si no se ha subido archivo
            if archivo is None and "df_original" not in st.session_state:
                st.write("")
                if st.button("Cargar dataset de prueba (datos_sucios_prueba.csv)", type="secondary", width="stretch"):
                    ruta_prueba = os.path.join(RUTA_RAIZ, "storage", "datasets", "datos_sucios_prueba.csv")
                    os.makedirs(os.path.dirname(ruta_prueba), exist_ok=True)
                    contenido_demo = (
                        "ID Cliente;Edad Cliente;Ingreso Mensual;Compras Mes;Metodo Pago;Abandono Cliente\n"
                        "1;25;450000;3;Tarjeta;No\n"
                        "2;34;620000;5;Transferencia;No\n"
                        "2;34;620000;5;Transferencia;No\n"
                        "3;150;510000;2;Efectivo;Si\n"
                        "4;;480000;1;Tarjeta;Si\n"
                        "5;29;590000;4;;No\n"
                        "6;42;8500000;6;Transferencia;No\n"
                        "7;31;530000;2;Efectivo;Si\n"
                        "8;27;490000;3;Tarjeta;No\n"
                        "9;38;610000;4;Transferencia;No\n"
                        "10;22;410000;1;Efectivo;Si\n"
                        "11;45;720000;5;Tarjeta;No\n"
                        "12;33;550000;2;Efectivo;Si\n"
                    )
                    with open(ruta_prueba, "w", encoding="utf-8") as f_demo:
                        f_demo.write(contenido_demo)
                    archivo_memoria = io.BytesIO(contenido_demo.encode("utf-8"))
                    archivo_memoria.name = "datos_sucios_prueba.csv"
                    archivo_memoria.size = len(contenido_demo.encode("utf-8"))
                    archivo = archivo_memoria

    if archivo is not None:
        # Invocación al módulo validador del backend
        exito, mensaje, df, meta = validar_y_cargar_csv(archivo)
        if not exito:
            st.error(mensaje)
        else:
            if st.session_state.get("nombre_dataset") != meta["nombre"]:
                st.toast(f"Dataset '{meta['nombre']}' validado correctamente.", icon="✔️")
                
            st.session_state["df_original"] = df
            st.session_state["meta_dataset"] = meta
            st.session_state["nombre_dataset"] = meta["nombre"]

    # Renderizar resultados si ya existe un dataset cargado en sesión
    if "df_original" in st.session_state and "meta_dataset" in st.session_state:
        df_mostrar_raw = st.session_state["df_original"]
        meta = st.session_state["meta_dataset"]

        st.write("")
        st.markdown('<div class="section-title">Diagnóstico técnico del archivo</div>', unsafe_allow_html=True)
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

# ==========================================
# PESTAÑA 2: LIMPIEZA AUTOMÁTICA (Preparación de Datos)
# ==========================================
with tab2:
    st.markdown('<div class="section-title">Preprocesamiento y reparación automatizada</div>', unsafe_allow_html=True)

    if "df_original" not in st.session_state:
        st.warning("Debes importar un archivo CSV válido en la pestaña **① Carga y Validación** antes de continuar.")
    else:
        df = st.session_state["df_original"]
        st.write(
            "Configura las reglas de limpieza para estandarizar cabeceras, descartar registros duplicados, "
            "imputar valores faltantes y mitigar el impacto estadístico de valores extremos (outliers)."
        )

        with st.container(border=True):
            st.markdown("##### Parámetros del pipeline de limpieza")
            st.caption("Ajusta el comportamiento de los algoritmos de reparación (los cambios se aplican en tiempo real):")
            
            c_opt1, c_opt2 = st.columns(2)
            metodo_nulos = c_opt1.selectbox(
                "Tratamiento de valores faltantes (Nulos / NaN)",
                options=["imputar", "eliminar"],
                format_func=lambda x: "Imputación estadística (Mediana / Moda) [Recomendado]" if x == "imputar" else "Eliminación de registros incompletos (Listwise deletion)",
                help="La imputación preserva el tamaño de la muestra rellenando variables numéricas con la Mediana y categóricas con la Moda."
            )
            metodo_outliers = c_opt2.selectbox(
                "Tratamiento de valores atípicos (Outliers vía IQR)",
                options=["mediana", "acotar", "eliminar"],
                format_func=lambda x: {
                    "mediana": "Sustitución por la Mediana de los datos normales",
                    "acotar": "Winsorizing (Acotar a los límites superior/inferior del IQR)",
                    "eliminar": "Descartar la fila completa si presenta valores extremos"
                }[x],
                help="Detecta anomalías mediante el Rango Intercuartílico (Q1 - 1.5*IQR y Q3 + 1.5*IQR) y aplica la corrección seleccionada."
            )

        # Ejecución del pipeline de limpieza en el backend
        df_limpio, resumen = limpiar_dataset_automatico(df, metodo_nulos, metodo_outliers)
        
        st.session_state["df_limpio"] = df_limpio
        st.session_state["resumen_limpieza"] = resumen

        st.markdown('<div class="section-title">Impacto del preprocesamiento</div>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Registros resultantes",
            resumen["filas_finales"],
            delta=f"{resumen['filas_finales'] - resumen['filas_iniciales']} filas respecto al original",
            help="Total de observaciones válidas disponibles para el entrenamiento."
        )
        m2.metric("Duplicados descartados", resumen["duplicados_eliminados"], help="Filas idénticas eliminadas para evitar sesgos.")
        m3.metric("Atributos imputados", len(resumen["nulos_tratados"]), help="Columnas que requerían tratamiento de celdas vacías.")
        m4.metric("Atributos con outliers", len(resumen["outliers_tratados"]), help="Columnas numéricas intervenidas por valores fuera de rango.")

        col_res1, col_res2 = st.columns([1, 1])
        with col_res1:
            with st.container(border=True):
                st.markdown("##### Registro de auditoría de limpieza")
                
                st.markdown("**1. Normalización de cabeceras (snake_case):**")
                if resumen["columnas_renombradas"]:
                    st.caption("Mapeo de nombres originales a formato estandarizado:")
                    st.json(resumen["columnas_renombradas"])
                else:
                    st.caption("Las cabeceras ya cumplían con el estándar de nomenclatura.")

                st.markdown("**2. Intervención de valores nulos:**")
                if resumen["nulos_tratados"]:
                    for col_n, detalle_n in resumen["nulos_tratados"].items():
                        st.markdown(f"- `{col_n}`: {detalle_n}")
                else:
                    st.caption("No se detectaron valores nulos en el dataset.")

                st.markdown("**3. Mitigación de valores atípicos (IQR):**")
                if resumen["outliers_tratados"]:
                    for col_o, detalle_o in resumen["outliers_tratados"].items():
                        st.markdown(f"- `{col_o}`: {detalle_o}")
                else:
                    st.caption("No se detectaron anomalías estadísticas en las variables numéricas.")

        with col_res2:
            with st.container(border=True):
                st.markdown("##### Vista previa del dataset procesado")
                st.caption("Datos depurados y tipificados, listos para ingresar a los algoritmos de Machine Learning:")
                st.dataframe(df_limpio, width="stretch")

# ==========================================
# PESTAÑA 3: ÁRBOL DE DECISIÓN (Modelado y Evaluación)
# ==========================================
with tab3:
    st.markdown('<div class="section-title">Entrenamiento de modelo clasificatorio (Árbol de Decisión)</div>', unsafe_allow_html=True)

    if "df_limpio" not in st.session_state:
        st.warning("Debes procesar los datos en las pestañas anteriores antes de configurar un modelo predictivo.")
    else:
        df_limpio = st.session_state["df_limpio"]
        st.write(
            "Selecciona la variable objetivo a predecir, los atributos predictores y ajusta los "
            "hiperparámetros del algoritmo para construir y evaluar el modelo."
        )

        columnas_disponibles = df_limpio.columns.tolist()
        indice_objetivo_default = len(columnas_disponibles) - 1

        with st.container(border=True):
            col_conf1, col_conf2 = st.columns(2)
            with col_conf1:
                st.markdown("##### 1. Definición de variables")
                col_objetivo = st.selectbox(
                    "Variable Objetivo (Target - Y)",
                    options=columnas_disponibles,
                    index=indice_objetivo_default,
                    help="Atributo categórico que el modelo aprenderá a clasificar."
                )
                
                opciones_predictoras = [c for c in columnas_disponibles if c != col_objetivo]
                default_predictoras = [c for c in opciones_predictoras if 'id' not in c.split('_')]
                
                cols_predictoras = st.multiselect(
                    "Variables Predictoras (Features - X)",
                    options=opciones_predictoras,
                    default=default_predictoras,
                    help="Atributos independientes utilizados por el modelo para encontrar patrones de decisión."
                )

            with col_conf2:
                st.markdown("##### 2. Hiperparámetros y partición")
                criterio = st.selectbox(
                    "Criterio de pureza de división",
                    options=["gini", "entropy"],
                    format_func=lambda x: "Índice Gini (Impureza de Gini)" if x == "gini" else "Entropía (Ganancia de Información)",
                    help="Fórmula matemática empleada para evaluar la calidad de cada partición en los nodos del árbol."
                )
                max_depth = st.slider(
                    "Profundidad máxima del árbol (max_depth)",
                    min_value=1, max_value=10, value=3,
                    help="Restringe los niveles jerárquicos del árbol para prevenir el sobreajuste (overfitting)."
                )
                porcentaje_prueba = st.slider(
                    "Proporción del conjunto de prueba (Test split %)",
                    min_value=10, max_value=50, value=25, step=5,
                    help="Porcentaje de registros reservados exclusivamente para validar la capacidad de generalización del modelo."
                )
                test_size = porcentaje_prueba / 100.0

            st.write("")
            if st.button("Ejecutar entrenamiento del modelo", type="primary", width="stretch"):
                with st.spinner("Ejecutando codificación One-Hot, particionando datos y ajustando el Árbol de Decisión..."):
                    exito_arbol, msj_arbol, res_arbol = entrenar_arbol_decision(
                        df_limpio, col_objetivo, cols_predictoras, criterio, max_depth, test_size
                    )
                if not exito_arbol:
                    st.error(msj_arbol)
                else:
                    st.session_state["ultimo_arbol"] = res_arbol
                    st.toast("Modelo entrenado y evaluado correctamente.", icon="✔️")

        if "ultimo_arbol" in st.session_state:
            res = st.session_state["ultimo_arbol"]
            st.markdown('<div class="section-title">Métricas de rendimiento (Validación sobre Test Set)</div>', unsafe_allow_html=True)
            st.caption(
                f"Partición de datos: **{res['filas_entrenamiento']} registros de entrenamiento** y "
                f"**{res['filas_prueba']} registros de prueba**."
            )

            k1, k2, k3, k4 = st.columns(4)
            k1.metric(
                "Exactitud (Accuracy)",
                f"{res['exactitud'] * 100:.1f}%",
                help="Proporción total de predicciones correctas sobre el conjunto de prueba."
            )
            k2.metric(
                "Precisión (Precision)",
                f"{res['precision'] * 100:.1f}%",
                help="Promedio ponderado de la fiabilidad de las predicciones positivas."
            )
            k3.metric(
                "Sensibilidad (Recall)",
                f"{res['recall'] * 100:.1f}%",
                help="Promedio ponderado de la capacidad del modelo para detectar los casos reales de cada clase."
            )
            k4.metric(
                "Partición Train / Test",
                f"{res['filas_entrenamiento']} / {res['filas_prueba']}",
                help="Relación de filas utilizadas para el ajuste y la evaluación."
            )

            col_vis1, col_vis2 = st.columns([3, 2])
            with col_vis1:
                with st.container(border=True):
                    st.markdown("##### Diagrama estructural del Árbol de Decisión")
                    st.caption(
                        "Representación jerárquica de las reglas inferidas. En cada nodo, la rama izquierda "
                        "evalúa la condición como Verdadera y la derecha como Falsa."
                    )
                    st.pyplot(res["figura_arbol"])

            with col_vis2:
                with st.container(border=True):
                    st.markdown("##### Matriz de Confusión")
                    st.caption(
                        "Contraste entre las etiquetas reales (eje Y) y las predicciones del modelo (eje X). "
                        "La diagonal principal concentra los aciertos."
                    )
                    fig_cm = px.imshow(
                        res["matriz_confusion"],
                        labels=dict(x="Predicción del Modelo", y="Valor Real (Ground Truth)", color="Registros"),
                        x=res["clases"],
                        y=res["clases"],
                        text_auto=True,
                        color_continuous_scale="Greens"
                    )
                    fig_cm.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_cm, width="stretch")

            with st.container(border=True):
                st.markdown("##### Persistencia del modelo")
                st.caption("Almacena el modelo serializado (.pkl) y registra sus hiperparámetros para futuras comparativas:")
                c_save1, c_save2 = st.columns([3, 1])
                nombre_modelo = c_save1.text_input(
                    "Identificador del modelo:",
                    placeholder="Ej: Árbol Gini Profundidad 3 - Predicción Abandono",
                    label_visibility="collapsed"
                )
                if c_save2.button("Guardar en el registro", type="primary", width="stretch"):
                    reg = guardar_modelo(nombre_modelo, res, st.session_state.get("nombre_dataset", "dataset.csv"))
                    st.toast(f"Modelo '{reg['nombre']}' almacenado en el historial.", icon="💾")
                    st.rerun()

# ==========================================
# PESTAÑA 4: GESTIÓN Y COMPARACIÓN DE MODELOS
# ==========================================
with tab4:
    st.markdown('<div class="section-title">Registro histórico y evaluación comparativa</div>', unsafe_allow_html=True)
    st.write(
        "Consulta los metadatos de los modelos previamente almacenados, contrasta su rendimiento "
        "mediante gráficos comparativos y gestiona los archivos persistentes."
    )

    modelos_guardados = listar_modelos_guardados()

    if not modelos_guardados:
        st.info("No existen modelos registrados actualmente. Entrena y guarda un modelo en la **Pestaña ③** para habilitar la comparativa.")
    else:
        df_modelos = pd.DataFrame(modelos_guardados)
        
        with st.container(border=True):
            st.markdown("##### Matriz de experimentos registrados")
            df_mostrar = df_modelos[[
                "id", "nombre", "fecha", "dataset", "variable_objetivo",
                "criterio", "profundidad_max", "division_prueba",
                "exactitud", "precision", "recall"
            ]].rename(columns={
                "id": "ID Registro",
                "nombre": "Identificador del Modelo",
                "fecha": "Fecha Entrenamiento",
                "dataset": "Dataset Origen",
                "variable_objetivo": "Target",
                "criterio": "Criterio",
                "profundidad_max": "Profundidad",
                "division_prueba": "Test Split",
                "exactitud": "Exactitud (0-1)",
                "precision": "Precisión (0-1)",
                "recall": "Recall (0-1)"
            })
            st.dataframe(df_mostrar, width="stretch", hide_index=True)

        with st.container(border=True):
            st.markdown("##### Comparativa visual de rendimiento")
            fig_comp = px.bar(
                df_modelos,
                x="nombre",
                y=["exactitud", "precision", "recall"],
                barmode="group",
                labels={"value": "Puntaje (Escala 0.0 - 1.0)", "nombre": "Modelo Evaluado", "variable": "Métrica"},
                color_discrete_sequence=["#165B33", "#10B981", "#D97706"]
            )
            fig_comp.update_layout(
                yaxis_range=[0, 1.05],
                legend_title_text="Métrica",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#FAFAF9"
            )
            st.plotly_chart(fig_comp, width="stretch")

        with st.container(border=True):
            st.markdown("##### Depuración del historial")
            col_del1, col_del2 = st.columns([3, 1])
            id_a_eliminar = col_del1.selectbox(
                "Selecciona un registro para eliminar su entrada y su archivo binario (.pkl):",
                options=[m["id"] for m in modelos_guardados],
                format_func=lambda x: next((f"{m['nombre']} — ({m['fecha']} | Exactitud: {m['exactitud']*100:.1f}%)" for m in modelos_guardados if m["id"] == x), x),
                label_visibility="collapsed"
            )
            if col_del2.button("Eliminar registro", type="secondary", width="stretch"):
                eliminar_modelo_guardado(id_a_eliminar)
                st.toast("Registro y archivo binario eliminados.", icon="🗑️")
                st.rerun()

# ==========================================
# BARRA LATERAL (ACTUALIZACIÓN EN TIEMPO REAL)
# ==========================================
with contenedor_sidebar.container():
    st.markdown("### Panel de Control")
    st.caption("Desarrollado por Franco Fajardo y Erick Mamani")
    st.divider()

    st.markdown("**ESTADO DEL PIPELINE**")
    tiene_archivo = "df_original" in st.session_state
    tiene_limpio = "df_limpio" in st.session_state
    tiene_arbol = "ultimo_arbol" in st.session_state

    st.markdown(
"""<div class="step-card">
<span>1. Ingesta de CSV</span>
<span class="{0}">{1}</span>
</div>
<div class="step-card">
<span>2. Limpieza de Datos</span>
<span class="{2}">{3}</span>
</div>
<div class="step-card">
<span>3. Modelo Predictivo</span>
<span class="{4}">{5}</span>
</div>""".format(
            'badge-ok' if tiene_archivo else 'badge-wait', 'LISTO' if tiene_archivo else 'PENDIENTE',
            'badge-ok' if tiene_limpio else 'badge-wait', 'LISTO' if tiene_limpio else 'PENDIENTE',
            'badge-ok' if tiene_arbol else 'badge-wait', 'LISTO' if tiene_arbol else 'PENDIENTE'
        ),
        unsafe_allow_html=True
    )

    if tiene_archivo:
        st.divider()
        st.caption("ARCHIVO EN MEMORIA")
        st.markdown(
            f"<div class='active-file-box'>{st.session_state.get('nombre_dataset', '')}</div>",
            unsafe_allow_html=True
        )

    st.divider()
    with st.expander("Guía rápida del flujo"):
        st.markdown(
            "1. **Carga y Validación:** Importa el dataset en bruto.\n"
            "2. **Preprocesamiento:** Imputación de nulos y control de valores atípicos.\n"
            "3. **Modelado:** Configuración y entrenamiento del Árbol de Decisión.\n"
            "4. **Evaluación:** Registro histórico y comparativa de métricas."
        )