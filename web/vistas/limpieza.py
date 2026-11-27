"""
Vista 2 - Preprocesamiento y Limpieza (RF2).
Ejecuta analisis.limpieza con las estrategias elegidas y muestra el registro de cambios.
"""

import streamlit as st

from analisis.limpieza import limpiar_dataset_automatico


def mostrar():
    """Dibuja el contenido de la pestaña."""
    st.markdown('<div class="section-title">Preprocesamiento y reparación automatizada</div>', unsafe_allow_html=True)

    if "df_original" not in st.session_state:
        st.warning("Debes importar un archivo CSV válido en la pestaña **① Carga** antes de continuar.")
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
