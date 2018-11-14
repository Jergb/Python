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
from ggplot import *
import scipy as sp
from IPython.display import Markdown
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
    fin = [datos.index[x-1] for x in fin]
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
    inicioi = pd.Timestamp(inicio)
    fini = pd.Timestamp(fin)
    data = dataset.loc[inicioi:fini,:]
    inicio = data.index[0]
    fin = data.index[-1]
    tiempo = fin - inicio
    registros = len(data)
    
    faltantes = transcurrido_fechas(fin, inicio) + 1 - registros
    r_registros = (registros / (transcurrido_fechas(fin, inicio) +1))*100
    n_registros = (faltantes / (transcurrido_fechas(fin, inicio) +1))*100
    info = pd.DataFrame({'Registro Inicial': [inicio], 'Registro Final': [fin],
                             'Registrado': [registros], 'No Registrado':[faltantes],
                             'Registrado(%)':[r_registros],'No Registrado(%)':[n_registros],
                             'Duración':[tiempo]})
    return data, info


def info_relation(df,v1,v2):
    'Permite visualizar la relación entre dos variables'
    df = df.loc[:,[v1, v2]].copy()
    corr = df.loc[:,[v1,v2]].corr().iloc[0,1]
    mag = {'TEMPERATURA':'°C', 'HUMEDAD RELATIVA':'%RH',
           'HUMEDAD DE LA TIERRA':'%', 'INTENSIDAD LUMÍNICA':'LX'}
    a=1    
    
    fig = plt.figure(figsize=[17,8])
    display(Markdown('<center>**GRÁFICOS DE \
                     %s Y %s**</center>'%(v1,v2)))
    display(Markdown('<center>$\\rho = %.2f$\
                     </center>'%corr))
    
    
    with plt.style.context(('seaborn')):
        
        plt.subplot(331) 
        plt.text(0.26,-.05,'%s'%(pd.DataFrame(      
            raw[v1].describe())),fontsize=15)
        plt.axis('off')
        plt.subplot(332)
        plt.boxplot(df[v1],vert=False,flierprops=dict(markerfacecolor='r'))
        plt.yticks([])
        plt.subplot(333)
        plt.text(0.26,-.05,'%s'%(pd.DataFrame(      
            raw[v2].describe())),fontsize=15)
        plt.axis('off')
        plt.subplot(334)
        plt.hist(df[v2],orientation='horizontal',alpha=.6)
        plt.xlabel('FRECUENCIA')
        plt.ylabel('%s %s'%(v2,mag[v2]))
        plt.subplot(337)
        plt.plot(df[v1],alpha=.6)
        plt.xlabel('FECHA')
        plt.ylabel('%s'%(mag[v1]))
        plt.subplot(339)
        plt.plot(df[v2],alpha=.6)
        plt.xlabel('FECHA')
        plt.ylabel('%s'%(mag[v2]))
        plt.subplot(338)
        plt.hist(df[v1],alpha=.6)
        plt.xlabel('%s %s'%(v1,mag[v1]))
        plt.ylabel('FRECUENCIA')
        plt.subplot(335)
        plt.scatter(df[v1],df[v2],linewidths=.8,alpha=.6)        
        for v in [v1,v2]:
            li,ls = tukey(df[v])
            try:
                ind = [[x,df[v][x]] for x in list(df[v].index)
                       if df[v].loc[x]<=li or df[v].loc[x]>=ls]
                df.loc[pd.DataFrame(ind).iloc[:,0],'o%d'%a] = pd.DataFrame(ind).iloc[:,1].values
                a+=1
                try:
                    plt.scatter(df['o1'],df[v2],color='r')
                    plt.subplot(337)
                    plt.plot(df['o1'],'ro')
                    plt.subplot(338)
                    plt.hist(df['o1'][~np.isnan(df['o1'])],
                             facecolor='r')
                    plt.subplot(335)
                except KeyError:
                    pass
                try: 
                    plt.scatter(df[v1],df['o2'],color='r')     
                    plt.subplot(339)
                    plt.plot(df['o2'],'ro')
                    plt.subplot(334)
                    plt.hist(df['o2'][~np.isnan(df['o2'])],
                             facecolor='r',orientation='horizontal')
                    plt.subplot(335)
                except KeyError:
                    pass
                
            except (IndexError,NameError) as e:
                pass

        plt.subplot(336)
        plt.boxplot(df[v2],flierprops=dict(markerfacecolor='r'))
        plt.xticks([])
    plt.tight_layout()

