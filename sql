import mysql.connector

dbConnect = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'prueba'
}

conexion = mysql.connector.connect(**dbConnect)
cursor = conexion.cursor()

# Lee todos los elementos de la tabla pruebatabla
sql = 'select * from pruebatabla'
cursor.execute(sql)
resultados = cursor.fetchall()
print(resultados)
d = 0
sum = 0
for datos in resultados:
    print(resultados[d][1])
    sum += float(resultados[d][1])
    d += 1
print('La suma de los valores es:', sum)

"""sqlInsertar = 'insert into tabladatos(Media,Mediana,Mayor)values(%s,%s,%s)'
cursor.execute(sqlInsertar,('1',sum,sum,))
conexion.commit()
cursor.close()
conexion.close()"""
"""
# Insertar valores
sqlInsertar = 'insert into pruebatabla(col1,col2,col3)values(%s,%s,%s)'
cursor.execute(sqlInsertar,('10','8','6',))
conexion.commit()
cursor.close()
conexion.close()"""

"""sql = 'select * from pruebatabla where col2 = %s'
cursor.execute(sql,('2',))
resultados = cursor.fetchone()
print(resultados)"""
for f in range()

"""conexion = mysql.connector.connect(**dbConnect)
cursor = conexion.cursor()

for pos,fila in enumerate(WSN.HUMEDADD):

    sql = 'update medidas set HUMEDADD = %s where IDMEDIDA=%s'
    cursor.execute(sql,(fila,pos+1,))
    
conexion.commit()
cursor.close()
conexion.close()"""

"""sql = 'delete from pruebatabla where col1 = %s'
cursor.execute(sql,('9',))
resultados = cursor.fetchone()
conexion.commit()
cursor.close()
conexion.close()"""


"""sqlInsertar = 'insert into tabladatos(col1,col2,col3)values(%s,%s,%s)'
cursor.execute(sqlInsertar,('101','7','27',))
conexion.commit()
cursor.close()
conexion.close()"""