"""
Módulo: validador.py
Propósito: Gestionar la fase de Ingesta y Validación de Datos.
En un proyecto de Minería de Datos, es el primer filtro de calidad (Data Quality).
Asegura que el archivo origen sea legible, no exceda los límites de memoria,
y tenga una estructura tabular válida antes de iniciar cualquier análisis o modelado.
"""

import pandas as pd
import io
import csv

def validar_y_cargar_csv(archivo_subido):
    """
    RF1: Valida el formato, tamaño, codificación de caracteres y delimitador de un archivo CSV.
    Convierte el archivo físico subido desde la interfaz web en un DataFrame de Pandas estructurado.
    
    Parámetros:
        archivo_subido (UploadedFile): Objeto de archivo en memoria proveniente de Streamlit.
        
    Retorna:
        tuple: (exito (bool), mensaje (str), df (DataFrame o None), metadatos (dict))
    """
    metadatos = {}

    # 1. Validar formato (extensión .csv)
    # Los modelos tabulares clásicos requieren datos estructurados. Se bloquean otros formatos
    # como imágenes, PDFs o ejecutables por seguridad y compatibilidad.
    nombre_archivo = archivo_subido.name
    if not nombre_archivo.lower().endswith('.csv'):
        return False, "Error: El archivo debe tener extensión .csv", None, metadatos

    # 2. Validar tamaño (que no esté vacío y no supere 50 MB)
    # Control de recursos: Evita errores de memoria (Out of Memory - OOM) al cargar 
    # datasets demasiado masivos en la memoria RAM del servidor.
    tamano_bytes = archivo_subido.size
    tamano_kb = round(tamano_bytes / 1024, 2)
    if tamano_bytes == 0:
        return False, "Error: El archivo está completamente vacío (0 bytes).", None, metadatos
    if tamano_bytes > 50 * 1024 * 1024:
        return False, "Error: El archivo supera el límite máximo de 50 MB.", None, metadatos

    # Leemos los bytes crudos del archivo en memoria para su posterior decodificación
    contenido_bytes = archivo_subido.getvalue()

    # 3. Detectar y validar codificación (UTF-8 vs Latin-1 / ISO-8859-1)
    # Paso crucial en Minería de Datos: Si se usa la codificación incorrecta, los caracteres 
    # especiales (tildes, ñ) se corrompen, arruinando las variables categóricas de texto.
    codificacion_detectada = None
    texto_decodificado = None
    for enc in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
        try:
            texto_decodificado = contenido_bytes.decode(enc)
            codificacion_detectada = 'utf-8' if enc == 'utf-8-sig' else enc
            break  # Si decodifica sin lanzar error, asume que es la codificación correcta
        except UnicodeDecodeError:
            continue

    if texto_decodificado is None:
        return False, "Error: No se pudo reconocer la codificación de caracteres del archivo.", None, metadatos

    # 4. Detectar y validar separador (coma, punto y coma, tabulación o pipe)
    # Filtramos líneas en blanco iniciales para asegurar que leemos el encabezado real
    lineas_validas = [linea.strip() for linea in texto_decodificado.splitlines() if linea.strip()]
    if not lineas_validas:
        return False, "Error: El archivo CSV no contiene líneas con datos.", None, metadatos

    primera_linea = lineas_validas[0]
    separadores_posibles = [',', ';', '\t', '|', ':']
    separador_detectado = max(separadores_posibles, key=lambda s: primera_linea.count(s))
    
    if primera_linea.count(separador_detectado) == 0:
        try:
            dialecto = csv.Sniffer().sniff("\n".join(lineas_validas[:5]))
            separador_detectado = dialecto.delimiter
        except Exception:
            separador_detectado = ','

    # 5. Intentar cargar el DataFrame con Pandas usando lo detectado
    # io.StringIO simula un archivo de texto en memoria a partir del string decodificado,
    # permitiendo que pd.read_csv lo procese como si fuera un archivo físico.
    texto_limpio = "\n".join(lineas_validas)
    try:
        buffer_texto = io.StringIO(texto_limpio)
        df = pd.read_csv(buffer_texto, sep=separador_detectado)
        # Respaldo automático si el separador elegido dejó todo en 1 sola columna
        if len(df.columns) < 2:
            for sep_alt in [';', ',', '\t', '|']:
                df_prueba = pd.read_csv(io.StringIO(texto_limpio), sep=sep_alt)
                if len(df_prueba.columns) >= 2:
                    df = df_prueba
                    separador_detectado = sep_alt
                    break
    except Exception as e:
        return False, f"Error al estructurar las columnas del CSV: {str(e)}", None, metadatos

    # Validar que tenga al menos filas y columnas válidas
    # Un algoritmo de Machine Learning necesita al menos 2 columnas (1 predictora 'X' y 1 objetivo 'y')
    # y suficientes filas para poder encontrar patrones (aprender).
    if df.empty or len(df.columns) < 2:
        return False, "Error: El CSV no contiene suficientes filas o columnas válidas para minería de datos.", None, metadatos

    # Armamos el resumen de validación para mostrarlo en la web (Data Profiling básico)
    nombres_sep = {',': 'Coma (,)', ';': 'Punto y coma (;)', '\t': 'Tabulación (\\t)', '|': 'Pipe (|)'}
    metadatos = {
        "nombre": nombre_archivo,
        "tamano_kb": f"{tamano_kb} KB",
        "codificacion": codificacion_detectada.upper(),
        "separador": nombres_sep.get(separador_detectado, separador_detectado),
        "filas": df.shape[0],
        "columnas": df.shape[1]
    }

    return True, "Archivo CSV validado y cargado correctamente.", df, metadatos