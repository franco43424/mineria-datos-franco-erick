"""
Vista 5 - Reglas de Asociación (RF4).
Genera reglas con analisis.asociacion, permite filtrarlas, ordenarlas y gestionar los resultados guardados.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from analisis.config import es_columna_id
from analisis.dashboard import clasificar_columnas
from analisis.asociacion import (
    generar_reglas_asociacion,
    filtrar_reglas,
    guardar_reglas,
    listar_reglas_guardadas,
    cargar_tabla_reglas,
    eliminar_reglas_guardadas,
)


def mostrar():
    """Dibuja el contenido de la pestaña."""
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

        columnas_asoc = [c for c in df_limpio.columns if not es_columna_id(c)]
        _, categoricas_asoc = clasificar_columnas(df_limpio)
        default_asoc = [c for c in categoricas_asoc if c in columnas_asoc][:15] or columnas_asoc[:4]

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
                solo_presentes = st.toggle(
                    "Ignorar valores de ausencia (No / 0)",
                    value=False,
                    help="Actívalo en datos tipo canasta (ej. compras de supermercado con columnas Si/No): "
                         "así solo se buscan productos que SÍ se compran juntos, y no reglas como 'pan=No → leche=No'."
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
                        df_limpio, cols_asoc, min_soporte, min_confianza, algoritmo, n_intervalos, max_longitud, solo_presentes
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
