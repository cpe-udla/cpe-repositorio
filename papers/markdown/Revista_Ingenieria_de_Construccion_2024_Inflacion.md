---
author: Revista Ingenieria de Construccion
year: 2024
title: Inflacion
source: Revista_Ingenieria_de_Construccion_2024_Inflacion.pdf
---

# Inflacion

**Author:** Revista Ingenieria de Construccion
**Year:** 2024
**Source:** Revista_Ingenieria_de_Construccion_2024_Inflacion.pdf

---

## Content

### Page 1

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
Inflation in Real Estate Development: A Time Series Analysis
of Incidental Variables on Construction Costs in Chile
Inflación en desarrollo inmobiliario: un análisis por serie de
tiempo sobre variables incidentales sobre los costos
edificatorios en Chile
Francisco Vergara-Perucich* 1 https://orcid.org/0000-0002-1930-469; Carlos Aguirre-Nuñez** https://orcid.org/0000-0001-7556-8352
* Centro Producción del Espacio, Universidad de Las Américas, Chile
** Escuela de Arquitectura, Universidad San Sebastián, Chile
Fecha de Recepción: 26/07/2023
Fecha de Aceptación: 01/04/2024
Fecha de Publicación: 30/04/2024
PAG: 96-105
Abstract
One of the expected consequences of the post-pandemic era has been the global inflationary process with multiscalar characteristics, where
construction prices in Chile have experienced unpredictable fluctuations, severely affecting various types of projects, both public and private,
from large companies to small public initiatives. On the other hand, the growing demand for housing in the midst of the housing crisis in
Chile has been hindered by the increase in material prices. In this scenario, it is relevant to generate an ecosystem of predictive models for
construction costs that take into account the external factors that influence construction costs and, therefore, the price of new homes and
public infrastructure. This study contributes to the development of this ecosystem by using a vector autoregressive (VAR) model to identify
the predictive factors that influence construction costs in Chile, particularly exploring the influence of macroeconomic variables on
construction costs by considering a set of incidental variables that are not always considered in this type of analysis and that involve
fundamentals from sectors other than construction. The methodological results allow for the testing of predictive models with a good level
of statistical significance, as well as clearly identifying those external factors that impact construction material prices.
Keywords: Inflation; construction costs; vector autoregressive (VAR); macroeconomic variables.
Resumen
Una de las consecuencias de la pandemia y su postpandemia fue un proceso inflacionario a nivel mundial, y de características multiescalares,
donde la producción de bienes y sus consecuencias en los precios de la construcción en Chile han experimentado fluctuaciones difíciles de
predecir, afectando severamente emprendimientos en esta materia de distinta naturaleza, pública y privada, de grandes empresas o pequeñas
iniciativas públicas. Por otro lado, la creciente demanda de viviendas en medio de la crisis habitacional en Chile enfrenta también el problema
del aumento en los precios de los materiales. Ante este escenario, resulta relevante generar un ecosistema de modelos predictivos de los
costos de construcción que tengan en cuenta los factores externos que inciden en el costo de construcción y, por ende, en el precio de las
nuevas viviendas y las infraestructuras públicas. Este estudio aporta a desarrollar este ecosistema mediante el de un modelo de vectores
autorregresivos (VAR) para identificar los factores predictivos que influyen en el costo de construcción en Chile, particularmente explorando
la influencia de variables macroeconómicas sobre los costos de construcción a partir de identificar un set de variables incidentales que no
siempre son consideradas para este tipo de análisis y que involucran fundamentales provenientes de sectores distintos al de la construcción.
Los resultados metodológicos permiten ensayar modelos predictivos con buen nivel de significancia estadística, además de identificar con
claridad esos factores externos que inciden sobre el precio de los materiales de la construcción.
Palabras clave: Inflación; costos edificatorios; vectores autorregresivos (VAR); variables macroeconómicas.
1 Corresponding author:
Centro Producción del Espacio, Universidad de Las Américas, Chile
Corresponding author: jvergara@udla.cl
96

