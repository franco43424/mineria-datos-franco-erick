"""
Vista 7 - Informe (RF5).
Genera el informe HTML con analisis.informe, lo muestra en vista previa y permite descargarlo.
"""

import os

import streamlit as st
import streamlit.components.v1 as components

from analisis.arbol_decision import listar_modelos_guardados
from analisis.dashboard import clasificar_columnas
from analisis.informe import generar_informe_html


def mostrar():
    """Dibuja el contenido de la pestaña."""
    st.markdown('<div class="section-title">Generación del informe final</div>', unsafe_allow_html=True)

    if "df_limpio" not in st.session_state:
        st.warning("Debes procesar los datos en las pestañas **① Carga** y **② Limpieza** antes de generar un informe.")
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
