"""
Módulo: informe.py
Propósito: RF5 - Generación del Informe final en formato HTML.
Reúne en un solo documento: resumen de los datos, limpieza realizada, modelos de árbol de decisión,
reglas de asociación y conclusiones (automáticas + escritas por el usuario).

El informe es un único archivo .html autocontenido: los gráficos se generan con Matplotlib y se
incrustan como imágenes (base64), por lo que se abre sin internet en cualquier navegador.
Para obtener un PDF basta con abrirlo y usar "Imprimir > Guardar como PDF" (el CSS ya está preparado).
"""

import io
import base64
import html
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Backend sin ventana: necesario para generar imágenes dentro de un servidor web
import matplotlib.pyplot as plt

from analisis.dashboard import matriz_correlacion, correlaciones_destacadas, interpretar_correlacion

# Paleta coherente con la interfaz (estilos.css)
COLOR_PRINCIPAL = "#4F46E5"
COLORES = ["#4F46E5", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]


# =====================================================================
# Utilidades
# =====================================================================
def _figura_a_base64(fig):
    """Convierte una figura de Matplotlib en una etiqueta <img> incrustada (base64)."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    codigo = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f'<img src="data:image/png;base64,{codigo}" alt="gráfico">'


def _tabla_html(df, index=False, max_filas=None):
    """Convierte un DataFrame en tabla HTML con el estilo del informe."""
    if df is None or df.empty:
        return "<p class='nota'>Sin datos para mostrar.</p>"
    if max_filas:
        df = df.head(max_filas)
    return df.to_html(index=index, classes="tabla", border=0, escape=True)


def _e(texto):
    """Escapa texto para insertarlo de forma segura en el HTML."""
    return html.escape(str(texto))


# =====================================================================
# Gráficos del informe
# =====================================================================
def _grafico_objetivo(df, col_objetivo):
    conteo = df[col_objetivo].astype(str).value_counts()
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.bar(conteo.index, conteo.values, color=COLORES[:len(conteo)])
    for i, v in enumerate(conteo.values):
        ax.text(i, v, f"{v} ({100 * v / conteo.sum():.0f}%)", ha="center", va="bottom", fontsize=9)
    ax.set_title(f"Distribución de '{col_objetivo}'")
    ax.set_ylabel("Registros")
    ax.spines[["top", "right"]].set_visible(False)
    return _figura_a_base64(fig)


def _grafico_correlacion(matriz):
    fig, ax = plt.subplots(figsize=(6, 4.8))
    im = ax.imshow(matriz.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(matriz.columns)), matriz.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(matriz.columns)), matriz.columns, fontsize=8)
    for i in range(len(matriz)):
        for j in range(len(matriz)):
            ax.text(j, i, f"{matriz.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7,
                    color="white" if abs(matriz.iloc[i, j]) > 0.5 else "black")
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Matriz de correlación (Pearson)")
    return _figura_a_base64(fig)


def _grafico_modelos(df_modelos):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    x = np.arange(len(df_modelos))
    ancho = 0.26
    for k, (metrica, nombre) in enumerate([("exactitud", "Exactitud"), ("precision", "Precisión"), ("recall", "Recall")]):
        ax.bar(x + (k - 1) * ancho, df_modelos[metrica], ancho, label=nombre, color=COLORES[k])
    ax.set_xticks(x, df_modelos["nombre"], rotation=20, ha="right", fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Puntaje (0-1)")
    ax.legend(fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=3)
    ax.set_title("Comparativa de modelos guardados")
    ax.spines[["top", "right"]].set_visible(False)
    return _figura_a_base64(fig)


def _grafico_reglas(tabla, top=10):
    datos = tabla.sort_values("lift", ascending=False).head(top).iloc[::-1]
    etiquetas = [f"{a} → {c}" for a, c in zip(datos["antecedente"], datos["consecuente"])]
    etiquetas = [e if len(e) <= 70 else e[:67] + "..." for e in etiquetas]
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(datos) + 1))
    ax.barh(etiquetas, datos["lift"], color=COLOR_PRINCIPAL)
    ax.axvline(1, color="#94A3B8", linestyle="--", linewidth=1)
    ax.set_xlabel("Lift (1 = independencia)")
    ax.set_title(f"Top {len(datos)} reglas por lift")
    ax.tick_params(axis="y", labelsize=7.5)
    ax.spines[["top", "right"]].set_visible(False)
    return _figura_a_base64(fig)


# =====================================================================
# Conclusiones automáticas
# =====================================================================
def generar_conclusiones(df_limpio, resumen_limpieza, modelos, tabla_reglas, col_objetivo):
    """
    Redacta conclusiones a partir de los resultados obtenidos.
    Son un punto de partida: el usuario puede añadir su propia interpretación en la interfaz.
    """
    conclusiones = []

    # Calidad de datos
    perdidas = resumen_limpieza["filas_iniciales"] - resumen_limpieza["filas_finales"]
    conclusiones.append(
        f"El dataset pasó de {resumen_limpieza['filas_iniciales']} a {resumen_limpieza['filas_finales']} registros "
        f"tras la limpieza ({perdidas} filas descartadas, {resumen_limpieza['duplicados_eliminados']} por duplicidad). "
        f"Se trataron valores nulos en {len(resumen_limpieza['nulos_tratados'])} columnas y valores atípicos en "
        f"{len(resumen_limpieza['outliers_tratados'])} columnas."
    )

    # Variable objetivo
    if col_objetivo and col_objetivo in df_limpio.columns:
        frec = df_limpio[col_objetivo].astype(str).value_counts(normalize=True)
        conclusiones.append(
            f"En la variable objetivo '{col_objetivo}' predomina la clase '{frec.index[0]}' "
            f"({100 * frec.iloc[0]:.1f}% de los registros)."
            + (" Las clases están desbalanceadas, por lo que conviene revisar precisión y recall además de la exactitud."
               if frec.iloc[0] >= 0.7 else "")
        )

    # Correlaciones
    pares = correlaciones_destacadas(matriz_correlacion(df_limpio), top=1)
    if pares:
        a, b, r = pares[0]
        conclusiones.append(
            f"La relación más marcada entre variables numéricas es entre '{a}' y '{b}' "
            f"(r = {r:.2f}, correlación {interpretar_correlacion(r)})."
        )

    # Modelos
    if modelos:
        df_m = pd.DataFrame(modelos)
        mejor = df_m.sort_values(["exactitud", "recall"], ascending=False).iloc[0]
        conclusiones.append(
            f"De {len(df_m)} modelo(s) de árbol de decisión guardado(s), el de mejor desempeño es "
            f"'{mejor['nombre']}' (criterio {mejor['criterio']}, profundidad {mejor['profundidad_max']}), con "
            f"exactitud {100 * mejor['exactitud']:.1f}%, precisión {100 * mejor['precision']:.1f}% "
            f"y recall {100 * mejor['recall']:.1f}%."
        )
        if mejor["exactitud"] >= 0.99:
            conclusiones.append(
                "Una exactitud cercana al 100% puede indicar un conjunto de prueba muy pequeño o una variable "
                "que 'delata' la respuesta; se recomienda validar con más datos."
            )

    # Reglas
    if tabla_reglas is not None and not tabla_reglas.empty:
        mejor_r = tabla_reglas.sort_values("lift", ascending=False).iloc[0]
        conclusiones.append(
            f"Se obtuvieron {len(tabla_reglas)} reglas de asociación. La más fuerte es "
            f"«{mejor_r['antecedente']} → {mejor_r['consecuente']}» (lift {mejor_r['lift']:.2f}, "
            f"confianza {100 * mejor_r['confianza']:.0f}%): cuando se cumple el antecedente, el consecuente es "
            f"{mejor_r['lift']:.1f} veces más probable que en el total de los datos."
        )
        if col_objetivo:
            relacionadas = tabla_reglas[tabla_reglas["consecuente"].str.contains(f"{col_objetivo}=", regex=False)]
            if not relacionadas.empty:
                r = relacionadas.sort_values(["confianza", "lift"], ascending=False).iloc[0]
                conclusiones.append(
                    f"Respecto de '{col_objetivo}', el perfil «{r['antecedente']}» conduce a "
                    f"«{r['consecuente']}» con {100 * r['confianza']:.0f}% de confianza."
                )
    return conclusiones


# =====================================================================
# Informe completo
# =====================================================================
def generar_informe_html(nombre_dataset, meta, df_original, df_limpio, resumen_limpieza,
                         modelos=None, ultimo_arbol=None, resultado_reglas=None, tabla_reglas=None,
                         col_objetivo=None, conclusiones_usuario="", titulo="Informe de Minería de Datos",
                         autores="Franco Fajardo y Erick Mamani"):
    """
    RF5: Construye el informe completo como texto HTML.

    Parámetros principales:
        meta (dict): metadatos de la carga (validador.py).
        resumen_limpieza (dict): resumen devuelto por limpieza.py.
        modelos (list): registros de modelos guardados (arbol_decision.listar_modelos_guardados()).
        ultimo_arbol (dict): resultado del último entrenamiento (opcional, incluye la figura del árbol).
        resultado_reglas (dict) / tabla_reglas (DataFrame): resultado del módulo de asociación (opcional).
        conclusiones_usuario (str): texto libre escrito por el usuario en la interfaz.

    Retorna:
        str: documento HTML completo.
    """
    modelos = modelos or []
    secciones = []
    fecha = datetime.now().strftime("%d-%m-%Y %H:%M")

    # ---------- 1. Resumen de datos ----------
    tipos = pd.DataFrame({
        "Columna": df_limpio.columns,
        "Tipo": [str(t) for t in df_limpio.dtypes],
        "Valores distintos": [df_limpio[c].nunique() for c in df_limpio.columns],
        "Ejemplo": [str(df_limpio[c].iloc[0]) if len(df_limpio) else "" for c in df_limpio.columns],
    })
    bloque = f"""
    <div class="kpis">
        <div class="kpi"><span>{_e(meta.get('filas', len(df_original)))}</span>Filas originales</div>
        <div class="kpi"><span>{len(df_limpio)}</span>Filas tras limpieza</div>
        <div class="kpi"><span>{df_limpio.shape[1]}</span>Variables</div>
        <div class="kpi"><span>{_e(meta.get('tamano_kb', ''))}</span>Tamaño</div>
    </div>
    <p>Archivo <b>{_e(nombre_dataset)}</b> · codificación {_e(meta.get('codificacion', ''))} ·
       separador {_e(meta.get('separador', ''))}.</p>
    <h3>Estructura del dataset limpio</h3>
    {_tabla_html(tipos)}
    """
    from analisis.dashboard import estadisticas_descriptivas
    desc = estadisticas_descriptivas(df_limpio)
    if not desc.empty:
        bloque += f"<h3>Estadísticas descriptivas</h3>{_tabla_html(desc, index=True)}"
    graficos = ""
    if col_objetivo and col_objetivo in df_limpio.columns:
        graficos += f"<div>{_grafico_objetivo(df_limpio, col_objetivo)}</div>"
    matriz = matriz_correlacion(df_limpio)
    if not matriz.empty:
        graficos += f"<div>{_grafico_correlacion(matriz)}</div>"
    if graficos:
        bloque += f"<div class='grid'>{graficos}</div>"
    secciones.append(("1. Resumen de los datos", bloque))

    # ---------- 2. Limpieza ----------
    filas_limp = [
        ("Duplicados eliminados", resumen_limpieza["duplicados_eliminados"]),
        ("Columnas renombradas (snake_case)", len(resumen_limpieza["columnas_renombradas"])),
        ("Columnas con tipo corregido", len(resumen_limpieza.get("tipos_corregidos", []))),
        ("Columnas con nulos tratados", len(resumen_limpieza["nulos_tratados"])),
        ("Columnas con outliers tratados", len(resumen_limpieza["outliers_tratados"])),
        ("Registros finales", resumen_limpieza["filas_finales"]),
    ]
    bloque = _tabla_html(pd.DataFrame(filas_limp, columns=["Operación", "Cantidad"]))
    detalle = []
    for col, txt in resumen_limpieza["nulos_tratados"].items():
        detalle.append(("Valores nulos", col, txt))
    for col, txt in resumen_limpieza["outliers_tratados"].items():
        detalle.append(("Outliers (IQR)", col, txt))
    for txt in resumen_limpieza.get("tipos_corregidos", []):
        detalle.append(("Tipo de dato", txt.split(" ")[0], txt))
    if detalle:
        bloque += "<h3>Detalle por columna</h3>" + _tabla_html(pd.DataFrame(detalle, columns=["Tratamiento", "Columna", "Detalle"]))
    secciones.append(("2. Limpieza automática", bloque))

    # ---------- 3. Árbol de decisión ----------
    bloque = ""
    if ultimo_arbol:
        bloque += f"""
        <h3>Último modelo entrenado</h3>
        <p>Objetivo <b>{_e(ultimo_arbol['col_objetivo'])}</b> · predictoras: {_e(', '.join(ultimo_arbol['cols_predictoras']))} ·
           criterio {_e(ultimo_arbol['criterio'])} · profundidad {ultimo_arbol['max_depth']} ·
           prueba {int(ultimo_arbol['test_size'] * 100)}% ({ultimo_arbol['filas_prueba']} registros).</p>
        <div class="kpis">
            <div class="kpi"><span>{100 * ultimo_arbol['exactitud']:.1f}%</span>Exactitud</div>
            <div class="kpi"><span>{100 * ultimo_arbol['precision']:.1f}%</span>Precisión</div>
            <div class="kpi"><span>{100 * ultimo_arbol['recall']:.1f}%</span>Recall</div>
        </div>
        """
        mc = pd.DataFrame(ultimo_arbol["matriz_confusion"],
                          index=[f"Real: {c}" for c in ultimo_arbol["clases"]],
                          columns=[f"Pred: {c}" for c in ultimo_arbol["clases"]])
        bloque += f"<h3>Matriz de confusión</h3>{_tabla_html(mc, index=True)}"
        if ultimo_arbol.get("figura_arbol") is not None:
            buffer = io.BytesIO()
            ultimo_arbol["figura_arbol"].savefig(buffer, format="png", bbox_inches="tight", dpi=90)
            codigo = base64.b64encode(buffer.getvalue()).decode("ascii")
            bloque += f'<h3>Diagrama del árbol</h3><img src="data:image/png;base64,{codigo}" alt="árbol">'
    if modelos:
        df_m = pd.DataFrame(modelos)
        tabla_m = df_m[["nombre", "fecha", "variable_objetivo", "criterio", "profundidad_max",
                        "division_prueba", "exactitud", "precision", "recall"]].rename(columns={
            "nombre": "Modelo", "fecha": "Fecha", "variable_objetivo": "Objetivo", "criterio": "Criterio",
            "profundidad_max": "Prof.", "division_prueba": "Test", "exactitud": "Exactitud",
            "precision": "Precisión", "recall": "Recall"})
        bloque += f"<h3>Modelos guardados</h3>{_tabla_html(tabla_m)}{_grafico_modelos(df_m)}"
    if not bloque:
        bloque = "<p class='nota'>No se entrenaron ni guardaron modelos de árbol de decisión en esta sesión.</p>"
    secciones.append(("3. Árbol de decisión", bloque))

    # ---------- 4. Reglas de asociación ----------
    if tabla_reglas is not None and not tabla_reglas.empty:
        parametros = ""
        if resultado_reglas:
            parametros = (f"<p>Algoritmo <b>{_e(resultado_reglas['algoritmo'])}</b> · soporte mínimo "
                          f"{resultado_reglas['min_soporte']:.0%} · confianza mínima {resultado_reglas['min_confianza']:.0%} · "
                          f"columnas: {_e(', '.join(resultado_reglas['columnas']))} · "
                          f"{resultado_reglas['n_transacciones']} transacciones.</p>")
        tabla_top = tabla_reglas.sort_values("lift", ascending=False).head(15).rename(columns={
            "antecedente": "Antecedente (SI)", "consecuente": "Consecuente (ENTONCES)",
            "soporte": "Soporte", "confianza": "Confianza", "lift": "Lift", "n_items": "Ítems"})
        bloque = (parametros + f"<p>Total de reglas: <b>{len(tabla_reglas)}</b>. Se muestran las 15 de mayor lift.</p>"
                  + _tabla_html(tabla_top) + _grafico_reglas(tabla_reglas))
    else:
        bloque = "<p class='nota'>No se generaron reglas de asociación en esta sesión.</p>"
    secciones.append(("4. Reglas de asociación", bloque))

    # ---------- 5. Conclusiones ----------
    automaticas = generar_conclusiones(df_limpio, resumen_limpieza, modelos, tabla_reglas, col_objetivo)
    bloque = "<h3>Conclusiones automáticas</h3><ul>" + "".join(f"<li>{_e(c)}</li>" for c in automaticas) + "</ul>"
    if conclusiones_usuario.strip():
        parrafos = "".join(f"<p>{_e(p)}</p>" for p in conclusiones_usuario.strip().split("\n") if p.strip())
        bloque += f"<h3>Conclusiones del equipo</h3>{parrafos}"
    secciones.append(("5. Conclusiones", bloque))

    # ---------- Ensamblado ----------
    indice = "".join(f"<li>{_e(t)}</li>" for t, _ in secciones)
    cuerpo = "".join(f"<section><h2>{_e(t)}</h2>{b}</section>" for t, b in secciones)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(titulo)}</title>
<style>
    body {{ font-family: "Segoe UI", Roboto, Arial, sans-serif; color: #1E293B; background: #F1F5F9; margin: 0; }}
    .hoja {{ max-width: 980px; margin: 0 auto; background: #FFFFFF; padding: 40px 48px; }}
    header {{ background: linear-gradient(135deg, #4F46E5, #0EA5E9); color: #FFFFFF; padding: 28px 32px; border-radius: 12px; }}
    header h1 {{ margin: 0 0 6px; font-size: 26px; }}
    header p {{ margin: 0; opacity: .9; }}
    h2 {{ color: #4F46E5; border-bottom: 2px solid #E2E8F0; padding-bottom: 6px; margin-top: 36px; }}
    h3 {{ font-size: 15px; margin: 22px 0 8px; color: #334155; }}
    .tabla {{ border-collapse: collapse; width: 100%; font-size: 12.5px; margin: 8px 0 14px; }}
    .tabla th {{ background: #EEF2FF; text-align: left; padding: 7px 9px; }}
    .tabla td {{ padding: 6px 9px; border-bottom: 1px solid #E2E8F0; }}
    .kpis {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 12px 0; }}
    .kpi {{ flex: 1; min-width: 130px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px; font-size: 12px; color: #64748B; }}
    .kpi span {{ display: block; font-size: 22px; font-weight: 700; color: #1E293B; }}
    .grid {{ display: flex; gap: 16px; flex-wrap: wrap; align-items: flex-start; }}
    .grid > div {{ flex: 1; min-width: 300px; }}
    img {{ max-width: 100%; height: auto; }}
    .nota {{ color: #64748B; font-style: italic; }}
    .indice ul {{ list-style: none; padding-left: 0; }}
    .indice {{ background: #F8FAFC; border-radius: 10px; padding: 12px 28px; margin-top: 18px; }}
    footer {{ margin-top: 40px; font-size: 12px; color: #94A3B8; text-align: center; }}
    @media print {{
        body {{ background: #FFFFFF; }}
        .hoja {{ padding: 0; }}
        section {{ page-break-inside: avoid; }}
        header {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    }}
</style>
</head>
<body>
<div class="hoja">
    <header>
        <h1>{_e(titulo)}</h1>
        <p>Dataset: {_e(nombre_dataset)} · Generado el {fecha} · {_e(autores)}</p>
    </header>
    <div class="indice"><b>Contenido</b><ul>{indice}</ul></div>
    {cuerpo}
    <footer>Informe generado automáticamente por la Plataforma de Minería de Datos.</footer>
</div>
</body>
</html>"""
