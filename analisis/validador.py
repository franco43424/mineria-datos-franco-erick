import pandas as pd
import io

def validar_y_cargar_csv(archivo_subido):
    """
    RF1: Valida formato, tamaño, codificación y separador de un archivo CSV.
    Retorna: (exito: bool, mensaje: str, df: DataFrame o None, metadatos: dict)
    """
    metadatos = {}

    # 1. Validar formato (extensión .csv)
    nombre_archivo = archivo_subido.name
    if not nombre_archivo.lower().endswith('.csv'):
        return False, "Error: El archivo debe tener extensión .csv", None, metadatos

    # 2. Validar tamaño (que no esté vacío y no supere 50 MB)
    tamano_bytes = archivo_subido.size
    tamano_kb = round(tamano_bytes / 1024, 2)
    if tamano_bytes == 0:
        return False, "Error: El archivo está completamente vacío (0 bytes).", None, metadatos
    if tamano_bytes > 50 * 1024 * 1024:
        return False, "Error: El archivo supera el límite máximo de 50 MB.", None, metadatos

    # Leemos los bytes crudos del archivo en memoria
    contenido_bytes = archivo_subido.getvalue()

    # 3. Detectar y validar codificación (UTF-8 vs Latin-1 / ISO-8859-1)
    codificacion_detectada = None
    texto_decodificado = None
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            texto_decodificado = contenido_bytes.decode(enc)
            codificacion_detectada = enc
            break
        except UnicodeDecodeError:
            continue

    if texto_decodificado is None:
        return False, "Error: No se pudo reconocer la codificación de caracteres del archivo.", None, metadatos

    # 4. Detectar y validar separador (coma, punto y coma, tabulación o pipe)
    primera_linea = texto_decodificado.splitlines()[0] if texto_decodificado.splitlines() else ""
    separadores_posibles = [',', ';', '\t', '|']
    # Contamos cuál separador aparece más veces en el encabezado
    separador_detectado = max(separadores_posibles, key=lambda s: primera_linea.count(s))
    
    if primera_linea.count(separador_detectado) == 0:
        # Si no encontró ninguno claro, usamos coma por defecto
        separador_detectado = ','

    # 5. Intentar cargar el DataFrame con Pandas usando lo detectado
    try:
        buffer_texto = io.StringIO(texto_decodificado)
        df = pd.read_csv(buffer_texto, sep=separador_detectado)
    except Exception as e:
        return False, f"Error al estructurar las columnas del CSV: {str(e)}", None, metadatos

    # Validar que tenga al menos filas y columnas válidas
    if df.empty or len(df.columns) < 2:
        return False, "Error: El CSV no contiene suficientes filas o columnas válidas para minería de datos.", None, metadatos

    # Armamos el resumen de validación para mostrarlo en la web
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