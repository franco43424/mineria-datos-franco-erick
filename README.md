#  Plataforma de Administración de Minería de Datos

¡Bienvenido! Este proyecto es una aplicación web interactiva inspirada en **Orange Data Mining**. Permite a cualquier usuario subir un archivo de datos (`.csv`), limpiarlo automáticamente sin saber programar, entrenar Árboles de Decisión, descubrir Reglas de Asociación, explorar los datos en un Dashboard interactivo y exportar un Informe final en HTML, todo de forma 100% visual.

**Equipo de Desarrollo y Roles:** 

* **Franco Fajardo — Desarrollo Core, Procesamiento de Datos y Funcionalidad Web:**  
  Encargado de la arquitectura base, programación de los motores de minería de datos en Python (`validador.py`, `limpieza.py`, `arbol_decision.py`, `asociacion.py`, `dashboard.py`, `informe.py`) y estructuración funcional de la plataforma web en Streamlit según los requerimientos del sistema.

* **Erick Mamani — Diseño de Interfaz (UI/UX), Validación y Mejora Continua:**  
  Encargado del diseño visual personalizado (`estilos.css`), refinamiento de la experiencia de usuario en la interfaz gráfica, validación de pruebas (QA), optimización visual de métricas y documentación técnica del código fuente.

---

##  ¿Qué puedes hacer en esta plataforma?

La aplicación está organizada en 7 pestañas que siguen el flujo de trabajo de Orange:

| Pestaña | Requerimiento | ¿Qué hace? |
|---|---|---|
| 1. Carga y Validación | RF1 | Sube tu CSV (o usa un dataset de ejemplo). El sistema detecta solo la codificación y el separador, valida formato y tamaño (máx. 50 MB) y muestra una vista previa. |
| 2. Preprocesamiento | RF2 | Limpieza automática: normaliza nombres de columnas, borra duplicados, corrige tipos de datos, trata nulos (mediana/moda o eliminación) y outliers (IQR: acotar, mediana o eliminar), con resumen del antes y después. |
| 3. Árbol de Decisión | RF3 | Elige la variable objetivo y las predictoras, ajusta criterio (Gini/Entropía), profundidad y % de prueba. Muestra el árbol, Exactitud, Precisión, Recall y Matriz de Confusión. |
| 4. Historial y Comparativa | RF3 | Guarda, lista, compara (tabla + gráfico de barras) y elimina modelos entrenados. |
| 5. Reglas de Asociación | RF4 | Configura soporte y confianza mínimos, genera reglas con **Apriori** o **FP-Growth** y revísalas con soporte, confianza y lift. Permite filtrar, ordenar, descargar, guardar, ver y eliminar resultados. |
| 6. Dashboard | RF6 | Panel interactivo con filtros dinámicos (por categorías y rangos), indicadores, histogramas, gráficos de barras, diagramas de caja, matriz de correlación y resultados de los modelos. |
| 7. Informe | RF5 | Genera un informe con resumen de datos, limpieza, modelos, reglas y conclusiones (automáticas + del equipo). Se descarga en **HTML**; desde el navegador se puede guardar como **PDF** (Imprimir → Guardar como PDF). |

Con esto se cubren los módulos mínimos de Orange exigidos (RF7): **Datos, Preprocesamiento, Visualización, Árbol de decisión y Asociación**.

---

##  ¿Cómo está organizado el proyecto? (Arquitectura por Capas)

Para mantener el orden, separamos el "cerebro matemático" de la "pantalla visual" en dos carpetas principales:

```text
mineria-datos-franco-erick/
├── analisis/                  # CAPA DE PROCESAMIENTO Y ANÁLISIS (Python)
│   ├── __init__.py
│   ├── validador.py           # RF1: Revisa que el CSV sea válido y detecta codificación y separador
│   ├── limpieza.py            # RF2: Repara vacíos, borra duplicados, corrige tipos y extremos
│   ├── arbol_decision.py      # RF3: Entrena el Árbol de Decisión, calcula métricas y gestiona modelos
│   ├── asociacion.py          # RF4: Reglas de asociación (Apriori / FP-Growth) y gestión de resultados
│   ├── dashboard.py           # RF6: Filtros, indicadores, correlaciones y estadísticas del dashboard
│   └── informe.py             # RF5: Construye el informe HTML con gráficos y conclusiones
├── web/                       # CAPA DE APLICACIÓN WEB (Streamlit)
│   ├── app.py                 # Interfaz interactiva por pestañas
│   └── estilos.css            # Diseño visual personalizado
├── storage/                   # PERSISTENCIA (archivos)
│   ├── datasets/              # CSV de ejemplo (datos_sucios_prueba.csv, clientes_abandono.csv)
│   ├── modelos/               # Modelos guardados (.pkl) y registro_modelos.json
│   └── reglas/                # Reglas guardadas (.csv) y registro_reglas.json (se crea solo)
├── docs/
│   └── capturas/              # Evidencias de las pruebas
├── requirements.txt           # Librerías del proyecto
├── README.md                  # Portada e instrucciones de instalación
└── VALIDACION_QA.md           # Reporte de pruebas (checklist)
```

