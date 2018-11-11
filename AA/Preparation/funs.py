# -*- coding: utf-8 -*-
"""
Contiene las funciones utilizadas en la preparación de los datos (pre-DL).
@author: Jergb
"""

import numpy as np
import pandas as pd
import mysql.connector
import seaborn as sns
import matplotlib.pyplot as plt
import scipy as sp
from scipy.spatial.distance import mahalanobis as MH
from scipy.spatial.distance import euclidean as EU
from matplotlib.ticker import FuncFormatter
from datetime import timedelta

def transcurrido_fechas(f2, f1):
    'Calcula el tiempo transcurrido entre dos fechas'
    
    tiempo_transcurrido = int((f2 - f1).seconds / 60)
    tiempo_transcurrido += (f2 - f1).days * 24 * 60

    return tiempo_transcurrido

def separa_datos(datos, edge):
    'Divide los datos cuando faltan edge registros'
    inicio, fin, p = [], [], 0
    inicio.append(0)
    for i in range(1, len(datos)):

        if transcurrido_fechas(datos.index[i], datos.index[i-1]) > edge:
            fin.append(i-1)
            inicio.append(i)

    fin.append(i)
    data, separados = [], []

    for fin_i in range(len(fin)):

        dataset = datos[inicio[fin_i]:fin[fin_i]]

        for dataset_i in range(len(dataset)):

            data.append(dataset.iloc[dataset_i])

        separar = pd.DataFrame(data)
        separados.append(separar)
        data = []
        
    inicio = [datos.index[x] for x in inicio]
    fin = [datos.index[x] for x in fin]
    registros = [len(separados[x])+1 for x in range(len(separados))]
    tiempo = [(fin[x] - inicio[x]) for x in range(len(fin))]
    inicio.append(inicio[-1])
    sregistros = [(inicio[x+1]-fin[x]) for x in range(len(fin))]
    inicio.pop(-1)
    sregistros[-1] = '-'
    faltantes = [(transcurrido_fechas(fin[x], inicio[x]) + 1 - registros[x]) for x in range(len(fin))]
    r_registros = [(registros[x] / (transcurrido_fechas(fin[x], inicio[x]) +1)*100) for x in range(len(fin))]
    n_registros = [(faltantes[x] / (transcurrido_fechas(fin[x], inicio[x]) +1)*100) for x in range(len(fin))]
    duracion = pd.DataFrame({'Registro Inicial': inicio, 'Registro Final': fin,
                             'Registrado': registros, 'No Registrado':faltantes,
                             'Registrado(%)':r_registros,'No Registrado(%)':n_registros,
                             'Duración': tiempo, 'Tiempo Hasta el Siguiente Registro':sregistros})
    return separados, duracion

def info_periodo(dataset,inicio,fin):
    'Presenta información detallada sobre un rango de registros de un dataset'
    registros = len(dataset.loc[inicio:fin,:])+1
    inicio = pd.Timestamp(inicio)
    fin = pd.Timestamp(fin)
    data = dataset.loc[inicio:fin,:]
    tiempo = fin - inicio
    
    faltantes = transcurrido_fechas(fin, inicio) + 1 - registros
    r_registros = (registros / (transcurrido_fechas(fin, inicio) +1))*100
    n_registros = (faltantes / (transcurrido_fechas(fin, inicio) +1))*100
    info = pd.DataFrame({'Registro Inicial': [inicio], 'Registro Final': [fin],
                             'Registrado': [registros], 'No Registrado':[faltantes],
                             'Registrado(%)':[r_registros],'No Registrado(%)':[n_registros],
                             'Duración':[tiempo]})
    return data, info


def info_var(v):
    'Grafica todos los valores medidos para la variable v'
    variable = mediciones_cacao.columns[v]
    plt.figure(figsize=[20,5])
    plt.plot(mediciones_cacao[variable],'orange',label='datos')
    plt.title(variable)
    plt.legend()
    
