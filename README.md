# Clasificación de la condición laboral en Lima y Callao

Proyecto del Grupo 4 para el curso Inteligencia Artificial (1INF24). Compara regresión logística multinomial, Random Forest y XGBoost en cuatro clases de la Encuesta Permanente de Empleo Nacional de enero a marzo de 2026.

## Diseño del proyecto

El [cuaderno de pandas](01_Exploracion_Estudio_EPEN.ipynb) sigue la secuencia de `Ejemplo1_Preprocesamiento_solucionado.ipynb` y `Lab_Guiado_MLP_Forest_Classification.ipynb` del curso. Usa DataFrames para revisar dimensiones, tipos, nulos, resúmenes y frecuencia de etiquetas. La codificación de variables nominales se ajusta dentro de cada pliegue, y la separación estratificada agrupa por hogar.

`experimento.py` concentra la carga, preparación, validación y evaluación. El cuaderno importa esa preparación para que los filtros de la exploración sean los mismos que usa el experimento. Consulta [los archivos oficiales y su propósito](datos/README.md).

## Reproducir el experimento

Desde este directorio, con Python 3.14:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe experimento.py --salida corrida-local
.\.venv\Scripts\python.exe -m unittest discover -s pruebas -v
```

El programa usa `datos/1029-Modulo76.zip` y lo descarga del INEI si falta. Puedes indicar otra ubicación del mismo ZIP con `--archivo`. Las pruebas verifican el filtro del código de edad 99, la separación por hogar y la coherencia entre las matrices y los puntajes publicados.

Para abrir el cuaderno en JupyterLab usando el mismo entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install jupyterlab
.\.venv\Scripts\python.exe -m jupyterlab 01_Exploracion_Estudio_EPEN.ipynb
```

## Resultados

- [Resultados de prueba](resultados/resultados.json) con la huella SHA-256 del ZIP, métricas, matrices, intervalos, versiones y tiempos.
- [Búsqueda de hiperparámetros](resultados/validacion.csv) con las 38 configuraciones evaluadas.
- [Importancia por permutación](resultados/importancia.csv), medida como caída del F1 ponderado.
- [Matrices de confusión](resultados/matrices.png), con observaciones en filas y predicciones en columnas. Los códigos 1, 2, 3 y 4 corresponden a ocupado, desocupado abierto, desocupado oculto e inactivo pleno. El color representa la proporción dentro de cada fila. Figura generada mediante código desarrollado con asistencia de ChatGPT (OpenAI).
