import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
from analisis.validador import validar_y_cargar_csv
from analisis.limpieza import limpiar_dataset_automatico
from analisis.arbol_decision import (
    entrenar_arbol_decision,
    guardar_modelo,
    listar_modelos_guardados,
    eliminar_modelo_guardado
)

st.set_page_config(
    page_title="Minería de Datos - Franco & Erick",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BARRA LATERAL (GUÍA Y ESTADO ACTUAL) ---
with st.sidebar:
    st.title("Panel de Control")
    st.caption("Desarrollado por Franco Fajardo y Erick")
    st.divider()

    st.subheader("Estado del Flujo")
    tiene_archivo = "df_original" in st.session_state
    tiene_limpio = "df_limpio" in st.session_state
    tiene_arbol = "ultimo_arbol" in st.session_state

    st.markdown(f"{'✅' if tiene_archivo else '⏳'} **Paso 1:** Carga de CSV")
    st.markdown(f"{'✅' if tiene_limpio else '⏳'} **Paso 2:** Limpieza Automática")
    st.markdown(f"{'✅' if tiene_arbol else '⏳'} **Paso 3:** Árbol de Decisión")

    if tiene_archivo:
        st.info(f"**Archivo activo:**\n{st.session_state.get('nombre_dataset', '')}")

    st.divider()
    with st.expander("¿Cómo funciona esta plataforma?"):
        st.write(
            "1. **Sube tu archivo CSV** en la Pestaña 1.\n"
            "2. **Revisa la limpieza** automática de datos vacíos y extremos en la Pestaña 2.\n"
            "3. **Crea un modelo predictivo** (Árbol de Decisión) en la Pestaña 3 sin escribir código.\n"
            "4. **Compara tus modelos** guardados en la Pestaña 4."
        )

# --- ENCABEZADO PRINCIPAL ---
st.title("Plataforma de Administración de Minería de Datos")
st.markdown(
    "Analiza datos, limpia errores automáticamente y entrena modelos predictivos de forma visual, "
    "siguiendo el flujo de trabajo de **Orange Data Mining**."
)

# Creación de pestañas organizadas por etapa
tab1, tab2, tab3, tab4 = st.tabs([
    "📁 1. Carga y Validación (RF1)",
    "🧹 2. Limpieza Automática (RF2)",
    "🌳 3. Entrenar Árbol de Decisión (RF3)",
    "📊 4. Modelos Guardados y Comparación"
])

# ==========================================
# PESTAÑA 1: CARGA Y VALIDACIÓN
# ==========================================
with tab1:
    st.header("Paso 1: Subir y validar tu archivo de datos")
    st.write(
        "Sube cualquier archivo en formato **.CSV**. El sistema detectará automáticamente si viene "
        "separado por comas o punto y coma, revisará las tildes (codificación) y verificará que sea válido."
    )

    archivo = st.file_uploader(
        "Arrastra tu archivo CSV aquí o haz clic en 'Browse files'",
        type=["csv"],
        help="Tamaño máximo permitido: 50 MB. Debe tener al menos 2 columnas."
    )

    if archivo is None:
        st.info("👆 Sube un archivo CSV arriba para desbloquear las siguientes etapas del análisis.")
    else:
        exito, mensaje, df, meta = validar_y_cargar_csv(archivo)
        if not exito:
            st.error(mensaje)
        else:
            st.success(f"¡Listo! {mensaje} Ahora puedes avanzar a la pestaña **2. Limpieza Automática**.")
            st.session_state["df_original"] = df
            st.session_state["nombre_dataset"] = meta["nombre"]

            st.subheader("Diagnóstico técnico del archivo")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Tamaño del archivo", meta["tamano_kb"], help="Peso del archivo en el disco.")
            col2.metric("Formato de texto", meta["codificacion"], help="Codificación detectada para leer tildes y eñes.")
            col3.metric("Separador de columnas", meta["separador"], help="Símbolo que divide cada dato en el CSV.")
            col4.metric("Total de Filas", meta["filas"], help="Cantidad de registros encontrados.")
            col5.metric("Total de Columnas", meta["columnas"], help="Cantidad de variables por registro.")

            st.subheader("Vista previa de tus datos originales (Sin modificar)")
            st.caption("Así es como vienen los datos crudos desde tu archivo. Si ves celdas que dicen 'None', son datos faltantes que repararemos en el Paso 2.")
            st.dataframe(df, use_container_width=True)

# ==========================================
# PESTAÑA 2: LIMPIEZA AUTOMÁTICA
# ==========================================
with tab2:
    st.header("Paso 2: Limpieza y reparación automática de datos")

    if "df_original" not in st.session_state:
        st.warning("⚠️ Primero debes subir un archivo CSV válido en la pestaña **1. Carga y Validación**.")
    else:
        df = st.session_state["df_original"]
        st.write(
            "Los datos reales suelen traer filas repetidas, casillas vacías o números exagerados por error de tipeo. "
            "Aquí el sistema limpia todo automáticamente para que tus modelos no fallen."
        )

        with st.container(border=True):
            st.subheader("⚙️ Ajustes de limpieza (Opcional)")
            st.caption("El sistema ya eligió la configuración recomendada, pero puedes cambiar cómo quieres tratar los datos faltantes o extremos:")
            c_opt1, c_opt2 = st.columns(2)
            metodo_nulos = c_opt1.selectbox(
                "¿Qué hacer con las celdas vacías (Valores Nulos)?",
                options=["imputar", "eliminar"],
                format_func=lambda x: "Rellenar automáticamente con el valor promedio/más común (Recomendado)" if x == "imputar" else "Borrar la fila completa si le falta algún dato",
                help="Imputar conserva tus filas rellenando números con la Mediana y textos con la Moda (el valor más repetido)."
            )
            metodo_outliers = c_opt2.selectbox(
                "¿Qué hacer con números exagerados o irreales (Valores Atípicos / Outliers)?",
                options=["mediana", "acotar", "eliminar"],
                format_func=lambda x: {
                    "mediana": "Reemplazar el número exagerado por un valor normal (Mediana)",
                    "acotar": "Ajustar al límite máximo/mínimo normal permitido (Acotar)",
                    "eliminar": "Borrar la fila completa si tiene un valor extremo"
                }[x],
                help="Ejemplo: Si en Edad alguien escribió '150 años' por error, el sistema lo detecta estadísticamente (método IQR) y lo corrige."
            )

        # Ejecutar limpieza
        df_limpio, resumen = limpiar_dataset_automatico(df, metodo_nulos, metodo_outliers)
        st.session_state["df_limpio"] = df_limpio
        st.session_state["resumen_limpieza"] = resumen

        st.subheader("Resumen de reparaciones realizadas")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Filas listas para usar",
            resumen["filas_finales"],
            delta=f"{resumen['filas_finales'] - resumen['filas_iniciales']} respecto al original",
            help="Registros limpios que quedaron después de quitar duplicados o filas incompletas."
        )
        m2.metric("Filas repetidas borradas", resumen["duplicados_eliminados"], help="Registros que estaban copiados exactamente igual más de una vez.")
        m3.metric("Columnas con vacíos rellenados", len(resumen["nulos_tratados"]), help="Columnas que tenían celdas en blanco y fueron reparadas.")
        m4.metric("Columnas con extremos corregidos", len(resumen["outliers_tratados"]), help="Columnas donde se detectaron números fuera de rango normal.")

        col_res1, col_res2 = st.columns([1, 1])
        with col_res1:
            with st.container(border=True):
                st.markdown("#### 🔍 Detalle paso a paso de lo que se limpió")
                
                st.markdown("**1. Nombres de columnas estandarizados:**")
                if resumen["columnas_renombradas"]:
                    st.caption("Se quitaron espacios y mayúsculas para facilitar el análisis:")
                    st.json(resumen["columnas_renombradas"])
                else:
                    st.write("✅ Los nombres ya estaban limpios.")

                st.markdown("**2. Celdas vacías (Nulos) reparadas:**")
                if resumen["nulos_tratados"]:
                    for col_n, detalle_n in resumen["nulos_tratados"].items():
                        st.write(f"- **{col_n}**: {detalle_n}")
                else:
                    st.write("✅ No se encontraron celdas vacías.")

                st.markdown("**3. Valores extremos (Outliers) corregidos:**")
                if resumen["outliers_tratados"]:
                    for col_o, detalle_o in resumen["outliers_tratados"].items():
                        st.write(f"- **{col_o}**: {detalle_o}")
                else:
                    st.write("✅ No se detectaron números anormales.")

        with col_res2:
            st.markdown("#### ✨ Tabla de Datos Limpios (Resultado Final)")
            st.caption("Observa cómo ya no hay valores 'None', filas repetidas ni números irreales:")
            st.dataframe(df_limpio, use_container_width=True)

