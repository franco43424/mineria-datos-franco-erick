"""RF2 - Limpieza automática (analisis/limpieza.py)."""

import pandas as pd
import pytest

from analisis.limpieza import limpiar_dataset_automatico, normalizar_texto_columna


def test_normaliza_nombres_de_columnas(clientes_limpio):
    """QA-RF2-01: Las cabeceras quedan en snake_case, sin tildes ni espacios."""
    df, resumen = clientes_limpio
    assert "antiguedad_meses" in df.columns and "region" in df.columns
    assert resumen["columnas_renombradas"]["Antigüedad Meses"] == "antiguedad_meses"
    assert normalizar_texto_columna(" Asistencia (%) ") == "asistencia"


def test_elimina_duplicados(clientes_limpio):
    """QA-RF2-02: Se eliminan las 5 filas repetidas del ejemplo de clientes."""
    df, resumen = clientes_limpio
    assert resumen["duplicados_eliminados"] == 5
    assert not df.duplicated().any()


def test_corrige_tipos_de_datos(clientes_limpio):
    """QA-RF2-03: 'ingreso_mensual' venía como texto (por 'sin dato' y 's/i') y queda numérico."""
    df, resumen = clientes_limpio
    assert "ingreso_mensual (Texto -> Numérico)" in resumen["tipos_corregidos"]
    assert pd.api.types.is_numeric_dtype(df["ingreso_mensual"])
    assert pd.api.types.is_numeric_dtype(df["compras_mes"])


def test_imputa_nulos(clientes_limpio):
    """QA-RF2-04: Con imputación no queda ninguna celda vacía (mediana en números, moda en texto)."""
    df, resumen = clientes_limpio
    assert df.isna().sum().sum() == 0
    assert "mediana" in resumen["nulos_tratados"]["edad_cliente"]
    assert "moda" in resumen["nulos_tratados"]["metodo_pago"]


def test_eliminar_nulos_reduce_filas(clientes_crudo):
    """QA-RF2-05: La estrategia 'eliminar' descarta las filas incompletas."""
    df, resumen = limpiar_dataset_automatico(clientes_crudo[0], metodo_nulos="eliminar")
    assert df.isna().sum().sum() == 0
    assert resumen["filas_finales"] < resumen["filas_iniciales"] - resumen["duplicados_eliminados"]


@pytest.mark.parametrize("metodo", ["acotar", "mediana", "eliminar"])
def test_trata_outliers(clientes_crudo, metodo):
    """QA-RF2-06: Las edades imposibles (120, 150, 210) desaparecen con las 3 estrategias de outliers."""
    df, resumen = limpiar_dataset_automatico(clientes_crudo[0], metodo_outliers=metodo)
    assert "edad_cliente" in resumen["outliers_tratados"]
    assert df["edad_cliente"].max() < 100


def test_no_trata_columnas_id(clientes_limpio):
    """QA-RF2-07: La columna ID no se considera para outliers."""
    _, resumen = clientes_limpio
    assert "id_cliente" not in resumen["outliers_tratados"]


def test_resumen_completo(clientes_limpio):
    """QA-RF2-08: El resumen informa filas iniciales/finales y cada transformación."""
    _, resumen = clientes_limpio
    for clave in ["filas_iniciales", "filas_finales", "columnas_renombradas", "duplicados_eliminados",
                  "tipos_corregidos", "nulos_tratados", "outliers_tratados"]:
        assert clave in resumen
    assert resumen["filas_iniciales"] == 305 and resumen["filas_finales"] == 300
