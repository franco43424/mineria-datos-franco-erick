"""RF3 - Árbol de decisión y gestión de modelos (analisis/arbol_decision.py)."""

import os
import pytest

from analisis.arbol_decision import (entrenar_arbol_decision, guardar_modelo, listar_modelos_guardados,
                                     eliminar_modelo_guardado)

PREDICTORAS = ["edad_cliente", "plan", "ingreso_mensual", "compras_mes", "metodo_pago", "antiguedad_meses", "reclamos"]


@pytest.mark.parametrize("criterio", ["gini", "entropy"])
def test_entrena_y_calcula_metricas(clientes_limpio, criterio):
    """QA-RF3-01: Entrena con Gini y Entropía y entrega exactitud, precisión, recall y matriz de confusión."""
    df, _ = clientes_limpio
    exito, mensaje, res = entrenar_arbol_decision(df, "abandono_cliente", PREDICTORAS, criterio, 3, 0.25)
    assert exito, mensaje
    for metrica in ["exactitud", "precision", "recall"]:
        assert 0.6 <= res[metrica] <= 1.0
    assert res["clases"] == ["No", "Si"]
    assert sum(map(sum, res["matriz_confusion"])) == res["filas_prueba"] == 75
    assert res["figura_arbol"] is not None


def test_respeta_profundidad(clientes_limpio):
    """QA-RF3-02: El árbol no supera la profundidad máxima configurada."""
    df, _ = clientes_limpio
    _, _, res = entrenar_arbol_decision(df, "abandono_cliente", PREDICTORAS, "gini", 2, 0.2)
    assert res["modelo_obj"].get_depth() <= 2


def test_valida_seleccion_de_variables(clientes_limpio):
    """QA-RF3-03: Mensajes de error si no hay predictoras o el objetivo no es categórico."""
    df, _ = clientes_limpio
    exito, mensaje, _ = entrenar_arbol_decision(df, "abandono_cliente", [])
    assert not exito and "predictora" in mensaje
    exito, mensaje, _ = entrenar_arbol_decision(df, "ingreso_mensual", ["edad_cliente"])
    assert not exito and "categórica" in mensaje


def test_guardar_listar_eliminar(clientes_limpio, almacenamiento_temporal):
    """QA-RF3-04: Gestión de modelos: guardar (.pkl + JSON), listar y eliminar."""
    import analisis.arbol_decision as arbol
    df, _ = clientes_limpio
    _, _, res = entrenar_arbol_decision(df, "abandono_cliente", PREDICTORAS)
    registro = guardar_modelo("Modelo de prueba", res, "01_clientes_tienda.csv")
    ruta_pkl = os.path.join(arbol.RUTA_MODELOS, registro["archivo_pkl"])
    assert os.path.exists(ruta_pkl)
    assert [m["nombre"] for m in listar_modelos_guardados()] == ["Modelo de prueba"]
    eliminar_modelo_guardado(registro["id"])
    assert listar_modelos_guardados() == [] and not os.path.exists(ruta_pkl)
