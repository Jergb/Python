# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 18:29:10 2018

@author: Jergb
"""
import numpy as np
import pandas as pd
import mysql.connector
import seaborn as sns
import matplotlib.pyplot as plt
import scipy as sp
from scipy.spatial.distance import mahalanobis as MH


#==============================================================================
#  impbd Importa tabla desde la bd
#============================================================================== 
def impbd(db,tabla):
    dbConnect ={
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
    return resultados
    
#==============================================================================
#   filtro mantiene sólo valores de mediciones simultaneas en los nodos 2 y 5
#==============================================================================
    
def filtro(matriz):
    matriz = ['aa']+matriz+['aa', 'aa']

    for j in range(1, len(matriz)-2):
        if not ((matriz[j][-1] == matriz[j+1][-1] and matriz[j][-1] != 
                 matriz[j+2][-1] and matriz[j][1]
                 != matriz[j+1][1]) or (matriz[j-1][-1] == matriz[j][-1]
                 and matriz[j][-1] != matriz[j+1][-1] and matriz[j-1][1]
                 != matriz[j][1])):
                matriz[j] = 'aa'

    matriz = [x for i, x in enumerate(matriz) if x != 'aa']
    for u,k in enumerate(matriz):
        matriz[u]=[float((x).replace(',','.')) for i, x in enumerate(k)]
    
    return matriz

#==============================================================================
#   tablas crea los DataFrames utilizadas para el analísis de la información
#==============================================================================
def tablas(resultados):
    columnas=['id_Variable','Nodo','Temperatura','Humedad','HumTierra','Nivel_UV',
      'INTLUMIN','YEAR','MES','DIA','HORA','MINUTO']
    datos2, datos5, data, data25, rr = {}, {}, {}, {}, {}
    for posicion in range(len(columnas)):
        datos2[columnas[posicion]] = [col[posicion] for col in resultados if col[1] == 2]
        datos5[columnas[posicion]] = [col[posicion] for col in resultados if col[1] == 5]
        paresdic = { 'Nodo2' : datos2['id_Variable'], 'Nodo5' : datos5['id_Variable']} 
        data25['NT'] = ([(col[8]+col[9]+col[10]+col[11]) for col in resultados
              if col[1] == '2'])
        data['NT'] = [col[8]+col[9]+col[10]+col[11] for col in resultados]
        rr[columnas[posicion]] = [float(col[posicion]) for col in resultados]
        
    tabla2, tabla5, pares = pd.DataFrame(datos2), pd.DataFrame(datos5), pd.DataFrame(paresdic)        
    tabla2=tabla2.iloc[:,[0,2,3,4,5,6]]
    tabla5=tabla5.iloc[:,[0,2,3,4,5,6]]
    Rr=pd.DataFrame(rr).iloc[:,0:7]
    return paresdic,Rr,tabla2,tabla5,pares

#==============================================================================
#   pdistribution presenta el diagrama de dispersión de las variables
#==============================================================================
def pdistribution(Rr):
    nodo=[]
    for lo in range(len(Rr['Nodo'])):
        nodo.append('N'+str(int(Rr['Nodo'][lo])))
    Rr['Nodo']=nodo
    sns.pairplot(Rr,hue='Nodo',plot_kws=dict(s=10))

#==============================================================================
#   pcorr presenta el grafico de correlación de las variables
#==============================================================================    
def pcorr(Rr):
    plt.matshow(Rr.corr())
    plt.xticks(range(len(Rr.columns)), Rr.columns)
    plt.yticks(range(len(Rr.columns)), Rr.columns)
    plt.colorbar()
    
#==============================================================================
#   mahal obtiene la distancias de Mahalanobis entre los nodos dos y cinco
#   para cada instante de tiempo
#==============================================================================
def mahal(tabla2,tabla5,pares,Rr):
    
    pares = pares.merge(tabla2, how='left', left_on=['Nodo2'],
                        right_on=['id_Variable'])
    pares = pares.merge(tabla5, how='left', left_on=['Nodo5'], 
                        right_on=['id_Variable'])
    pares['vector2'] = pares[['Temperatura_x','Humedad_x','HumTierra_x',
         'Nivel_UV_x','INTLUMIN_x']].values.tolist()
    pares['vector5'] = pares[['Temperatura_y','Humedad_y','HumTierra_y',
         'Nivel_UV_y','INTLUMIN_y']].values.tolist()
    mahala = pares[['Nodo2', 'Nodo5', 'vector2', 'vector5']]  
    covmx = Rr.iloc[:,1:6].cov()
    invcovmx = sp.linalg.inv(covmx)
    mahala['mahala_dist'] = mahala.apply(lambda m: MH(m['vector2'],
          m['vector5'],invcovmx), axis=1)
    Nodo2, Nodo5, mahaladist = mahala.Nodo2, mahala.Nodo5, mahala.mahala_dist
    vector2=pares.vector2
    vector5=pares.vector5 
    return  Nodo2, Nodo5, mahaladist, vector2, vector5

#==============================================================================
#   Tukey obtiene los límites inferiores y superiores para cada columna de
#   Datos, apartir de los cuales los valores son considerados ouliers
#   univariantes
#==============================================================================  
def tukey(Datos,variables):
    
    desc=Datos.describe()
    Li={}
    Ls={}
    for var in range(len(variables)):
            RIQ=desc[variables[var]][6]-desc[variables[var]][4]
            Li[var]=desc[variables[var]][4]-RIQ*1.5
            Ls[var]=desc[variables[var]][6]+RIQ*1.5
    return Li, Ls
#==============================================================================
#   Tukeytest aplica el test a cada elemento de tabla y devuelve tuplas con 
#   indices y valores correspondiendientes a outliers univariantes
#==============================================================================  
def Tukeytest(datos,tabla,Li,Ls):
    idVar=tabla.iloc[:,0]
    tabla=tabla.iloc[:,1:6]
    Fila={}
    Columna={}
    filn={}
    for ncol in range(len(tabla.iloc[0])):
        Fila[ncol]=[]
        Columna[ncol]=[]
        filn[ncol]=[]
        for nfil in range(tabla.iloc[:,0].count()):                        
            if tabla.iloc[nfil,ncol]<Li[ncol] or tabla.iloc[nfil,ncol]>Ls[ncol]:
                Fila[ncol].append(np.where(datos==[idVar[nfil]]))
                filn[ncol].append(nfil)
                Columna[ncol].append(tabla.iloc[nfil,ncol])
    return Fila, Columna,filn
#==============================================================================
#   pvhist
#==============================================================================  
def pvhist(variables,Rr):
    for nvar,var in enumerate(variables):
        plt.figure()    
        plt.title(variables[nvar])
        plt.hist(Rr[var]) # Histograma de las variables

def pvarg(variables,Rr,fil2,fil5,col2,col5):
        for vamo in range(len(variables)):
            plt.subplot(2,2,2)
            plt.title('Variables Globlal')
            plt.plot(Rr[variables[vamo]],linewidth=1,label=variables[vamo])
            plt.scatter(fil2[vamo],col2[vamo],color='r')
            plt.scatter(fil5[vamo],col5[vamo],color='r')
            plt.legend()

def pvars(variables,Rr,fil2,fil5,col2,col5):
    for nvar,var in enumerate(variables):
        plt.subplot(2,5,nvar+6)
        plt.title(var)
        plt.plot(Rr[var],linewidth=1)
        plt.scatter(fil2[nvar],col2[nvar],color='r')
        plt.scatter(fil5[nvar],col5[nvar],color='r')

def pvarnodo(variables,tabla2,tabla5,col2,col5,fila2,fila5):
    for nvar in range(len(variables)):
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(tabla2[variables[nvar]])
        plt.scatter(fila2[nvar],col2[nvar],color='r')
        plt.subplot(2,1,2)
        plt.plot(tabla5[variables[nvar]])
        plt.scatter(fila5[nvar],col5[nvar],color='r')