### Page 2

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
1. Introducción
La pandemia de COVID-19 ha tenido un impacto significativo en los costos de construcción, tanto por los efectos en la baja de
la producción industrial, los problemas de la misma industria de la construcción, como también los cambios en los factores de logística
para su distribución. En esa lógica, diversos autores presentan efectos de este periodo. En Malasia, se identificaron como factores
relevantes, la necesidad sanitaria de dar cumplimiento a la seguridad y salud en el lugar de trabajo, la suspensión y terminación de las
construcciones, y la pérdida de productividad como factores que contribuyen al aumento de los costos de construcción (Abdullah et al.,
2021). Como consecuencia de la pandemia, se produjeron problemas financieros para los actores comerciales en la industria de la
construcción en Indonesia, dado que implementar protocolos de salud requiere costos adicionales (Larasati et al., 2021). Finalmente,
Gamil y Alhagar encontraron que los impactos más prominentes de COVID-19 en la industria de la construcción son la suspensión de
proyectos, el impacto en la mano de obra y la pérdida de empleo, el retraso en el tiempo, el aumento de costos y las implicaciones
financieras (Gamil and Alhagar, 2020). Además, la pandemia vino acompañada de una crisis inflacionaria mundial, que ha agudizo los
problemas que ya tenía el mercado de la vivienda en diversos estados. Demary plantea que los shocks en las tasas de interés impactan los
precios reales de las viviendas, lo que ha sido parte de las estrategias monetarias para hacer frente a la inflación postpandemia (Demary,
2010). Li y Zhang encontraron una relación de influencia entre la crisis de la pandemia de COVID-19 con los cambios en los precios de
la vivienda en suburbios más asequibles, ciudades más pequeñas y áreas alejadas de los centros urbanos de alta densidad y alto costo (Li
and Zhang, 2021). Botequilha (2021) encontró que durante la pandemia de COVID-19, los precios de bienes raíces en Estados Unidos
fueron impulsados principalmente por condiciones favorables en el mercado asociadas con tasas de interés bajas, y hubo una creciente
demanda de propiedades ubicadas en áreas con menor densidad de población e ingresos más bajos. En el contexto de la pandemia y la
crisis mundial de inflación, el desarrollo inmobiliario en Chile ha enfrentado desafíos significativos, los que permanecen abiertos a nuevas
interpretaciones de la relación entre el período histórico de la pandemia 2019-2023, la crisis inflacionaria y la producción de este sector
industrial.
Los precios de los materiales de construcción han sido volátiles y difíciles de predecir, afectando directamente los costos
edificatorios y, en consecuencia, el precio de las nuevas viviendas y las obras de infraestructura pública. La crisis habitacional en el país
ha exacerbado la demanda por unidades de vivienda, lo que a su vez ha aumentado la presión sobre los costos de construcción (Ministerio
de Vivienda y Urbanismo, 2022). Ante este panorama, se requiere un enfoque integral que permita anticipar y entender cómo los factores
macroeconómicos inciden en los costos de construcción y, en última instancia, en el desarrollo inmobiliario y la política habitacional. Por
sobre la mera contingencia, desarrollar estas exploraciones permite contribuir a avanzar hacia modelos predictivos precisos que ayuden
a planificar y gestionar proyectos de construcción a largo plazo. La incertidumbre en los precios de los materiales de construcción,
agravada por la crisis mundial, hace indispensable comprender cómo las variables macroeconómicas afectan el costo de construcción en
Chile. Al identificar las relaciones entre estas variables y los costos edificatorios, los desarrolladores y las autoridades podrán tomar
decisiones informadas sobre las fluctuaciones futuras a esperar y actuar con precaución ante escenarios internacionales o nacionales que
impacten en los precios de materiales. Además, el conocimiento obtenido a través de este estudio puede contribuir a la formulación de
políticas habitacionales más efectivas, abordando la problemática de la vivienda en el país.
La relación entre variables macroeconómicas y costos de construcción no es nueva en la literatura internacional, pero muy escasa
en los estudios recientes en Chile. Los estudios sugieren que varias variables macroeconómicas afectan los costos de construcción. Asuquo
y Ogwueleka encontraron que el PIB, la oferta monetaria, el tipo de cambio y la tasa de inflación tienen una relación positiva significativa
con los costos de construcción de viviendas en Nigeria; sin embargo, solo la tasa de inflación y el PIB se pueden utilizar para predecir los
costos de construcción de viviendas (Asuquo and Ogwueleka, 2019). Puci et al. encontraron que el crecimiento del PIB y la tasa de interés
impactan positivamente en la rentabilidad de las empresas que operan en el sector de la construcción, mientras que la tasa de inflación y
el tipo de cambio impactan negativamente en el rendimiento de los activos (Puci et al., 2023). Oladipo y Oni encontraron que la inflación,
el tipo de cambio, las importaciones, la tasa de interés, la oferta monetaria y la demanda de dinero tienen un efecto significativo en los
precios de los materiales de construcción en Nigeria (Oladipo and Oni, 2012). En el caso de Chile, la relación entre desarrollo minero y
desarrollo inmobiliario ha sido identificada como significativamente relevante (Idrovo-Aguirre and Contreras-Reyes, 2021); (Medina,
2021). También se ha presentado una relación estadísticamente significativa entre factores financieros internacionales y el precio de la
vivienda (Vergara-Perucich, 2022). Sin embargo, la relación entre variables macroeconómicas y costos de construcción sigue abierta a
contribuciones.
El objetivo de esta investigación es identificar las variables macroeconómicas más relevantes que afectan los costos de edificación
en Chile mediante un modelo VAR para analizar las relaciones dinámicas entre las variables seleccionadas. Esto permitirá realizar
pruebas estadísticas para validar el modelo y asegurar la robustez de los resultados. El modelo VAR capturará las relaciones dinámicas
y permitirá predecir futuras fluctuaciones en los precios de materiales de construcción. Este artículo se estructurará de la siguiente
manera: la primera sección presentará la metodología utilizada, incluyendo el enfoque de series de tiempo y el modelo VAR, junto con las
pruebas estadísticas realizadas. La segunda sección revisará la literatura existente sobre desarrollo inmobiliario y costos de construcción
en Chile, destacando la falta de investigaciones que exploren las relaciones entre variables macroeconómicas y costos edificatorios
utilizando un enfoque de series de tiempo. La tercera sección presentará los resultados obtenidos, destacando las variables
macroeconómicas más relevantes y las relaciones identificadas a través del modelo VAR. Se discutirán las implicancias para el desarrollo
inmobiliario y la política habitacional en Chile, resaltando la importancia de considerar estos factores en la planificación y toma de
decisiones. Por último, se ofrecerán conclusiones y recomendaciones para futuras investigaciones en este campo. Los resultados de este
estudio proporcionarán una comprensión más profunda de las dinámicas entre las variables macroeconómicas y los costos de construcción
97

