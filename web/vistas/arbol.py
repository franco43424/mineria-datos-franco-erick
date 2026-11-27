"""
Vista 3 - Árbol de Decisión (RF3).
Configura y entrena el modelo con analisis.arbol_decision, muestra métricas, árbol y matriz de confusión,
y permite guardar el modelo.
"""

import streamlit as st
import plotly.express as px

from analisis.config import es_columna_id
from analisis.arbol_decision import entrenar_arbol_decision, guardar_modelo


def mostrar():
    """Dibuja el contenido de la pestaña."""
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
                default_predictoras = [c for c in opciones_predictoras if not es_columna_id(c)]
                
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
