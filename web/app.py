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
import importlib

# Asegurar que el intérprete de Python encuentre el paquete 'analisis' ubicando la raíz del proyecto
RUTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if RUTA_RAIZ not in sys.path:
    sys.path.append(RUTA_RAIZ)

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px

# Importación y recarga forzada de los módulos de lógica de negocio (Backend)
# Evita que Streamlit retenga versiones antiguas en caché de memoria
import analisis.validador
import analisis.limpieza
import analisis.arbol_decision
import analisis.asociacion
import analisis.dashboard
import analisis.informe
importlib.reload(analisis.validador)
importlib.reload(analisis.limpieza)
importlib.reload(analisis.arbol_decision)
importlib.reload(analisis.asociacion)
importlib.reload(analisis.dashboard)
importlib.reload(analisis.informe)

from analisis.validador import validar_y_cargar_csv
from analisis.limpieza import limpiar_dataset_automatico
from analisis.arbol_decision import (
    entrenar_arbol_decision,
    guardar_modelo,
    listar_modelos_guardados,
    eliminar_modelo_guardado
)
from analisis.asociacion import (
    generar_reglas_asociacion,
    filtrar_reglas,
    guardar_reglas,
    listar_reglas_guardadas,
    cargar_tabla_reglas,
    eliminar_reglas_guardadas
)
from analisis.dashboard import (
    clasificar_columnas,
    aplicar_filtros,
    calcular_kpis,
    matriz_correlacion,
    correlaciones_destacadas,
    interpretar_correlacion,
    estadisticas_descriptivas
)
from analisis.informe import generar_informe_html

# Configuración principal de la página web (Diseño ancho y barra lateral expandida)
st.set_page_config(
    page_title="Plataforma de Minería de Datos",
    layout="wide",
    initial_sidebar_state="expanded"
)

def cargar_estilos_css(nombre_archivo="estilos.css"):
    """
    Lee una hoja de estilos CSS externa ubicada en el mismo directorio que app.py
    y la inyecta en el DOM de la aplicación Streamlit junto con reglas de contraste.
    """
    ruta_css = os.path.join(os.path.dirname(__file__), nombre_archivo)
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

# Aplicar los estilos visuales desde el archivo externo
cargar_estilos_css()

# Reservamos el contenedor de la barra lateral para actualizarlo al final del script
contenedor_sidebar = st.sidebar.empty()

# ==========================================
# ENCABEZADO PRINCIPAL (HERO BANNER)
# ==========================================
st.markdown("""
    <div class="hero-banner">
        <div class="hero-badge">Suite Analítica • Machine Learning</div>
        <h1>Plataforma de Minería de Datos</h1>
        <p>Entorno interactivo para validación de calidad de datos, preprocesamiento estadístico automatizado y entrenamiento de Árboles de Decisión.</p>
    </div>
""", unsafe_allow_html=True)

# Definición de pestañas estilizadas como botones tipo píldora (Pill Tabs)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Carga y Validación (RF1)",
    "2. Preprocesamiento y Limpieza (RF2)",
    "3. Modelado: Árbol de Decisión (RF3)",
    "4. Historial y Comparativa (RF3)",
    "5. Reglas de Asociación (RF4)",
    "6. Dashboard (RF6)",
    "7. Informe (RF5)"
])

