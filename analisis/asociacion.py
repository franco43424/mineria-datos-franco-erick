"""
Módulo: asociacion.py
Propósito: RF4 - Módulo de Reglas de Asociación.
Descubre patrones del tipo "SI ocurre A ENTONCES suele ocurrir B" dentro del dataset
(análisis tipo "canasta de mercado"), usando el algoritmo Apriori o FP-Growth de mlxtend.

Flujo:
    1. Transformar el dataset tabular en "transacciones" (cada fila = conjunto de ítems 'columna=valor').
    2. Encontrar los conjuntos de ítems frecuentes (que superan el soporte mínimo).
    3. Generar las reglas que superan la confianza mínima y calcular su lift.
    4. Guardar / listar / eliminar los resultados en storage/reglas/.

Métricas de una regla A -> B:
    - Soporte:   proporción de filas donde aparecen A y B juntos.          P(A y B)
    - Confianza: de las filas que tienen A, qué proporción también tiene B. P(B | A)
    - Lift:      cuánto más probable es B cuando ocurre A, versus al azar. Confianza / P(B)
                 lift > 1 = asociación positiva, lift = 1 = independientes, lift < 1 = negativa.
"""

import os
import json
from datetime import datetime
from itertools import combinations

import pandas as pd

from analisis.config import RUTA_REGLAS

# Registro (.json) con los metadatos de los análisis de asociación guardados
ARCHIVO_REGISTRO_REGLAS = os.path.join(RUTA_REGLAS, 'registro_reglas.json')


# =====================================================================
# 1. PREPARACIÓN: De tabla a transacciones (matriz booleana One-Hot)
# =====================================================================
# Valores que significan "ausencia" (el producto NO se compró, la condición NO se cumple)
VALORES_AUSENCIA = {"no", "0", "false", "n", "falso"}


def preparar_transacciones(df, columnas, n_intervalos=3, solo_presentes=False):
    """
    Convierte las columnas elegidas en una matriz booleana (True/False) apta para Apriori.

    - Columnas categóricas: cada valor se transforma en un ítem 'columna=valor'
      (ej. 'metodo_pago=Tarjeta').
    - Columnas numéricas: se discretizan en intervalos por cuantiles (Bajo / Medio / Alto),
      porque Apriori trabaja con ítems presentes/ausentes, no con números continuos.

    Parámetros:
        df (DataFrame): Dataset ya limpio.
        columnas (list): Columnas a incluir en el análisis.
        n_intervalos (int): Cantidad de intervalos para discretizar columnas numéricas (2 a 5).
        solo_presentes (bool): Si es True, descarta los ítems de "ausencia" (ej. 'pan=No').
            Útil en datos tipo canasta de compras, donde interesa qué productos SÍ se compran juntos.

    Retorna:
        DataFrame booleano: filas = transacciones, columnas = ítems.
    """
    etiquetas_por_n = {
        2: ["Bajo", "Alto"],
        3: ["Bajo", "Medio", "Alto"],
        4: ["Muy bajo", "Bajo", "Alto", "Muy alto"],
        5: ["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"],
    }
    datos = pd.DataFrame(index=df.index)

    for col in columnas:
        serie = df[col]
        es_numerica = pd.api.types.is_numeric_dtype(serie)
        # Una columna numérica con muy pocos valores distintos (ej. 0/1) se trata como categoría
        if es_numerica and serie.nunique() > n_intervalos:
            try:
                etiquetas = etiquetas_por_n.get(n_intervalos, [f"Q{i + 1}" for i in range(n_intervalos)])
                intervalos = pd.qcut(serie, q=n_intervalos, labels=etiquetas, duplicates='drop')
            except ValueError:
                # Si hay muchos valores repetidos, qcut no logra crear todos los intervalos
                intervalos = pd.qcut(serie.rank(method='first'), q=n_intervalos,
                                     labels=etiquetas_por_n.get(n_intervalos))
            datos[col] = intervalos.astype(str)
        else:
            datos[col] = serie.astype(str)

    # One-Hot: cada 'columna=valor' pasa a ser una columna booleana
    matriz = pd.get_dummies(datos, prefix_sep='=').astype(bool)

    if solo_presentes:
        columnas_presentes = [c for c in matriz.columns
                              if c.split('=', 1)[1].strip().lower() not in VALORES_AUSENCIA]
        matriz = matriz[columnas_presentes]
    return matriz