### Page 3

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
en Chile, permitiendo una mejor planificación y gestión de proyectos de desarrollo inmobiliario en el futuro.
2. Metodología
Se utiliza un enfoque cuantitativo y técnicas econométricas para evaluar la capacidad predictiva de un conjunto de variables
macroeconómicas sobre el índice de costos de edificación en Chile. Este tipo de estudios no se han aplicado previamente sobre costos de
edificación en Chile, por esta razón las variables independientes seleccionadas son exploratorias, basadas en una revisión de literatura
que dé asidero teórico a su inclusión en la modelación. Todas las variables fueron evaluadas en sus valores originales en un comienzo,
para luego ser transformadas en series de variaciones inter-períodos, que es lo recomendable en materia de estudios de series de tiempo
buscando relaciones predictivas entre las observaciones. Para ordenar la decisión de qué variables macroeconómicas incluir, se ha optado
por la inflación (de Dios Tena et al., 2010); (Demary, 2010), tasa política monetaria (Domeij and Ellingsen, 2018); (Gelain et al., 2013);
(McDonald and Stokes, 2013) y rendimiento financiero del mercado de valores (Apostolakis and Papadopoulos, 2019); (Sabaté, 2016);
(Vergara-Perucich, 2022). Al usar una modelación econométrica por serie de tiempo se pueden pronosticar cambios en las variaciones
del índice de costos de edificación, en base a la relación (eventualmente causal) entre los patrones históricos del índice para conocer
tendencias o proyecciones futuras (Cheng et al., 2013). El modelo seleccionado para este propósito es el modelo VAR (Vector
Autoregressive).
Antes de construir el modelo VAR, se realiza una prueba de raíz unitaria conocida como ADF (Augmented Dickey-Fuller) test en
las variables incluidas en el análisis. En parte, la decisión de hacer transformar las series de variables en variaciones inter-períodos
buscaba asegurar que la prueba de raíz unitaria fuera favorable, es decir, que las variables son estacionarias. Como se puede observar
en la (Tabla 1), la mayoría de las variables tuvieron que ser ajustadas por una diferencia para lograr la estacionariedad según el test de
Dickey-Fuller. El set de datos entonces se trabaja con dicha transformación. Los resultados de la transformación de las variables se
pueden ver en la (Figura 1).
Tabla 1. Resultados del Test de Dickey-Fuller para las variables del estudio
El estudio contará con tres etapas secuenciales de modelación. En la primera etapa, se estudian variables del contexto
macroeconómico chileno, específicamente los costos de materiales y los sueldos de los trabajadores de la construcción, proporcionados por
la Cámara Chilena de la Construcción. Además, se incluyen la tasa política monetaria, el Índice de Precios al Consumidor (IPC) y el Índice
Mensual de Actividad Económica (IMACEC), proporcionados por el Banco Central de Chile (Tabla 2).
98

