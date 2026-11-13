"""
Módulo: arbol_decision.py
Propósito: Gestionar el entrenamiento, evaluación, visualización y persistencia 
de modelos de clasificación basados en Árboles de Decisión.
"""

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
    """
    Verifica que el directorio de almacenamiento de modelos exista.
    Si no existe, lo crea junto con un archivo JSON vacío para el registro histórico.
    """
    os.makedirs(RUTA_MODELOS, exist_ok=True)
    if not os.path.exists(ARCHIVO_REGISTRO):
        with open(ARCHIVO_REGISTRO, 'w', encoding='utf-8') as f:
            json.dump([], f)

def entrenar_arbol_decision(df, col_objetivo, cols_predictoras, criterio='gini', max_depth=3, test_size=0.2, random_state=42):
    """
    RF3: Entrena un modelo predictivo utilizando el algoritmo de Árbol de Decisión.
    
    Parámetros:
        df (DataFrame): Conjunto de datos original.
        col_objetivo (str): El nombre de la columna que el modelo intentará predecir (Target/Clase).
        cols_predictoras (list): Lista de nombres de columnas usadas para predecir (Features).
        criterio (str): Medida de calidad de la división ('gini' o 'entropy').
        max_depth (int): Profundidad máxima permitida para el árbol (controla el sobreajuste/overfitting).
        test_size (float): Proporción del dataset reservada para pruebas (ej. 0.2 = 20%).
        random_state (int): Semilla para garantizar la reproducibilidad de los resultados.
        
    Retorna:
        tuple: (éxito (bool), mensaje (str), resultados (dict o None))
    """
    if not cols_predictoras:
        return False, "Debes seleccionar al menos una variable predictora.", None

    # Limpieza previa: Se eliminan filas con valores nulos (NaN) exclusivamente en las columnas seleccionadas
    # para evitar errores matemáticos durante el entrenamiento.
    df_modelo = df[cols_predictoras + [col_objetivo]].dropna().copy()

    # Separar variables predictoras (X - Atributos independientes) y variable objetivo (y - Etiqueta dependiente)
    X_raw = df_modelo[cols_predictoras]
    y_raw = df_modelo[col_objetivo].astype(str)

    # Validar que la variable objetivo sea adecuada para un problema de clasificación
    # (Clasificación requiere predecir categorías discretas, no valores continuos infinitos)
    clases_unicas = sorted(y_raw.unique().tolist())
    if len(clases_unicas) < 2:
        return False, "La variable objetivo debe tener al menos 2 categorías distintas para clasificar.", None
    if len(clases_unicas) > 15:
        return False, f"La variable '{col_objetivo}' tiene {len(clases_unicas)} valores distintos. Elige una variable categórica (ej. abandono_cliente o metodo_pago).", None

    # Transformación de datos (One-Hot Encoding):
    # Convierte variables predictoras categóricas (texto) en múltiples variables binarias (0 y 1).
    # Esto es crucial porque scikit-learn requiere matrices numéricas para sus cálculos algebraicos.
    X_encoded = pd.get_dummies(X_raw, drop_first=False)
    nombres_features = X_encoded.columns.tolist()

    # División del dataset (Holdout Method):
    # Se particiona aleatoriamente en un conjunto de Entrenamiento (Train) para construir el modelo
    # y un conjunto de Prueba (Test) para evaluar su capacidad de generalización con datos nuevos.
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X_encoded, y_raw, test_size=test_size, random_state=random_state
        )
    except Exception as e:
        return False, f"Error al dividir datos de entrenamiento y prueba: {str(e)}", None

    # Instanciación y entrenamiento del algoritmo del Árbol de Decisión
    modelo = DecisionTreeClassifier(
        criterion=criterio,
        max_depth=max_depth,
        random_state=random_state
    )
    # FASE DE APRENDIZAJE: El modelo encuentra los patrones en los datos de entrenamiento
    modelo.fit(X_train, y_train)

    # FASE DE INFERENCIA: El modelo hace predicciones sobre los datos ocultos (Test)
    y_pred = modelo.predict(X_test)

    # Evaluación del rendimiento del modelo utilizando métricas estándar de Machine Learning
    # Exactitud (Accuracy): Porcentaje total de predicciones correctas.
    exactitud = round(float(accuracy_score(y_test, y_pred)), 4)
    # Precisión (Precision): Proporción de identificaciones positivas que fueron realmente correctas.
    precision = round(float(precision_score(y_test, y_pred, average='weighted', zero_division=0)), 4)
    # Sensibilidad (Recall): Proporción de positivos reales que se identificaron correctamente.
    recall = round(float(recall_score(y_test, y_pred, average='weighted', zero_division=0)), 4)
    # Matriz de Confusión: Tabla que resume los Verdaderos/Falsos Positivos y Negativos.
    matriz_conf = confusion_matrix(y_test, y_pred, labels=clases_unicas).tolist()

    # Generación de la visualización estructural del árbol generado
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

    # Empaquetado de todos los artefactos y métricas resultantes
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
    """
    Serializa y guarda el objeto del modelo entrenado de forma persistente.
    Usa 'pickle' para el binario del modelo y actualiza un JSON con los metadatos y métricas.
    """
    asegurar_directorio_modelos()
    
    # Generar un identificador único basado en la marca de tiempo (timestamp)
    id_modelo = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo_pkl = f"arbol_{id_modelo}.pkl"
    ruta_pkl = os.path.join(RUTA_MODELOS, nombre_archivo_pkl)

    # Guardar archivo binario Pickle (serialización del objeto en Python)
    with open(ruta_pkl, 'wb') as f:
        pickle.dump(resultado_entrenamiento["modelo_obj"], f)

    # Preparar los metadatos para el registro JSON (útil para auditoría y comparación de modelos)
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

    # Leer el registro histórico, añadir el nuevo y reescribir
    registros = listar_modelos_guardados()
    registros.append(nuevo_registro)

    with open(ARCHIVO_REGISTRO, 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)

    return nuevo_registro

def listar_modelos_guardados():
    """
    Lee y retorna la lista de todos los metadatos de modelos previamente guardados 
    desde el archivo JSON. Se utiliza para poblar tablas comparativas en la interfaz web.
    """
    asegurar_directorio_modelos()
    try:
        with open(ARCHIVO_REGISTRO, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def eliminar_modelo_guardado(id_modelo):
    """
    Busca y elimina de forma permanente tanto el archivo binario (.pkl) 
    como el registro de metadatos (.json) asociado a un ID específico.
    """
    asegurar_directorio_modelos()
    registros = listar_modelos_guardados()
    nuevos_registros = []
    
    for reg in registros:
        if reg["id"] == id_modelo:
            # Eliminar el archivo físico (Pickle)
            ruta_pkl = os.path.join(RUTA_MODELOS, reg.get("archivo_pkl", ""))
            if os.path.exists(ruta_pkl):
                os.remove(ruta_pkl)
        else:
            # Mantener los registros que no coinciden con el ID a eliminar
            nuevos_registros.append(reg)

    # Actualizar el archivo JSON con los registros restantes
    with open(ARCHIVO_REGISTRO, 'w', encoding='utf-8') as f:
        json.dump(nuevos_registros, f, indent=4, ensure_ascii=False)