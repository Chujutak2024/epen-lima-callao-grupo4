# Clasificación de la condición laboral en Lima y Callao

Proyecto del Grupo 4 para el curso Inteligencia Artificial (1INF24). Compara regresión logística multinomial, Random Forest y XGBoost en cuatro clases de la Encuesta Permanente de Empleo Nacional de enero a marzo de 2026.

## Diseño del proyecto

El [cuaderno de pandas del proyecto](01_Exploracion_Estudio_EPEN.ipynb) usa DataFrames para revisar dimensiones, tipos, nulos, resúmenes y frecuencia de etiquetas. Los notebooks `Ejemplo1_Preprocesamiento_solucionado.ipynb` y `Lab_Guiado_MLP_Forest_Classification.ipynb` sirvieron de referencia. Son material externo del curso y su descarga es opcional para reproducir el proyecto. La codificación de variables nominales se ajusta dentro de cada pliegue y la separación estratificada agrupa por hogar.

`experimento.py` permite ejecutar la carga, preparación, validación y evaluación desde la terminal. El cuaderno contiene el mismo procedimiento para ejecutarlo en Colab con el CSV oficial. Consulta [los archivos oficiales y su propósito](datos/README.md).

Para probar el cuaderno en Colab, abre el `.ipynb`, sube `Trim Ene-Feb-Mar26.csv` al panel **Archivos** y ejecuta todas las celdas. El cuaderno genera sus salidas agregadas en `resultados_notebook/`.

## Reproducir el experimento

Se verificó con Python 3.14.4 en Windows. Desde PowerShell, con Git y Python 3.14 instalados:

```powershell
git clone https://github.com/Chujutak2024/epen-lima-callao-grupo4.git
cd epen-lima-callao-grupo4
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe experimento.py --salida corrida-local
.\.venv\Scripts\python.exe -m unittest discover -s pruebas -v
.\.venv\Scripts\python.exe generar_figuras.py --resultados corrida-local/resultados.json --salida corrida-local/figuras
```

Si ya tienes el repositorio abierto localmente, empieza con la creación del entorno. El programa usa `datos/1029-Modulo76.zip` y lo descarga del INEI si falta. Si falla la descarga automática, descarga el ZIP del [enlace oficial](datos/README.md) y colócalo en esa ruta o pasa la ubicación mediante `--archivo`. `corrida-local/` recibe los resultados de tu ejecución. Las pruebas verifican el filtro de edad, la separación por hogar, la coherencia de los resultados versionados y la correspondencia entre el CSV de validación y el JSON.

Para abrir el cuaderno en JupyterLab usando el mismo entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install jupyterlab
.\.venv\Scripts\python.exe -m jupyterlab 01_Exploracion_Estudio_EPEN.ipynb
```

## Resultados

- [Resultados de prueba](resultados/resultados.json) con la huella SHA-256 del ZIP, métricas, matrices, intervalos, versiones y tiempos.
- [Búsqueda de hiperparámetros](resultados/validacion.csv) con las 38 configuraciones evaluadas y sensibilidad media para cada clase en los cinco pliegues internos.
- [Importancia por permutación](resultados/importancia.csv), medida como caída del F1 ponderado.
- [Matrices de confusión](resultados/matrices.png), con observaciones en filas y predicciones en columnas. Los códigos 1, 2, 3 y 4 corresponden a ocupado, desocupado abierto, desocupado oculto e inactivo pleno. El color representa la proporción dentro de cada fila. Figura generada mediante código desarrollado con asistencia de ChatGPT (OpenAI).

El JSON también registra los puntajes medios y la frecuencia con que la clase verdadera figura entre los dos puntajes más altos. Son diagnósticos de prueba posteriores al ajuste. La comparación de pesos uniformes e inversos por clase se mantiene en la validación interna. [Bitácora de la revisión local](REVISION_FINAL.md).

La corrida del informe y de los resultados de esta revisión registró **91,3 s**. La [corrida inicial publicada en `da401bc`](https://github.com/Chujutak2024/epen-lima-callao-grupo4/blob/da401bc842acfcf342483e6698e4a88a7fcea585/resultados/resultados.json) registró **106,6 s**. Las dos usan el mismo ZIP y reproducen 10 199 registros, 4 313 hogares, 38 configuraciones y los mismos F1 y matrices de prueba. El tiempo de una nueva corrida depende del equipo y la carga.
