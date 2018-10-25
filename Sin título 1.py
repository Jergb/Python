# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 09:02:43 2018

@author: Jergb
"""

Distancia de Mahalanobis permite determinar la distancia entre individuos de un mismo grupo
Distancia de Mahalanobis es invariante ante los cambios de escala
con la distancia de Mahalanobis se detectan los instantes de tiempo en los que ocurren
más outliers
Para detectar outliers en tiempo real se debe comparar la distancia de mahalanobis 
para los valores medidos en tiempo t con el valor de la distancia que separa los valores normales 
de los outliers
La distancia de Mahalanobis es la distancia entre un punto de los datos y el centroide de un espacio multivariado (la media general). *****
 Examinar la distancia de Mahalanobis es un método multivariado más potente para detectar valores atípicos que examinar una variable a la vez, porque la distancia toma en cuenta las diferentes escalas entre las variables y las correlaciones entre estas. *****
 
 la distancia de mahalanobis es igual para [1,2,3] que para [0.001,0,001,001], [1000, 2000, 3000], [1000, 2, 0.03]???
 
  La utilización de la distancia euclidiana supone que los conglomerados tienen covarianzas de identidad, es decir, que todas las dimensiones son estadísticamente independientes y la varianza de cada una de las dimensiones (columnas) es igual a uno.******
  
  En general, las variables aleatorias pueden ser incorreladas, pero altamente dependientes.*******
  
  
  Si r = 0, no existe relación lineal. Pero esto no necesariamente implica que las variables son independientes: pueden existir todavía relaciones no lineales entre las dos variables.****
  
  Los autovectores asociados a autovalores distintos son linealmente independientes. Demostración para dos autovalores Supongamos que tengo dos autovalores distintos: λ1≠λ2. Como son autovalores, se cumple: A.v1=λ1.v1 A.v2=λ2.v2****
  
  Si λ es un autovalor de A, se denomina autoespacio Sλ al subespacio que contiene todos los autovectores asociados al autovalor λ y además el vector nulo. 
  
  Objetivo:
Obtener una representacion euclıdea, exacta oaproximada, de los elementos de un conjunto
E de n objetos o individuos, a partir de una matriz de distancias D sobre E.
Atencion:
No disponemos de una matriz de datos, sino de una matriz de distancias entre individuos. Y buscamos representar estosindividuos en un plano.****

Los métodos de reducción de dimensionalidad son técnicas estadísticas que mapean el conjunto de los datos a subespacios derivados del espacio original, de menor dimensión, que permiten hacer una descripción de los datos a un menor costo. Estas técnicas cobran importancia ya que muchos algoritmos de diversos campos tales como análisis numérico, aprendizaje automático o minería de datos suelen degradar su rendimiento cuando se usan con datos de alta dimensionalidad. En los casos extemos, el algoritmo deja de ser útil para el fin que fue diseñado. ****

O una visualización agradable alternativa es a través de un diagrama de Hinton. El color de los cuadros determina el signo de la correlación, en este caso, rojo para positivo y azul para las correlaciones negativas; mientras que el tamaño de las cajas determina su magnitud, cuanto más grande es la caja, mayor es la magnitud.****

Método de extracción de factores utilizado para formar combinaciones lineales no correlacionadas de las variables observadas. La primera componente tiene la varianza máxima. Las componentes sucesivas explican progresivamente proporciones menores de la varianza y no están correlacionadas las unas con las otras.******


Entre las diferentes técnicas (índice de Pearson, Análisis de Componentes Principales, ...) se ha empleado el análisis de la Distancia Geométrica Euclídea (DGE) a la diagonal del espacio de color como descriptor cromático, pues se busca evitar generalizaciones que puedan distorsionar las características individuales de cada punto de la imagen.****

La determinaci´on del nu´mero de factores a retener es, en parte, arbitraria y queda a juicio del investigador. Un criterio es retener los factores con valor propio superior a 1. Tambi´en podemos representar un gr´aﬁco de sedimentaci´on (scree plot) de los valores propios como el de la ﬁgura 1 y considerar el nu´mero de componentes en el que el descenso se estabiliza.*****

Cuando los contornos de la elipse de distancia constante son aproximadamente circulares, o equivalentemente, los valores propios de S son casi iguales, la variación es homogénea en todas las direcciones. En este caso, no es posible representar bien los datos en menos de p dimensiones. *****

Como regla general, se sugiere retener solamente aquellas componentes principales cuyas varianzas ˆi λ sean mayores que la unidad, o equivalentemente, aquellas componentes 
______________________________________________________Elkin Castaño V. 
 
Como regla general, se sugiere retener solamente aquellas componentes principales cuyas varianzas ˆi λ sean mayores que la unidad, o equivalentemente, aquellas componentes principales que, individualmente, expliquen al menos una proporción 1/p de la varianza total muestral****

 Los casos atípicos (outliers) son observaciones con valores extremos (notablemente diferentes de las restantes observaciones)****
 
 A veces, pueden convertirse en observaciones inﬂuyentes que distorsionan los resultados (vg: relaciones no signiﬁcativas, normalidad, etc.)	*****

Las razones por las que pueden surgir estos casos aislados son variadas, pero debemos controlar posibles errores en la introducción datos (analizar frecuencias para detectar valores erróneos).******

 un conjunto se cinco variables, donde 
una sea copia fiel de otra. La copia es su 
gemela y por tanto completamente 
correlacionada. La distancia Euclidiana no 
tiene manera de tomar en consideración que la 
copia no aporta información nueva y por tanto, 
en los cálculos, hará pesar más esta variable 
que las otras.  

(PDF) P. Ch. Mahalanobis y las aplicaciones de.... Available from: https://www.researchgate.net/publication/28249208_P_Ch_Mahalanobis_y_las_aplicaciones_de_su_distancia_estadistica [accessed Aug 28 2018].*****
