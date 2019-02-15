import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd
import numpy as np
import scipy as sp
import seaborn as sb
from scipy.spatial.distance import mahalanobis as MH
from pylab import rcParams


importe=1
if importe==1:
    db='prueba'
    tabla='pruebatabla'
else:
    db='WSN'
    tabla='medidas'
# Importar tabla de la base de datos
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

# Comienza el filtro de datos duplicados en el tiempo
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

#   Separación de datos de los nodos dos y cinco

cols=['id_Variable','id_nodo','Temperatura','Humedad','HumTierra','Nivel_UV',
      'INTLUMIN','YEAR','MES','DIA','HORA','MINUTO']


for pos in range(len(cols)):
    datos2[cols[pos]] = np.array([float((col[pos]).replace(',','.')) for col
          in resultados if col[1] == '2'])
    datos5[cols[pos]] = np.array([float((col[pos]).replace(',','.')) for col
          in resultados if col[1] == '5'])
    paresdic = { 'Nodo2' : datos2['id_Variable'], 'Nodo5' : datos5['id_Variable']} 
    data25['NT'] = np.array([(col[8]+col[9]+col[10]+col[11]) for col in resultados
          if col[1] == '2'])
    data['NT'] = np.array([(col[8]+col[9]+col[10]+col[11]) for col in resultados
        if col[1] != 'aa'])
    rr[cols[pos]] = np.array([float((col[pos]).replace(',','.')) for col
      in resultados if col[1] != 'aa'])
    
del(resultados,cols)
del(datos2['id_nodo'],datos2['YEAR'],datos2['MES'],datos2['DIA'],datos2['HORA'],datos2['MINUTO'])
del(datos5['id_nodo'],datos5['YEAR'],datos5['MES'],datos5['DIA'],datos5['HORA'],datos5['MINUTO'])
Dia=rr['DIA']
del(rr['id_nodo'],rr['YEAR'],rr['MES'],rr['DIA'],rr['HORA'],rr['MINUTO'])
id_Variable=rr['id_Variable']

del(rr['id_Variable'],)
plo={}
Rr = pd.DataFrame(rr)        
tabla2, tabla5, pares = pd.DataFrame(datos2), pd.DataFrame(datos5), pd.DataFrame(paresdic)

del(datos2,datos5,paresdic)

#   Aplicación de la Distancia de Mahalanobis para detección de outliers multivariables
pares = pares.merge(tabla2, how='left', left_on=['Nodo2'], right_on=['id_Variable'])
pares = pares.merge(tabla5, how='left', left_on=['Nodo5'], right_on=['id_Variable'])

#del(tabla2,tabla5)

pares['vector2'] = pares[['Temperatura_x','Humedad_x','HumTierra_x','Nivel_UV_x','INTLUMIN_x']].values.tolist()
pares['vector5'] = pares[['Temperatura_y','Humedad_y','HumTierra_y','Nivel_UV_y','INTLUMIN_y']].values.tolist()

mahala = pares[['Nodo2', 'Nodo5', 'vector2', 'vector5']]

vector2=pares.vector2
vector5=pares.vector5

del(pares)

covmx = Rr.cov()
invcovmx = sp.linalg.inv(covmx)

mahala['mahala_dist'] = mahala.apply(lambda m: MH(m['vector2'], m['vector5'], invcovmx), axis=1)
Nodo2, Nodo5, mahaladist = mahala.Nodo2, mahala.Nodo5, mahala.mahala_dist

del(covmx)


#   Aplicación del Criterio de Tukey para detección de outliers univariables
vars=['Temperatura','Humedad','HumTierra','Nivel_UV','INTLUMIN']

pd.options.display.float_format ='{:.1f}'.format
desc=Rr.describe()
desc2=tabla2.describe()
desc5=tabla5.describe()
Li={}
Ls={}

for ff in range(len(vars)):
        RIQ=desc[vars[ff]][6]-desc[vars[ff]][4]
        Li[ff]=desc[vars[ff]][4]-RIQ*1.5
        Ls[ff]=desc[vars[ff]][6]+RIQ*1.5
        
i=[0,1,2,3,4]

outlierf,outlierf2,outlierf5,outlierc,outlierc2,outlierc5={},{},{},{},{},{}
sw2,sw5,sn2,sn5={},{},{},{}
for io in vars:
    outlierf[io],outlierf2[io],outlierf5[io],outlierc[io],sw2[io]=[],[],[],[],[]
    outlierc2[io],outlierc5[io],sw5[io],sn2[io],sn5[io]=[],[],[],[],[] 
    

plt.close('all')
plt.figure()
plt.title('Distribución datos nodo2 vs nodo 5')

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

for pos in range(len(vector2)):
    fila2, fila5= vector2[pos],vector5[pos]
    if mahaladist[pos]<0.9:
        for ubi,fila in enumerate(fila2):
            sn2[vars[ubi]].append(vector2[pos])
            sn5[vars[ubi]].append(vector5[pos])
    else:
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

#Boxplots
#sb.boxplot(x='Temperatura',y='Humedad',data=Rr,palette='hls')
#scatterplot matrix
Rr['Dia']=Dia
sb.pairplot(Rr,hue='Dia',palette='hls')

#
#for vamo in vars:
#    plt.subplot(2,2,1)
#    if vamo!='INTLUMIN':
#        plt.scatter(sn5[vamo],sn2[vamo],color='b')
#        plt.plot(sw5[vamo],sw2[vamo],'ro')
#    else:
#        plt.scatter(sn5[vamo],sn2[vamo],color='b',label='normales')
#        plt.plot(sw5[vamo],sw2[vamo],'ro',label='outliers')
#        plt.legend()
##        
#for vamo in vars:
#    plt.subplot(2,2,2)
#    plt.title('Variables Globlal')
#    plt.plot(Rr[vamo],linewidth=1,label=vamo)
#    plt.scatter(outlierc[vamo],outlierf[vamo],color='r')
#    plt.legend()
# 
#for num,vamo in enumerate(vars):
#    plt.subplot(2,5,num+6)
#    plt.title(vamo)
#    plt.plot(Rr[vamo],linewidth=1)
#    plt.scatter(outlierc[vamo],outlierf[vamo],color='r')
#
#for vamo in vars:
#    plt.figure()
#    plt.subplot(2,1,1)
#    plt.plot(tabla2[vamo])
#    plt.scatter(outlierc2[vamo],outlierf2[vamo],color='r')
#    plt.subplot(2,1,2)
#    plt.plot(tabla5[vamo])
#    plt.scatter(outlierc5[vamo],outlierf5[vamo],color='r')

    
"""
Qué pasa con las humedadades?
Solucionar el efecto enmascaramiento!!!
Probar outlier univariable primero?
Hacer el outlier referido al otro nodo, al mismo nodo o globla?
Qué se debe tener en cuenta para la detección de los outliers por Mahalanobis??
Outliers cercanos a lamedia!!!!!"""