### Page 4

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
Figura 1. Gráfico de variables usadas para cálculo de VAR asegurando condiciones de estacionariedad
Tabla 2. Resumen de estadísticas de variables a modelar
Figura 2. Esquema de síntesis de la metodología de análisis
99

### Page 5

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
La (Figura 2) presenta una síntesis metodológica del estudio. En una primera instancia, se estima un modelo VAR con las
variables mencionadas anteriormente para determinar qué variables tienen influencia significativa sobre el índice de costos de edificación
dentro del contexto económico en Chile. En una segunda instancia, se construye un segundo modelo VAR que incluye variables relacionadas
con la tasa política monetaria de los bancos centrales, la inflación y el rendimiento de los índices agregados de las bolsas de valores de
Estados Unidos, Reino Unido, Eurozona y China. El objetivo es identificar las variables internas relevantes (del primer modelo) y las
variables externas relevantes para el análisis cruzado. En un tercer modelo VAR, se agregan tanto las variables internas como las externas
en un mismo análisis para determinar si las variables internas o externas tienen una influencia más preponderante sobre el índice de costos
de edificación. El método usado para calcular el modelo VAR es el siguiente (Ecuación 1):
(1)
Donde y representa el vector de variables endógenas en el tiempo . En este modelo VAR, se plantea como supuesto que las variables a usar
t t
están interrelacionadas. El ejercicio exploratorio busca revisar si existe validez estadística en este supuesto. Luego A, A, [...], A son
1 2 p
matrices de coeficientes que capturan la relación de retroceso entre las variables endógenas. Cada matriz Ai corresponde a un retardo
específico de las variables. Las variables , yt−2, [...], y son los valores rezagados de las variables endógenas. Estos términos representan
yt−1 t−p
los valores pasados de las variables utilizados en la predicción actual. Finalmente ϵt es el vector de errores o residuos en el tiempo t, que
representa la parte no explicada por el modelo y captura la información no incluida en las variables endógenas. Al estimar un modelo VAR,
el objetivo es encontrar los coeficientes (matrices A, A, ..., A) que minimicen la suma de los cuadrados de los residuos y que expliquen de
1 2 p
manera adecuada la dinámica de las variables endógenas. Los rezagos a incorporar en la modelación se basan en un test de selección de
orden del VAR según el criterio de Akaike. El Criterio de Información de Akaike (CIA) es una medida que se usa para comparar la bondad
de ajuste de los modelos estadísticos. El valor de CIA se interpreta donde el modelo con el valor más bajo se considera el mejor, en términos
de equilibrio entre el ajuste y la complejidad del modelo. Así, para un modelo VAR, permite identificar el número de períodos pasados que
se utilizan para predecir los valores actuales de las series temporales manteniendo idoneidad del modelo. El test que se hizo para determinar
el valor del rezago en este caso se ve en la (Tabla 3), indicando 12 rezagos
.
Tabla 3. Criterio de información de Akaike para el modelo VAR
La fórmula general para el test de Akaike tiene la siguiente notación (Ecuación 2):
(2)
Dónde:
log(L) es el logaritmo de la función de verosimilitud máxima para el modelo.
k es el número total de parámetros estimados en el modelo.
p es el número de rezagos.
3. Resultados
En primer orden, se realiza una modelación VAR para la relación causal entre el índice de costos de edificación y variables
internas en Chile, cuyos resultados se pueden ver en la (Tabla 3). Las observaciones son un total de 228, que van desde febrero de 2004
hasta enero de 2023 en variaciones mensuales, configuradas por una diferencia. Se aplicaron 12 rezagos de evaluación para estudiar cómo
las variables de precio de materiales, sueldos y salarios, tasa política monetaria del Banco Central, IPC, IPSA e IMACEC influyen sobre el
logaritmo del índice de costos de edificación.
100

