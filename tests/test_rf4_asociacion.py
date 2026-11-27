"""RF4 - Reglas de asociación (analisis/asociacion.py)."""

import pytest

from analisis.asociacion import (generar_reglas_asociacion, filtrar_reglas, preparar_transacciones,
                                 guardar_reglas, listar_reglas_guardadas, cargar_tabla_reglas,
                                 eliminar_reglas_guardadas)

PRODUCTOS = ["pan", "mantequilla", "leche", "huevos", "cafe", "azucar", "arroz", "fideos", "salsa_de_tomate",
             "bebida", "cerveza", "papas_fritas", "panales", "detergente"]


def test_discretiza_numericas(clientes_limpio):
    """QA-RF4-01: Las columnas numéricas se convierten en intervalos (Bajo / Medio / Alto)."""
    df, _ = clientes_limpio
    matriz = preparar_transacciones(df, ["compras_mes", "plan"], n_intervalos=3)
    assert {"compras_mes=Bajo", "compras_mes=Medio", "compras_mes=Alto", "plan=Premium"} <= set(matriz.columns)
    assert matriz.dtypes.eq(bool).all()


@pytest.mark.parametrize("algoritmo", ["apriori", "fpgrowth"])
def test_encuentra_patrones_de_canasta(supermercado_limpio, algoritmo):
    """QA-RF4-02: En el supermercado descubre los patrones escondidos (Pan→Mantequilla, Cerveza→Papas Fritas...)."""
    exito, mensaje, res = generar_reglas_asociacion(supermercado_limpio, PRODUCTOS, 0.05, 0.5, algoritmo,
                                                    max_longitud=2, solo_presentes=True)
    assert exito, mensaje
    reglas = set(zip(res["tabla_reglas"]["antecedente"], res["tabla_reglas"]["consecuente"]))
    for regla in [("pan=Si", "mantequilla=Si"), ("cafe=Si", "azucar=Si"),
                  ("fideos=Si", "salsa_de_tomate=Si"), ("cerveza=Si", "papas_fritas=Si")]:
        assert regla in reglas


def test_umbrales_y_metricas(clientes_limpio):
    """QA-RF4-03: Todas las reglas cumplen soporte y confianza mínimos e incluyen lift."""
    df, _ = clientes_limpio
    exito, _, res = generar_reglas_asociacion(df, ["plan", "metodo_pago", "reclamos", "abandono_cliente"], 0.1, 0.6)
    tabla = res["tabla_reglas"]
    assert exito and len(tabla) > 0
    assert (tabla["soporte"] >= 0.1).all() and (tabla["confianza"] >= 0.6).all()
    assert "lift" in tabla.columns


def test_solo_presentes_quita_items_no(supermercado_limpio):
    """QA-RF4-04: La opción 'ignorar ausencias' elimina ítems como 'pan=No'."""
    matriz = preparar_transacciones(supermercado_limpio, PRODUCTOS, solo_presentes=True)
    assert not any(c.endswith("=No") for c in matriz.columns)


def test_mensajes_cuando_no_hay_reglas(clientes_limpio):
    """QA-RF4-05: Avisa cuando faltan columnas o los umbrales son demasiado altos."""
    df, _ = clientes_limpio
    assert not generar_reglas_asociacion(df, ["plan"])[0]
    exito, mensaje, _ = generar_reglas_asociacion(df, ["plan", "metodo_pago"], 0.9, 0.9)
    assert not exito and "soporte" in mensaje


def test_filtrar_y_ordenar(clientes_limpio):
    """QA-RF4-06: Filtrado por texto, lift y confianza, y ordenamiento."""
    df, _ = clientes_limpio
    _, _, res = generar_reglas_asociacion(df, ["plan", "compras_mes", "reclamos", "abandono_cliente"], 0.05, 0.5)
    filtrada = filtrar_reglas(res["tabla_reglas"], "abandono_cliente=Si", min_lift=1.0, orden="confianza")
    assert len(filtrada) > 0
    texto = filtrada["antecedente"] + filtrada["consecuente"]
    assert texto.str.contains("abandono_cliente=Si").all()
    assert (filtrada["lift"] >= 1.0).all()
    assert filtrada["confianza"].is_monotonic_decreasing


def test_guardar_ver_eliminar(clientes_limpio, almacenamiento_temporal):
    """QA-RF4-07: Gestión de resultados: guardar, listar, ver y eliminar."""
    df, _ = clientes_limpio
    _, _, res = generar_reglas_asociacion(df, ["plan", "reclamos", "abandono_cliente"], 0.1, 0.5)
    registro = guardar_reglas("Reglas de prueba", res, "01_clientes_tienda.csv")
    assert listar_reglas_guardadas()[0]["cantidad_reglas"] == len(res["tabla_reglas"])
    assert len(cargar_tabla_reglas(registro["id"])) == len(res["tabla_reglas"])
    eliminar_reglas_guardadas(registro["id"])
    assert listar_reglas_guardadas() == []
