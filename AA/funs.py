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

def time_transcurrido(datos, i):
    'Calcula el tiempo transcurrido entre dos mediciones'
    
    tiempo_transcurrido = int((datos.TIME[i] - datos.TIME[i - 1]).seconds / 60)
    tiempo_transcurrido += (datos.TIME[i] - datos.TIME[i - 1]).days * 24 * 60

    return tiempo_transcurrido

def separa_datos(datos, edge):
    'Divide los datos cuando faltan edge mediciones'
    inicio, fin, p = [], [], 0

    for i in range(1, len(datos)):

        if p == 0:
            inicio.append(i)
            p = 1

        if time_transcurrido(datos, i) > edge:
            fin.append(i)
            p = 0

    fin.append(i)
    data, separados = [], []

    for fin_i in range(len(fin)):

        dataset = datos[inicio[fin_i]:fin[fin_i]]

        for dataset_i in range(len(dataset)):

            data.append(dataset.iloc[dataset_i])

        separar = pd.DataFrame(data).reset_index(drop=True)
        data = []
        separados.append(separar)
        
    inicio = [datos.TIME[x] for x in inicio]
    fin = [datos.TIME[x-1] for x in fin]
    tamaño= [len(separados[x]) for x in range(len(separados))]
    duracion = pd.DataFrame({'inicio': inicio, 'fin': fin, 'datos': tamaño})
    return separados, duracion

def info_var(v):
    'Grafica todos los valores medidos para la variable v'
    variable = mediciones_cacao.columns[v]
    
    plt.plot(mediciones_cacao[variable],'orange',label='datos')
    plt.title(variable)
    plt.legend()
    
def tukey(variable):
    'Obtiene los límites superiores e inferiores para v'
    
    RIQ = variable.quantile(q=.75) - variable.quantile(q=.25)
    Li = variable.quantile(q=.25) - RIQ * 1.5
    Ls = variable.quantile(q=.75) + RIQ * 1.5
    return Li, Ls

def filtro(variable,i,q):
    'Iguala el valor de una medición a un determinado valor límite'
    global filtrado
    
    try:
        filtrado[variable][i] = filtrado[variable][i-120:i].median()   
        
    except KeyError:
        filtrado[variable][i]= q
    return

def filtro_var(v,lim_i,lim_s):
    'Ajusta los valores atípicos en las mediciones de la variable v'
    
    global filtrado
    variable=filtrado.columns[v]
    Li, Ls = tukey(filtrado[variable])

    for i in range(len(filtrado[variable])):
              
        if filtrado[variable][i] >= lim_s:
            filtro(variable,i,filtrado[variable].quantile(.75))
        
        elif filtrado[variable][i] <= lim_i:
            filtro(variable,i,filtrado[variable].quantile(.25))
            
        elif filtrado[variable][i] >= Ls and Ls > lim_s:
            filtro(variable,i,filtrado[variable].quantile(.75))
            
        elif filtrado[variable][i] <= Li and Li < lim_i:
            filtro(variable,i,filtrado[variable].quantile(.25))
            
    return filtrado.corr()

def up_ajuste(filtrado,v):
    global ajustado
    variable=ajustado.columns[v]
    ajustado[variable]=filtrado[variable].copy()
    return

def ajuste_variacion(v):
    'Ajusta los valores que presentan una variación superior a la std'
    global ajustado
    up_ajuste(filtrado,v)
    variable=ajustado.columns[v]
    ventana=60
    rolling_std = ajustado[variable].rolling(ventana).std()
    rolling_std_inv=ajustado[variable].iloc[::-1].rolling(ventana).std().iloc[::-1]
    indice=rolling_std[rolling_std.isnull().values].index
    rolling_std[indice[0]]=rolling_std_inv[indice[0]]

    nvalores=ajustado[variable][rolling_std>(rolling_std.mean())].index.values
    rolling_median=ajustado[variable].rolling(ventana).median()
    rolling_median_inv=ajustado[variable].iloc[::-1].rolling(ventana).median().iloc[::-1]
    indice=rolling_median[rolling_median.isnull().values].index
    rolling_median[indice[0]]=rolling_median_inv[indice[0]]
    suave=ajustado[variable].copy()
    suave[nvalores]=rolling_median[nvalores+ventana]
    plt.figure()
    plt.plot(filtrado[variable],label='filtrado')
    plt.plot(suave,label='suavizado')
    plt.legend()
    ajustado[variable]=suave
    return

def val_menor(L1,L2,lim_s,var,var_rel):
    'Determia la columna de correlación entre dos variables'
    global filtrado
    correl={'corre':[],'lim':[]}
    #ciclo for para variar el rango desde el límite inferior hasta el límite de Tukey
    for rango in range(int(L1),int(L2)):
        # Eto se puede  variar y que filtro var devuelva el indice de correlación de Pearson
#        filtrado = mediciones_cacao.copy()
        # Aplcación del filtro de rango
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