### Page 6

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
Tabla 3. Resultado modelo VAR con variable internas al mercado en Chile. Observaciones = 228. Log-verosimilitud = 2941.885. R-
cuadrado = 0.316769 (R-cuadrado corregido = 0.133556). Valor p = 0.005547
Sobre los resultados de esta primera etapa del estudio, se desprenden algunos hallazgos importantes de considerar. El modelo
mostró una capacidad explicativa moderada, con un R-cuadrado de 0.316769 y un R-cuadrado corregido de 0.133556, y fue estadísticamente
significativo con un valor p de 0.005547. Los retardos de 8 meses en el Índice de Costos de Construcción presentaron un efecto negativo
significativo sobre el índice actual, indicando posibles mecanismos de autocorrección o ajustes en el mercado. Simultáneamente, los sueldos
y materiales de construcción de 8 meses atrás tuvieron un impacto positivo y significativo, reflejando su contribución directa al aumento en
los costos de construcción. En segundo orden de relevancia estadística aparece también el IPSA, indicador de rendimiento del mercado
accionario, lo que podría ser indicativo de potenciales efectos de financierización sobre el costo de edificar en Chile. Un hallazgo relevante
de este primer estudio es que ni el IPC ni la Tasa Política Monetaria terminan siendo buenos predictores de los costos de edificación.
Tabla 4. Resultado modelo VAR con variable externas al mercado en Chile para variable dependiente = Índice de Costos de Construcción
2003-2022. Observaciones T = 228. Log-verosimilitud = 4831.8503. R-cuadrado = 0.781664 (R-cuadrado corregido=0.159963). Valor p
= 0.155563
En el modelo VAR considerando factores externos al mercado de construcción chileno entre 2003 y 2022, inicialmente se aprecia
una fuerte relación explicativa, evidenciada por un R-cuadrado de 0.781664, aunque el ajuste del modelo se reduce significativamente
después de la corrección (R-cuadrado corregido = 0.159963). Los coeficientes indican la influencia de las variables externas rezagadas en
el Índice de Costos de Construcción. La Inflación de Europa (IPC Europa) con un retardo de 9 meses, los Costos de Edificación con un
retardo de 4 meses, y la Tasa Política Monetaria del Reino Unido (TPM Reino Unido) con un retardo de 4 meses, presentan los efectos más
101

### Page 7

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
fuertes y significativos sobre el índice en estudio. Además, la presencia significativa del NASDAQ al décimo, y la Tasa de Política Monetaria
de EE.UU. (TPM EEUU) y el índice SSE con sus rezagos, sugiere que estos factores son predictores relevantes y de corto plazo del Índice
de Costos de Edificación. Los coeficientes negativos para el Dow Jones (retardo de 6 meses) y Euronext (retardo de 7 meses) indican que el
aumento en sus valores estaba asociado con una disminución en el índice de costos en el período analizado. En diálogo con los resultados
del estudio interno, se evidencia una relevancia de las variables financieras internacionales en los costos de edificar en Chile, reflejando la
interdependencia económica global y cómo factores como la política monetaria y los mercados de valores pueden impactar en la industria
de la construcción a nivel nacional. Sin embargo, el valor p del modelo sugiere que las relaciones detectadas podrían deberse a la
variabilidad aleatoria en la muestra (valor p = 0.155563). Es decir, el modelo no permite sacar conclusiones categóricas y por eso se lleva
a cabo una tercera modelación con todas las variables estadísticamente significativas, internas y externas, para buscar complejizar el
análisis. (Tabla 4)
Tabla 5. Resultado modelo VAR con variable externas e internas estadísticamente relevantes para variable dependiente = Índice de Costos
de Construcción 2003-2022. Observaciones = 228. Log-verosimilitud = 4774.45. R-cuadrado = 0.618176 (R-cuadrado corregido =
0.189963). Valor p = 0.026648
Al contar con los modelos VAR para variables únicamente internas y otro para variables únicamente externas en cuanto a factores
macroeconómicos, se hace una nueva modelación que incorpora las variables internas y externas que fueron estadísticamente significativas
en las dos etapas anteriores. Los resultados estadísticamente relevantes se pueden ver en la (Tabla 5). A partir de los resultados de la (Tabla
5), se pueden presentar algunos hallazgos relevantes para este análisis. El modelo arrojó un R-cuadrado de 0.618176, lo que indica una
fuerte relación entre las variables incluidas en el modelo y la variable dependiente. El R-cuadrado ajustado es de 0.189963, sugiriendo que,
después de ajustar por el número de predictores, el modelo aún explica una proporción significativa de la variabilidad del índice de costos
de construcción. La significancia del modelo se confirma con un valor p de 0.026648, indicando que las relaciones encontradas son
estadísticamente significativas. El análisis revela influencias tanto internas como externas. Los coeficientes negativos significativos para la
Tasa de Política Monetaria de EE. UU. con seis meses de rezago (p = 0.0043) y los costos de construcción con ocho meses de rezago (p =
0.0064) indican una relación inversa con el índice de costos de construcción actual. La Inflación de Europa con doce meses de rezago (p =
0.0054) y la Tasa de Política Monetaria de EE. UU. con nueve meses de rezago (p = 0.0074) tienen una influencia positiva significativa, lo
que implica que los aumentos en estas variables se asocian con aumentos en el índice de costos de construcción.
Los coeficientes positivos y significativos para los sueldos y materiales de construcción sugieren que estos factores son predictores
clave del índice de costos de construcción. En particular, los materiales de construcción con ocho meses de rezago (p = 0.0085) y los sueldos
de trabajadores de la construcción con el mismo rezago (p = 0.0094) muestran una fuerte relación predictiva. Esto destaca la importancia
de los costos de los insumos en la industria de la construcción.
Los mercados de valores, representados por NASDAQ y Dow Jones con retardos específicos, también muestran una relación
predictiva, indicando la relevancia de las condiciones económicas generales en los costos de construcción. El modelo sugiere una interacción
dinámica entre factores económicos tanto locales como globales que influyen en el índice de costos de construcción en Chile, donde los
factores con mayor peso estadístico son externos. Finalmente, se procede a revisar la sensibilidad del Indice de Costos de Edificación ante
un shock del tamaño de una desviación estándar en las variables del último modelo. La síntesis de estos resultados se pueden ver en la
102

