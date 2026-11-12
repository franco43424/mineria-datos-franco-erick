"""
Módulo: limpieza.py
Propósito: Realizar la fase de Preparación de Datos (Data Preparation).
Se encarga de estandarizar formatos, corregir tipos de datos, manejar valores faltantes (nulos) 
y mitigar el impacto de valores atípicos (outliers) para asegurar la calidad de los datos 
antes de alimentar los modelos de Machine Learning.
"""

import pandas as pd
import numpy as np
import unicodedata
import re

def normalizar_texto_columna(nombre):
    """
    Estandariza los nombres de las columnas para evitar errores de sintaxis y facilitar su manipulación.
    Convierte formatos inconsistentes (ej. 'Ingreso Mensual ') a un formato estandarizado ('ingreso_mensual')
    sin tildes, sin espacios y en minúsculas (formato snake_case).
    
    Parámetros:
        nombre (str): Nombre original de la columna.
    Retorna:
        str: Nombre de la columna normalizado.
    """
    texto = str(nombre).strip().lower()
    # Descompone los caracteres (NFD) para separar las letras de sus acentos/tildes
    # y luego filtra eliminando los caracteres diacríticos (categoría 'Mn')
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Reemplaza cualquier secuencia de caracteres que no sean letras o números por un guion bajo '_'
    texto = re.sub(r'[^a-z0-9]+', '_', texto)
    return texto.strip('_')