# ==========================================
# PESTAÑA 3: ÁRBOL DE DECISIÓN
# ==========================================
with tab3:
    st.header("Paso 3: Crear y entrenar un Árbol de Decisión")

    if "df_limpio" not in st.session_state:
        st.warning("⚠️ Primero debes cargar un archivo en la Pestaña 1 para poder entrenar un modelo.")
    else:
        df_limpio = st.session_state["df_limpio"]
        st.write(
            "Un **Árbol de Decisión** aprende patrones de tus datos limpios haciendo preguntas paso a paso "
            "(como un diagrama de flujo) para adivinar un resultado final."
        )

        columnas_disponibles = df_limpio.columns.tolist()
        indice_objetivo_default = len(columnas_disponibles) - 1

        with st.container(border=True):
            col_conf1, col_conf2 = st.columns(2)
            with col_conf1:
                st.subheader("1. ¿Qué quieres predecir?")
                col_objetivo = st.selectbox(
                    "Variable Objetivo (Lo que el árbol intentará adivinar):",
                    options=columnas_disponibles,
                    index=indice_objetivo_default,
                    help="Elige una columna de categorías (por ejemplo: Si/No, Tipo de pago, Categoría)."
                )
                opciones_predictoras = [c for c in columnas_disponibles if c != col_objetivo]
                default_predictoras = [c for c in opciones_predictoras if 'id' not in c.split('_')]
                cols_predictoras = st.multiselect(
                    "Variables Predictoras (Pistas que usará el árbol para decidir):",
                    options=opciones_predictoras,
                    default=default_predictoras,
                    help="Son los datos de entrada (ej. edad, sueldo, compras) que ayudan a predecir el objetivo. Se recomienda no incluir columnas de ID."
                )

            with col_conf2:
                st.subheader("2. Ajusta cómo aprende el árbol")
                criterio = st.selectbox(
                    "Fórmula matemática para dividir las ramas:",
                    options=["gini", "entropy"],
                    format_func=lambda x: "Índice Gini (Más rápido y directo)" if x == "gini" else "Entropía / Ganancia de Información (Más detallado)",
                    help="Ambos miden qué tan bien una pregunta separa tus datos en grupos puros."
                )
                max_depth = st.slider(
                    "Profundidad máxima del árbol (Niveles de preguntas):",
                    min_value=1, max_value=10, value=3,
                    help="Un árbol de nivel 3 hace hasta 3 preguntas seguidas antes de dar un veredicto. Si es muy alto puede memorizar de más."
                )
                porcentaje_prueba = st.slider(
                    "Porcentaje de datos reservados para poner a prueba el árbol (%):",
                    min_value=10, max_value=50, value=25, step=5,
                    help="Si eliges 25%, el árbol estudiará con el 75% de las filas y luego le haremos un examen sorpresa con el 25% restante."
                )
                test_size = porcentaje_prueba / 100.0

            st.write("")
            if st.button("🚀 Entrenar Árbol de Decisión ahora", type="primary", use_container_width=True):
                exito_arbol, msj_arbol, res_arbol = entrenar_arbol_decision(
                    df_limpio, col_objetivo, cols_predictoras, criterio, max_depth, test_size
                )
                if not exito_arbol:
                    st.error(msj_arbol)
                else:
                    st.session_state["ultimo_arbol"] = res_arbol
                    st.success(f"¡{msj_arbol}! Revisa abajo qué tan bien aprendió.")

        # Mostrar resultados si ya se entrenó un árbol
        if "ultimo_arbol" in st.session_state:
            res = st.session_state["ultimo_arbol"]
            st.divider()
            st.subheader("🎯 Calificación del Modelo (Métricas de Evaluación)")
            st.caption(
                f"El árbol estudió con **{res['filas_entrenamiento']} filas** y fue evaluado con **{res['filas_prueba']} filas de prueba**. "
                "Mientras más cercano al 100%, mejor acertó:"
            )

            k1, k2, k3, k4 = st.columns(4)
            k1.metric(
                "Exactitud General (Accuracy)",
                f"{res['exactitud'] * 100:.1f}%",
                help="De todos los casos de prueba, ¿qué porcentaje acertó correctamente en total?"
            )
            k2.metric(
                "Precisión (Precision)",
                f"{res['precision'] * 100:.1f}%",
                help="Cuando el árbol afirma una categoría, ¿qué tan confiable o seguro es ese acierto?"
            )
            k3.metric(
                "Sensibilidad (Recall)",
                f"{res['recall'] * 100:.1f}%",
                help="De los casos reales que existían, ¿cuántos logró detectar sin que se le escaparan?"
            )
            k4.metric(
                "Filas Estudio / Examen",
                f"{res['filas_entrenamiento']} / {res['filas_prueba']}",
                help="División de registros usada para entrenar vs evaluar."
            )

            col_vis1, col_vis2 = st.columns([3, 2])
            with col_vis1:
                with st.container(border=True):
                    st.subheader("🌳 Mapa Visual del Árbol")
                    st.caption(
                        "Lee de arriba hacia abajo: cada caja muestra la condición evaluada. "
                        "Si se cumple vas a la rama izquierda; si no, a la derecha. **`class`** indica la decisión final."
                    )
                    st.pyplot(res["figura_arbol"])

            with col_vis2:
                with st.container(border=True):
                    st.subheader("🎯 Matriz de Confusión (Aciertos vs Errores)")
                    st.caption(
                        "Compara la realidad (eje vertical) contra lo que predijo el árbol (eje horizontal). "
                        "Los cuadros en la **diagonal principal** son aciertos perfectos."
                    )
                    fig_cm = px.imshow(
                        res["matriz_confusion"],
                        labels=dict(x="Lo que predijo el Árbol", y="Lo que ocurrió en Realidad", color="Casos"),
                        x=res["clases"],
                        y=res["clases"],
                        text_auto=True,
                        color_continuous_scale="Blues"
                    )
                    st.plotly_chart(fig_cm, use_container_width=True)

            # Guardar modelo entrenado
            with st.container(border=True):
                st.subheader("💾 Guardar este modelo para compararlo después")
                st.write("Ponle un nombre descriptivo para guardarlo en tu historial y compararlo en la **Pestaña 4**:")
                c_save1, c_save2 = st.columns([3, 1])
                nombre_modelo = c_save1.text_input(
                    "Nombre del modelo:",
                    placeholder="Ej: Árbol Gini Nivel 3 - Clientes",
                    label_visibility="collapsed"
                )
                if c_save2.button("💾 Guardar Modelo", use_container_width=True):
                    reg = guardar_modelo(nombre_modelo, res, st.session_state.get("nombre_dataset", "dataset.csv"))
                    st.success(f"✅ Modelo **'{reg['nombre']}'** guardado. Ve a la Pestaña 4 para compararlo.")

