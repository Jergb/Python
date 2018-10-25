# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 09:54:17 2018

@author: Jergb
"""

import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import pandas as pd
import scipy as sp
import seaborn as sns
from scipy.spatial.distance import mahalanobis as MH
from ggplot import *

importe=18
if importe==1:
    db='prueba'
    tabla='pruebatabla'
else:
    db='WSN'
    tabla='medidas'
    
#==============================================================================
#   Importar tabla de la base de datos
#==============================================================================    

dbConnect = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': db
}

conexion = mysql.connector.connect(**dbConnect)
cursor = conexion.cursor()

sql = 'select * from '+ tabla
cursor.execute(sql)
resultados = cursor.fetchall()

#==============================================================================
#   Comienza el filtro de datos duplicados en el tiempo
#==============================================================================

resultados = ['aa']+resultados+['aa', 'aa']

for j in range(1, len(resultados)-2):
    if not ((resultados[j][-1] == resultados[j+1][-1] and resultados[j][-1] != 
            resultados[j+2][-1] and resultados[j][1]
            != resultados[j+1][1]) or (resultados[j-1][-1] == resultados[j][-1]
            and resultados[j][-1] != resultados[j+1][-1] and resultados[j-1][1]
            != resultados[j][1])):
            resultados[j] = 'aa'

resultados = [x for i, x in enumerate(resultados) if x != 'aa']
datos2, datos5, data, data25, rr = {}, {}, {}, {}, {}


#==============================================================================
#   Separación de datos de los nodos dos y cinco
#==============================================================================

vars=['Temperatura','Humedad','HumTierra','Nivel_UV','INTLUMIN']

cols=['id_Variable','id_nodo','Temperatura','Humedad','HumTierra','Nivel_UV',
      'INTLUMIN','YEAR','MES','DIA','HORA','MINUTO']


for pos in range(len(cols)):
    
    datos2[cols[pos]] = ([col[pos] for col in resultados if col[1] == 2])
    datos5[cols[pos]] = ([col[pos] for col in resultados if col[1] == 5])
    paresdic = { 'Nodo2' : datos2['id_Variable'], 'Nodo5' : datos5['id_Variable']} 
    data25['NT'] = ([(col[8]+col[9]+col[10]+col[11]) for col in resultados
          if col[1] == '2'])
#    data['NT'] = ([(col[8]+col[9]+col[10]+col[11]) for col in resultados
#        if col[1] != 'aa'])
    rr[cols[pos]] = ([col[pos]for col in resultados if col[1] != 'aa'])

#del(resultados,cols)
del(datos2['id_nodo'],datos2['YEAR'],datos2['MES'],datos2['DIA'],datos2['HORA'],datos2['MINUTO'])
del(datos5['id_nodo'],datos5['YEAR'],datos5['MES'],datos5['DIA'],datos5['HORA'],datos5['MINUTO'])
id_nodo=rr['id_nodo']
del(rr['id_nodo'],rr['YEAR'],rr['MES'],rr['DIA'],rr['HORA'],rr['MINUTO'])
id_Variable=rr['id_Variable']

del(rr['id_Variable'])

tabla2, tabla5, pares = pd.DataFrame(datos2), pd.DataFrame(datos5), pd.DataFrame(paresdic)

Rr = pd.DataFrame(rr)        
outlierf,outlierf2,outlierf5,outlierc,outlierc2,outlierc5={},{},{},{},{},{}
sw2,sw5,sn2,sn5={},{},{},{}
so2={}
so5={}
Dist2={}
Dist5={}

#==============================================================================
#   Creación del espacio euclídeo para la representación de las distancias
#   Escalamiento multidimensional
#==============================================================================

#==============================================================================
#   Representación de distribución y dispersión de las variables
#   PCA
#==============================================================================

for var in vars:
    #   Resta de la media de las variables
    Dist2[var]=tabla2[var]-tabla2[var].mean()
    Dist5[var]=tabla5[var]-tabla5[var].mean()
    outlierf[var],outlierf2[var],outlierf5[var],outlierc[var],sw2[var]=[],[],[],[],[]
    outlierc2[var],outlierc5[var],sw5[var],sn2[var],sn5[var]=[],[],[],[],[] 
    so2[var],so5[var]=[],[]
    
    
plt.close('all')
Nodo=[]
for lo in range(len(id_nodo)):
    Nodo.append('N'+str(int(id_nodo[lo])))
Rr['Nodo']=Nodo
sns.pairplot(Rr,hue='Nodo',plot_kws=dict(s=10)) #  Distribución y dispersión 
#   de las variables
#del(Rr['Nodo'])


plt.matshow(Rr.corr())
plt.xticks(range(len(Rr.columns)), Rr.columns)
plt.yticks(range(len(Rr.columns)), Rr.columns)
plt.colorbar()
    

del(datos2,datos5,paresdic)

#==============================================================================
#   Aplicación de la Distancia de Mahalanobis para detección de outliers 
#   multivariables
#==============================================================================
import Algfuns as Af
pares = pares.merge(tabla2, how='left', left_on=['Nodo2'],
                    right_on=['id_Variable'])
pares = pares.merge(tabla5, how='left', left_on=['Nodo5'], 
                    right_on=['id_Variable'])

#del(tabla2,tabla5)

pares['vector2'] = pares[['Temperatura_x','Humedad_x','HumTierra_x',
     'Nivel_UV_x','INTLUMIN_x']].values.tolist()
pares['vector5'] = pares[['Temperatura_y','Humedad_y','HumTierra_y',
     'Nivel_UV_y','INTLUMIN_y']].values.tolist()

mahala = pares[['Nodo2', 'Nodo5', 'vector2', 'vector5']]

vector2=pares.vector2
vector5=pares.vector5
#
covmx = Rr.cov()
invcovmx = sp.linalg.inv(covmx)
#
mahala['mahala_dist'] = mahala.apply(lambda m: MH(m['vector2'], m['vector5'],
      invcovmx), axis=1)
Nodo2, Nodo5, mahaladist = mahala.Nodo2, mahala.Nodo5, mahala.mahala_dist
#





#del(covmx)
#mahaladist=Af.mahal(tabla2.iloc[:,1:6],tabla5.iloc[:,1:6],Rr.iloc[:,2:7])

#==============================================================================
#   Aplicación del Criterio de Tukey para detección de outliers univariables
#==============================================================================

pd.options.display.float_format ='{:.1f}'.format

desc=Rr.describe()
desc2=tabla2.describe()
desc5=tabla5.describe()
Li={}
Ls={}
#
for ff in range(len(vars)):
        RIQ=desc[vars[ff]][6]-desc[vars[ff]][4]
        Li[ff]=desc[vars[ff]][4]-RIQ*1.5
        Ls[ff]=desc[vars[ff]][6]+RIQ*1.5
        
i=[0,1,2,3,4]
   

def ord2():
    fi2,fe2=list(id_Variable).index(f2),list(tabla2['id_Variable']).index(f2)
    sw2[vars[ubi]].append(fila2[mar])
    sw5[vars[ubi]].append(fila5[mar])
    outlierc2[vars[ubi]].append(fe2)
    outlierf2[vars[ubi]].append(Rr[vars[ubi]][fi2])
    outlierc[vars[ubi]].append(fi2)
    outlierf[vars[ubi]].append(Rr[vars[ubi]][fi2])
    return(sw2,sw5,outlierc2,outlierc5,outlierf2,outlierf5,outlierc,outlierf)
                
def ord5():
    fi5,fe5 = list(id_Variable).index(f5),list(tabla5['id_Variable']).index(f5)
    sw2[vars[ubi]].append(fila2[mar])
    sw5[vars[ubi]].append(fila5[mar])
    outlierc5[vars[ubi]].append(fe5) 
    outlierf5[vars[ubi]].append(Rr[vars[ubi]][fi5])                
    outlierc[vars[ubi]].append(fi5)
    outlierf[vars[ubi]].append(Rr[vars[ubi]][fi5])
    return(sw2,sw5,outlierc2,outlierc5,outlierf2,outlierf5,outlierc,outlierf)



#fig, (ax1, ax2) = plt.subplots(1, 2)
#plt.title('Distribución datos nodo2 vs nodo 5')


for pos in range(len(vector2)):
    fila2, fila5= vector2[pos],vector5[pos]
    if mahaladist[pos]<3:
        for ubi,fila in enumerate(fila2):
            sn2[vars[ubi]].append(vector2[pos])
            sn5[vars[ubi]].append(vector5[pos])
    
    else:
        for ubi,fila in enumerate(fila2):
            f2, f5= Nodo2[pos],Nodo5[pos]
        for ubi,fila in enumerate(fila2):
            mar=fila2.index(fila)
            if fila2[mar]<Li[i[ubi]] and fila5[mar]<Li[i[ubi]]:
                ord2(), ord5()
            elif fila2[mar]>Ls[i[ubi]] and fila5[mar]>Ls[i[ubi]]:
                ord2(), ord5()
            elif fila2[mar]<Li[i[ubi]] and fila5[mar]<=Ls[i[ubi]]:
                ord2()
            elif fila5[mar]<Li[i[ubi]] and fila2[mar]<=Ls[i[ubi]]:
                ord5()
            elif fila2[mar]>Ls[i[ubi]] and fila5[mar]>=Li[i[ubi]]:
                ord2()
            elif fila5[mar]>Ls[i[ubi]] and fila2[mar]>=Li[i[ubi]]:
                ord5()
            else:
                for ubi,fila in enumerate(fila2):
                     sn2[vars[ubi]].append(vector2[pos])
                     sn5[vars[ubi]].append(vector5[pos])
                     
#lx=list(Dist2[so2])
#ly=list(Dist5[so5])


#sns.boxplot(x='Temperatura',y='Humedad',data=Rr,palette='hls')
#scatterplot matrix
 
#
#lo=len(tabla2['Temperatura'])
#no={'Nodo2':[2]*lo,'Nodo5':[5]*lo}
#
for bb,va in enumerate(vars):
    plt.figure()    
    plt.title(vars[bb])
    plt.hist(Rr[va]) # Histograma de las variables


#ax1.scatter(sn5['Humedad'],sn2['Humedad'],color='b',s=20,label='normales')
plt.subplot(2,2,1)
plt.scatter(sn5['Humedad'],sn2['Humedad'],color='b',s=20,label='normales')
for vamo in vars:
    plt.scatter(sw5[vamo],sw2[vamo],color='r')
    if vamo=='INTLUMIN':
        plt.plot([],[],'ro',label='outliers')
plt.legend()

#plo=ggplot(Rr, aes(x = 'Temperatura', y ='Humedad')) + \
#    geom_point(alpha=1, size=100, color='dodgerblue') + \
#    geom_point(data = Rr,alpha=1, size = 100, color='red')
#plo.show()



#plt.figure()

#        
for vamo in vars:
    plt.subplot(2,1,1)
    plt.title('Variables Globlal')
    plt.plot(Rr[vamo],linewidth=1,label=vamo)
    plt.scatter(outlierc[vamo],outlierf[vamo],color='r')
    plt.legend()
 
for num,vamo in enumerate(vars):
    plt.subplot(2,5,num+6)
    plt.title(vamo)
    plt.plot(Rr[vamo],linewidth=1)
    plt.scatter(outlierc[vamo],outlierf[vamo],color='r')

for vamo in vars:
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(tabla2[vamo])
    plt.scatter(outlierc2[vamo],outlierf2[vamo],color='r')
    plt.subplot(2,1,2)
    plt.plot(tabla5[vamo])
    plt.scatter(outlierc5[vamo],outlierf5[vamo],color='r')

    
#"""
#Qué pasa con las humedadades?
#Solucionar el efecto enmascaramiento!!!
#Probar outlier univariable primero?
#Hacer el outlier referido al otro nodo, al mismo nodo o globla?
#Qué se debe tener en cuenta para la detección de los outliers por Mahalanobis??
#Outliers cercanos a lamedia!!!!!"""
#
#"""Graficar distancaia de mahalanobis??????"""
#