def tukey(variable):
    'Obtiene los límites superiores e inferiores para v'
    
    RIQ = variable.quantile(q=.75) - variable.quantile(q=.25)
    Li = variable.quantile(q=.25) - RIQ * 1.5
    Ls = variable.quantile(q=.75) + RIQ * 1.5
    return Li, Ls

def filtro(filtrado,variable,i,q):
    'Iguala el valor de una medición a un determinado valor límite'
       
    try:
        filtrado[variable][i] = filtrado[variable][i-120:i].median()   
        
    except KeyError:
        filtrado[variable][i]= q
    return filtrado

def filtrar_variables(v,lim_i,lim_s):
    'Ajusta los valores atípicos en las mediciones de la variable v'
    global filtrar
    variable =filtrar.columns[v]
    Li, Ls = tukey(filtrado[variable])

    for i in range(len(filtrado[variable])):
              
        if filtrado[variable][i] >= lim_s:
            filtro(filtrar,variable,i,filtrar[variable].quantile(.75))
        
        elif filtrado[variable][i] <= lim_i:
            filtro(filtrar,variable,i,filtrar[variable].quantile(.25))
            
        elif filtrado[variable][i] >= Ls and Ls > lim_s:
            filtro(filtrar,variable,i,filtrar[variable].quantile(.75))
            
        elif filtrado[variable][i] <= Li and Li < lim_i:
            filtro(filtrar,variable,i,filtrar[variable].quantile(.25))
            
    plt.plot(filtrar.iloc[:,v],'blue',label='filtrado')
    plt.legend()
    return filtrar.corr()
def filtro_var(v,lim_i,lim_s):
    'Ajusta los valores atípicos en las mediciones de la variable v'
    
    global mediciones_cacao
    filtrado = mediciones_cacao.copy()
    variable=filtrado.columns[v]
    Li, Ls = tukey(filtrado[variable])

    for i in range(len(filtrado[variable])):
              
        if filtrado[variable][i] >= lim_s:
            filtro(filtrado,variable,i,filtrado[variable].quantile(.75))
        
        elif filtrado[variable][i] <= lim_i:
            filtro(filtrado,variable,i,filtrado[variable].quantile(.25))
            
        elif filtrado[variable][i] >= Ls and Ls > lim_s:
            filtro(filtrado,variable,i,filtrado[variable].quantile(.75))
            
        elif filtrado[variable][i] <= Li and Li < lim_i:
            filtro(filtrado,variable,i,filtrado[variable].quantile(.25))
            
    return filtrado.corr()

def up_ajuste(filtrado,v):
    global ajustado,filtar
    variable=ajustado.columns[v]
    ajustado[variable]=filtrar[variable].copy()
    return

def ajuste_variacion(v):
    'Ajusta los valores que presentan una variación superior a la std'
    global ajustado,filtrar,mediciones_cacao
    up_ajuste(filtrar,v)
    variable=ajustado.columns[v]
    ventana=60
    rolling_std = ajustado[variable].rolling(ventana).std()
    rolling_std_inv=ajustado[variable].iloc[::-1].rolling(ventana).std().iloc[::-1]
    indice=rolling_std[rolling_std.isnull().values].index
    rolling_std.loc[indice]=rolling_std_inv.loc[indice]
   
    suave=ajustado[variable].copy()
    nvalores=suave[rolling_std>(rolling_std.mean())].index
    nnvalores=[suave.index.get_loc(x) for x in nvalores]
    #print('nvalores: ',nvalores)
    rolling_median=suave.rolling(ventana).median()
    
    
    # Hace una ventana deslizante desde la última fila
    rolling_median_inv=suave.iloc[::-1].rolling(ventana).median().iloc[::-1]
    indice=rolling_median[rolling_median.isnull().values].index
    rolling_median.loc[indice]=rolling_median_inv.loc[indice]

     # mueve el dataframe ventana filas
    nsu = [x+int(ventana/2) for x in nnvalores if x+ventana < len(suave)]
    #nsu = [x+ventana for x in nnvalores if x+ventana < len(suave)]
    suave[nnvalores[0:len(nsu)]]=rolling_median[nsu]
    
    plt.figure(figsize=[20,5])
    plt.title(mediciones_cacao.columns[v])
    plt.plot(mediciones_cacao[variable],label='datos')
    plt.plot(suave,label='suavizado')
    plt.legend()
    ajustado[variable]=suave
    return

