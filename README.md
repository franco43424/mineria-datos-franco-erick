#  Plataforma de Administración de Minería de Datos

¡Bienvenido! Este proyecto es una aplicación web interactiva inspirada en **Orange Data Mining**[cite: 1]. Permite a cualquier usuario subir un archivo de datos (`.csv`), limpiarlo automáticamente sin saber programar y entrenar modelos de Inteligencia Artificial (Árboles de Decisión) de forma 100% visual[cite: 1].

**Desarrollado por:** 

**Franco Fajardo** — Desarrollador Core y Arquitectura del Sistema (Backend & Integración Web):
Responsabilidad principal: Construir la estructura del proyecto y programar desde cero los módulos funcionales en Python y su conexión con la aplicación web según los requerimientos del profesor.   

**Tareas en el proyecto:** Desarrollo de los algoritmos de validación (validador.py), limpieza automática (limpieza.py), entrenamiento y persistencia de modelos (arbol_decision.py), lógica funcional de las vistas en Streamlit (web/app.py) y creación de los próximos módulos (Reglas de Asociación, Informes y Dashboard).   

  
**Erick Mamani** — Encargado de Interfaz (UI/UX), QA (Validación) y Mejora Continua:
Responsabilidad principal: Tomar los módulos funcionales construidos por Franco, auditarlos, refinar la experiencia visual del usuario y documentar técnicamente el código.   
  
**Tareas en el proyecto:** Diseño y estilizado visual mediante hojas de estilo (web/estilos.css) y componentes HTML/CSS en Streamlit, pruebas de validación de calidad, optimización de gráficos interactivos y redacción de documentación interna (docstrings y comentarios explicativos en todo el código).

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
│
├── web/                       # PANTALLA: La interfaz gráfica amigable
│   └── app.py                 # Página web interactiva creada con Streamlit (por pestañas)
│
├── storage/                   # MEMORIA: Donde se guardan los archivos y modelos
│   ├── datasets/              # CSV de prueba listos para usar
│   └── modelos/               # Historial de modelos guardados (.json y .pkl)
│
├── requirements.txt           # Lista de librerías que usa el proyecto
└── README.md                  # Esta guía de uso
```

---

##  Herramientas que utilizamos

 **Python 3** como lenguaje principal de principio a fin[cite: 1, 2].
 **Streamlit** para crear la interfaz web rápida y por pestañas.
 **Pandas y NumPy** para limpiar y ordenar las tablas de datos[cite: 3].
 **Scikit-Learn** para entrenar los Árboles de Decisión[cite: 3].
 **Plotly y Matplotlib** para dibujar los gráficos interactivos y el mapa del árbol[cite: 3].

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