def limpiar_dataset_automatico(df_original, metodo_nulos="imputar", metodo_outliers="acotar"):
    """
    RF2: Ejecuta un pipeline de limpieza automática del DataFrame aplicando técnicas 
    clásicas de minería de datos.
    
    Parámetros:
        df_original (DataFrame): El conjunto de datos crudo (raw data).
        metodo_nulos (str): Estrategia para manejar datos faltantes ('imputar' o 'eliminar').
        metodo_outliers (str): Estrategia para valores atípicos ('acotar', 'mediana' o 'eliminar').
        
    Retorna:
        tuple: (df_limpio (DataFrame), resumen_limpieza (dict con las estadísticas del proceso))
    """
    # Se trabaja sobre una copia para no alterar el DataFrame original en memoria
    df = df_original.copy()
    filas_iniciales = len(df)
    
    # Diccionario para registrar cada modificación, útil para auditoría y visualización en Streamlit
    resumen = {
        "filas_iniciales": filas_iniciales,
        "columnas_renombradas": {},
        "duplicados_eliminados": 0,
        "tipos_corregidos": [],
        "nulos_tratados": {},
        "outliers_tratados": {},
        "filas_finales": 0
    }

    # 1. Normalización de nombres de columnas
    # Crucial en minería de datos para evitar que 'Edad' y 'edad ' sean tratadas de forma inconsistente
    nuevas_columnas = {}
    for col in df.columns:
        col_norm = normalizar_texto_columna(col)
        if col != col_norm:
            resumen["columnas_renombradas"][col] = col_norm
        nuevas_columnas[col] = col_norm
    df.rename(columns=nuevas_columnas, inplace=True)

    # 2. Eliminación de duplicados
    # Los datos duplicados introducen sesgos en el entrenamiento, dando un "peso" artificial a ciertos patrones
    duplicados = int(df.duplicated().sum())
    if duplicados > 0:
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
    resumen["duplicados_eliminados"] = duplicados

    # 3. Corrección de tipos de datos (Data Type Casting)
    # Los algoritmos matemáticos fallan si un número está almacenado como texto (ej. "1500")
    for col in df.columns:
        if df[col].dtype == 'object':
            # Limpiar espacios en blanco invisibles al inicio o final de las cadenas de texto
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            # Normalizar distintas representaciones de valores vacíos hacia el estándar NaN de NumPy
            df[col] = df[col].replace(['', 'nan', 'None', 'null', 'NA'], np.nan)
            
            # Heurística: Si al menos el 80% de los datos de la columna pueden convertirse a número, 
            # forzamos la conversión de toda la columna (útil cuando hay números mezclados con algunos errores de tipeo)
            conversion = pd.to_numeric(df[col], errors='coerce')
            no_nulos_orig = df[col].notna().sum()
            if no_nulos_orig > 0 and (conversion.notna().sum() / no_nulos_orig) >= 0.8:
                df[col] = conversion
                resumen["tipos_corregidos"].append(f"{col} (Texto -> Numérico)")

    # 4. Detección y tratamiento de valores nulos (Missing Values)
    # La mayoría de los modelos de Machine Learning (como los Árboles de Decisión clásicos) no admiten valores nulos
    for col in df.columns:
        cant_nulos = int(df[col].isna().sum())
        if cant_nulos > 0:
            if metodo_nulos == "eliminar":
                # Listwise deletion: Se pierde toda la fila si falta un dato (reduce el tamaño del dataset)
                df.dropna(subset=[col], inplace=True)
                resumen["nulos_tratados"][col] = f"{cant_nulos} filas eliminadas"
            else:
                # Imputación automática: Reemplaza el nulo por un valor estadísticamente representativo
                if pd.api.types.is_numeric_dtype(df[col]):
                    # Para números se usa la Mediana (es más robusta frente a valores extremos que el Promedio/Media)
                    valor_imputado = df[col].median()
                    df[col] = df[col].fillna(valor_imputado)
                    resumen["nulos_tratados"][col] = f"{cant_nulos} imputados con mediana ({round(valor_imputado, 2)})"
                else:
                    # Para variables categóricas (texto), se usa la Moda (el valor más frecuente)
                    moda = df[col].mode()
                    valor_imputado = moda[0] if not moda.empty else "Desconocido"
                    df[col] = df[col].fillna(valor_imputado)
                    resumen["nulos_tratados"][col] = f"{cant_nulos} imputados con moda ('{valor_imputado}')"

    # Se reasignan los índices por si se eliminaron filas en el paso anterior
    df.reset_index(drop=True, inplace=True)

    # 5. Detección y manejo de valores atípicos (Outliers)
    # Se utiliza el método del Rango Intercuartílico (IQR), una técnica estadística clásica.
    # Los outliers pueden deformar el aprendizaje del modelo (ej. un sueldo de 10 millones en un dataset donde el promedio es 500 mil)
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    for col in columnas_numericas:
        # Evitar tratar los IDs (identificadores) como variables analizables
        if 'id' in col.split('_'):
            continue
            
        # Q1 (percentil 25) y Q3 (percentil 75)
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        # Si no hay dispersión (todos los datos son iguales), se salta la columna
        if IQR == 0:
            continue
            
        # Bigotes estadísticos de Tukey
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        
        # Máscara booleana para identificar qué registros se salen de los límites "normales"
        mascara_outliers = (df[col] < limite_inferior) | (df[col] > limite_superior)
        cant_outliers = int(mascara_outliers.sum())
        
        if cant_outliers > 0:
            if metodo_outliers == "mediana":
                # Reemplazo por una medida central que no está afectada por el outlier
                mediana_sin_outliers = df.loc[~mascara_outliers, col].median()
                df.loc[mascara_outliers, col] = mediana_sin_outliers
                resumen["outliers_tratados"][col] = f"{cant_outliers} reemplazados por mediana ({round(mediana_sin_outliers, 2)})"
            elif metodo_outliers == "eliminar":
                # Se descartan las filas (puede resultar en gran pérdida de datos si hay muchos outliers)
                df = df[~mascara_outliers].reset_index(drop=True)
                resumen["outliers_tratados"][col] = f"{cant_outliers} filas atípicas eliminadas"
            else:
                # Acotar (Winsorizing / Clipping): Todo valor extremo se "topa" en el límite estadístico permitido.
                # Retiene la fila completa pero suaviza el impacto extremo de esa variable.
                df[col] = df[col].clip(lower=limite_inferior, upper=limite_superior)
                resumen["outliers_tratados"][col] = (
                    f"{cant_outliers} acotados al rango [{round(limite_inferior, 1)}, {round(limite_superior, 1)}]"
                )

    # Optimización final:
    # Si una columna numérica (float) solo contiene valores enteros (sin decimales reales), 
    # se convierte a tipo int para ahorrar memoria RAM.
    for col in df.select_dtypes(include=[np.number]).columns:
        if df[col].notna().all() and (df[col] % 1 == 0).all():
            df[col] = df[col].astype(int)

    # Actualizar contador final
    resumen["filas_finales"] = len(df)
    
    return df, resumen