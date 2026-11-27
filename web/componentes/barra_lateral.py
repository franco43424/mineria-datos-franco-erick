"""
Componente: barra_lateral.py
Propósito: Panel de control lateral con el estado de cada etapa del flujo de trabajo.
Se dibuja al final de app.py para que refleje lo que ocurrió en las pestañas durante esa ejecución.
"""

import streamlit as st


def mostrar_barra_lateral(contenedor):
    """Dibuja el estado del pipeline dentro del contenedor reservado en la barra lateral."""
    with contenedor.container():
        st.markdown("### Panel de Control")
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