# =====================================================================
# 2. ALGORITMO: Apriori / FP-Growth
# =====================================================================
def _apriori_propio(matriz, min_soporte, max_longitud=None):
    """
    Implementación de respaldo del algoritmo Apriori (se usa solo si mlxtend no está instalado).
    Principio Apriori: si un conjunto de ítems NO es frecuente, ninguno de sus superconjuntos
    lo será; por eso se construyen los candidatos de tamaño k solo a partir de los frecuentes de tamaño k-1.
    """
    n = len(matriz)
    valores = matriz.values
    columnas = list(matriz.columns)
    resultados = []

    # Nivel 1: ítems individuales frecuentes
    soporte_1 = valores.mean(axis=0)
    frecuentes = [(i,) for i, s in enumerate(soporte_1) if s >= min_soporte]
    for f in frecuentes:
        resultados.append((soporte_1[f[0]], frozenset([columnas[f[0]]])))

    k = 2
    while frecuentes and (max_longitud is None or k <= max_longitud):
        # Generar candidatos uniendo conjuntos frecuentes que comparten los primeros k-2 ítems
        conjunto_frec = set(frecuentes)
        candidatos = set()
        for a, b in combinations(frecuentes, 2):
            if a[:-1] == b[:-1]:
                cand = tuple(sorted(set(a) | set(b)))
                # Poda: todos los subconjuntos de tamaño k-1 deben ser frecuentes
                if all(sub in conjunto_frec for sub in combinations(cand, k - 1)):
                    candidatos.add(cand)
        frecuentes = []
        for cand in sorted(candidatos):
            soporte = valores[:, list(cand)].all(axis=1).sum() / n
            if soporte >= min_soporte:
                frecuentes.append(cand)
                resultados.append((soporte, frozenset(columnas[i] for i in cand)))
        k += 1

    return pd.DataFrame(resultados, columns=['support', 'itemsets'])


def _reglas_propias(frecuentes, min_confianza):
    """Genera reglas A -> B a partir de los conjuntos frecuentes (respaldo sin mlxtend)."""
    soporte_de = {row.itemsets: row.support for row in frecuentes.itertuples()}
    filas = []
    for itemset, soporte_ab in soporte_de.items():
        if len(itemset) < 2:
            continue
        for r in range(1, len(itemset)):
            for antecedente in combinations(itemset, r):
                antecedente = frozenset(antecedente)
                consecuente = itemset - antecedente
                confianza = soporte_ab / soporte_de[antecedente]
                if confianza >= min_confianza:
                    lift = confianza / soporte_de[consecuente]
                    filas.append({
                        'antecedents': antecedente,
                        'consequents': consecuente,
                        'support': soporte_ab,
                        'confidence': confianza,
                        'lift': lift,
                    })
    return pd.DataFrame(filas, columns=['antecedents', 'consequents', 'support', 'confidence', 'lift'])


def generar_reglas_asociacion(df, columnas, min_soporte=0.1, min_confianza=0.5,
                              algoritmo="apriori", n_intervalos=3, max_longitud=4, solo_presentes=False):
    """
    RF4: Genera reglas de asociación a partir de las columnas seleccionadas.

    Parámetros:
        df (DataFrame): Dataset limpio.
        columnas (list): Columnas incluidas en el análisis (mínimo 2).
        min_soporte (float): Soporte mínimo (0-1) para considerar un conjunto de ítems como frecuente.
        min_confianza (float): Confianza mínima (0-1) para aceptar una regla.
        algoritmo (str): 'apriori' o 'fpgrowth'.
        n_intervalos (int): Intervalos para discretizar variables numéricas.
        max_longitud (int): Tamaño máximo de los conjuntos de ítems (controla el tiempo de cálculo).
        solo_presentes (bool): Ignorar ítems de ausencia como 'producto=No' (ver preparar_transacciones).

    Retorna:
        tuple: (éxito (bool), mensaje (str), resultado (dict o None))
    """
    if len(columnas) < 2:
        return False, "Selecciona al menos 2 columnas para buscar asociaciones entre ellas.", None

    matriz = preparar_transacciones(df, columnas, n_intervalos, solo_presentes)
    if matriz.shape[1] == 0:
        return False, "No quedaron ítems para analizar con las columnas elegidas.", None

    # Se intenta usar mlxtend (librería sugerida en el enunciado); si no está, se usa la versión propia
    motor = "mlxtend"
    try:
        from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
        funcion = fpgrowth if algoritmo == "fpgrowth" else apriori
        frecuentes = funcion(matriz, min_support=min_soporte, use_colnames=True, max_len=max_longitud)
        if frecuentes.empty:
            reglas = pd.DataFrame()
        else:
            try:
                reglas = association_rules(frecuentes, metric="confidence", min_threshold=min_confianza)
            except TypeError:
                # Algunas versiones de mlxtend (0.23.x) exigen el parámetro num_itemsets
                reglas = association_rules(frecuentes, num_itemsets=len(matriz),
                                           metric="confidence", min_threshold=min_confianza)
    except ImportError:
        motor = "Apriori propio (mlxtend no instalado)"
        frecuentes = _apriori_propio(matriz, min_soporte, max_longitud)
        reglas = _reglas_propias(frecuentes, min_confianza) if not frecuentes.empty else pd.DataFrame()

    if frecuentes.empty:
        return False, ("No se encontraron conjuntos frecuentes con ese soporte mínimo. "
                       "Prueba bajando el soporte."), None
    if reglas.empty:
        return False, ("Se encontraron conjuntos frecuentes, pero ninguna regla supera la confianza mínima. "
                       "Prueba bajando la confianza."), None

    # Tabla final legible para la interfaz
    tabla = pd.DataFrame({
        "antecedente": reglas["antecedents"].apply(lambda s: ", ".join(sorted(s))),
        "consecuente": reglas["consequents"].apply(lambda s: ", ".join(sorted(s))),
        "soporte": reglas["support"].astype(float).round(4),
        "confianza": reglas["confidence"].astype(float).round(4),
        "lift": reglas["lift"].astype(float).round(4),
        "n_items": reglas["antecedents"].apply(len) + reglas["consequents"].apply(len),
    }).sort_values(["lift", "confianza"], ascending=False).reset_index(drop=True)

    resultado = {
        "tabla_reglas": tabla,
        "columnas": columnas,
        "algoritmo": algoritmo,
        "motor": motor,
        "min_soporte": min_soporte,
        "min_confianza": min_confianza,
        "n_intervalos": n_intervalos,
        "solo_presentes": solo_presentes,
        "n_transacciones": len(matriz),
        "n_items": matriz.shape[1],
        "n_frecuentes": len(frecuentes),
    }
    return True, f"Se generaron {len(tabla)} reglas de asociación.", resultado


