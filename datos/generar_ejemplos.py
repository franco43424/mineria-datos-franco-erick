"""
Script: generar_ejemplos.py
Propósito: Crear los CSV de ejemplo de datos/ejemplos/ con datos FICTICIOS y errores puestos a propósito
(duplicados, celdas vacías, textos en columnas numéricas, valores imposibles, espacios de más),
para demostrar la limpieza automática y los módulos de minería de datos.

Uso (desde la raíz del proyecto):
    python datos/generar_ejemplos.py

Se usa una semilla fija (random_state), así que siempre genera exactamente los mismos archivos.
"""

import os
import numpy as np
import pandas as pd

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejemplos")
RUTA_ERRORES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruebas_error")


def ensuciar(df, rng, vacios, duplicados):
    """Agrega celdas vacías en las columnas indicadas y repite algunas filas al final (duplicados)."""
    df = df.astype(object)
    for col, cantidad in vacios.items():
        df.loc[rng.choice(len(df), cantidad, replace=False), col] = np.nan
    repetidas = df.iloc[rng.choice(len(df), duplicados, replace=False)]
    return pd.concat([df, repetidas]).sort_index(kind="stable").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 01 - Clientes de una tienda: ¿qué clientes dejan de comprar? (árbol + asociación)
# ---------------------------------------------------------------------------
def clientes_tienda():
    rng = np.random.default_rng(7)
    n = 300
    plan = rng.choice(["Básico", "Estándar", "Premium"], n, p=[.45, .35, .2])
    compras = rng.poisson(np.where(plan == "Básico", 2, np.where(plan == "Estándar", 4, 6)))
    pago = rng.choice(["Tarjeta", "Transferencia", "Efectivo"], n, p=[.45, .35, .2])
    antig = rng.integers(1, 60, n)
    reclamos = rng.poisson(np.where(compras < 3, 2.0, 0.6))
    logit = (-0.5 + 0.9 * reclamos - 0.35 * compras - 0.03 * antig
             + np.where(pago == "Efectivo", 0.8, 0) + np.where(plan == "Premium", -0.8, 0))
    df = pd.DataFrame({
        "ID Cliente": range(1, n + 1),
        "Edad Cliente": rng.integers(18, 70, n),
        "Región": rng.choice(["Tarapacá", "Antofagasta", "Valparaíso", "Metropolitana", "Biobío"], n,
                             p=[.25, .15, .15, .3, .15]),
        "Plan": plan,
        "Ingreso Mensual": (rng.normal(750000, 250000, n) + np.where(plan == "Premium", 350000, 0))
        .clip(350000, None).round(-3).astype(int),
        "Compras Mes": compras,
        "Metodo Pago": pago,
        "Antigüedad Meses": antig,
        "Reclamos": reclamos,
        "Abandono Cliente": np.where(rng.random(n) < 1 / (1 + np.exp(-logit)), "Si", "No"),
    })
    df = ensuciar(df, rng, {"Edad Cliente": 9, "Ingreso Mensual": 7, "Metodo Pago": 8, "Compras Mes": 5,
                            "Región": 4}, duplicados=5)
    df.loc[[10, 77, 150], "Edad Cliente"] = [150, 210, 120]           # edades imposibles
    df.loc[[30, 201], "Ingreso Mensual"] = [9800000, 15000000]        # sueldos exagerados
    df.loc[[12, 90], "Ingreso Mensual"] = ["sin dato", "s/i"]         # texto en columna numérica
    df.loc[[5, 60], "Compras Mes"] = [" 3 ", " 5"]                    # números con espacios
    df.to_csv(os.path.join(RUTA, "01_clientes_tienda.csv"), sep=";", index=False, encoding="utf-8")


