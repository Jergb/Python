# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 18:29:10 2018

Contiene las funciones necesarias para el análisis del dataset.
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


def impbd(db, tabla):
    'impbd Importa tabla desde la bd'
    dbConnect = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': db
    }

    conexion = mysql.connector.connect(**dbConnect)
    cursor = conexion.cursor()

    sql = 'select * from ' + tabla
    cursor.execute(sql)
    resultados = pd.DataFrame.from_records(cursor.fetchall(), columns=[desc[0]
                                           for desc in cursor.description])
    return resultados


def timeTranscurrido(WSN, i):

    TiempoTranscurrido = int((WSN.TIME[i] - WSN.TIME[i - 1]).seconds / 60)
    TiempoTranscurrido += (WSN.TIME[i] - WSN.TIME[i - 1]).days * 24 * 60

    return TiempoTranscurrido


def MesDiaPlot(WSN):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(WSN.DIA, 'g', label='DIAS')
    ax2.plot(WSN.MES, 'k.', ms=.01, label='MESES')
    ax1.set_ylabel("DIAS")
    ax2.set_ylabel("MESES")


def datosplot(MedidaDuplicadaN, CantidadDuplicadosN, MedidaAnalizar,
              CantidadAnalizar, MedidaFaltantesN, CantidadFaltantesN, WSN):

        alp, c, cc = '0.5', ['r', 'g'], ['#B452CD', '#FFF68F']
        m, mm, y = ['^', 'v'], ['h', 'D'], []
        plt.scatter(MedidaAnalizar, CantidadAnalizar, alpha=alp, c='b',
                    label='Datos para Analizar')

        for p, N in enumerate([2, 5]):
            plt.scatter(MedidaFaltantesN[N], CantidadFaltantesN[N],
                        alpha=alp, c=c[p], marker=m[p],
                        label='Faltantes en el Nodo' + str(N))
            plt.scatter(MedidaDuplicadaN[N], CantidadDuplicadosN[N],
                        alpha=alp, c=cc[p], marker=mm[p],
                        label='Duplicados en el Nodo' + str(N))
            y.append(len(CantidadFaltantesN[N]))
            y.append(len(CantidadDuplicadosN[N]))

        y.append(len(CantidadAnalizar))
        plt.title('Limpieza de datos')
        plt.legend()
    #    plt.figure()

    #    def mil(x, pos):
    #        return '%1.1fk' % (x * 1e-3)

    #    formatter = FuncFormatter(mil)
    #    f, ax = plt.subplots()

    #    ax.yaxis.set_major_formatter(formatter)
    #    cl = len([2, 5])
    #    co = ['r', 'g', '#B452CD', '#FFF68F', 'b']
    #    x = np.arange(cl * 2 + 1)
    #    plt.bar(x, y, color=co)
    #    plt.xticks(x, ('Faltantes del N2', 'DuplicadosN2','Faltantes del N5',
    #                   'DuplicadosN5', 'Valores para el Análisis'),
    #               rotation='vertical')


def Nfalt(WSN, Ni):
    F = []
    for N in [2, 5]:
        if N not in Ni:
            F.append(N)
    return F


def filtro(WSN):
    'filtro mantiene sólo valores de mediciones simultaneas en los nodos 2 y 5'
    WSN.loc[:, 'TIME'] = [pd.Timestamp(x) for x in WSN['TIME']]
    WSN = pd.DataFrame([WSN.iloc[0, :]]).append(WSN, ignore_index=True)
    WSN.loc[0, 'TIME'] = WSN.loc[0, 'TIME'] - timedelta(seconds=60)
    WSN = WSN.append(pd.DataFrame(WSN.iloc[[len(WSN)-2, len(WSN)-1], :]),
                     ignore_index=True)
    WSN.loc[len(WSN)-1:, 'TIME'] = WSN.loc[len(WSN)-1:, 'TIME']\
        + timedelta(seconds=60)
    WSN.loc[len(WSN)-2:, 'TIME'] = WSN.loc[len(WSN)-2:, 'TIME']\
        + timedelta(seconds=60)
    WSN.loc[[0, len(WSN)-1, len(WSN)-2], 'NODO'] = 0