### Page 8

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
(Figura 3) y en la (Tabla 6).
Figura 3. Resultado de shock del tamaño de una desviación estándar sobre la variable log Indice de Costos de Edificación
Tabla 6. Síntesis de variaciones por mes del impacto de un shock de una desviación estándar sobre log Indice de Costos de Edificación
El análisis de sensibilidad para el Índice de Costos de Edificación frente a shocks de una desviación estándar en las variables
externas e internas revela variaciones significativas en respuesta a los distintos factores económicos y financieros. Las tres variables que
presentan el mayor impacto son el IPC de Europa, la Tasa Política Monetaria de Estados Unidos y de Reino Unido, el indicador de la bolsa
de valores de Shanghái (SSE) y el NASDAQ de Estados Unidos, cerca del Dow Jones. Las variables internas, por su parte, tienen un impacto
agregado algo menor, siendo el sueldo de los trabajadores y el IPSA los que presentan mayores efectos sobre el Índice de Costos de
Edificación.
103

### Page 9

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
Para verificar la validez de este modelo, se hace una evaluación por raíz del error cuadrático medio (RMSE) de las predicciones
del modelo VAR. El resultado es RMSE = 0.00687754, donde un RMSE bajo indica un mejor ajuste del modelo a los datos. En este caso, el
RMSE es óptimo por lo que el resultado ofrece buena capacidad predictiva y se pueden sacar conclusiones de sus hallazgos.
4. Discusión y conclusiones
Gamil y Alhagar planteaba que los eventos asociados al COVID-19 tuvieron un impacto importante la industria de la construcción,
especialmente por la suspensión de proyectos, el impacto en la mano de obra y la pérdida de empleo, lo que devino en el aumento de costos
(Gamil and Alhagar, 2020). Uno de los aprendizajes de la pandemia para la industria de la construcción fue que es imperioso generar
mecanismo preventivos ante eventos que inicialmente poco se relacionan con la industria pero que le terminan afectando. En este caso, se ha
revisado la implicancia de factores externos constantes como IPC, tasa política monetaria y rendimiento financiero de las bolsas de valores
en diversos lugares del mundo. La evidencia aquí presentada indica que es necesario que la industria de la construcción reconozca sin
complejos como propias de sus vaivenes las influencias de factores externos sobre el proceso de producción local. Esto permitirá planificar
mejor y, eventualmente, ampliar las variables a considerar antes de iniciar una obra. En este ámbito, se ha revisado el índice de costos de
edificación con evidencia que permite complejizar el desarrollo de un plan de negocios inmobiliario, al complementar con factores
internacionales la modelación de costos. Por ejemplo, la inflación en la Eurozona y la tasa política monetaria de Estados Unidos tienen
impactos considerables sobre el costo de la edificación en Chile y esto, también, podría estar repercutiendo sobre el precio de la vivienda,
dificultando su acceso en una nación que enfrenta una crisis habitacional. Por otro lado, dentro de los aspectos inflacionarios, se ha estudiado
cómo la guerra entre Rusia y Ucrania ha tenido impactos sobre el proceso inflacionario en la Eurozona (Maurya et al., 2023); (Mayr, 2022),
lo que, a partir de la evidencia entregada por este estudio, bien podría estar impactando también en la producción edificatoria local. Los
ciclos del costo de edificación en Chile, entonces, no solo dependen de la capacidad productiva local y de la salud de la economía nacional,
sino también de lo que ocurre con algunos de los principales socios comerciales internacionales de esta nación. En esta materia, especial
cuidado merece la inflación en Estados Unidos, que según este modelo tiene un mayor impacto al alza sobre el costo de edificación en Chile
entre las variables estudiadas. Por otro lado, el peso de factores financieros externos como políticas monetarias o rendimientos de bolsas de
valores, está muy presente en los resultados. La financierización también afecta al proceso de producción edificatoria, algo que debiera
abordarse de manera integral e interdisciplinaria por las complejidades que implica para el desarrollo de un mercado inmobiliario sano.
Debido a la importancia de revisar las variables de mayor significancia sobre los costos de edificación, la evidencia indica que los
shocks de precio del petróleo en las naciones G7 tiene un peso estadístico considerable sobre las crisis financieras e inflacionarias (Wen et
al., 2021). Luego, están también los efectos de rebote. En un inicio, la pandemia produjo un declive en la inflación mundial pero que luego de
un periodo de adaptación decantó en una crisis inflacionaria de la que se viene hablando en los últimos años (Ha et al., 2021). También es
considerable el problema de la avaricia instalado por la economista Isabella Weber, indicando que parte la inflación en Europa se debe a la
escasa regulación sobre rentabilidades y acaparamiento de oferta por parte de algunos grupos empresariales, lo que también tendría efecto
en los costos edificatorios en Chile (Weber and Wasner, 2023). Debido a que el IPC de Europa es una de las variables con mayor impacto en
este modelo, esa avaricia explicada por Weber y Wasner podría estar influyendo directamente en el costo de producción chileno.
Al aplicar un modelo de series de tiempo con buenos resultados para la proyección de escenarios, este artículo contribuye en
desarrollar un enfoque integral por encima de la contingencia, encontrando patrones estructurales que ayudan a explicar la formación de los
costos de construcción. Otros factores podrían usarse para complementar este estudio, como el PIB por sectores, las expectativas económicas
o el endeudamiento, por mencionar algunas. Metodológicamente, el enfoque presentado en este artículo facilita la incorporación de otras
variables para robustecer el análisis y lograr un modelo predictivo óptimo. Aun así, los resultados aquí presentados ofrecen significancias
estadísticas óptimas y relaciones de interdependencia entre las variables sin multicolinealidad que permiten plantear que la evidencia da
cuenta de relaciones con características causales y con cierta capacidad predictiva, enfoques que ya habían sido dados por (Idrovo-Aguirre
y Contreras-Reyes, 2021) para el caso de la relación entre minería y desarrollo inmobiliario. El artículo cumple su objetivo de identificar
variables macroeconómicas estadísticamente relevantes sobre los costos de edificación en Chile. Al respecto, las pruebas econométricas han
resultado robustas.
5. Referencias
Abdullah, N. A.; Mohd Kamar, I. F.; Mustapa, N. A.; Che Ahmad, A.; Abdullah, M. N.; Syed Mustafa, S. A. H. (2021). Economic
challenges: Conceptual framework on factors affecting construction cost during COVID-19 pandemic in malaysia. IOP
Conference Series: Earth and Environmental Science, 881(1), 012020. https://doi.org/10.1088/1755-1315/881/1/012020
Apostolakis, G.; Papadopoulos, A. P. (2019). Financial Stability, Monetary Stability and Growth: A PVAR Analysis. En OPEN
ECONOMIES REVIEW (Vol. 30, Número 1, pp. 157-178). SPRINGER. https://doi.org/10.1007/s11079-018-9507-y
Asuquo, C. F.; Ogwueleka, A. C. (2019). Identification of key macroeconomic variables for forecasting housing construction costs in
Nigeria. International Journal of Sustainable Real Estate and Construction Economics, 1(3), 261.
https://doi.org/10.1504/IJSRECE.2019.097679
Cheng, M.-Y.; Hoang, N.-D.; Wu, Y.-W. (2013). Hybrid intelligence approach based on LS-SVM and Differential Evolution for
construction cost index estimation: A Taiwan case study. Automation in Construction, 35, 306-313.
https://doi.org/10.1016/j.autcon.2013.05.018
de Dios Tena, J.; Espasa, A.; Pino, G. (2010). Forecasting Spanish Inflation Using the Maximum Disaggregation Level by Sectors and
Geographical Areas. International Regional Science Review, 33(2), 181-204. https://doi.org/10.1177/0160017609336629
Demary, M. (2010). The interplay between output, inflation, interest rates and house prices: International evidence. Journal of Property
Research, 27(1), 1-17. https://doi.org/10.1080/09599916.2010.499015
104

