import numpy as np
import matplotlib.pyplot as plt
import collections as cl
import scipy as sp
import scipy.stats as sps


datos = [1, 2, 3, 4, 5, 3, 2, 2]
datos_counter = cl.Counter(datos)
tablaFreqAbs = datos_counter.most_common()
tablaFreqAbs.sort()
valoresUnicos = [item[0] for item in tablaFreqAbs]
freqAbs = [item[1] for item in tablaFreqAbs]
print("Diagrama de barras a partir de la tabla de frecuencias:")
posiciones = valoresUnicos
alturas = freqAbs
print(posiciones, alturas)
plt.bar(posiciones, alturas, color='tan')
plt.plot(datos)

plt.show()