#    WSN['HUMEDAD DE LA TIERRA'] = [float(str(x).replace(',', '.'))
#                                   for x in WSN['HUMEDAD DE LA TIERRA']]
    wsn = []

    for i in range(1, len(WSN) - 2):

        if ((WSN.TIME[i].minute == WSN.TIME[i+1].minute and
           WSN.TIME[i].minute != WSN.TIME[i + 2].minute and
           WSN.NODO[i] != WSN.NODO[i+1]) or (WSN.TIME[i-1].minute
           == WSN.TIME[i].minute and WSN.TIME[i].minute !=
           WSN.TIME[i+1].minute and WSN.NODO[i-1] != WSN.NODO[i])):

            wsn.append(WSN.iloc[i])

    WSN = pd.DataFrame(wsn).reset_index(drop=True)
    return WSN


def filtrop(WSN):
    'filtro mantiene sólo valores de mediciones simultaneas en los nodos 2 y 5'
    WSN.loc[:, 'TIME'] = [pd.Timestamp(x) for x in WSN['TIME']]
    WSN = pd.DataFrame([WSN.iloc[0, :]]).append(WSN, ignore_index=True)
    WSN.loc[0, 'TIME'] = WSN.loc[0, 'TIME'] - timedelta(seconds=60)
    WSN = WSN.append(pd.DataFrame(WSN.iloc[[len(WSN)-2, len(WSN)-1], :]),
                     ignore_index=True)
    WSN.loc[len(WSN)-1:, 'TIME'] = WSN.loc[len(WSN)-1:, 'TIME']\
        + timedelta(seconds=60)
    WSN.loc[len(WSN)-2:, 'TIME'] = WSN.loc[len(WSN)-2:, 'TIME']\
        + timedelta(seconds=60)
    WSN.loc[[0, len(WSN)-1, len(WSN) - 2], 'NODO'] = 0
#    WSN['HUMEDAD DE LA TIERRA'] = [float(str(x).replace(',', '.'))
#                                   for x in WSN['HUMEDAD DE LA TIERRA']]

    CuentaDuplicados, CuentaFaltante, TiempoTotal, CuentaAnalizar = 0, 0, 0, 0
    CantidadFaltantes, MedidaAnalizar = [], []
    CantidadAnalizar, CantidadDuplicados = [], []
    MedidaFaltante, MedidaDuplicada, wsn = [], [], []
    VectorTiempoTranscurrido, VectorTiempoTotal = [], []
    CantidadDuplicadosN, MedidaFaltantesN = {}, {}
    CantidadFaltantesN, MedidaDuplicadaN = {}, {}

    for nodo in [2, 5]:
        CantidadDuplicadosN[nodo], MedidaFaltantesN[nodo] = [], []
        CantidadFaltantesN[nodo], MedidaDuplicadaN[nodo] = [], []

    Ni = []
    F = []

    for i in range(1, len(WSN) - 2):

        TiempoTranscurrido = timeTranscurrido(WSN, i)
        VectorTiempoTranscurrido.append(TiempoTranscurrido)
        TiempoTotal += TiempoTranscurrido
        VectorTiempoTotal.append(TiempoTotal)

        if (TiempoTranscurrido == 0 or (TiempoTranscurrido == 1 and
           WSN.NODO[i] == WSN.NODO[i - 1]) or Ni == []):

            Ni.append(WSN.NODO[i])

        if ((WSN.TIME[i].minute == WSN.TIME[i + 1].minute and
             WSN.TIME[i].minute != WSN.TIME[i + 2].minute and
             WSN.NODO[i] != WSN.NODO[i + 1]) or (WSN.TIME[i-1].minute
           == WSN.TIME[i].minute and WSN.TIME[i].minute
           != WSN.TIME[i+1].minute and WSN.NODO[i - 1] != WSN.NODO[i])):

            wsn.append(WSN.iloc[i])
            CuentaAnalizar += 1
            CuentaDatos = CuentaAnalizar + CuentaFaltante + CuentaDuplicados
            CantidadAnalizar.append(CuentaAnalizar)
            MedidaAnalizar.append(CuentaDatos)

        else:

            if WSN.TIME[i] == WSN.TIME[i - 1] and WSN.NODO[i]\
               == WSN.NODO[i - 1]:

                CuentaDuplicados += 1
                CuentaDatos = (CuentaAnalizar + CuentaFaltante
                               + CuentaDuplicados)
                CantidadDuplicados.append(CuentaDuplicados)
                MedidaDuplicada.append(CuentaDatos)
                CantidadDuplicadosN[WSN.NODO[i]].append(CuentaDuplicados)
                MedidaDuplicadaN[WSN.NODO[i]].append(CuentaDatos)

            elif TiempoTranscurrido >= 1:

                F = Nfalt(WSN, Ni)

                for F_i in F:
                    CuentaFaltante += 1
                    CuentaDatos = (CuentaAnalizar + CuentaFaltante
                                   + CuentaDuplicados)
                    CantidadFaltantesN[F_i].append(CuentaFaltante)
                    MedidaFaltantesN[F_i].append(CuentaDatos)

                for CountF in range(TiempoTranscurrido - 1):

                    CuentaFaltante += 1
                    CuentaDatos = CuentaAnalizar + CuentaFaltante\
                        + CuentaDuplicados
                    CantidadFaltantes.append(CuentaFaltante)
                    MedidaFaltante.append(CuentaDatos)

                    for N in [2, 5]:

                        CantidadFaltantesN[N].append(CuentaFaltante)
                        MedidaFaltantesN[N].append(CuentaDatos)

                F = []
                Ni = []
    print('Faltantes nodo 2: ', len(CantidadFaltantesN[2]))
    print('Faltantes nodo 5: ', len(CantidadFaltantesN[5]))
    WSN = pd.DataFrame(wsn).reset_index(drop=True)

    return MedidaDuplicadaN, CantidadDuplicadosN, MedidaAnalizar,\
        CantidadAnalizar, MedidaFaltantesN, CantidadFaltantesN, WSN


