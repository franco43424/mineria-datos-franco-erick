"""RF1 - Carga y validación del CSV (analisis/validador.py)."""

import io
import pytest

from analisis.validador import validar_y_cargar_csv
from tests.conftest import cargar, RUTA_ERRORES


@pytest.mark.parametrize("archivo, separador, codificacion", [
    ("01_clientes_tienda.csv", "Punto y coma (;)", "UTF-8"),
    ("02_estudiantes_notas.csv", "Coma (,)", "LATIN-1"),
    ("03_compras_supermercado.csv", "Punto y coma (;)", "UTF-8"),
    ("04_prestamos_banco.csv", "Pipe (|)", "UTF-8"),
])
def test_detecta_separador_y_codificacion(archivo, separador, codificacion):
    """QA-RF1-01: Detecta automáticamente el separador y la codificación de cada ejemplo."""
    exito, mensaje, df, meta = cargar(archivo)
    assert exito, mensaje
    assert meta["separador"] == separador
    assert meta["codificacion"] == codificacion
    assert meta["columnas"] >= 8


def test_latin1_conserva_tildes():
    """QA-RF1-02: Un archivo Latin-1 se lee sin romper las tildes (ej. 'Situación Final', 'Psicología')."""
    _, _, df, _ = cargar("02_estudiantes_notas.csv")
    assert "Situación Final" in df.columns
    assert df["Carrera"].astype(str).str.contains("Psicología").any()


def test_ignora_lineas_en_blanco():
    """QA-RF1-03: Las líneas en blanco dentro del archivo no generan filas vacías."""
    _, _, df, meta = cargar("04_prestamos_banco.csv")
    assert meta["filas"] == 285          # 280 solicitudes + 5 duplicadas, sin las 3 líneas en blanco
    assert not df.isna().all(axis=1).any()


@pytest.mark.parametrize("archivo, texto_esperado", [
    ("error_archivo_vacio.csv", "vacío"),
    ("error_una_sola_columna.csv", "suficientes filas o columnas"),
    ("error_solo_encabezado.csv", "suficientes filas o columnas"),
])
def test_rechaza_archivos_invalidos(archivo, texto_esperado):
    """QA-RF1-04: Archivos inválidos se rechazan con un mensaje claro."""
    exito, mensaje, df, _ = cargar(archivo, carpeta=RUTA_ERRORES)
    assert not exito
    assert df is None
    assert texto_esperado in mensaje


def test_rechaza_extension_distinta_de_csv():
    """QA-RF1-05: Solo se aceptan archivos .csv."""
    archivo = io.BytesIO(b"a;b\n1;2\n")
    archivo.name, archivo.size = "datos.xlsx", 8
    exito, mensaje, _, _ = validar_y_cargar_csv(archivo)
    assert not exito and ".csv" in mensaje


def test_rechaza_archivo_mayor_a_50mb():
    """QA-RF1-06: Se bloquean archivos que superan el límite de 50 MB."""
    archivo = io.BytesIO(b"a;b\n1;2\n")
    archivo.name, archivo.size = "grande.csv", 51 * 1024 * 1024
    exito, mensaje, _, _ = validar_y_cargar_csv(archivo)
    assert not exito and "50 MB" in mensaje