def val_menor(L1,L2,lim_s,var,var_rel):
    'Determia la columna de correlación entre dos variables'
    correl={'corre':[],'lim':[]}
    #ciclo for para variar el rango desde el límite inferior hasta el límite de Tukey
    for rango in range(int(L1),int(L2)):
        # Eto se puede  variar y que filtro var devuelva el indice de correlación de Pearson
#        filtrado = mediciones_cacao.copy()
        # Aplcación del filtro de rango
    #### Definir el dataset al que se le aplicará el filtro
        corre = filtro_var(var,rango,lim_s)
        correl['corre'].append(corre.iloc[var,var_rel])
        correl['lim'].append(rango)
    return correl


def filtro_menor(v,vr,lim_i,lim_s,c):
    global filtrado
    
    variable = filtrado.columns[v]
            
    # Se realiza el test de Tukey
    Li, Ls = tukey(filtrado[variable])
    if Li>lim_i:
        # val_rngo determina unna columna de correlación para diferentes rangos       
        correl = val_menor(lim_i,int(Li),lim_s,v,vr)
        L = lim_i
    else:
        correl = val_menor(int(Li),lim_i,lim_s,v,vr)
        L = Li
            
    correl=pd.DataFrame(correl)
    # Devuelve el límite infeior más cercano al límite de Tukey con menor correlación
    if c == 1:
        menor = correl.index[correl['corre'] == correl.corre.max()].tolist()
    else:
        menor = correl.index[correl['corre'] == correl.corre.min()].tolist()
    if len(menor) == abs(Li-lim_i):
        menor_ = L
    else:
        menor_ = correl['lim'][menor[-1]]
    #print(correl['lim'][menor],correl['corre'][menor])
    return menor_

def val_mayor(L1,L2,lim_i,var,var_rel):
    'Determia la columna de correlación entre dos variables'
    global filtrado
    correl={'corre':[],'lim':[]}
    #ciclo for para variar el rango desde el límite inferior hasta el límite de Tukey
    for rango in range(int(L1),int(L2)):
        # Eto se puede  variar y que filtro var devuelva el indice de correlación de Pearson
        #filtrado = mediciones_cacao.copy()
        # Aplcación del filtro de rango
        corre = filtro_var(var,lim_i,rango)
        correl['corre'].append(corre.iloc[var,var_rel])
        correl['lim'].append(rango)
    return correl

def filtro_mayor(v,vr,lim_i,lim_s,c):
    global filtrado
    
    variable = filtrado.columns[v]
            
    # Se realiza el test de Tukey
    Li, Ls = tukey(filtrado[variable])
    if Ls>lim_s:
        # val_rngo determina unna columna de correlación para diferentes rangos       
        correl = val_mayor(lim_s,int(Ls),lim_i,v,vr)
        L=lim_s
    else:
        correl = val_mayor(int(Ls),lim_s,lim_i,v,vr)
        L=Ls    
    correl=pd.DataFrame(correl)
    # Devuelve el límite infeior más cercano al límite de Tukey con menor correlación
    if c == 1:
        mayor = correl.index[correl['corre'] == correl.corre.max()].tolist()
    else:
        mayor = correl.index[correl['corre'] == correl.corre.min()].tolist()
    if len(mayor) == abs(Ls-lim_s):
        mayor_ = L
    else:
        mayor_ = correl['lim'][mayor[0]]
    return mayor_