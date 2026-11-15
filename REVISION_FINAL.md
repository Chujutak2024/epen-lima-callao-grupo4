# Revisión de la tarea académica final del Grupo 4

El informe final conserva la discusión ampliada sobre la capacidad de los modelos para identificar la desocupación. El PDF y el Word de cuatro páginas se conservan localmente en `version_anterior/`. El PDF de respaldo es idéntico al original según su huella SHA-256. La versión de siete páginas usada como base también se conserva localmente con el sufijo `-Revisado`.

## Fuentes y cambios académicos

La ampliación anterior partió del informe de cuatro páginas y comparó `GRUPOX-TA-PARCIAL-V2.docx.pdf` (Unidad 6), `GRUPO4-TA-PARCIAL.pdf`, `1INF24-Guia-TA-2026-2.pdf` y `Formato de Informe de Tarea Académica.docx`. El cierre partió de `Grupo4-TA-Final-Revisado.docx` y se limitó al enlace y el acceso al repositorio, la procedencia de los tiempos, los campos de aportes y el vínculo directo de Ding et al.

- **P1, problema y justificación.** Recuperé del Parcial V2 el crecimiento interanual de 4,7 % en ocupación, verificado en el boletín del INEI, la brecha entre la clasificación oficial y la señal disponible en perfiles indirectos, y el aporte del diagnóstico por categoría.
- **P2, pregunta e hipótesis.** La pregunta nombra los tres modelos y las tres medidas de evaluación. Se mantuvo la hipótesis comparativa en F1 ponderado y se conservaron los objetivos general y específicos.
- **P3, antecedentes.** Recuperé a Silva y Fernandes del Parcial V2. El artículo original distingue 540 entrevistas totales, 378 para entrenamiento y 162 para prueba. El informe mantiene a Ezzaaime y Traka, y conserva el antecedente censal de Ding incluido en el Final anterior. Describe objetivos, datos, categorías, métricas y relación con el proyecto en los cuatro casos.
- **P4, metodología.** Recuperé la formulación de entrada, transformación y salida, y mantuve el flujo experimental. Detallé la clave de hogar, el preprocesamiento por pliegue, la codificación y la cuadrícula que realmente ejecuta el código.
- **P5, redacción y formato.** Se normalizaron las citas por orden de aparición y los registros bibliográficos con enlaces a fuentes primarias. Se conservaron la doble columna, Montserrat, los encabezados y elementos de la plantilla PUCP. Las figuras indican la asistencia de IA.
- **Discusión, ética y conclusiones.** Se analizó la sensibilidad nula en desocupación, el peso de las clases frecuentes, la regla de máximo puntaje, la comparación de estrategias de ponderación y los riesgos de aplicación individual. Se precisaron los límites del análisis por sexo y de la importancia por permutación.

## Ejecución y comprobaciones

Se repitió la cuadrícula completa de 38 configuraciones sobre el ZIP oficial `1029-Modulo76.zip`, con huella SHA-256 `be4b7725f69681599a50e96f23ae27e4c7c30fbec2289e2f760d4c4e5644b6d0`. La nueva corrida utilizó Windows, Python 3.14.4, pandas 2.3.3, scikit-learn 1.7.2 y XGBoost 3.1.3. Las demás versiones constan en `requirements.txt` y `resultados/resultados.json`.

- El CSV contiene 13 587 registros y 129 columnas. Tras los filtros quedaron 10 199 personas de 4 313 hogares. La distribución de las clases 1–4 fue 6 111, 475, 152 y 3 461.
- Entrenamiento y prueba reunieron 8 205 y 1 994 registros respectivamente, en 3 452 y 861 hogares. Se comprobó que no comparten hogares y que los cinco pliegues internos respetan el agrupamiento. Las transformaciones se ajustan dentro de cada pliegue.
- Coincidieron las selecciones, los F1, las sensibilidades y matrices de prueba, los intervalos descriptivos, las importancias y las métricas por sexo con las salidas anteriores, con tolerancia numérica para redondeo de coma flotante. Los tiempos se midieron nuevamente y dependen del entorno.
- **Procedencia de los tiempos.** El [JSON de `da401bc`](https://github.com/Chujutak2024/epen-lima-callao-grupo4/blob/da401bc842acfcf342483e6698e4a88a7fcea585/resultados/resultados.json) contiene `total_seconds = 106.58799239998916` (106,6 s). El JSON que respalda el PDF revisado y el cierre contiene `total_seconds = 91.25101409998024` (91,3 s). Se contrastaron ambas salidas, sus 38 filas de validación y el CSV de importancia. Las métricas comunes se conservaron y las nuevas columnas documentan sensibilidad interna.
- XGBoost reprodujo F1 ponderado 0,718 y F1 macro 0,370, sin aciertos en los 121 casos de desocupación. Su diferencia en F1 ponderado frente a logística fue 0,104 (intervalo descriptivo de 0,084 a 0,122). El F1 macro por sexo registrado reprodujo 0,398 en hombres y 0,346 en mujeres.
- En la validación interna, el mejor XGBoost con pesos inversos obtuvo 38,5 % de sensibilidad en desocupación abierta y 22,4 % en oculta, frente a 0 % en ambas con pesos uniformes. Su F1 ponderado medio fue 0,597 frente a 0,709. Los modelos ponderados quedan comparados en validación interna.
- Para el XGBoost seleccionado, la etiqueta verdadera figuró entre los dos puntajes más altos en 4 de 93 casos abiertos y 0 de 28 ocultos. Este diagnóstico descriptivo se calculó después del ajuste. Se mantuvieron los umbrales, la selección y los conjuntos de prueba y entrenamiento.

Comandos desde la carpeta `entregable`, con el entorno del README activo:

```powershell
python experimento.py --archivo datos/1029-Modulo76.zip --salida corrida-local
python -m unittest discover -s pruebas -v
python generar_figuras.py --resultados corrida-local/resultados.json --salida corrida-local/figuras
```

Pasaron cuatro pruebas automatizadas. Se exportó el informe con Microsoft Word y se inspeccionó el PDF página por página. Se comprobó el formato de dos columnas del cuerpo, las figuras y leyendas, la lectura de tablas y fórmulas, los enlaces y el límite de páginas.

## Archivos y pendientes

- Informe local `Grupo4-TA-Final.pdf` y `Grupo4-TA-Final.docx`. La presentación sigue en `Grupo4-TA-Exposicion.pptx`.
- [Figuras del informe](figuras/), [generador de gráficos](generar_figuras.py), [resultados agregados](resultados/) y [pruebas](pruebas/).
- Se actualizaron `experimento.py`, `README.md`, `.gitignore` y las salidas de resultados. El cuaderno anterior sigue usando la misma carga y el mismo protocolo.
- Queda pendiente que el grupo complete y valide los cuatro campos de aportes. El [repositorio es público](https://github.com/Chujutak2024/epen-lima-callao-grupo4) y el docente puede consultarlo mediante la URL.
- El código, los resultados agregados y la documentación de cierre se prepararon en la rama `correcciones-finales-ta`, con `main` como base de revisión. Los informes, la presentación y los microdatos se conservan localmente. Las diapositivas mantienen las métricas principales que se comprobaron en la auditoría.
