import pandas as pd
import numpy as np
import unicodedata
import re

def normalizar_texto_columna(nombre):
    """Convierte 'Ingreso Mensual' -> 'ingreso_mensual' sin tildes ni símbolos."""
    texto = str(nombre).strip().lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = re.sub(r'[^a-z0-9]+', '_', texto)
    return texto.strip('_')

def limpiar_dataset_automatico(df_original, metodo_nulos="imputar", metodo_outliers="acotar"):
    """
    RF2: Ejecuta la limpieza automática del DataFrame y devuelve:
    (df_limpio, resumen_limpieza: dict)
    """
    df = df_original.copy()
    filas_iniciales = len(df)
    
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
    nuevas_columnas = {}
    for col in df.columns:
        col_norm = normalizar_texto_columna(col)
        if col != col_norm:
            resumen["columnas_renombradas"][col] = col_norm
        nuevas_columnas[col] = col_norm
    df.rename(columns=nuevas_columnas, inplace=True)

    # 2. Eliminación de duplicados
    duplicados = int(df.duplicated().sum())
    if duplicados > 0:
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
    resumen["duplicados_eliminados"] = duplicados

    # 3. Corrección de tipos de datos
    for col in df.columns:
        if df[col].dtype == 'object':
            # Limpiar espacios en blanco en textos
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
            # Reemplazar textos vacíos por NaN real
            df[col] = df[col].replace(['', 'nan', 'None', 'null', 'NA'], np.nan)
            
            # Intentar convertir a numérico si la mayoría de los valores son números
            conversion = pd.to_numeric(df[col], errors='coerce')
            no_nulos_orig = df[col].notna().sum()
            if no_nulos_orig > 0 and (conversion.notna().sum() / no_nulos_orig) >= 0.8:
                df[col] = conversion
                resumen["tipos_corregidos"].append(f"{col} (Texto -> Numérico)")

    # 4. Detección y tratamiento de valores nulos
    for col in df.columns:
        cant_nulos = int(df[col].isna().sum())
        if cant_nulos > 0:
            if metodo_nulos == "eliminar":
                df.dropna(subset=[col], inplace=True)
                resumen["nulos_tratados"][col] = f"{cant_nulos} filas eliminadas"
            else:
                # Imputación automática: Mediana para números, Moda para texto/categorías
                if pd.api.types.is_numeric_dtype(df[col]):
                    valor_imputado = df[col].median()
                    df[col] = df[col].fillna(valor_imputado)
                    resumen["nulos_tratados"][col] = f"{cant_nulos} imputados con mediana ({round(valor_imputado, 2)})"
                else:
                    moda = df[col].mode()
                    valor_imputado = moda[0] if not moda.empty else "Desconocido"
                    df[col] = df[col].fillna(valor_imputado)
                    resumen["nulos_tratados"][col] = f"{cant_nulos} imputados con moda ('{valor_imputado}')"

    df.reset_index(drop=True, inplace=True)

    # 5. Detección y manejo de valores atípicos (Outliers con método IQR)
    columnas_numericas = df.select_dtypes(include=[np.number]).columns
    for col in columnas_numericas:
        # Ignorar columnas que sean identificadores (ID)
        if 'id' in col.split('_'):
            continue
            
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            continue
            
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        
        mascara_outliers = (df[col] < limite_inferior) | (df[col] > limite_superior)
        cant_outliers = int(mascara_outliers.sum())
        
        if cant_outliers > 0:
            if metodo_outliers == "mediana":
                mediana_sin_outliers = df.loc[~mascara_outliers, col].median()
                df.loc[mascara_outliers, col] = mediana_sin_outliers
                resumen["outliers_tratados"][col] = f"{cant_outliers} reemplazados por mediana ({round(mediana_sin_outliers, 2)})"
            elif metodo_outliers == "eliminar":
                df = df[~mascara_outliers].reset_index(drop=True)
                resumen["outliers_tratados"][col] = f"{cant_outliers} filas atípicas eliminadas"
            else:
                # Acotar (Winsorizing / Clipping) a los límites normales
                df[col] = df[col].clip(lower=limite_inferior, upper=limite_superior)
                resumen["outliers_tratados"][col] = (
                    f"{cant_outliers} acotados al rango [{round(limite_inferior, 1)}, {round(limite_superior, 1)}]"
                )

    # Si una columna numérica no tiene decimales reales (ej. edad), dejarla como entero limpio
    for col in df.select_dtypes(include=[np.number]).columns:
        if df[col].notna().all() and (df[col] % 1 == 0).all():
            df[col] = df[col].astype(int)

    resumen["filas_finales"] = len(df)
    return df, resumen