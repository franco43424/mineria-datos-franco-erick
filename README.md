#  Plataforma de Administración de Minería de Datos

¡Bienvenido! Este proyecto es una aplicación web interactiva inspirada en **Orange Data Mining**[cite: 1]. Permite a cualquier usuario subir un archivo de datos (`.csv`), limpiarlo automáticamente sin saber programar y entrenar modelos de Inteligencia Artificial (Árboles de Decisión) de forma 100% visual[cite: 1].

**Equipo de Desarrollo y Roles:** 

* **Franco Fajardo — Desarrollo Core, Procesamiento de Datos y Funcionalidad Web:**  
  Encargado de la arquitectura base, programación de los motores de minería de datos en Python (`validador.py`, `limpieza.py`, `arbol_decision.py`) y estructuración funcional de la plataforma web en Streamlit según los requerimientos del sistema.

* **Erick Mamani — Diseño de Interfaz (UI/UX), Validación y Mejora Continua:**  
  Encargado del diseño visual personalizado (`estilos.css`), refinamiento de la experiencia de usuario en la interfaz gráfica, validación de pruebas (QA), optimización visual de métricas y documentación técnica del código fuente.

---

##  ¿Qué puedes hacer en esta plataforma? (Avance 1)

1. **Subir y validar tu CSV (RF1):** Sube tu archivo y el sistema detecta solo si viene separado por comas o punto y coma, revisa el formato, las tildes y te muestra una vista previa[cite: 1].
2. **Limpieza Automática (RF2):** Olvídate de los datos rotos[cite: 1]. El programa borra filas repetidas, rellena casillas vacías (con la mediana o la moda) y corrige números exagerados o irreales (outliers) mostrándote un resumen del antes y después[cite: 1].
3. **Entrenar Árboles de Decisión (RF3):** Elige qué columna quieres predecir, ajusta la profundidad del árbol con un par de clics, mira el dibujo del árbol generado y revisa su calificación (Exactitud, Precisión, Recall y Matriz de Confusión)[cite: 1, 2].
4. **Guardar y Comparar Modelos:** Guarda tus mejores árboles entrenados para compararlos en una tabla y un gráfico de barras, o elimina los que ya no necesites[cite: 2].

---

##  ¿Cómo está organizado el proyecto? (Arquitectura por Capas)

Para mantener el orden, separamos el "cerebro matemático" de la "pantalla visual" en dos carpetas principales[cite: 2, 3]:

```text
mineria-datos-franco-erick/
├── analisis/                  # CEREBRO: Todo el procesamiento pesado en Python
│   ├── __init__.py
│   ├── validador.py           # Revisa que el CSV sea válido y detecta su separador
│   ├── limpieza.py            # Repara vacíos, borra duplicados y corrige extremos
│   └── arbol_decision.py      # Entrena el Árbol de Decisión, calcula notas y guarda modelos
├── docs/
│   └── capturas/              # Fotos de evidencia tomadas por Erick
│       ├── rf1_carga.png
│       ├── rf2_limpieza.png
│       ├── rf3_arbol.png
│       └── rf3_comparativa.png
├── web/                       # PANTALLA: La interfaz gráfica amigable
│   └── app.py                 # Página web interactiva creada con Streamlit (por pestañas)
│
├── storage/                   # MEMORIA: Donde se guardan los archivos y modelos
│   ├── datasets/              # CSV de prueba listos para usar
│   └── modelos/               # Historial de modelos guardados (.json y .pkl)
│
├── requirements.txt           # Lista de librerías que usa el proyecto
├── README.md                      # Portada e instrucciones de instalación
└── VALIDACION_QA.md               # Reporte oficial de pruebas (Checklist del profesor)
```

---

##  Herramientas que utilizamos

**Python 3 (Lenguaje de programación):** Es la base del proyecto; lo elegimos por ser el estándar en Minería de Datos.   
Captura de pantalla 2026-11-13 a la(s) 5.34.09 p.m..png

**Streamlit + CSS (Framework web y hojas de estilo):** Crean la página web y su diseño (estilos.css). Los elegimos en vez de Flask o FastAPI porque muestran tablas y gráficos de datos al instante.   

**Pandas y NumPy (Librerías de análisis de datos):** Funcionan como un Excel dentro del código; las usamos para leer el CSV, limpiar nulos, borrar repetidos y corregir outliers.

**Scikit-Learn (Librería de Machine Learning):** Es el motor de inteligencia artificial; lo usamos para entrenar el Árbol de Decisión (Gini y Entropía) y calcular sus métricas.   

**Matplotlib y Plotly (Librerías de gráficos):** Matplotlib dibuja el esquema del árbol y Plotly crea los gráficos interactivos (Matriz de Confusión y barras comparativas).

**Joblib y JSON (Formatos de almacenamiento):** Joblib guarda el modelo entrenado en un archivo .pkl y JSON (registro_modelos.json) guarda la lista de puntajes e historial en disco.   

**Git y GitHub (Control de versiones y repositorio en la nube):** Los usamos para trabajar los dos en ramas separadas (develop y main), uniendo tu código base con el diseño y las pruebas QA de Erick.


---

##  Guía rápida: ¿Cómo instalarlo y probarlo en tu computador?

Sigue estos 4 pasos en tu terminal para levantar la página web desde cero[cite: 3, 4]:

**1. Descarga el proyecto desde GitHub:**
```bash
git clone [https://github.com/franco43424/mineria-datos-franco-erick.git](https://github.com/franco43424/mineria-datos-franco-erick.git)
cd mineria-datos-franco-erick
```

**2. Crea y activa la "cápsula" del entorno virtual (`venv`):**
 **Si estás en Mac o Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
 **Si estás en Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

**3. Instala todas las librerías con un solo comando:**
```bash
pip install -r requirements.txt
```

**4. ¡Enciende la aplicación web!**
```bash
streamlit run web/app.py
```
*(Se abrirá sola una pestaña en tu navegador en `http://localhost:8501` lista para usar).*
