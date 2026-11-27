"""
Vista 6 - Dashboard interactivo (RF6).
Los cálculos (filtros, KPIs, correlaciones) vienen de analisis.dashboard; aquí solo se dibujan con Plotly.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from analisis.arbol_decision import listar_modelos_guardados
from analisis.dashboard import (
    clasificar_columnas,
    aplicar_filtros,
    calcular_kpis,
    matriz_correlacion,
    correlaciones_destacadas,
    interpretar_correlacion,
    estadisticas_descriptivas,
)


def mostrar():
    """Dibuja el contenido de la pestaña."""
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