def filtrar_reglas(tabla, texto="", min_lift=0.0, min_confianza=0.0, orden="lift", ascendente=False):
    """
    Filtra y ordena la tabla de reglas.
    - texto: busca la palabra en el antecedente o consecuente (ej. 'abandono_cliente=Si').
    - min_lift / min_confianza: umbrales adicionales sobre los resultados ya generados.
    """
    t = tabla.copy()
    if texto:
        patron = texto.strip().lower()
        t = t[t["antecedente"].str.lower().str.contains(patron, regex=False) |
              t["consecuente"].str.lower().str.contains(patron, regex=False)]
    t = t[(t["lift"] >= min_lift) & (t["confianza"] >= min_confianza)]
    return t.sort_values(orden, ascending=ascendente).reset_index(drop=True)


# =====================================================================
# 3. GESTIÓN: guardar, listar y eliminar resultados
# =====================================================================
def asegurar_directorio_reglas():
    """Crea storage/reglas/ y su registro JSON si no existen."""
    os.makedirs(RUTA_REGLAS, exist_ok=True)
    if not os.path.exists(ARCHIVO_REGISTRO_REGLAS):
        with open(ARCHIVO_REGISTRO_REGLAS, 'w', encoding='utf-8') as f:
            json.dump([], f)


def listar_reglas_guardadas():
    """Retorna la lista de metadatos de los análisis de asociación guardados."""
    asegurar_directorio_reglas()
    try:
        with open(ARCHIVO_REGISTRO_REGLAS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def guardar_reglas(nombre_personalizado, resultado, nombre_dataset, tabla=None):
    """
    Guarda un análisis de asociación: la tabla de reglas en CSV y sus metadatos en el registro JSON.
    Si se entrega 'tabla', se guarda esa versión (por ejemplo, ya filtrada por el usuario).
    """
    asegurar_directorio_reglas()
    tabla = resultado["tabla_reglas"] if tabla is None else tabla

    id_reglas = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_csv = f"reglas_{id_reglas}.csv"
    tabla.to_csv(os.path.join(RUTA_REGLAS, nombre_csv), index=False, encoding='utf-8')

    mejor = tabla.iloc[0] if not tabla.empty else None
    registro = {
        "id": id_reglas,
        "nombre": nombre_personalizado.strip() or f"Reglas_{id_reglas}",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dataset": nombre_dataset,
        "algoritmo": resultado["algoritmo"],
        "columnas": ", ".join(resultado["columnas"]),
        "min_soporte": resultado["min_soporte"],
        "min_confianza": resultado["min_confianza"],
        "cantidad_reglas": int(len(tabla)),
        "lift_maximo": float(tabla["lift"].max()) if not tabla.empty else 0.0,
        "confianza_promedio": round(float(tabla["confianza"].mean()), 4) if not tabla.empty else 0.0,
        "mejor_regla": f"{mejor['antecedente']} → {mejor['consecuente']}" if mejor is not None else "",
        "archivo_csv": nombre_csv,
    }
    registros = listar_reglas_guardadas()
    registros.append(registro)
    with open(ARCHIVO_REGISTRO_REGLAS, 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)
    return registro


def cargar_tabla_reglas(id_reglas):
    """Lee desde disco la tabla de reglas de un análisis guardado."""
    for reg in listar_reglas_guardadas():
        if reg["id"] == id_reglas:
            ruta = os.path.join(RUTA_REGLAS, reg["archivo_csv"])
            if os.path.exists(ruta):
                return pd.read_csv(ruta)
    return pd.DataFrame()


def eliminar_reglas_guardadas(id_reglas):
    """Elimina el CSV de reglas y su entrada en el registro JSON."""
    registros = listar_reglas_guardadas()
    restantes = []
    for reg in registros:
        if reg["id"] == id_reglas:
            ruta = os.path.join(RUTA_REGLAS, reg.get("archivo_csv", ""))
            if os.path.exists(ruta):
                os.remove(ruta)
        else:
            restantes.append(reg)
    with open(ARCHIVO_REGISTRO_REGLAS, 'w', encoding='utf-8') as f:
        json.dump(restantes, f, indent=4, ensure_ascii=False)