### Page 10

Revista Ingeniería de Construcción RIC
Vol 39 Nº1 2024
www.ricuc.cl
DOI: 10.7764/RIC.00100.21
ENGLISH VERSION..........................................................................................................................................................................................................................................................................
Domeij, D.; Ellingsen, T. (2018). Rational bubbles and public debt policy: A quantitative analysis. Journal of Monetary Economics, 96,
109-123. https://doi.org/10.1016/j.jmoneco.2018.04.005
Gamil, Y.; Alhagar, A. (2020). The Impact of Pandemic Crisis on the Survival of Construction Industry: A Case of COVID-19.
Mediterranean Journal of Social Sciences, 11(4), 122. https://doi.org/10.36941/mjss-2020-0047
Gelain, P.; Lansing, K. J.; Mendicino, C. (2013). House prices, credit growth, and excess volatility: Implications for monetary and
macroprudential policy. International Journal of Central Banking, 9(2), 219-276.
http://www.frbsf.org/publications/economics/papers/2012/wp12-11bk.pdf
Ha, J.; Kose, M. A.; Ohnsorge, F. (2021). Inflation During the Pandemic: What Happened? What is Next? SSRN Electronic Journal.
https://doi.org/10.2139/ssrn.3881502
Idrovo-Aguirre, B. J.; Contreras-Reyes, J. E. (2021). The Response of Housing Construction to a Copper Price Shock in Chile (2009–
2020). Economies, 9(3), 98. https://doi.org/10.3390/economies9030098
Larasati, D.; Ekawati, N.; Triyadi, S.; Muchlis, A. F.; Wardhani, A. (2021). Impact of the Pandemic COVID-19 on the Implementation
of Construction Contracts. IOP Conference Series: Earth and Environmental Science, 738(1), 012075.
https://doi.org/10.1088/1755-1315/738/1/012075
Li, X.; Zhang, C. (2021). Did the COVID-19 Pandemic Crisis Affect Housing Prices Evenly in the U.S.? Sustainability, 13(21), 12277.
https://doi.org/10.3390/su132112277
Maurya, P. K.; Bansal, R.; Mishra, A. K. (2023). Russia–Ukraine conflict and its impact on global inflation: An event study-based
approach. Journal of Economic Studies. https://doi.org/10.1108/JES-01-2023-0003
Mayr, J. (2022). Inflationsausblick—Kosten des Krieges treiben Inflation in neue Höhen. Wirtschaftsdienst, 102(3), 236-238.
https://doi.org/10.1007/s10273-022-3140-5
McDonald, J. F.; Stokes, H. H. (2013). Monetary Policy and the Housing Bubble. En JOURNAL OF REAL ESTATE FINANCE AND
ECONOMICS (Vol. 46, Número 3, pp. 437-451). SPRINGER. https://doi.org/10.1007/s11146-011-9329-9
Medina, J. P. (2021). Mining development and macroeconomic spillovers in Chile. Resources Policy, 70, 101217.
https://doi.org/10.1016/j.resourpol.2018.06.008
Ministerio de Vivienda y Urbanismo. (2022). Plan de Emergencia Habitacional. Ministerio de Vivienda y Urbanismo.
https://www.minvu.gob.cl/plan-de-emergencia-habitacional/
Oladipo, F.; Oni, O. (2012). Review of Selected Macroeconomic Factors Impacting Building Material Prices in Developing Countries –
A Case Of Nigeria. Ethiopian Journal of Environmental Studies and Management, 5(2), 131-137.
https://doi.org/10.4314/ejesm.v5i2.3
Puci, J.; Demi, A.; Kadiu, A. (2023). Impact of macroeconomic variables on the construction sector. Corporate and Business Strategy
Review, 4(1), 22-30. https://doi.org/10.22495/cbsrv4i1art2
Sabaté, I. (2016). Mortgage indebtedness and home repossessions as symptoms of the financialisation of housing provisioning in Spain.
Critique of Anthropology, 36(2), 197-211. https://doi.org/10.1177/0308275X15614636
Vergara-Perucich, J.-F. (2022). Is There Financialization of Housing Prices? Empirical Evidence from Santiago de Chile. En
ECONOMIES (Vol. 10, Número 6). MDPI. https://doi.org/10.3390/economies10060125
Weber, I.; Wasner, E. (2023). Sellers’ Inflation, Profits and Conflict: Why can Large Firms Hike Prices in an Emergency? Economics
Department Working Paper Series, 2023(2), 1-52. https://scholarworks.umass.edu/econ_workingpaper/343/
Wen, F.; Zhang, K.; Gong, X. (2021). The effects of oil price shocks on inflation in the G7 countries. The North American Journal of
Economics and Finance, 57, 101391. https://doi.org/10.1016/j.najef.2021.101391
105

