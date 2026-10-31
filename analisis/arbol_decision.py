import os
import json
import pickle
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

# Ruta donde se guardarán los modelos (.pkl) y el registro (.json)
RUTA_MODELOS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage', 'modelos'))
ARCHIVO_REGISTRO = os.path.join(RUTA_MODELOS, 'registro_modelos.json')

def asegurar_directorio_modelos():
    os.makedirs(RUTA_MODELOS, exist_ok=True)
    if not os.path.exists(ARCHIVO_REGISTRO):
        with open(ARCHIVO_REGISTRO, 'w', encoding='utf-8') as f:
            json.dump([], f)

def entrenar_arbol_decision(df, col_objetivo, cols_predictoras, criterio='gini', max_depth=3, test_size=0.2, random_state=42):
    """
    RF3: Entrena un Árbol de Decisión, calcula métricas (exactitud, precisión, recall, matriz de confusión)
    y genera la figura visual del árbol.
    """
    if not cols_predictoras:
        return False, "Debes seleccionar al menos una variable predictora.", None

    df_modelo = df[cols_predictoras + [col_objetivo]].dropna().copy()

    # Separar variables predictoras (X) y variable objetivo (y)
    X_raw = df_modelo[cols_predictoras]
    y_raw = df_modelo[col_objetivo].astype(str)

    # Validar que la variable objetivo sea de clasificación (no tenga demasiadas clases únicas sueltas)
    clases_unicas = sorted(y_raw.unique().tolist())
    if len(clases_unicas) < 2:
        return False, "La variable objetivo debe tener al menos 2 categorías distintas para clasificar.", None
    if len(clases_unicas) > 15:
        return False, f"La variable '{col_objetivo}' tiene {len(clases_unicas)} valores distintos. Elige una variable categórica (ej. abandono_cliente o metodo_pago).", None

    # Convertir variables predictoras de texto a numéricas (One-Hot Encoding)
    X_encoded = pd.get_dummies(X_raw, drop_first=False)
    nombres_features = X_encoded.columns.tolist()

    # División entrenamiento / prueba
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y_raw, test_size=test_size, random_state=random_state
        )
    except Exception as e:
        return False, f"Error al dividir datos de entrenamiento y prueba: {str(e)}", None

    # Crear y entrenar el Árbol de Decisión
    modelo = DecisionTreeClassifier(
        criterion=criterio,
        max_depth=max_depth,
        random_state=random_state
    )
    modelo.fit(X_train, y_train)

    # Predicciones sobre el conjunto de prueba
    y_pred = modelo.predict(X_test)

    # Calcular las 4 métricas exigidas en RF3
    exactitud = round(float(accuracy_score(y_test, y_pred)), 4)
    precision = round(float(precision_score(y_test, y_pred, average='weighted', zero_division=0)), 4)
    recall = round(float(recall_score(y_test, y_pred, average='weighted', zero_division=0)), 4)
    matriz_conf = confusion_matrix(y_test, y_pred, labels=clases_unicas).tolist()

    # Generar gráfico visual del árbol
    fig, ax = plt.subplots(figsize=(14, 7), dpi=150)
    plot_tree(
        modelo,
        feature_names=nombres_features,
        class_names=clases_unicas,
        filled=True,
        rounded=True,
        fontsize=9,
        ax=ax
    )
    plt.tight_layout()

    resultado = {
        "modelo_obj": modelo,
        "figura_arbol": fig,
        "col_objetivo": col_objetivo,
        "cols_predictoras": cols_predictoras,
        "criterio": criterio,
        "max_depth": max_depth,
        "test_size": test_size,
        "filas_entrenamiento": len(X_train),
        "filas_prueba": len(X_test),
        "clases": clases_unicas,
        "exactitud": exactitud,
        "precision": precision,
        "recall": recall,
        "matriz_confusion": matriz_conf
    }

    return True, "Árbol de decisión entrenado correctamente.", resultado

def guardar_modelo(nombre_personalizado, resultado_entrenamiento, nombre_dataset):
    """Guarda el objeto del modelo en .pkl y sus métricas en registro_modelos.json"""
    asegurar_directorio_modelos()
    
    id_modelo = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo_pkl = f"arbol_{id_modelo}.pkl"
    ruta_pkl = os.path.join(RUTA_MODELOS, nombre_archivo_pkl)

    # Guardar archivo binario Pickle
    with open(ruta_pkl, 'wb') as f:
        pickle.dump(resultado_entrenamiento["modelo_obj"], f)

    # Guardar metadatos en JSON para listar y comparar
    nuevo_registro = {
        "id": id_modelo,
        "nombre": nombre_personalizado if nombre_personalizado.strip() else f"Modelo_{id_modelo}",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dataset": nombre_dataset,
        "variable_objetivo": resultado_entrenamiento["col_objetivo"],
        "variables_predictoras": ", ".join(resultado_entrenamiento["cols_predictoras"]),
        "criterio": resultado_entrenamiento["criterio"],
        "profundidad_max": resultado_entrenamiento["max_depth"],
        "division_prueba": f"{int(resultado_entrenamiento['test_size'] * 100)}%",
        "exactitud": resultado_entrenamiento["exactitud"],
        "precision": resultado_entrenamiento["precision"],
        "recall": resultado_entrenamiento["recall"],
        "archivo_pkl": nombre_archivo_pkl
    }

    registros = listar_modelos_guardados()
    registros.append(nuevo_registro)

    with open(ARCHIVO_REGISTRO, 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)

    return nuevo_registro

def listar_modelos_guardados():
    """Retorna la lista de todos los modelos guardados para mostrarlos y compararlos."""
    asegurar_directorio_modelos()
    try:
        with open(ARCHIVO_REGISTRO, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def eliminar_modelo_guardado(id_modelo):
    """Elimina el registro del JSON y borra el archivo .pkl correspondiente."""
    asegurar_directorio_modelos()
    registros = listar_modelos_guardados()
    nuevos_registros = []
    
    for reg in registros:
        if reg["id"] == id_modelo:
            ruta_pkl = os.path.join(RUTA_MODELOS, reg.get("archivo_pkl", ""))
            if os.path.exists(ruta_pkl):
                os.remove(ruta_pkl)
        else:
            nuevos_registros.append(reg)

    with open(ARCHIVO_REGISTRO, 'w', encoding='utf-8') as f:
        json.dump(nuevos_registros, f, indent=4, ensure_ascii=False)