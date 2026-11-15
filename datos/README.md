# Insumos oficiales del INEI

Usamos el **Archivo Empleo de la EPEN de enero a marzo de 2026**, correspondiente al dominio de Lima Metropolitana, que abarca la Provincia de Lima y la Provincia Constitucional del Callao.

| Archivo | Uso |
| --- | --- |
| [1029-Modulo76.zip](https://proyectos.inei.gob.pe/iinei/srienaho/descarga/CSV/1029-Modulo76.zip) | Insumo de ejecución. El programa lee `1029-Modulo76/Trim Ene-Feb-Mar26.csv` dentro del ZIP. La descarga incluye versiones `.dta` y `.sav` del mismo archivo para Stata y SPSS. |
| [Diccionario de la EPEN de marzo de 2026](https://proyectos.inei.gob.pe/iinei/srienaho/Descarga/DocumentosMetodologicos/2026-36/Diccionario.pdf) | Documentación de códigos, variables y filtros. Es la referencia para interpretar el CSV. |
| [Informe técnico n.º 4 del INEI](https://www.inei.gob.pe/media/MenuRecursivo/boletines/boletin-epen-ene_mar-26.pdf) | Contexto y cifras poblacionales. El entrenamiento utiliza los registros del ZIP. |

## Variables y filtros

- **Población.** Año 2026, meses 01 a 03, `REGION = 1`, `RESIDENT = 1` y edad válida de 14 a 98 años. El diccionario marca `C208 = 99` como dato faltante. Entre los residentes del dominio se excluyeron dos códigos 99 y dos edades de 100, fuera del rango documentado.
- **Etiqueta.** `OCUP300` conserva los códigos 1 (ocupado), 2 (desocupado abierto), 3 (desocupado oculto) y 4 (inactivo pleno). El código 0 y los valores ausentes quedan fuera.
- **Predictores.** Edad, sexo registrado, nivel educativo, limitaciones funcionales, lengua materna y autoidentificación étnica. `REGION` y `ESTRATO` son constantes en la publicación usada.
- **Separación.** Las claves de hogar se usan en el agrupamiento. Las horas de trabajo, ingresos y preguntas que definen la condición laboral quedan fuera de los predictores.
- **Unidad de evaluación.** Las métricas describen registros de la muestra. `fa_efm26` es el factor de expansión de la encuesta, distinto de los pesos de clase usados como condición experimental.

Los archivos de datos se guardan localmente. El repositorio contiene enlaces oficiales, código y resultados agregados.