# ==========================================
# PESTAÑA 4: GESTIÓN Y COMPARACIÓN DE MODELOS
# ==========================================
with tab4:
    st.header("Paso 4: Historial y Comparador de Modelos Guardados")
    st.write(
        "Aquí puedes revisar todos los árboles que has entrenado, comparar sus puntajes en un gráfico "
        "para elegir el mejor y borrar los que ya no necesites."
    )

    modelos_guardados = listar_modelos_guardados()

    if not modelos_guardados:
        st.info("📭 Aún no tienes modelos guardados. Entrena un árbol en la **Pestaña 3** y presiona el botón **Guardar Modelo**.")
    else:
        df_modelos = pd.DataFrame(modelos_guardados)
        
        st.subheader("📋 Tabla comparativa de modelos")
        df_mostrar = df_modelos[[
            "id", "nombre", "fecha", "dataset", "variable_objetivo",
            "criterio", "profundidad_max", "division_prueba",
            "exactitud", "precision", "recall"
        ]].rename(columns={
            "id": "ID",
            "nombre": "Nombre del Modelo",
            "fecha": "Fecha",
            "dataset": "Archivo CSV",
            "variable_objetivo": "Variable Predicha",
            "criterio": "Criterio",
            "profundidad_max": "Profundidad",
            "division_prueba": "% Prueba",
            "exactitud": "Exactitud (0-1)",
            "precision": "Precisión (0-1)",
            "recall": "Recall (0-1)"
        })
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

        st.subheader("📊 Gráfico comparativo: ¿Cuál modelo rinde mejor?")
        fig_comp = px.bar(
            df_modelos,
            x="nombre",
            y=["exactitud", "precision", "recall"],
            barmode="group",
            labels={"value": "Puntaje (de 0.0 a 1.0)", "nombre": "Nombre del Modelo", "variable": "Métrica Evaluada"},
            color_discrete_sequence=["#3b82f6", "#10b981", "#f59e0b"]
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        st.divider()
        with st.container(border=True):
            st.subheader("🗑️ Eliminar modelos antiguos")
            col_del1, col_del2 = st.columns([3, 1])
            id_a_eliminar = col_del1.selectbox(
                "Elige el modelo que deseas borrar del registro:",
                options=[m["id"] for m in modelos_guardados],
                format_func=lambda x: next((f"{m['nombre']} (Fecha: {m['fecha']} | Exactitud: {m['exactitud']*100:.0f}%)" for m in modelos_guardados if m["id"] == x), x)
            )
            if col_del2.button("🗑️ Eliminar Modelo", type="secondary", use_container_width=True):
                eliminar_modelo_guardado(id_a_eliminar)
                st.rerun()