def wsnbp(WSN):
    b = 150
    for a in range(5):
        b += 1
        plt.subplot(b)
        WSN.iloc[:, a:a+1].boxplot()


def Datasets(WSN, edge):
    inicio, fin, p = [], [], 0

    for i in range(1, len(WSN)):

        if p == 0:
            inicio.append(i)
            p = 1

        if timeTranscurrido(WSN, i) > edge:
            fin.append(i)
            p = 0

    fin.append(i)
    data, DataSet = [], []

    for fin_i in range(len(fin)):

        dataset = WSN[inicio[fin_i]:fin[fin_i]]

        for dataset_i in range(len(dataset)):

            data.append(dataset.iloc[dataset_i])

        Datas = pd.DataFrame(data).reset_index(drop=True)
        data = []
        DataSet.append(Datas)
        Tiempo = pd.DataFrame({'inicio': inicio, 'fin': fin})
    return DataSet, Tiempo


def norma(tabla):
    'norma normaliza la matriz de datos.'
    from sklearn.preprocessing import StandardScaler
    norma = pd.DataFrame(StandardScaler().fit_transform(tabla))
    norma.columns = tabla.columns.tolist()
    return norma


def tablas(resultados):
    'tablas crea los DataFraMes utilizadas para el analísis de la información.'
    tabla2 = resultados.query('NODO==2').reset_index(drop=True)
    tabla5 = resultados.query('NODO==5').reset_index(drop=True)
    return tabla2, tabla5


def distributionplot(Tabla):
    'pdistribution presenta el Díagrama de dispersión de las variables.'
    Tabla = Tabla.iloc[:, 1:7]
    Tabla['NODO'].replace(to_replace=[-1, 2], value='Nodo2', inplace=True)
    Tabla['NODO'].replace(to_replace=[1, 5], value='Nodo5', inplace=True)
    sns.pairplot(Tabla, hue='NODO', plot_kws=dict(s=10))


def corrplot(Data):
    'pcorr presenta el grafico de correlación de las variables.'
    Data = Data.iloc[:, 2:7]
    plt.matshow(Data.corr())
    plt.xticks(range(len(Data.columns)), Data.columns)
    plt.yticks(range(len(Data.columns)), Data.columns)
    plt.colorbar()


