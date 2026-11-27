# Guía para sacar las capturas de QA (Entrega final)

Las pruebas automáticas ya están hechas (`python -m pytest -v`). Faltan las **capturas de la aplicación funcionando**, que solo se pueden sacar con la app abierta en el navegador.

## Antes de empezar

1. Abre la terminal en la carpeta del proyecto y enciende la app:
   ```bash
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run web/app.py
   ```
2. Pon el navegador en **pantalla completa** y con el zoom en 90% o 100% (Cmd/Ctrl + 0), para que entre todo en la captura.
3. Cómo capturar:
   - **Mac:** `Cmd + Shift + 4`, luego presiona la **barra espaciadora** y haz clic en la ventana del navegador (captura la ventana completa). Se guarda en el Escritorio.
   - **Windows:** `Windows + Shift + S` y selecciona el área. Pégala en Paint y guárdala como PNG.
4. **Renombra** cada imagen exactamente como dice la tabla (en minúsculas, sin espacios, terminada en `.png`) y guárdala en `docs/capturas/entrega2/`. El reporte `docs/VALIDACION_QA.md` ya tiene esos nombres, así que las imágenes aparecen solas.

## Lista de capturas (13)

| # | Nombre del archivo | Pestaña | Qué hacer | Qué debe verse en la captura |
|---|---|---|---|---|
| 1 | `rf1_carga_ejemplo.png` | 1. Carga | Elegir `01_clientes_tienda.csv` → **Cargar ejemplo** | Las 5 tarjetas (peso, codificación UTF-8, delimitador "Punto y coma", 305 filas, 10 columnas) y la tabla con celdas vacías |
| 2 | `rf1_carga_latin1.png` | 1. Carga | Elegir `02_estudiantes_notas.csv` → **Cargar ejemplo** | Codificación **LATIN-1**, delimitador **Coma** y las tildes bien escritas (Psicología, Ingeniería) |
| 3 | `rf1_error_validacion.png` | 1. Carga | Arrastrar al cuadro de carga el archivo `datos/pruebas_error/error_una_sola_columna.csv` | El mensaje rojo de error |
| 4 | `rf2_limpieza_resumen.png` | 2. Limpieza | Volver a cargar `01_clientes_tienda.csv`, ir a la pestaña 2 con las opciones por defecto | Tarjetas (300 registros, 5 duplicados...) y el registro de auditoría con nulos y outliers |
| 5 | `rf2_limpieza_eliminar.png` | 2. Limpieza | Cambiar ambas opciones a **Eliminación** / **Descartar la fila** | Cómo baja la cantidad de registros resultantes |
| 6 | `rf3_arbol_metricas.png` | 3. Árbol | Volver las opciones de la pestaña 2 a las por defecto. Objetivo `abandono_cliente`, Gini, profundidad 3, prueba 25% → **Ejecutar entrenamiento** | Las 4 tarjetas de métricas, el dibujo del árbol y la matriz de confusión |
| 7 | `rf3_historial.png` | 4. Historial | En la pestaña 3, guardar el modelo como "Árbol Gini prof 3"; cambiar a Entropía, entrenar y guardar como "Árbol Entropía prof 3". Ir a la pestaña 4 | La tabla con los 2 modelos y el gráfico de barras comparativo |
| 8 | `rf4_reglas_config.png` | 5. Asociación | Cargar `03_compras_supermercado.csv`. En la pestaña 5: en "Columnas a analizar" quitar `dia` (dejar solo los productos), activar **Ignorar valores de ausencia**, soporte 0,05, confianza 0,50, máximo 2 ítems → **Generar reglas** | Los parámetros y las tarjetas de resultados (reglas generadas, conjuntos frecuentes...) |
| 9 | `rf4_reglas_filtradas.png` | 5. Asociación | En "Buscar ítem" escribir `cerveza=Si` y ordenar por confianza | La tabla filtrada (cerveza → papas fritas) y el mapa soporte vs. confianza |
| 10 | `rf4_reglas_guardadas.png` | 5. Asociación | Borrar el filtro, escribir el nombre "Canasta supermercado" → **Guardar reglas**. Luego en la lista de guardados → **Ver reglas** | La tabla de resultados guardados y las reglas abiertas |
| 11 | `rf6_dashboard_filtros.png` | 6. Dashboard | Cargar `01_clientes_tienda.csv` (pasar por la pestaña 2). En el dashboard: segmentar por `abandono_cliente`, filtrar `plan` dejando solo **Básico** | Los filtros, las tarjetas recalculadas y el histograma |
| 12 | `rf6_dashboard_correlacion.png` | 6. Dashboard | Bajar en la misma pestaña | Matriz de correlación, relaciones más fuertes y resultados de los modelos |
| 13 | `rf5_informe_vista_previa.png` | 7. Informe | Escribir una conclusión del equipo → **Generar informe** | El botón "Descargar informe (.html)" y la vista previa del informe |

**Opcional (PDF):** descarga el informe, ábrelo en el navegador, `Cmd/Ctrl + P` → **Guardar como PDF** y guárdalo como `docs/qa/informe_ejemplo.pdf`.

## Al terminar

1. Revisa `docs/VALIDACION_QA.md` en GitHub: deben verse todas las imágenes.
2. Cambia los `[ ]` por `[x]` en los puntos que ya tienen su captura.
3. Haz el commit (idealmente desde la cuenta de Erick, que está a cargo del QA).