# ---------------------------------------------------------------------------
# 02 - Notas de estudiantes: ¿quién aprueba el ramo? (árbol de decisión)
#      Guardado como Excel en Windows: separado por comas y con codificación Latin-1
# ---------------------------------------------------------------------------
def estudiantes_notas():
    rng = np.random.default_rng(11)
    n = 250
    asistencia = rng.normal(80, 12, n).clip(30, 100).round()
    horas = rng.gamma(3, 2.5, n).round(1)
    trabaja = rng.choice(["Si", "No"], n, p=[.35, .65])
    tareas = (1.7 + 0.03 * asistencia + 0.08 * horas + rng.normal(0, 0.6, n)).clip(1, 7).round(1)
    prueba = (0.7 + 0.035 * asistencia + 0.1 * horas - np.where(trabaja == "Si", 0.4, 0)
              + rng.normal(0, 0.8, n)).clip(1, 7).round(1)
    final = 0.4 * tareas + 0.6 * prueba
    df = pd.DataFrame({
        "ID Alumno": [f"A{str(i).zfill(3)}" for i in range(1, n + 1)],
        "Carrera": rng.choice(["Ingeniería Comercial", "Ingeniería Civil", "Contador Auditor", "Psicología"], n),
        "Asistencia (%)": asistencia.astype(int),
        "Horas Estudio Semana": horas,
        "Trabaja": trabaja,
        "Promedio Tareas": tareas,
        "Nota Prueba 1": prueba,
        "Situación Final": np.where(final >= 4.0, "Aprobado", "Reprobado"),
    })
    df = ensuciar(df, rng, {"Asistencia (%)": 6, "Horas Estudio Semana": 8, "Trabaja": 5, "Nota Prueba 1": 4},
                  duplicados=4)
    df.loc[[3, 120], "Asistencia (%)"] = [180, 250]                   # porcentajes imposibles
    df.loc[[40, 41, 199], "Nota Prueba 1"] = ["sin nota", "NP", "pendiente"]  # texto en notas
    df.loc[[15, 88], "Horas Estudio Semana"] = [95, 120]             # horas exageradas
    df.loc[[7, 50, 130], "Carrera"] = ["  Psicología", "Ingeniería Civil  ", " Contador Auditor "]  # espacios
    df.columns = [c + " " if i % 3 == 0 else c for i, c in enumerate(df.columns)]  # cabeceras con espacios
    df.to_csv(os.path.join(RUTA, "02_estudiantes_notas.csv"), sep=",", index=False, encoding="latin-1")


# ---------------------------------------------------------------------------
# 03 - Compras de supermercado: ¿qué productos se compran juntos? (reglas de asociación)
#      Cada fila es una boleta; cada producto dice Si/No
# ---------------------------------------------------------------------------
def compras_supermercado():
    rng = np.random.default_rng(23)
    n = 400
    base = {"Pan": .55, "Leche": .45, "Huevos": .30, "Café": .25, "Arroz": .30, "Fideos": .30,
            "Bebida": .35, "Cerveza": .18, "Pañales": .10, "Detergente": .15}
    compra = {p: rng.random(n) < q for p, q in base.items()}
    # Patrones que el algoritmo debería descubrir:
    compra["Mantequilla"] = np.where(compra["Pan"], rng.random(n) < .55, rng.random(n) < .06)
    compra["Azúcar"] = np.where(compra["Café"], rng.random(n) < .65, rng.random(n) < .10)
    compra["Salsa de Tomate"] = np.where(compra["Fideos"], rng.random(n) < .70, rng.random(n) < .08)
    compra["Papas Fritas"] = np.where(compra["Cerveza"], rng.random(n) < .75, rng.random(n) < .12)
    compra["Cerveza"] = compra["Cerveza"] | (compra["Pañales"] & (rng.random(n) < .5))
    productos = ["Pan", "Mantequilla", "Leche", "Huevos", "Café", "Azúcar", "Arroz", "Fideos", "Salsa de Tomate",
                 "Bebida", "Cerveza", "Papas Fritas", "Pañales", "Detergente"]
    df = pd.DataFrame({"ID Boleta": range(10001, 10001 + n),
                       "Día": rng.choice(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], n)})
    for p in productos:
        df[p] = np.where(compra[p], "Si", "No")
    n_productos = df[productos].eq("Si").sum(axis=1)
    df["Total Compra"] = (n_productos * rng.normal(2300, 500, n) + 500).round(-1).astype(int)
    df = ensuciar(df, rng, {"Leche": 5, "Café": 4, "Total Compra": 6, "Día": 3}, duplicados=6)
    df.loc[[25, 300], "Total Compra"] = [999999, 1250000]            # montos exagerados
    df.loc[[60], "Total Compra"] = ["error caja"]
    df.to_csv(os.path.join(RUTA, "03_compras_supermercado.csv"), sep=";", index=False, encoding="utf-8")