def dist_variable(var):
    plt.figure(figsize=[17,6])
    variable = pd.DataFrame(var)
    vari = variable.columns
    mag = {'TEMPERATURA':'°C', 'HUMEDAD RELATIVA':'%RH',
           'HUMEDAD DE LA TIERRA':'%', 'INTENSIDAD LUMÍNICA':'LX'}
    plt.suptitle('DISTRIBUCIÓN DE VALORES DE LA VARIABLE %s'%vari[0])
    plt.subplot(121)
    plt.hist(var,orientation='horizontal',alpha=.6)
    plt.title('HISTOGRAMA DE %s'%vari[0])
    plt.xlabel('Frecuencia')
    plt.ylabel('%s'%(mag[vari[0]]))
    plt.subplot(122)
    plt.boxplot(var,flierprops=dict(markerfacecolor='r'))
    plt.text(1.08, var.quantile(.25), 'Q1', fontsize=12)
    plt.text(1.08, var.quantile(.75), 'Q3', fontsize=12)
    li,ls=tukey(var)
    if var.max() > ls:
        plt.text(1.04, ls, 'Límite superior', fontsize=12)
        plt.text(0.85, np.mean([var.max(),ls]), 'OUTLIERS', fontsize=12,color='r')
    else:
        plt.text(1.04, np.mean([var.max()]), 'Valor máximo', fontsize=12)
    if var.min() < li:
        plt.text(1.04, li, 'Límite inferior', fontsize=12)
        plt.text(0.85, np.mean([var.min(),li]), 'OUTLIERS', fontsize=12,color='r')
    else:
        plt.text(1.04, np.mean([var.min()]), 'Valor mínimo', fontsize=12)
    plt.ylabel('%s'%(mag[vari[0]]))
    plt.xlabel('%s'%vari[0])
    plt.title('DIAGRAME DE CAJAS Y BIGOTES PARA %s'%vari[0])
    display(variable.describe())

def info_var(v):
    'Grafica todos los valores medidos para la variable v'
    variable = raw.columns[v]
    plt.figure(figsize=[17,5])
    plt.plot(raw[variable],'orange',label='datos')
    plt.title(variable)
    plt.legend()
    
def tukey(variable):
    'Obtiene los límites superiores e inferiores para v'
    
    RIQ = variable.quantile(q=.75) - variable.quantile(q=.25)
    Li = variable.quantile(q=.25) - RIQ * 1.5
    Ls = variable.quantile(q=.75) + RIQ * 1.5
    return Li, Ls

def filtro(filtrar,variable,i,q):
    'Iguala el valor de una medición a un determinado valor límite'
    
    try:
        
        d=len(filtrar[variable].iloc[0:i])/(60*24)
        val=[filtrar[variable][i-(60*24)*(1+j)] for j in range(int(d)) if d>1]
        val.append(filtrar[variable][i-1])
        filtrar[variable][i] = np.mean(val)

    except KeyError:
        filtrar[variable][i]= q
    return filtrar

def filtrar_variables(variable,lim_i,lim_s):
    'Ajusta los valores atípicos en las mediciones de la variable v'
    global filtrado
    Li, Ls = tukey(filtrar[variable])

    for i in range(len(filtrar[variable])):
        if filtrar[variable][i] >= lim_s:
            filtro(filtrado,variable,i,filtrado[variable].quantile(.75))
        
        elif filtrar[variable][i] <= lim_i:
            filtro(filtrado,variable,i,filtrado[variable].quantile(.25))
            
#    plt.plot(filtrado.loc[:,variable],'blue',label='filtrar')
    #plt.legend()
    return

