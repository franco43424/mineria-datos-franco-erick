# Datos de ejemplo

Esta carpeta contiene archivos CSV **ficticios** para probar la plataforma sin tener que buscar datos propios.
Todos vienen **"sucios" a propósito**, igual que los datos reales: con filas repetidas, celdas vacías, textos donde debería haber números, valores imposibles y espacios de más. Así se puede ver la limpieza automática en acción.

Para usarlos: en la pestaña **1. Carga y Validación**, elige el archivo en el selector *"...o utiliza uno de los datasets de ejemplo"* y presiona **Cargar ejemplo**. También puedes descargarlos y subirlos con el botón de carga.

---

## `ejemplos/` — Archivos para usar en la plataforma

### 01_clientes_tienda.csv — ¿Qué clientes dejan de comprar?
Una tienda registra a 300 clientes y si **abandonaron** (dejaron de comprar) o no.

| Columna | Qué significa |
|---|---|
| ID Cliente | Número del cliente (no se usa para analizar) |
| Edad Cliente | Edad en años |
| Región | Región donde vive |
| Plan | Tipo de membresía: Básico, Estándar o Premium |
| Ingreso Mensual | Sueldo del cliente en pesos |
| Compras Mes | Cuántas compras hace al mes |
| Metodo Pago | Tarjeta, Transferencia o Efectivo |
| Antigüedad Meses | Hace cuántos meses es cliente |
| Reclamos | Cuántos reclamos ha hecho |
| **Abandono Cliente** | **Si / No** ← lo que se quiere predecir |

**Errores puestos a propósito:** 5 filas repetidas · celdas vacías en edad, región, ingreso, compras y método de pago · edades imposibles (120, 150 y 210 años) · sueldos exagerados (9.800.000 y 15.000.000) · la palabra "sin dato" y "s/i" en la columna de ingreso · números con espacios (" 3 ") · nombres de columna con tildes y espacios.

**Qué probar:** Árbol de decisión con objetivo `abandono_cliente`. En asociación, buscar `abandono_cliente=Si` para ver qué perfil tienen los clientes que se van (pocas compras + muchos reclamos).

---

### 02_estudiantes_notas.csv — ¿Quién aprueba el ramo?
Notas de 250 estudiantes y si **aprobaron** o **reprobaron**. Fue "guardado desde Excel en Windows", por eso usa **comas** como separador y la codificación **Latin-1** (las tildes se ven raras si lo abres con el Bloc de notas; la plataforma lo detecta y lo lee bien).

| Columna | Qué significa |
|---|---|
| ID Alumno | Código del alumno (A001, A002...) |
| Carrera | Carrera que estudia |
| Asistencia (%) | Porcentaje de asistencia a clases |
| Horas Estudio Semana | Horas que estudia por semana |
| Trabaja | Si / No |
| Promedio Tareas | Nota promedio de tareas (1,0 a 7,0) |
| Nota Prueba 1 | Nota de la primera prueba |
| **Situación Final** | **Aprobado / Reprobado** ← lo que se quiere predecir |

**Errores puestos a propósito:** 4 filas repetidas · celdas vacías · asistencias imposibles (180% y 250%) · horas de estudio exageradas (95 y 120 por semana) · textos en la columna de nota ("sin nota", "NP", "pendiente") · carreras con espacios al inicio o al final · cabeceras con espacios y paréntesis · codificación Latin-1.

**Qué probar:** Árbol de decisión con objetivo `situacion_final`. El dashboard muestra que la asistencia y la nota están relacionadas.

---

### 03_compras_supermercado.csv — ¿Qué productos se compran juntos?
400 boletas de un supermercado. Cada columna de producto dice **Si** (se compró) o **No**. Es el ejemplo clásico de **reglas de asociación** ("canasta de mercado").

| Columna | Qué significa |
|---|---|
| ID Boleta | Número de la boleta |
| Día | Día de la semana de la compra |
| Pan, Mantequilla, Leche, ... Detergente | Si / No según si el producto está en la boleta |
| Total Compra | Monto total en pesos |

**Patrones escondidos que el algoritmo debería encontrar:** Pan → Mantequilla · Café → Azúcar · Fideos → Salsa de Tomate · Cerveza ↔ Papas Fritas · Pañales → Cerveza.

**Errores puestos a propósito:** 6 boletas repetidas · celdas vacías · montos exagerados (999.999 y 1.250.000) · el texto "error caja" en el total.

**Qué probar:** En **5. Reglas de Asociación**, selecciona solo las columnas de productos, activa **"Ignorar valores de ausencia (No / 0)"** y usa soporte 5% y confianza 50%.

---

### 04_prestamos_banco.csv — ¿Se aprueba el crédito?
280 solicitudes de préstamo y si el banco las **aprobó**. Está separado con **barras verticales `|`** y tiene **líneas en blanco** entre medio, para mostrar que la validación detecta separadores poco comunes.

| Columna | Qué significa |
|---|---|
| ID Solicitud | Número de la solicitud |
| Edad | Edad del solicitante |
| Ingreso Mensual | Sueldo en pesos |
| Deuda Actual | Deuda que ya tiene, en pesos |
| Años en Empleo | Años en su trabajo actual |
| Historial Crediticio | Bueno, Regular o Malo |
| Tipo Vivienda | Propia, Arrendada o Familiar |
| **Préstamo Aprobado** | **Si / No** ← lo que se quiere predecir |

**Errores puestos a propósito:** 5 filas repetidas · celdas vacías · edades imposibles (5 y 199 años) · un ingreso de 45.000.000 · textos "no informa" y "?" en la deuda · separador `|` · líneas en blanco.

**Qué probar:** Árbol de decisión con objetivo `prestamo_aprobado`; comparar Gini vs. Entropía y distintas profundidades.

---

### 00_mini_clientes.csv — Ejemplo mínimo
El primer archivo de prueba del proyecto (20 filas). Sirve para una demostración rápida, pero por ser tan pequeño el árbol puede salir con 100% de exactitud, lo que no es realista.

---

## `pruebas_error/` — Archivos inválidos (para probar la validación)

Súbelos con el botón de carga para comprobar que la plataforma **rechaza** archivos incorrectos con un mensaje claro:

| Archivo | Mensaje esperado |
|---|---|
| error_archivo_vacio.csv | El archivo está completamente vacío (0 bytes) |
| error_una_sola_columna.csv | El CSV no contiene suficientes filas o columnas válidas |
| error_solo_encabezado.csv | El CSV no contiene suficientes filas o columnas válidas |

---

## ¿Cómo se generaron?

Con el script `generar_ejemplos.py` (datos aleatorios con semilla fija, siempre resultan iguales):

```bash
python datos/generar_ejemplos.py
```