def mahalM(tabla2, tabla5, Rr):
    'mahal obtiene la distancias de Mahalanobis entre los nodos dos y cinco.'
    nodos = {}
    nodos['nodo2'] = tabla2.values.tolist()
    nodos['nodo5'] = tabla5.values.tolist()
    nodos = pd.DataFrame(nodos)
    nodos25 = nodos[['nodo2', 'nodo5']]
    CovVars = Rr.cov()
    iCovVars = Inv(CovVars)
    DM = nodos25.apply(lambda m: MH(m.nodo2, m.nodo5, iCovVars), axis=1)
    return DM


def Inv(m):
    from scipy.linalg import LinAlgError

    try:
        inv = sp.linalg.inv(m)
        print('normal')
        return inv

    except LinAlgError:
        print('buscada')
        s = m.shape
        i = sp.eye(s[1], s[1])
        return sp.linalg.lstsq(m, i)[0]


def euclidea(tabla2, tabla5):
    from sklearn.preprocessing import StandardScaler
    tabla2 = pd.DataFrame(StandardScaler().fit_transform(tabla2))
    tabla5 = pd.DataFrame(StandardScaler().fit_transform(tabla5))
    nodos = {}
    nodos['nodo2'] = tabla2.values.tolist()
    nodos['nodo5'] = tabla5.values.tolist()
    nodos = pd.DataFrame(nodos)
    nodos25 = nodos[['nodo2', 'nodo5']]
    DE = nodos25.apply(lambda m: EU(m.nodo2, m.nodo5), axis=1)
    return DE


#   Tukey obtiene los límites inferiores y superiores para cada columna de
#   Datos, apartir de los cuales los valores son considerados ouliers
#   univariantes

def tukey(Datos, variables):

    desc = Datos.describe()
    Li = {}
    Ls = {}
    for var in range(len(variables)):
            RIQ = desc[variables[var]][6] - desc[variables[var]][4]
            Li[var] = desc[variables[var]][4] - RIQ * 1.5
            Ls[var] = desc[variables[var]][6] + RIQ * 1.5
    return Li, Ls

#   Tukeytest aplica el test a cada elemento de tabla y devuelve tuplas con
#   indices y valores correspondiendientes a outliers univariantes

def Tukeytest(datos, tabla, Li, Ls):
    idVar=tabla.iloc[:, 0]
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
#   pvhist grafica los histogramas de las variables
#==============================================================================  
def pvhist(variables,Rr):
    for nvar,var in enumerate(variables):
        plt.figure()    
        plt.title(variables[nvar])
        plt.hist(Rr[var]) # Histograma de las variables
#==============================================================================
#   pvarg grafica todas las variables sobre una sola grafica identificando los 
#   outliers univariantes meDíante un punto rojo
#==============================================================================  
def pvarg(variables,Rr,fil2,fil5,col2,col5):
        for vamo in range(len(variables)):
            plt.subplot(2,1,1)
            plt.title('Variables Globlal')
            plt.plot(Rr[variables[vamo]],linewidth=1,label=variables[vamo])
            plt.scatter(fil2[vamo],col2[vamo],color='r')
            plt.scatter(fil5[vamo],col5[vamo],color='r')
            plt.legend()
#==============================================================================
#   pvars grafica cada variable por separado identificando los outliers
#==============================================================================  
def pvaro(variables,Rr,fil2,fil5,col2,col5):
    for nvar,var in enumerate(variables):
        plt.subplot(5,1,nvar+1)
        plt.title(var)
        plt.plot(Rr[var],linewidth=.5)
        plt.scatter(fil2[nvar],col2[nvar],color='r')
        plt.scatter(fil5[nvar],col5[nvar],color='r')
#==============================================================================
#   pvarnodo grafica el comportamiento de las variables en cada nodo
#==============================================================================  
def pvarnodo(variables,tabla2,tabla5,col2,col5,fila2,fila5):
    for nvar in range(len(variables)):
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(tabla2[variables[nvar]])
        plt.scatter(fila2[nvar],col2[nvar],color='r')
        plt.subplot(2,1,2)
        plt.plot(tabla5[variables[nvar]])
        plt.scatter(fila5[nvar],col5[nvar],color='r')
        
def p3d():
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')
#    Axes3D.scatter(xs, ys, zs=0, zdir=’z’, s=20, c=None, depthshade=True, *args, **kwargs)
    