# ---------------------------------------------------------------------------
# 04 - Solicitudes de préstamo: ¿se aprueba o no el crédito? (árbol de decisión)
#      Separado por barras verticales "|" y con líneas en blanco entre medio
# ---------------------------------------------------------------------------
def prestamos_banco():
    rng = np.random.default_rng(5)
    n = 280
    ingreso = rng.lognormal(13.6, 0.45, n).round(-3)
    deuda = (ingreso * rng.uniform(0, 0.8, n)).round(-3)
    anios = rng.integers(0, 25, n)
    historial = rng.choice(["Bueno", "Regular", "Malo"], n, p=[.55, .3, .15])
    puntaje = (0.000003 * ingreso - 3.5 * deuda / ingreso + 0.08 * anios
               + np.select([historial == "Bueno", historial == "Regular"], [1.5, 0], -2.0) + rng.normal(0, 0.7, n))
    df = pd.DataFrame({
        "ID Solicitud": range(1, n + 1),
        "Edad": rng.integers(21, 68, n),
        "Ingreso Mensual": ingreso.astype(int),
        "Deuda Actual": deuda.astype(int),
        "Años en Empleo": anios,
        "Historial Crediticio": historial,
        "Tipo Vivienda": rng.choice(["Propia", "Arrendada", "Familiar"], n, p=[.4, .45, .15]),
        "Préstamo Aprobado": np.where(puntaje > 2.0, "Si", "No"),
    })
    df = ensuciar(df, rng, {"Ingreso Mensual": 6, "Historial Crediticio": 5, "Edad": 4, "Tipo Vivienda": 3},
                  duplicados=5)
    df.loc[[9, 140], "Edad"] = [5, 199]                               # edades imposibles
    df.loc[[70], "Ingreso Mensual"] = [45000000]
    df.loc[[33, 210], "Deuda Actual"] = ["no informa", "?"]
    texto = df.to_csv(sep="|", index=False)
    lineas = texto.split("\n")
    for pos in (5, 60, 150):                                          # líneas en blanco
        lineas.insert(pos, "")
    with open(os.path.join(RUTA, "04_prestamos_banco.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))


# ---------------------------------------------------------------------------
# Archivos inválidos para probar los mensajes de error de la validación (RF1)
# ---------------------------------------------------------------------------
def archivos_con_error():
    os.makedirs(RUTA_ERRORES, exist_ok=True)
    open(os.path.join(RUTA_ERRORES, "error_archivo_vacio.csv"), "w").close()
    with open(os.path.join(RUTA_ERRORES, "error_una_sola_columna.csv"), "w", encoding="utf-8") as f:
        f.write("nombres\nAna\nLuis\nPedro\nMaría\n")
    with open(os.path.join(RUTA_ERRORES, "error_solo_encabezado.csv"), "w", encoding="utf-8") as f:
        f.write("edad;ingreso;compras\n")


if __name__ == "__main__":
    os.makedirs(RUTA, exist_ok=True)
    clientes_tienda()
    estudiantes_notas()
    compras_supermercado()
    prestamos_banco()
    archivos_con_error()
    print("Archivos generados en:", RUTA, "y", RUTA_ERRORES)