def filtro_var(variable,lim_i,lim_s):
    'Ajusta los valores atípicos en las mediciones de la variable v'
    
    global raw
    filtrar = raw.copy()
    Li, Ls = tukey(filtrar[variable])

    for i in range(len(filtrar[variable])):
              
        if filtrar[variable][i] >= lim_s:
            filtro(filtrar,variable,i,filtrar[variable].quantile(.75))
        
        elif filtrar[variable][i] <= lim_i:
            filtro(filtrar,variable,i,filtrar[variable].quantile(.25))
            
    return filtrar.corr()

def up_ajuste(filtrar,variable):
    global ajustado,filtar
    ajustado[variable]=filtrado[variable].copy()
    return

def ajuste_variacion(variable):
    'Ajusta los valores que presentan una variación superior a la std'
    global ajustado,filtrado,raw
    mag = {'TEMPERATURA':'°C', 'HUMEDAD RELATIVA':'%RH',
           'HUMEDAD DE LA TIERRA':'%', 'INTENSIDAD LUMÍNICA':'LX'}
    up_ajuste(filtrado,variable)
    ventana=60
    rolling_std = ajustado[variable].rolling(ventana).std()
    rolling_std_inv=ajustado[variable].iloc[::-1].rolling(ventana).std().iloc[::-1]
    indice=rolling_std[rolling_std.isnull().values].index
    rolling_std.loc[indice]=rolling_std_inv.loc[indice]
   
    suave=ajustado[variable].copy()
    nvalores=suave[rolling_std>(rolling_std.quantile(.5))].index
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
    
    plt.figure(figsize=[17,5])
    plt.title(variable)
    plt.plot(raw[variable],label='datos')
    plt.plot(suave,label='suavizado')
    plt.ylabel('%s'%mag[variable])
    plt.xlabel('FECHA')
    plt.legend()
    ajustado[variable]=suave
    return

def val_menor(L1,L2,lim_s,var,var_rel):
    'Determia la columna de correlación entre dos variables'

    correl = [[filtro_var(var,rango,lim_s).loc[var,var_rel],rango] for rango in range(int(L1),int(L2))]    
    
    return correl


def filtro_menor(v,vr,lim_i,lim_s,c):
    global filtrar
            
    # Se realiza el test de Tukey
    Li, Ls = tukey(filtrar[v])
    if Li>lim_i:
        # val_rngo determina unna columna de correlación para diferentes rangos       
        correl = val_menor(lim_i,int(Li),lim_s,v,vr)
        L = lim_i
    else:
        correl = val_menor(int(Li),lim_i,lim_s,v,vr)
        L = Li
    
    corre={'corre':[],'lim':[]} 
    corre['corre']=[f0[0] for f0 in correl]
    corre['lim']=[f1[1] for f1 in correl]
    correl=pd.DataFrame(corre)
    #correl=pd.DataFrame(correl)
    
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
    global filtrar
    
    correl = [[filtro_var(var,lim_i,rango).loc[var,var_rel],rango] for rango in range(int(L1),int(L2))]
    
    return correl

def filtro_mayor(v,vr,lim_i,lim_s,c):
    global filtrar

    # Se realiza el test de Tukey
    Li, Ls = tukey(filtrar[v])
    if Ls>lim_s:
        # val_rngo determina unna columna de correlación para diferentes rangos       
        correl = val_mayor(lim_s,int(Ls),lim_i,v,vr)
        L=lim_s
    else:
        correl = val_mayor(int(Ls),lim_s,lim_i,v,vr)
        L=Ls    
    #correl=pd.DataFrame(correl)
    
    corre={'corre':[],'lim':[]} 
    corre['corre']=[f0[0] for f0 in correl]
    corre['lim']=[f1[1] for f1 in correl]
    corre=pd.DataFrame(corre)
    
    # Devuelve el límite infeior más cercano al límite de Tukey con menor correlación
    if c == 1:
        mayor = corre.index[corre['corre'] == corre.corre.max()].tolist()
    else:
        mayor = corre.index[corre['corre'] == corre.corre.min()].tolist()
    if len(mayor) == abs(Ls-lim_s):
        mayor_ = L
    else:
        mayor_ = corre['lim'][mayor[0]]
    return mayor_