"""
Configuración compartida de las pruebas automáticas (pytest).

Ejecutar desde la raíz del proyecto:
    python -m pytest -v
"""

import io
import os
import sys

import pytest
import matplotlib

matplotlib.use("Agg")  # Sin ventanas: los gráficos se generan en memoria

RUTA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RUTA_RAIZ not in sys.path:
    sys.path.insert(0, RUTA_RAIZ)

from analisis.config import RUTA_EJEMPLOS  # noqa: E402
from analisis.validador import validar_y_cargar_csv  # noqa: E402
from analisis.limpieza import limpiar_dataset_automatico  # noqa: E402

RUTA_ERRORES = os.path.join(RUTA_RAIZ, "datos", "pruebas_error")


def archivo_simulado(ruta):
    """Imita el archivo que entrega el botón de carga de Streamlit (tiene .name, .size y .getvalue())."""
    with open(ruta, "rb") as f:
        contenido = f.read()
    archivo = io.BytesIO(contenido)
    archivo.name = os.path.basename(ruta)
    archivo.size = len(contenido)
    return archivo


def cargar(nombre, carpeta=RUTA_EJEMPLOS):
    """Valida y carga un CSV de ejemplo; retorna lo mismo que validar_y_cargar_csv()."""
    return validar_y_cargar_csv(archivo_simulado(os.path.join(carpeta, nombre)))


@pytest.fixture(scope="session")
def clientes_crudo():
    exito, _, df, meta = cargar("01_clientes_tienda.csv")
    assert exito
    return df, meta


@pytest.fixture(scope="session")
def clientes_limpio(clientes_crudo):
    df_limpio, resumen = limpiar_dataset_automatico(clientes_crudo[0])
    return df_limpio, resumen


@pytest.fixture(scope="session")
def supermercado_limpio():
    exito, _, df, _ = cargar("03_compras_supermercado.csv")
    assert exito
    return limpiar_dataset_automatico(df)[0]


@pytest.fixture
def almacenamiento_temporal(tmp_path, monkeypatch):
    """Redirige storage/ a una carpeta temporal para que las pruebas no ensucien los resultados reales."""
    import analisis.arbol_decision as arbol
    import analisis.asociacion as asociacion
    monkeypatch.setattr(arbol, "RUTA_MODELOS", str(tmp_path / "modelos"))
    monkeypatch.setattr(arbol, "ARCHIVO_REGISTRO", str(tmp_path / "modelos" / "registro_modelos.json"))
    monkeypatch.setattr(asociacion, "RUTA_REGLAS", str(tmp_path / "reglas"))
    monkeypatch.setattr(asociacion, "ARCHIVO_REGISTRO_REGLAS", str(tmp_path / "reglas" / "registro_reglas.json"))
    return tmp_path
