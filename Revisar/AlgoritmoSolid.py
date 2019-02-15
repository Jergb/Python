# -*- coding: utf-8 -*
"""
Created on Thu Aug  9 09:54:17 2018
5
@author: Jergb
"""

import matplotlib.pyplot as plt
import pandas as pd
from ggplot import *
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import Algfuns as Af
plt.close('all')
importe=16
if importe==1:
    db='prueba'
    tabla='pruebatabla'
    resultados=Af.impbd('prueba','pruebatabla')
else:
    db='WSN'
    tabla='medidas'
    resultados=Af.impbd('WSN','medidas')

#resultados=resultados.iloc[0:100,:]

print('La serie general tiene ', len(resultados), 'observaciones')

#while 1:
#    salute=input()
#    if salute == 'Y':
#        break


datos=Af.filtro(resultados)
print('La serie general tiene', len(resultados), 'valores')
print('La serie general filtrada tiene', len(datos), 'observaciones')


rr=resultados

periodos,Tiempo=Af.Datasets(resultados,60*24) #Permite obtener los periodos de medición ralizados
#Af.pairT(periodos)
#plt.show()
Af.distributionplot(resultados)
Af.corrplot(resultados)
variables=['Temperatura','Humedad Relativa','Humedad de la Tierra','Nivel UV','Intensidad Lumínica']

[tabla2,tabla5]=Af.tablas(datos) #Crea las tablas que se van a utilizar para
#el análisis de la información

#==============================================================================
#   Creación del espacio euclídeo para la representación de las distancias
#==============================================================================

#==============================================================================
#   Escalamiento multidimensional
#X_std =pd.DataFrame(StandardScaler().fit_transform(Rr))
#
#==============================================================================
#   Representación de distribución y dispersión de las variables
#   PCA
#==============================================================================  
   



#Af.pcorr(Rr.iloc[:,2:6])
#==============================================================================
##   Aplicación de la Distancia de Mahalanobis para detección de outliers 5
##   multivariables
#==============================================================================
Nodo2=tabla2.iloc[:,0]
Nodo5=tabla5.iloc[:,0]
mahaladist=Af.mahal(tabla2.iloc[:,2:7],tabla5.iloc[:,2:7],datos.iloc[:,2:7])
eucli=Af.euclidea(tabla2.iloc[:,2:7],tabla5.iloc[:,2:7],datos.iloc[:,2:7])
#del(covmx)
#
#sns.residplot(tabla2['Humedad Relativa'], tabla5['Humedad Relativa'], lowess=True, color="g")

#==============================================================================
#   Aplicación del Criterio de Tukey para detección de outliers univariables
#==============================================================================
#plt.figure()
def pvarsm(tabla2,tabla5,variables,mahaladist):
    plt.subplot(611)
    plt.plot(mahaladist,linewidth=1)
    plt.title('Distancia de Mahalanobis')
    f=612
    for variable in variables:
        
        plt.subplot(f)
        f+=1
        plt.title(variable)
        plt.plot(tabla2[variable],label='N2',linewidth=1)
        plt.plot(tabla5[variable],label='N5',linewidth=1)
        plt.legend()
#plt.figure()

[Li,Ls]=Af.tukey(Rr,variables)        
[Li2,Ls2]=Af.tukey(tabla2,variables)        
[Li5,Ls5]=Af.tukey(tabla5,variables)        

[fil2,col2,fila2]=Af.Tukeytest(Rr.VariableID,tabla2,Li2,Ls2)
[fil5,col5,fila5]=Af.Tukeytest(Rr.VariableID,tabla5,Li5,Ls5)

#fig, (ax1, ax2) = plt.subplots(1, 2)
#plt.title('Distribución datos nodo2 vs nodo 5')
                    
#Af.pvhist(variables,Rr)

#ax1.scatter(sn5['Humedad Relativa'],sn2['Humedad Relativa'],color='b',s=20,label='normales')

#pvarsm(tabla2,tabla5,variables,mahaladist)
#plt.figure()
#Af.pvarg(variables,Rr,fil2,fil5,col2,col5)

#Af.pvaro(variables,Rr,fil2,fil5,col2,col5)
    
#Af.pvarnodo(variables,tabla2,tabla5,col2,col5,fila2,fila5)
#    
##"""
##Qué pasa con las Humedad Relativaades?
##Solucionar el efecto enmascaramiento!!!
##Probar outlier univariable primero?
##Hacer el outlier referido al otro nodo, al mismo nodo o globla?
##Qué se debe tener en cuenta para la detección de los outliers por Mahalanobis??
##Outliers cercanos a lamedia!!!!!"""
#plt.close('all')
##
##"""Graficar distancaia de mahalanobis??????"""
##
