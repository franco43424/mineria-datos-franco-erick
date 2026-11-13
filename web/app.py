"""
Módulo: app.py
Propósito: Interfaz Gráfica de Usuario (Frontend) creada con Streamlit.
Actúa como la capa de presentación del proyecto, permitiendo a los usuarios interactuar 
con los procesos de minería de datos (ingesta, limpieza, modelado y evaluación) 
de forma visual, interactiva y sin necesidad de escribir código.
"""

import sys
import os
# Asegurar que el intérprete de Python encuentre el paquete 'analisis' ubicando la raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px

# Importación de los módulos de lógica de negocio (Backend)
from analisis.validador import validar_y_cargar_csv
from analisis.limpieza import limpiar_dataset_automatico
from analisis.arbol_decision import (
    entrenar_arbol_decision,
    guardar_modelo,
    listar_modelos_guardados,
    eliminar_modelo_guardado
)

# Configuración principal de la página web (Diseño ancho y barra lateral expandida)
st.set_page_config(
    page_title="Plataforma de Minería de Datos",
    layout="wide",
    initial_sidebar_state="expanded"
)

def cargar_estilos_css(nombre_archivo="estilos.css"):
    """
    Lee una hoja de estilos CSS externa ubicada en el mismo directorio que app.py
    y la inyecta en el DOM de la aplicación Streamlit.
    """
    ruta_css = os.path.join(os.path.dirname(__file__), nombre_archivo)
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Aplicar los estilos visuales desde el archivo externo
cargar_estilos_css()

# ==========================================
# BARRA LATERAL (MONITOREO DE FLUJO Y GUÍA)
# ==========================================
# La barra lateral mantiene el contexto del flujo de trabajo actual apoyándose en 'st.session_state'.
with st.sidebar:
    st.markdown("## Panel de Control")
    st.caption("Desarrollado por Franco Fajardo y Erick Mamani")
    st.divider()

    st.markdown("**ESTADO DEL PIPELINE**")
    # Verificación del estado en memoria caché de la sesión actual
    tiene_archivo = "df_original" in st.session_state
    tiene_limpio = "df_limpio" in st.session_state
    tiene_arbol = "ultimo_arbol" in st.session_state

    # Indicadores de progreso tipo tarjeta con badges de colores (definidos en estilos.css)
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
            "4. **Evaluación:** Registro histórico y comparativa de métricas."
        )

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
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Carga y Validación (RF1)",
    "2. Preprocesamiento y Limpieza (RF2)",
    "3. Modelado: Árbol de Decisión (RF3)",
    "4. Historial y Comparativa"
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

    if archivo is None:
        st.info("Sube un archivo CSV en el panel superior para habilitar las herramientas de preprocesamiento y modelado.")
    else:
        # Invocación al módulo validador del backend
        exito, mensaje, df, meta = validar_y_cargar_csv(archivo)
        if not exito:
            st.error(mensaje)
        else:
            # Control para disparar la notificación flotante (Toast) solo cuando se carga un archivo nuevo
            if st.session_state.get("nombre_dataset") != meta["nombre"]:
                st.toast(f"Dataset '{meta['nombre']}' validado correctamente.", icon="✔️")
                
            # Almacenamiento en el estado de la sesión para persistencia entre pestañas
            st.session_state["df_original"] = df
            st.session_state["nombre_dataset"] = meta["nombre"]

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
                st.dataframe(df, width="stretch")

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