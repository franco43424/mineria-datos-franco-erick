"""
Módulo: dashboard.py
Propósito: RF6 - Cálculo de los datos que alimentan el Dashboard interactivo.
Siguiendo la arquitectura por capas, aquí solo se hacen los cálculos (filtros, estadísticas,
correlaciones, frecuencias). La capa web (app.py) se limita a dibujar los gráficos con Plotly.
"""

import pandas as pd
import numpy as np

from analisis.config import es_columna_id as _es_id


def clasificar_columnas(df, max_categorias=25):
    """
    Separa las columnas en numéricas y categóricas para decidir qué gráfico usar en cada una.
    - Se excluyen columnas ID.
    - Una columna numérica con pocos valores distintos (ej. 0/1) también se ofrece como categórica.
    - Las categóricas con demasiados valores distintos (texto libre) se descartan del filtrado.

    Retorna:
        tuple: (lista_numericas, lista_categoricas)
    """
    numericas, categoricas = [], []
    for col in df.columns:
        if _es_id(col):
            continue
        n_unicos = df[col].nunique(dropna=True)
        if pd.api.types.is_numeric_dtype(df[col]):
            numericas.append(col)
            if n_unicos <= 10:
                categoricas.append(col)
        elif n_unicos <= max_categorias:
            categoricas.append(col)
    return numericas, categoricas


def aplicar_filtros(df, filtros):
    """
    Aplica los filtros dinámicos elegidos por el usuario.

    Parámetros:
        df (DataFrame): Dataset limpio.
        filtros (dict): {columna: ("valores", [lista de categorías permitidas])}
                        o {columna: ("rango", (minimo, maximo))}

    Retorna:
        DataFrame filtrado.
    """
    mascara = pd.Series(True, index=df.index)
    for col, (tipo, valor) in filtros.items():
        if col not in df.columns:
            continue
        if tipo == "valores":
            mascara &= df[col].isin(valor)
        elif tipo == "rango":
            minimo, maximo = valor
            mascara &= df[col].between(minimo, maximo)
    return df[mascara]


def calcular_kpis(df_filtrado, df_total, col_objetivo=None):
    """
    Indicadores rápidos para las tarjetas superiores del dashboard.
    Si hay variable objetivo, calcula la clase más frecuente y su porcentaje.
    """
    kpis = {
        "registros": len(df_filtrado),
        "porcentaje_del_total": round(100 * len(df_filtrado) / len(df_total), 1) if len(df_total) else 0,
        "variables": df_filtrado.shape[1],
    }
    if col_objetivo and col_objetivo in df_filtrado.columns and len(df_filtrado):
        frecuencias = df_filtrado[col_objetivo].value_counts(normalize=True)
        kpis["clase_mayoritaria"] = str(frecuencias.index[0])
        kpis["porcentaje_clase"] = round(100 * frecuencias.iloc[0], 1)
    return kpis


def matriz_correlacion(df, metodo="pearson"):
    """
    Calcula la matriz de correlación entre variables numéricas (sin IDs).
    metodo: 'pearson' (relación lineal) o 'spearman' (relación monótona, robusta a outliers).
    Retorna un DataFrame vacío si hay menos de 2 columnas numéricas.
    """
    numericas = [c for c in df.select_dtypes(include=[np.number]).columns if not _es_id(c)]
    # Se descartan columnas constantes: su correlación no está definida
    numericas = [c for c in numericas if df[c].nunique() > 1]
    if len(numericas) < 2:
        return pd.DataFrame()
    return df[numericas].corr(method=metodo).round(3)


def correlaciones_destacadas(matriz, top=5):
    """
    Lista los pares de variables con correlación más fuerte (en valor absoluto),
    útil para el texto interpretativo del dashboard y del informe.
    """
    if matriz.empty:
        return []
    pares = []
    cols = matriz.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pares.append((cols[i], cols[j], float(matriz.iloc[i, j])))
    pares.sort(key=lambda p: abs(p[2]), reverse=True)
    return pares[:top]


def interpretar_correlacion(r):
    """Traduce un coeficiente de correlación a palabras."""
    fuerza = abs(r)
    if fuerza >= 0.7:
        nivel = "fuerte"
    elif fuerza >= 0.4:
        nivel = "moderada"
    elif fuerza >= 0.2:
        nivel = "débil"
    else:
        nivel = "casi nula"
    sentido = "positiva" if r > 0 else "negativa"
    return f"{nivel} {sentido}" if nivel != "casi nula" else nivel


def tabla_frecuencias(df, columna, col_objetivo=None):
    """
    Cuenta registros por categoría. Si se indica variable objetivo, desglosa por clase
    (ej. cuántos clientes de cada plan abandonaron y cuántos no).
    """
    if col_objetivo and col_objetivo in df.columns and col_objetivo != columna:
        tabla = df.groupby([columna, col_objetivo]).size().reset_index(name="registros")
    else:
        tabla = df[columna].value_counts().reset_index()
        tabla.columns = [columna, "registros"]
    return tabla


def estadisticas_descriptivas(df):
    """Resumen estadístico (media, mediana, desviación, mínimo, máximo) de las variables numéricas."""
    numericas = [c for c in df.select_dtypes(include=[np.number]).columns if not _es_id(c)]
    if not numericas:
        return pd.DataFrame()
    desc = df[numericas].agg(["mean", "median", "std", "min", "max"]).T
    desc.columns = ["Media", "Mediana", "Desv. estándar", "Mínimo", "Máximo"]
    return desc.round(2)