# ==========================================
# PESTAÑA 1: CARGA Y VALIDACIÓN (Ingesta de Datos)
# ==========================================
with tab1:
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

    # Selector de datasets de ejemplo incluidos en storage/datasets (se leen tal cual, sin modificarlos)
    ruta_datasets = os.path.join(RUTA_RAIZ, "storage", "datasets")
    datasets_demo = sorted(f for f in os.listdir(ruta_datasets) if f.lower().endswith(".csv")) if os.path.isdir(ruta_datasets) else []
    if archivo is None and datasets_demo:
        c_demo1, c_demo2 = st.columns([3, 1])
        demo_elegido = c_demo1.selectbox(
            "...o utiliza uno de los datasets de ejemplo incluidos en el proyecto:",
            options=datasets_demo,
            index=datasets_demo.index("clientes_abandono.csv") if "clientes_abandono.csv" in datasets_demo else 0
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

# ==========================================
# PESTAÑA 2: LIMPIEZA AUTOMÁTICA (Preparación de Datos)
# ==========================================
with tab2:
    st.markdown('<div class="section-title">Preprocesamiento y reparación automatizada</div>', unsafe_allow_html=True)

    if "df_original" not in st.session_state:
        st.warning("Debes importar un archivo CSV válido en la pestaña **1. Carga y Validación** antes de continuar.")
    else:
        df = st.session_state["df_original"]
        st.write(
            "Configura las reglas de limpieza para estandarizar cabeceras, descartar registros duplicados, "
            "imputar valores faltantes y mitigar el impacto estadístico de valores extremos (outliers)."
        )

        with st.container(border=True):
            st.markdown("##### Parámetros del pipeline de limpieza")
            st.caption("Ajusta el comportamiento de los algoritmos de reparación (los cambios se aplican en tiempo real):")
            
            # Controles interactivos para definir la estrategia de limpieza
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
        
        # Guardar el dataset procesado en memoria para la etapa de entrenamiento
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
        # Por convención, se sugiere la última columna como variable Target por defecto
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
                
                # Filtrar la variable objetivo de las predictoras para evitar fuga de datos (Data Leakage)
                opciones_predictoras = [c for c in columnas_disponibles if c != col_objetivo]
                # Excluir automáticamente columnas identificadoras (ID) de la selección por defecto
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
            # Botón de acción principal con retroalimentación de carga (Spinner)
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

        # Renderizado de resultados y artefactos visuales si existe un modelo en sesión
        if "ultimo_arbol" in st.session_state:
            res = st.session_state["ultimo_arbol"]
            st.markdown('<div class="section-title">Métricas de rendimiento (Validación sobre Test Set)</div>', unsafe_allow_html=True)
            st.caption(
                f"Partición de datos: **{res['filas_entrenamiento']} registros de entrenamiento** y "
                f"**{res['filas_prueba']} registros de prueba**."
            )

            # Tarjetas con las métricas estándar de clasificación
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
                    # Mapa de calor interactivo con Plotly en gama cromática Purple-Blue ('PuBu')
                    fig_cm = px.imshow(
                        res["matriz_confusion"],
                        labels=dict(x="Predicción del Modelo", y="Valor Real (Ground Truth)", color="Registros"),
                        x=res["clases"],
                        y=res["clases"],
                        text_auto=True,
                        color_continuous_scale="PuBu"
                    )
                    fig_cm.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_cm, width="stretch")

            # Sección de persistencia del modelo (.pkl y .json)
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

    # Lectura del archivo JSON de registro desde el backend
    modelos_guardados = listar_modelos_guardados()

    if not modelos_guardados:
        st.info("No existen modelos registrados actualmente. Entrena y guarda un modelo en la **Pestaña 3** para habilitar la comparativa.")
    else:
        df_modelos = pd.DataFrame(modelos_guardados)
        
        with st.container(border=True):
            st.markdown("##### Matriz de experimentos registrados")
            # Formateo de nombres de columnas para presentación ejecutiva
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
            # Gráfico interactivo de barras agrupadas con paleta de alto contraste (Índigo, Cian, Esmeralda)
            fig_comp = px.bar(
                df_modelos,
                x="nombre",
                y=["exactitud", "precision", "recall"],
                barmode="group",
                labels={"value": "Puntaje (Escala 0.0 - 1.0)", "nombre": "Modelo Evaluado", "variable": "Métrica"},
                color_discrete_sequence=["#4F46E5", "#0EA5E9", "#10B981"]
            )
            fig_comp.update_layout(
                yaxis_range=[0, 1.05],
                legend_title_text="Métrica",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#F8FAFC"
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
# PESTAÑA 5: REGLAS DE ASOCIACIÓN (RF4)
# ==========================================
with tab5:
    st.markdown('<div class="section-title">Descubrimiento de patrones: Reglas de Asociación</div>', unsafe_allow_html=True)

    if "df_limpio" not in st.session_state:
        st.warning("Debes procesar los datos en las pestañas **1** y **2** antes de buscar reglas de asociación.")
    else:
        df_limpio = st.session_state["df_limpio"]
        st.write(
            "Busca combinaciones de valores que aparecen juntas con frecuencia, del tipo "
            "**SI** (antecedente) **ENTONCES** (consecuente). Cada fila se transforma en una transacción de ítems "
            "`columna=valor`; las variables numéricas se agrupan en intervalos (Bajo / Medio / Alto)."
        )

        columnas_asoc = [c for c in df_limpio.columns if 'id' not in c.split('_')]
        _, categoricas_asoc = clasificar_columnas(df_limpio)
        default_asoc = [c for c in categoricas_asoc if c in columnas_asoc][:6] or columnas_asoc[:4]

        with st.container(border=True):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                st.markdown("##### 1. Datos de entrada")
                cols_asoc = st.multiselect(
                    "Columnas a analizar",
                    options=columnas_asoc,
                    default=default_asoc,
                    help="Variables cuyos valores se combinarán para buscar patrones. Más columnas = más reglas y más tiempo de cálculo."
                )
                n_intervalos = st.slider(
                    "Intervalos para variables numéricas",
                    min_value=2, max_value=5, value=3,
                    help="Las columnas numéricas se dividen en grupos de igual tamaño (cuantiles) antes de aplicar el algoritmo."
                )
                algoritmo = st.selectbox(
                    "Algoritmo",
                    options=["apriori", "fpgrowth"],
                    format_func=lambda x: "Apriori (clásico, por niveles)" if x == "apriori" else "FP-Growth (árbol de patrones, más rápido)",
                    help="Ambos encuentran los mismos conjuntos frecuentes; FP-Growth es más eficiente en datasets grandes."
                )
            with col_a2:
                st.markdown("##### 2. Umbrales")
                min_soporte = st.slider(
                    "Soporte mínimo",
                    min_value=0.01, max_value=0.50, value=0.10, step=0.01,
                    help="Proporción mínima de registros en que debe aparecer la combinación completa de la regla."
                )
                min_confianza = st.slider(
                    "Confianza mínima",
                    min_value=0.10, max_value=1.00, value=0.60, step=0.05,
                    help="Probabilidad mínima de que ocurra el consecuente cuando ocurre el antecedente."
                )
                max_longitud = st.slider(
                    "Máximo de ítems por regla",
                    min_value=2, max_value=5, value=3,
                    help="Limita el largo de las reglas para que sean fáciles de interpretar."
                )

            st.write("")
            if st.button("Generar reglas de asociación", type="primary", width="stretch"):
                with st.spinner("Construyendo transacciones y buscando conjuntos frecuentes..."):
                    exito_asoc, msj_asoc, res_asoc = generar_reglas_asociacion(
                        df_limpio, cols_asoc, min_soporte, min_confianza, algoritmo, n_intervalos, max_longitud
                    )
                if not exito_asoc:
                    st.session_state.pop("resultado_reglas", None)
                    st.error(msj_asoc)
                else:
                    st.session_state["resultado_reglas"] = res_asoc
                    st.toast(msj_asoc, icon="✔️")

        if "resultado_reglas" in st.session_state:
            res_asoc = st.session_state["resultado_reglas"]
            tabla_reglas = res_asoc["tabla_reglas"]

            st.markdown('<div class="section-title">Resultados</div>', unsafe_allow_html=True)
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Reglas generadas", len(tabla_reglas))
            r2.metric("Conjuntos frecuentes", res_asoc["n_frecuentes"])
            r3.metric("Ítems distintos", res_asoc["n_items"], help="Cantidad de pares columna=valor posibles.")
            r4.metric("Transacciones", res_asoc["n_transacciones"])

            with st.container(border=True):
                st.markdown("##### Filtrado y ordenamiento")
                f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
                texto_busqueda = f1.text_input(
                    "Buscar ítem (antecedente o consecuente)",
                    placeholder="Ej: abandono_cliente=Si"
                )
                lift_min_filtro = f2.number_input("Lift mínimo", min_value=0.0, value=1.0, step=0.1)
                conf_min_filtro = f3.number_input("Confianza mínima", min_value=0.0, max_value=1.0,
                                                  value=float(res_asoc["min_confianza"]), step=0.05)
                orden_reglas = f4.selectbox("Ordenar por", ["lift", "confianza", "soporte", "n_items"])
                ascendente = st.toggle("Orden ascendente", value=False)

                tabla_filtrada = filtrar_reglas(tabla_reglas, texto_busqueda, lift_min_filtro,
                                                conf_min_filtro, orden_reglas, ascendente)
                st.caption(f"Mostrando **{len(tabla_filtrada)}** de {len(tabla_reglas)} reglas. "
                           "Lift > 1 indica que antecedente y consecuente aparecen juntos más de lo esperable por azar.")
                st.dataframe(
                    tabla_filtrada.rename(columns={
                        "antecedente": "SI (Antecedente)", "consecuente": "ENTONCES (Consecuente)",
                        "soporte": "Soporte", "confianza": "Confianza", "lift": "Lift", "n_items": "Ítems"
                    }),
                    width="stretch", hide_index=True
                )

            col_g1, col_g2 = st.columns([3, 2])
            with col_g1:
                with st.container(border=True):
                    st.markdown("##### Mapa de reglas: soporte vs. confianza")
                    if not tabla_filtrada.empty:
                        fig_reglas = px.scatter(
                            tabla_filtrada, x="soporte", y="confianza", color="lift", size="n_items",
                            hover_data={"antecedente": True, "consecuente": True, "lift": ":.2f"},
                            color_continuous_scale="PuBu",
                            labels={"soporte": "Soporte", "confianza": "Confianza", "lift": "Lift"}
                        )
                        fig_reglas.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_reglas, width="stretch")
                    else:
                        st.info("Ninguna regla cumple los filtros actuales.")
            with col_g2:
                with st.container(border=True):
                    st.markdown("##### Guardar resultado")
                    st.caption("Se guardan las reglas **tal como están filtradas** (CSV + registro JSON en storage/reglas).")
                    nombre_reglas = st.text_input(
                        "Nombre del análisis",
                        placeholder="Ej: Perfil de abandono - soporte 10%"
                    )
                    if st.button("Guardar reglas", type="primary", width="stretch"):
                        if tabla_filtrada.empty:
                            st.error("No hay reglas para guardar con los filtros actuales.")
                        else:
                            reg_r = guardar_reglas(nombre_reglas, res_asoc,
                                                   st.session_state.get("nombre_dataset", "dataset.csv"), tabla_filtrada)
                            st.toast(f"Análisis '{reg_r['nombre']}' guardado.", icon="💾")
                            st.rerun()
                    st.download_button(
                        "Descargar reglas (.csv)",
                        data=tabla_filtrada.to_csv(index=False).encode("utf-8"),
                        file_name="reglas_asociacion.csv",
                        mime="text/csv"
                    )

        # Gestión de resultados guardados
        st.markdown('<div class="section-title">Resultados de asociación guardados</div>', unsafe_allow_html=True)
        reglas_guardadas = listar_reglas_guardadas()
        if not reglas_guardadas:
            st.info("Aún no hay análisis de asociación guardados.")
        else:
            df_reglas_g = pd.DataFrame(reglas_guardadas)
            with st.container(border=True):
                st.dataframe(
                    df_reglas_g[["nombre", "fecha", "dataset", "algoritmo", "min_soporte", "min_confianza",
                                 "cantidad_reglas", "lift_maximo", "confianza_promedio", "mejor_regla"]].rename(columns={
                        "nombre": "Análisis", "fecha": "Fecha", "dataset": "Dataset", "algoritmo": "Algoritmo",
                        "min_soporte": "Soporte mín.", "min_confianza": "Confianza mín.", "cantidad_reglas": "N° reglas",
                        "lift_maximo": "Lift máx.", "confianza_promedio": "Confianza prom.", "mejor_regla": "Regla con mayor lift"
                    }),
                    width="stretch", hide_index=True
                )
                if len(df_reglas_g) > 1:
                    fig_comp_r = px.bar(
                        df_reglas_g, x="nombre", y=["lift_maximo", "confianza_promedio"], barmode="group",
                        labels={"nombre": "Análisis", "value": "Valor", "variable": "Indicador"},
                        color_discrete_sequence=["#4F46E5", "#10B981"]
                    )
                    fig_comp_r.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#F8FAFC")
                    st.plotly_chart(fig_comp_r, width="stretch")

            with st.container(border=True):
                g1, g2, g3 = st.columns([3, 1, 1])
                id_reglas_sel = g1.selectbox(
                    "Selecciona un análisis guardado:",
                    options=[r["id"] for r in reglas_guardadas],
                    format_func=lambda x: next((f"{r['nombre']} — {r['fecha']} ({r['cantidad_reglas']} reglas)"
                                                for r in reglas_guardadas if r["id"] == x), x),
                    label_visibility="collapsed"
                )
                ver_reglas = g2.button("Ver reglas", width="stretch")
                if g3.button("Eliminar", type="secondary", width="stretch"):
                    eliminar_reglas_guardadas(id_reglas_sel)
                    st.toast("Análisis de asociación eliminado.", icon="🗑️")
                    st.rerun()
                if ver_reglas:
                    st.dataframe(cargar_tabla_reglas(id_reglas_sel), width="stretch", hide_index=True)

