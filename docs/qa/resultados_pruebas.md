# Resultados de las pruebas automáticas

Comando: `python -m pytest -v` · **40 de 40 pruebas aprobadas** · tiempo 2.6 s

| Código | Qué se verifica | Archivo | Resultado |
|---|---|---|---|
| QA-RF1-01 | Detecta automáticamente el separador y la codificación de cada ejemplo. `01_clientes_tienda.csv` | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-01 | Detecta automáticamente el separador y la codificación de cada ejemplo. `02_estudiantes_notas.csv` | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-01 | Detecta automáticamente el separador y la codificación de cada ejemplo. `03_compras_supermercado.csv` | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-01 | Detecta automáticamente el separador y la codificación de cada ejemplo. `04_prestamos_banco.csv` | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-02 | Un archivo Latin-1 se lee sin romper las tildes (ej. 'Situación Final', 'Psicología'). | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-03 | Las líneas en blanco dentro del archivo no generan filas vacías. | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-04 | Archivos inválidos se rechazan con un mensaje claro. `error_archivo_vacio.csv` | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-04 | Archivos inválidos se rechazan con un mensaje claro. `error_una_sola_columna.csv` | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-04 | Archivos inválidos se rechazan con un mensaje claro. `error_solo_encabezado.csv` | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-05 | Solo se aceptan archivos .csv. | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF1-06 | Se bloquean archivos que superan el límite de 50 MB. | `tests/test_rf1_carga.py` | ✅ Aprobada |
| QA-RF2-01 | Las cabeceras quedan en snake_case, sin tildes ni espacios. | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF2-02 | Se eliminan las 5 filas repetidas del ejemplo de clientes. | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF2-03 | 'ingreso_mensual' venía como texto (por 'sin dato' y 's/i') y queda numérico. | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF2-04 | Con imputación no queda ninguna celda vacía (mediana en números, moda en texto). | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF2-05 | La estrategia 'eliminar' descarta las filas incompletas. | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF2-06 | Las edades imposibles (120, 150, 210) desaparecen con las 3 estrategias de outliers. `acotar` | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF2-06 | Las edades imposibles (120, 150, 210) desaparecen con las 3 estrategias de outliers. `mediana` | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF2-06 | Las edades imposibles (120, 150, 210) desaparecen con las 3 estrategias de outliers. `eliminar` | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF2-07 | La columna ID no se considera para outliers. | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF2-08 | El resumen informa filas iniciales/finales y cada transformación. | `tests/test_rf2_limpieza.py` | ✅ Aprobada |
| QA-RF3-01 | Entrena con Gini y Entropía y entrega exactitud, precisión, recall y matriz de confusión. `gini` | `tests/test_rf3_arbol.py` | ✅ Aprobada |
| QA-RF3-01 | Entrena con Gini y Entropía y entrega exactitud, precisión, recall y matriz de confusión. `entropy` | `tests/test_rf3_arbol.py` | ✅ Aprobada |
| QA-RF3-02 | El árbol no supera la profundidad máxima configurada. | `tests/test_rf3_arbol.py` | ✅ Aprobada |
| QA-RF3-03 | Mensajes de error si no hay predictoras o el objetivo no es categórico. | `tests/test_rf3_arbol.py` | ✅ Aprobada |
| QA-RF3-04 | Gestión de modelos: guardar (.pkl + JSON), listar y eliminar. | `tests/test_rf3_arbol.py` | ✅ Aprobada |
| QA-RF4-01 | Las columnas numéricas se convierten en intervalos (Bajo / Medio / Alto). | `tests/test_rf4_asociacion.py` | ✅ Aprobada |
| QA-RF4-02 | En el supermercado descubre los patrones escondidos (Pan→Mantequilla, Cerveza→Papas Fritas...). `apriori` | `tests/test_rf4_asociacion.py` | ✅ Aprobada |
| QA-RF4-02 | En el supermercado descubre los patrones escondidos (Pan→Mantequilla, Cerveza→Papas Fritas...). `fpgrowth` | `tests/test_rf4_asociacion.py` | ✅ Aprobada |
| QA-RF4-03 | Todas las reglas cumplen soporte y confianza mínimos e incluyen lift. | `tests/test_rf4_asociacion.py` | ✅ Aprobada |
| QA-RF4-04 | La opción 'ignorar ausencias' elimina ítems como 'pan=No'. | `tests/test_rf4_asociacion.py` | ✅ Aprobada |
| QA-RF4-05 | Avisa cuando faltan columnas o los umbrales son demasiado altos. | `tests/test_rf4_asociacion.py` | ✅ Aprobada |
| QA-RF4-06 | Filtrado por texto, lift y confianza, y ordenamiento. | `tests/test_rf4_asociacion.py` | ✅ Aprobada |
| QA-RF4-07 | Gestión de resultados: guardar, listar, ver y eliminar. | `tests/test_rf4_asociacion.py` | ✅ Aprobada |
| QA-RF6-01 | Separa variables numéricas y categóricas, sin incluir el ID. | `tests/test_rf5_rf6_informe_dashboard.py` | ✅ Aprobada |
| QA-RF6-02 | Los filtros por categoría y por rango se combinan correctamente. | `tests/test_rf5_rf6_informe_dashboard.py` | ✅ Aprobada |
| QA-RF6-03 | Matriz de correlación simétrica en [-1, 1]; detecta la relación compras-reclamos. | `tests/test_rf5_rf6_informe_dashboard.py` | ✅ Aprobada |
| QA-RF6-04 | Estadísticas descriptivas de las variables numéricas. | `tests/test_rf5_rf6_informe_dashboard.py` | ✅ Aprobada |
| QA-RF5-01 | El informe HTML incluye las 5 secciones, gráficos incrustados y conclusiones. | `tests/test_rf5_rf6_informe_dashboard.py` | ✅ Aprobada |
| QA-RF5-02 | El informe se genera aunque todavía no haya modelos ni reglas. | `tests/test_rf5_rf6_informe_dashboard.py` | ✅ Aprobada |