### Comunicación entre capas

Elegimos **Python para ambas capas** (opción permitida por el enunciado). La comunicación es mediante **importación directa de módulos**: `web/app.py` importa las funciones de `/analisis` (por ejemplo `limpiar_dataset_automatico()` o `generar_reglas_asociacion()`), les entrega un `DataFrame` de pandas y recibe los resultados como diccionarios/DataFrames, que luego dibuja con Plotly. La capa web **no realiza cálculos**: solo muestra y gestiona.

Los resultados persistentes se intercambian como archivos: **pickle** (`.pkl`) para los modelos, **JSON** para los registros e historial y **CSV** para las reglas guardadas.

---

##  Herramientas que utilizamos

**Python 3 (Lenguaje de programación):** Es la base del proyecto; lo elegimos por ser el estándar en Minería de Datos.   

**Streamlit + CSS (Framework web y hojas de estilo):** Crean la página web y su diseño (`estilos.css`). Los elegimos en vez de Flask o FastAPI porque muestran tablas y gráficos de datos al instante.   

**Pandas y NumPy (Librerías de análisis de datos):** Funcionan como un Excel dentro del código; las usamos para leer el CSV, limpiar nulos, borrar repetidos, corregir outliers, filtrar y calcular correlaciones.

**Scikit-Learn (Librería de Machine Learning):** Es el motor de inteligencia artificial; lo usamos para entrenar el Árbol de Decisión (Gini y Entropía) y calcular sus métricas.   

**mlxtend (Librería de reglas de asociación):** Implementa los algoritmos Apriori y FP-Growth y el cálculo de soporte, confianza y lift. Si no estuviera instalada, `asociacion.py` usa una implementación propia de Apriori como respaldo.

**Matplotlib y Plotly (Librerías de gráficos):** Matplotlib dibuja el esquema del árbol y los gráficos del informe; Plotly crea los gráficos interactivos (matriz de confusión, comparativas, mapa de reglas y dashboard).

**Pickle y JSON (Formatos de almacenamiento):** `pickle` guarda el modelo entrenado en un archivo `.pkl` y JSON (`registro_modelos.json`, `registro_reglas.json`) guarda el historial en disco.   

**Git y GitHub (Control de versiones y repositorio en la nube):** Trabajamos con ramas `main`, `develop` y ramas por funcionalidad, integrando el código base con el diseño y las pruebas QA.

---

##  Guía rápida: ¿Cómo instalarlo y probarlo en tu computador?

Sigue estos 4 pasos en tu terminal para levantar la página web desde cero:

**1. Descarga el proyecto desde GitHub:**
```bash
git clone https://github.com/franco43424/mineria-datos-franco-erick.git
cd mineria-datos-franco-erick
```

**2. Crea y activa el entorno virtual (`venv`):**

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

---

##  Flujo de uso recomendado (demo)

1. **Pestaña 1:** selecciona `clientes_abandono.csv` en el selector de ejemplos y presiona **Cargar ejemplo** (300 clientes con datos "sucios" a propósito: duplicados, vacíos, textos en columnas numéricas y valores extremos).
2. **Pestaña 2:** revisa el resumen de limpieza y prueba las distintas estrategias.
3. **Pestaña 3:** predice `abandono_cliente`, entrena con Gini y con Entropía y guarda ambos modelos.
4. **Pestaña 4:** compara los modelos guardados.
5. **Pestaña 5:** genera reglas (soporte 10%, confianza 60%) y busca `abandono_cliente=Si` para ver qué perfiles se asocian al abandono. Guarda el resultado.
6. **Pestaña 6:** filtra por plan o método de pago y observa cómo cambian los gráficos.
7. **Pestaña 7:** escribe las conclusiones del equipo, genera el informe y descárgalo en HTML.
