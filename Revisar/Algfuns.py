# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 10:08:31 2018

Funciones para detección de valores atípicos, duplicados y/o faltantes.
@author: Jergb
"""

import pandas as pd
import sqlalchemy
# import time
from datetime import timedelta


def bajar():
    'Consulta filas de la tabla "mediciones" en la base de datos de la red.'
    global WSN, fila
    fila = str(fila)
    motor = 'mysql+pymysql://root:@localhost:3306/WSN'
    engine = sqlalchemy.create_engine(motor)
    if pd.read_sql_query('select * from medidas where IDMEDIDA ='
                         + fila, engine).empty == 0:
        WSN = WSN.append(pd.read_sql_query('select * from medidas\
                         where IDMEDIDA ='+fila, engine), ignore_index=True)

        if len(WSN) == 1:
            WSN = pd.DataFrame([WSN.iloc[0, :]]).append(WSN, ignore_index=True)
            WSN.loc[0, 'TIME'] = WSN.loc[0, 'TIME'] - timedelta(seconds=60)
            WSN.loc[0, 'NODO'] = 0

        fila = int(fila) + 1
        return


def bajarprueba():
    global WSN, fila
    fila = str(fila)
    motor = 'mysql+pymysql://root:@localhost:3306/WSN'
    engine = sqlalchemy.create_engine(motor)
    if pd.read_sql_query('select * from pruebatabla where ID ='
                         + fila, engine).empty == 0:
        WSN = WSN.append(pd.read_sql_query('select * from pruebatabla\
                         where ID ='+fila, engine), ignore_index=True)

        if len(WSN) == 1:
            WSN = pd.DataFrame([WSN.iloc[0, :]]).append(WSN, ignore_index=True)
            WSN.loc[0, 'TIME'] = WSN.loc[0, 'TIME'] - timedelta(seconds=60)
            WSN.loc[0, 'NODO'] = 0

        fila = int(fila) + 1
        return


def timeTranscurrido(i):
    global WSN
    TiempoTranscurrido = int((WSN.TIME[i] - WSN.TIME[i-1]).seconds / 60)
    TiempoTranscurrido += (WSN.TIME[i]-WSN.TIME[i-1]).days * 24 * 60
    return TiempoTranscurrido


def Nfalt(Ni):
    F = []
    for N in [2, 5]:
        if N not in Ni:
            F.append(N)
    return F


def agregar(row):
    global WSN
    WSN = WSN.append(pd.DataFrame(WSN.iloc[[len(WSN) - 2, len(WSN) - 1], :]),
                     ignore_index=True)
    WSN.loc[len(WSN) - 1:, 'TIME'] = WSN.loc[len(WSN) - 1:, 'TIME']\
        + timedelta(seconds=60)
    WSN.loc[len(WSN) - 2:, 'TIME'] = WSN.loc[len(WSN) - 2:, 'TIME']\
        + timedelta(seconds=60)
    WSN.loc[[len(WSN) - 1, len(WSN) - 2], 'NODO'] = 0
    filtro(row+1)
    filtro(row+2)
    return


def filtro(i):
    global WSN, Duplicados, Faltantes, RIS, Ni, Faltan
    WSN['TIME'] = [pd.Timestamp(x) for x in WSN['TIME']]

    TiempoTranscurrido = timeTranscurrido(i)

    if (TiempoTranscurrido == 0 or (TiempoTranscurrido == 1
       and WSN.NODO[i] == WSN.NODO[i-1]) or Ni == []):
        Ni.append(WSN.NODO[i])

    if ((WSN.TIME[i].minute == WSN.TIME[i+1].minute and WSN.TIME[i].minute
       != WSN.TIME[i+2].minute and WSN.NODO[i] != WSN.NODO[i+1])
       or (WSN.TIME[i-1].minute == WSN.TIME[i].minute and WSN.TIME[i].minute
       != WSN.TIME[i+1].minute and WSN.NODO[i-1] != WSN.NODO[i])):

        RIS = RIS.append(pd.DataFrame([WSN.iloc[i]]), ignore_index=True)

    else:
        if WSN.TIME[i] == WSN.TIME[i-1] and WSN.NODO[i] == WSN.NODO[i-1]:

            Duplicados[WSN.NODO[i]][0] += 1

        elif TiempoTranscurrido >= 1:

            F = Nfalt(Ni)
            Faltan += TiempoTranscurrido - 1
            for F_i in F:

                Faltantes[F_i][0] += 1

            for N in [2, 5]:

                Faltantes[N][0] += TiempoTranscurrido - 1

            F = []
            Ni = []
    return

def tablas(resultados):
    'tablas crea los DataFraMes utilizadas para el analísis de la información.'
    tabla2 = resultados.query('NODO==2').reset_index(drop=True)
    tabla5 = resultados.query('NODO==5').reset_index(drop=True)
    return tabla2, tabla5
