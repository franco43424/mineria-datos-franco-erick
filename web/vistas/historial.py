"""
Vista 4 - Historial y Comparativa de modelos (gestión del RF3).
Lista, compara y elimina los árboles guardados en storage/modelos.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from componentes.estilos import PALETA

from analisis.arbol_decision import listar_modelos_guardados, eliminar_modelo_guardado


def mostrar():
    """Dibuja el contenido de la pestaña."""
    st.markdown('<div class="section-title">Registro histórico y evaluación comparativa</div>', unsafe_allow_html=True)
    st.write(
        "Consulta los metadatos de los modelos previamente almacenados, contrasta su rendimiento "
        "mediante gráficos comparativos y gestiona los archivos persistentes."
    )

    # Lectura del archivo JSON de registro desde el backend
    modelos_guardados = listar_modelos_guardados()

    if not modelos_guardados:
        st.info("No existen modelos registrados actualmente. Entrena y guarda un modelo en la pestaña **③ Árbol de Decisión** para habilitar la comparativa.")
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
                color_discrete_sequence=PALETA
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
