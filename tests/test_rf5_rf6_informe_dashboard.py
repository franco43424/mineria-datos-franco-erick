"""RF5 - Informe HTML (analisis/informe.py) y RF6 - Dashboard (analisis/dashboard.py)."""

from analisis.dashboard import (clasificar_columnas, aplicar_filtros, calcular_kpis, matriz_correlacion,
                                correlaciones_destacadas, estadisticas_descriptivas)
from analisis.informe import generar_informe_html
from analisis.arbol_decision import entrenar_arbol_decision
from analisis.asociacion import generar_reglas_asociacion


def test_clasifica_columnas_sin_id(clientes_limpio):
    """QA-RF6-01: Separa variables numéricas y categóricas, sin incluir el ID."""
    df, _ = clientes_limpio
    numericas, categoricas = clasificar_columnas(df)
    assert "id_cliente" not in numericas + categoricas
    assert "ingreso_mensual" in numericas and "plan" in categoricas


def test_filtros_dinamicos(clientes_limpio):
    """QA-RF6-02: Los filtros por categoría y por rango se combinan correctamente."""
    df, _ = clientes_limpio
    filtrado = aplicar_filtros(df, {"plan": ("valores", ["Premium"]), "edad_cliente": ("rango", (30, 50))})
    assert len(filtrado) > 0
    assert set(filtrado["plan"]) == {"Premium"}
    assert filtrado["edad_cliente"].between(30, 50).all()
    kpis = calcular_kpis(filtrado, df, "abandono_cliente")
    assert kpis["registros"] == len(filtrado) and 0 < kpis["porcentaje_del_total"] < 100


def test_correlaciones(clientes_limpio):
    """QA-RF6-03: Matriz de correlación simétrica en [-1, 1]; detecta la relación compras-reclamos."""
    df, _ = clientes_limpio
    matriz = matriz_correlacion(df)
    assert (matriz.values == matriz.values.T).all()
    assert matriz.abs().max().max() <= 1
    a, b, r = correlaciones_destacadas(matriz, top=1)[0]
    assert {a, b} == {"compras_mes", "reclamos"} and r < 0


def test_estadisticas(clientes_limpio):
    """QA-RF6-04: Estadísticas descriptivas de las variables numéricas."""
    df, _ = clientes_limpio
    desc = estadisticas_descriptivas(df)
    assert list(desc.columns) == ["Media", "Mediana", "Desv. estándar", "Mínimo", "Máximo"]


def test_informe_html_completo(clientes_crudo, clientes_limpio):
    """QA-RF5-01: El informe HTML incluye las 5 secciones, gráficos incrustados y conclusiones."""
    df_original, meta = clientes_crudo
    df, resumen = clientes_limpio
    _, _, arbol = entrenar_arbol_decision(df, "abandono_cliente", ["plan", "compras_mes", "reclamos"])
    _, _, reglas = generar_reglas_asociacion(df, ["plan", "reclamos", "abandono_cliente"], 0.1, 0.5)
    html = generar_informe_html("01_clientes_tienda.csv", meta, df_original, df, resumen,
                                ultimo_arbol=arbol, resultado_reglas=reglas, tabla_reglas=reglas["tabla_reglas"],
                                col_objetivo="abandono_cliente", conclusiones_usuario="Conclusión del equipo")
    assert html.startswith("<!DOCTYPE html>")
    for seccion in ["Resumen de los datos", "Limpieza automática", "Árbol de decisión",
                    "Reglas de asociación", "Conclusiones", "Conclusión del equipo"]:
        assert seccion in html
    assert html.count("data:image/png;base64") >= 4


def test_informe_sin_modelos(clientes_crudo, clientes_limpio):
    """QA-RF5-02: El informe se genera aunque todavía no haya modelos ni reglas."""
    df_original, meta = clientes_crudo
    df, resumen = clientes_limpio
    html = generar_informe_html("01_clientes_tienda.csv", meta, df_original, df, resumen)
    assert "No se generaron reglas" in html
