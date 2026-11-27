"""
Módulo: config.py
Propósito: Reunir en un solo lugar las rutas y parámetros generales del proyecto.
Así, si una carpeta cambia de nombre, se modifica solo aquí y no en cada archivo.
"""

import os

# Carpeta raíz del proyecto (la que contiene analisis/, web/, datos/, storage/)
RUTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Entradas: CSV de ejemplo listos para cargar desde la interfaz
RUTA_EJEMPLOS = os.path.join(RUTA_RAIZ, 'datos', 'ejemplos')

# Salidas: resultados que genera la aplicación
RUTA_STORAGE = os.path.join(RUTA_RAIZ, 'storage')
RUTA_MODELOS = os.path.join(RUTA_STORAGE, 'modelos')   # árboles (.pkl) + registro_modelos.json
RUTA_REGLAS = os.path.join(RUTA_STORAGE, 'reglas')     # reglas (.csv) + registro_reglas.json

# Límites de validación del CSV (RF1)
TAMANO_MAXIMO_MB = 50
COLUMNAS_MINIMAS = 2


def es_columna_id(nombre_columna):
    """
    Indica si una columna es un identificador (ej. 'id_cliente', 'id').
    Los IDs no aportan información al análisis, por eso se excluyen de outliers, modelos y gráficos.
    """
    return 'id' in str(nombre_columna).lower().split('_')