# ==========================================
# PESTAÑA 6: DASHBOARD INTERACTIVO (RF6)
# ==========================================
with tab6:
    st.markdown('<div class="section-title">Dashboard interactivo</div>', unsafe_allow_html=True)

    if "df_limpio" not in st.session_state:
        st.warning("Debes procesar los datos en las pestañas **1** y **2** para habilitar el dashboard.")
    else:
        df_dash = st.session_state["df_limpio"]
        numericas, categoricas = clasificar_columnas(df_dash)

        # Variable objetivo sugerida: la usada en el último árbol, o la última columna categórica
        objetivo_sugerido = st.session_state.get("ultimo_arbol", {}).get("col_objetivo")
        if objetivo_sugerido not in categoricas:
            objetivo_sugerido = categoricas[-1] if categoricas else None

        with st.container(border=True):
            st.markdown("##### Filtros dinámicos")
            fc1, fc2 = st.columns([1, 2])
            opciones_color = ["(ninguna)"] + categoricas
            col_color = fc1.selectbox(
                "Variable para segmentar (color)",
                options=opciones_color,
                index=opciones_color.index(objetivo_sugerido) if objetivo_sugerido in opciones_color else 0,
                help="Los gráficos se colorean según esta variable (por ejemplo, la variable objetivo)."
            )
            col_color = None if col_color == "(ninguna)" else col_color
            cols_filtro = fc2.multiselect(
                "Columnas por las que filtrar",
                options=list(dict.fromkeys(categoricas + numericas)),
                default=[c for c in categoricas if c != col_color][:2],
                help="Elige columnas y ajusta sus valores: todos los gráficos e indicadores se recalculan al instante."
            )

            filtros = {}
            if cols_filtro:
                columnas_widgets = st.columns(min(len(cols_filtro), 3))
                for k, col_f in enumerate(cols_filtro):
                    with columnas_widgets[k % len(columnas_widgets)]:
                        if col_f in numericas and df_dash[col_f].nunique() > 10:
                            vmin, vmax = float(df_dash[col_f].min()), float(df_dash[col_f].max())
                            if vmin < vmax:
                                rango = st.slider(col_f, min_value=vmin, max_value=vmax, value=(vmin, vmax), key=f"dash_{st.session_state.get('nombre_dataset', '')}_{col_f}")
                                filtros[col_f] = ("rango", rango)
                        else:
                            valores = sorted(df_dash[col_f].dropna().unique().tolist(), key=str)
                            elegidos = st.multiselect(col_f, options=valores, default=valores, key=f"dash_{st.session_state.get('nombre_dataset', '')}_{col_f}")
                            filtros[col_f] = ("valores", elegidos)

        df_filtrado = aplicar_filtros(df_dash, filtros)
        kpis = calcular_kpis(df_filtrado, df_dash, col_color)

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Registros filtrados", kpis["registros"], help="Filas que cumplen todos los filtros.")
        d2.metric("% del dataset", f"{kpis['porcentaje_del_total']}%")
        d3.metric("Variables", kpis["variables"])
        if "clase_mayoritaria" in kpis:
            d4.metric(f"Clase mayoritaria ({col_color})", kpis["clase_mayoritaria"], f"{kpis['porcentaje_clase']}% de los filtrados",
                      delta_color="off")
        else:
            d4.metric("Clase mayoritaria", "—")

        if df_filtrado.empty:
            st.warning("Ningún registro cumple los filtros seleccionados. Amplía los rangos o categorías.")
        else:
            # --- Distribuciones ---
            st.markdown('<div class="section-title">Distribuciones</div>', unsafe_allow_html=True)
            g1, g2 = st.columns(2)
            with g1:
                with st.container(border=True):
                    if numericas:
                        var_num = st.selectbox("Variable numérica", numericas, key="dash_var_num")
                        fig_hist = px.histogram(
                            df_filtrado, x=var_num, color=col_color, nbins=20, barmode="overlay", opacity=0.75,
                            color_discrete_sequence=["#4F46E5", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444"]
                        )
                        fig_hist.update_layout(margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)",
                                               title=f"Histograma de {var_num}")
                        st.plotly_chart(fig_hist, width="stretch")
                    else:
                        st.info("El dataset no tiene variables numéricas.")
            with g2:
                with st.container(border=True):
                    opciones_cat = [c for c in categoricas if c != col_color] or categoricas
                    if opciones_cat:
                        var_cat = st.selectbox("Variable categórica", opciones_cat, key="dash_var_cat")
                        fig_cat = px.histogram(
                            df_filtrado, x=var_cat, color=col_color, barmode="group",
                            color_discrete_sequence=["#4F46E5", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444"]
                        )
                        fig_cat.update_layout(margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)",
                                              title=f"Registros por {var_cat}", yaxis_title="Registros")
                        st.plotly_chart(fig_cat, width="stretch")
                    else:
                        st.info("El dataset no tiene variables categóricas.")

            if numericas and col_color:
                with st.container(border=True):
                    var_box = st.selectbox("Comparar distribución por grupo (diagrama de caja)", numericas, key="dash_var_box")
                    fig_box = px.box(df_filtrado, x=col_color, y=var_box, color=col_color, points="outliers",
                                     color_discrete_sequence=["#4F46E5", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444"])
                    fig_box.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                    st.plotly_chart(fig_box, width="stretch")

            # --- Correlaciones ---
            st.markdown('<div class="section-title">Correlaciones</div>', unsafe_allow_html=True)
            c_corr1, c_corr2 = st.columns([3, 2])
            with c_corr1:
                with st.container(border=True):
                    metodo_corr = st.radio("Método", ["pearson", "spearman"], horizontal=True,
                                           format_func=lambda x: "Pearson (lineal)" if x == "pearson" else "Spearman (por rangos)")
                    matriz = matriz_correlacion(df_filtrado, metodo_corr)
                    if matriz.empty:
                        st.info("Se necesitan al menos 2 variables numéricas con variación para calcular correlaciones.")
                    else:
                        fig_corr = px.imshow(matriz, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
                        fig_corr.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_corr, width="stretch")
            with c_corr2:
                with st.container(border=True):
                    st.markdown("##### Relaciones más fuertes")
                    for a, b, r in correlaciones_destacadas(matriz, top=5):
                        st.markdown(f"- `{a}` ↔ `{b}`: **{r:.2f}** ({interpretar_correlacion(r)})")
                    st.markdown("##### Estadísticas descriptivas")
                    st.dataframe(estadisticas_descriptivas(df_filtrado), width="stretch")

            # --- Resultados de modelos ---
            st.markdown('<div class="section-title">Resultados de los modelos</div>', unsafe_allow_html=True)
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                with st.container(border=True):
                    st.markdown("##### Árboles de decisión guardados")
                    modelos_dash = listar_modelos_guardados()
                    if modelos_dash:
                        df_mod_dash = pd.DataFrame(modelos_dash)
                        fig_mod = px.bar(df_mod_dash, x="nombre", y=["exactitud", "precision", "recall"], barmode="group",
                                         labels={"nombre": "Modelo", "value": "Puntaje", "variable": "Métrica"},
                                         color_discrete_sequence=["#4F46E5", "#0EA5E9", "#10B981"])
                        fig_mod.update_layout(yaxis_range=[0, 1.05], paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#F8FAFC",
                                              margin=dict(l=10, r=10, t=10, b=10))
                        st.plotly_chart(fig_mod, width="stretch")
                    else:
                        st.info("No hay modelos guardados (pestaña 3).")
            with m_col2:
                with st.container(border=True):
                    st.markdown("##### Top 10 reglas de asociación (por lift)")
                    if "resultado_reglas" in st.session_state:
                        top_reglas = st.session_state["resultado_reglas"]["tabla_reglas"].head(10).copy()
                        top_reglas["regla"] = top_reglas["antecedente"] + " → " + top_reglas["consecuente"]
                        fig_top = px.bar(top_reglas.iloc[::-1], x="lift", y="regla", orientation="h",
                                         hover_data=["soporte", "confianza"], color="confianza",
                                         color_continuous_scale="PuBu", labels={"regla": "", "lift": "Lift"})
                        fig_top.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
                        st.plotly_chart(fig_top, width="stretch")
                    else:
                        st.info("Genera reglas en la pestaña 5 para verlas aquí.")

            with st.expander(f"Ver datos filtrados ({len(df_filtrado)} registros)"):
                st.dataframe(df_filtrado, width="stretch")
                st.download_button("Descargar datos filtrados (.csv)", data=df_filtrado.to_csv(index=False).encode("utf-8"),
                                   file_name="datos_filtrados.csv", mime="text/csv")

# ==========================================
# PESTAÑA 7: INFORME (RF5)
# ==========================================
with tab7:
    st.markdown('<div class="section-title">Generación del informe final</div>', unsafe_allow_html=True)

    if "df_limpio" not in st.session_state:
        st.warning("Debes procesar los datos en las pestañas **1** y **2** antes de generar un informe.")
    else:
        st.write(
            "El informe reúne el **resumen de los datos**, la **limpieza** realizada, los **modelos** de árbol de decisión, "
            "las **reglas de asociación** y las **conclusiones**. Se exporta como un archivo HTML autocontenido."
        )
        df_inf = st.session_state["df_limpio"]
        _, categoricas_inf = clasificar_columnas(df_inf)
        objetivo_inf = st.session_state.get("ultimo_arbol", {}).get("col_objetivo")

        with st.container(border=True):
            i1, i2 = st.columns(2)
            titulo_informe = i1.text_input("Título del informe", value="Informe de Minería de Datos")
            opciones_obj_inf = ["(ninguna)"] + categoricas_inf
            col_obj_inf = i2.selectbox(
                "Variable objetivo a destacar",
                options=opciones_obj_inf,
                index=opciones_obj_inf.index(objetivo_inf) if objetivo_inf in opciones_obj_inf else len(opciones_obj_inf) - 1
            )
            conclusiones_usuario = st.text_area(
                "Conclusiones del equipo (opcional)",
                placeholder="Escribe aquí la interpretación del equipo. El informe también incluye conclusiones automáticas.",
                height=120
            )
            st.caption(
                f"Contenido disponible: último árbol {'✔' if 'ultimo_arbol' in st.session_state else '✘'} · "
                f"modelos guardados: {len(listar_modelos_guardados())} · "
                f"reglas de asociación {'✔' if 'resultado_reglas' in st.session_state else '✘'}"
            )

            if st.button("Generar informe", type="primary", width="stretch"):
                res_reglas_inf = st.session_state.get("resultado_reglas")
                with st.spinner("Generando gráficos y redactando el informe..."):
                    st.session_state["informe_html"] = generar_informe_html(
                        nombre_dataset=st.session_state.get("nombre_dataset", "dataset.csv"),
                        meta=st.session_state.get("meta_dataset", {}),
                        df_original=st.session_state["df_original"],
                        df_limpio=df_inf,
                        resumen_limpieza=st.session_state["resumen_limpieza"],
                        modelos=listar_modelos_guardados(),
                        ultimo_arbol=st.session_state.get("ultimo_arbol"),
                        resultado_reglas=res_reglas_inf,
                        tabla_reglas=res_reglas_inf["tabla_reglas"] if res_reglas_inf else None,
                        col_objetivo=None if col_obj_inf == "(ninguna)" else col_obj_inf,
                        conclusiones_usuario=conclusiones_usuario,
                        titulo=titulo_informe
                    )
                st.toast("Informe generado.", icon="📄")

        if "informe_html" in st.session_state:
            nombre_base = os.path.splitext(st.session_state.get("nombre_dataset", "dataset"))[0]
            st.download_button(
                "Descargar informe (.html)",
                data=st.session_state["informe_html"].encode("utf-8"),
                file_name=f"informe_{nombre_base}.html",
                mime="text/html",
                type="primary"
            )
            st.caption("Para obtener un **PDF**: abre el archivo descargado en el navegador y usa *Imprimir → Guardar como PDF*.")
            with st.container(border=True):
                st.markdown("##### Vista previa")
                components.html(st.session_state["informe_html"], height=900, scrolling=True)

# ==========================================
# BARRA LATERAL (ACTUALIZACIÓN EN TIEMPO REAL)
# ==========================================
with contenedor_sidebar.container():
    st.markdown("## Panel de Control")
    st.caption("Desarrollado por Franco Fajardo y Erick Mamani")
    st.divider()

    st.markdown("**ESTADO DEL PIPELINE**")
    tiene_archivo = "df_original" in st.session_state
    tiene_limpio = "df_limpio" in st.session_state
    tiene_arbol = "ultimo_arbol" in st.session_state
    tiene_reglas = "resultado_reglas" in st.session_state
    tiene_informe = "informe_html" in st.session_state

    st.markdown(f"""
        <div class="step-card">
            <span>1. Ingesta de CSV</span>
            <span class="{'badge-ok' if tiene_archivo else 'badge-wait'}">{'LISTO' if tiene_archivo else 'PENDIENTE'}</span>
        </div>
        <div class="step-card">
            <span>2. Limpieza de Datos</span>
            <span class="{'badge-ok' if tiene_limpio else 'badge-wait'}">{'LISTO' if tiene_limpio else 'PENDIENTE'}</span>
        </div>
        <div class="step-card">
            <span>3. Modelo Predictivo</span>
            <span class="{'badge-ok' if tiene_arbol else 'badge-wait'}">{'LISTO' if tiene_arbol else 'PENDIENTE'}</span>
        </div>
        <div class="step-card">
            <span>4. Reglas de Asociación</span>
            <span class="{'badge-ok' if tiene_reglas else 'badge-wait'}">{'LISTO' if tiene_reglas else 'PENDIENTE'}</span>
        </div>
        <div class="step-card">
            <span>5. Informe HTML</span>
            <span class="{'badge-ok' if tiene_informe else 'badge-wait'}">{'LISTO' if tiene_informe else 'PENDIENTE'}</span>
        </div>
    """, unsafe_allow_html=True)

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
            "4. **Evaluación:** Registro histórico y comparativa de métricas.\n"
            "5. **Asociación:** Reglas SI→ENTONCES con soporte, confianza y lift.\n"
            "6. **Dashboard:** Gráficos interactivos con filtros dinámicos.\n"
            "7. **Informe:** Exportación del resumen completo a HTML."
        )