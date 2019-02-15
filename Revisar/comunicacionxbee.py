#!/usr/bin/python
import serial
import time
from xbee import XBee, ZigBee
import MySQLdb
import datetime
import math
ser = serial.Serial('/dev/ttyAMA0',9600) #Configuracion - puerto serial
db = MySQLdb.connect(host="localhost",user="root",passwd="xbee1234", db="Supervision_WSN") #Conexion db
db.autocommit(True) #Ejecutar cambios en la base de datos automaticamente
cur = db.cursor()   #Inicializar el cursor

cur.execute ("SELECT DIR64,id_nodo,Padre,Tipo,DIR16,Latitud,Longitud,Estado FROM NODOS_SENSORES") #Seleccionar los datos basicos de la db
addresses_list={} #Inicializar Diccionario
#AGREGAR VARIABLE DEL FUNCIONAMIENTO INICIAL PARA LA PREGUNTA DE LA HORA...
Nnodo=1 
LunesP=1	#EJECUCION PROMEDIO UNA VEZ LUNES
MesP=1		#EJECUCION PROMEDIO UNA VEZ AL MES
DiaP=0		#EJECUCUIB PROMEDIO UNA VEZ AL DIA
cant_nodos=0	#CANTIDAD DE NODOS DENTRO DE LA WSN
CAMBIO="01"	#CAMBIO DE PARAMETROS XBEE
cont_succ=0	#CONTADOR DE EXITO EN EL CAMBIO DE PARAMETROS - HASTA 3
Fallo_end=0	#Fallo de end device #1=Funcional #0=Averiado #2=Posible Fallo
Ejecucion_lectura=1 #Lectura de nodo
#CAMBIO='0013a20041540fdf'
print "INICIANDO ALGORITMO DE SUPERVISION"
tiempoinicial=datetime.datetime.now()
horainicial=tiempoinicial.hour
addresses_list={}
Lista_ed_cercanos=[]
Nodo_FAIL='0'
def Distancia(Primer_nodo,Segundo_nodo):
#	print "Calculando distancia"
	Distancia = math.sqrt(((addresses_list[Primer_nodo][7]-addresses_list[Segundo_nodo][7])*10000000/90)**2+((addresses_list[Primer_nodo][6]-addresses_list[Segundo_nodo][6])*10000000/90)**2)
	return Distancia

for row in cur.fetchall():
	if row[0]!="-": 
#		print row[1]
		lista=[]
		lista.append(row[1]) #[0] id_nodo
		lista.append(row[2]) #[1] Padre
		lista.append(row[3]) #[2] Tipo
		lista.append(row[4]) #[3] DIR16
		lista.append(horainicial) #[4] Comprobar si es padre#cambiar a hora...
		lista.append(0)	     #[5] Ejecutar cambio al nodo ##1-Pasar a router##2-Pasar a End device##SE PUEDEN AGREGAR MAS COMANDOS...
#		lista.append(row[0]) #[6] DIR64 - Item- NO ES NECESARIO HASTA EL MOMENTO
		lista.append(row[5]) #[6] Latitud
		lista.append(row[6]) #[7] Longitud
		lista.append(row[7]) #[8] Estado #0 Averiado- 1 Funcional original - 2 Posible Fallo - 3 Con posible fallo e Intentando arreglar - 4 Fallo el intento de arreglo
				     #	         #5 Funcional End Device transformado a router para intentar asociar #6 Router a end device por dejar de ser padre
#		lista.append(0)	     #[9] Intento de asociacion por cambio de End Device a Router #0 No se esta intentando - 1 En intento - 2 No se logro
		lista.append(0)#9 Distancia al coordinador
		lista.append(9)#10 Posicion de cercania al coordinador
		lista.append(0)#11 Nodo que trata de re ingresar a la red
		addresses_list[row[0]]=lista # Key = DIR64
		cant_nodos=cant_nodos+1
#print addresses_list
Nodos_total= addresses_list.keys()
ord_dist=[]
for nodo_i in Nodos_total:
	addresses_list[nodo_i][9]=Distancia(nodo_i,'0013a20041541017')	
	ord_dist.append(addresses_list[nodo_i][9])
#addresses_list[CAMBIO][5]=1
print cant_nodos
ord_dist.sort()
#Creo que no es necesario...
for nodo_i in Nodos_total:
	cont_nodos=0
	for n in ord_dist:
		if addresses_list[nodo_i][9]==n:			
			addresses_list[nodo_i][10]=cont_nodos
		cont_nodos=cont_nodos+1
print addresses_list
########################################SENTENCIAS SQL###########################################################
#sentencia = "INSERT into Variables (id_Variable,id_nodo, Temperatura) values (15,5,32)"
#cur.execute("INSERT into Variables (id_Variable,id_nodo, Temperatura) values (%s,%s, %s)",(idV,id, Temperatura))

#cur.execute("INSERT into Variables (id_nodo, Temperatura) values (5,33)")
#cur.execute ("UPDATE Variables SET Temperatura=35 WHERE id_nodo=5 ORDER BY id_variable DESC LIMIT 1")
#cur.execute ("SELECT Temperatura FROM Variables WHERE id_nodo=5 ORDER BY id_Variable DESC LIMIT 1")
#for row in cur.fetchall():
#	print row[0]
#db.commit()
#db.close()
#################################################################################################################

#Funcion para convertir a hexadecimal
#PROMEDIOS DE LA SEMANA INMEDIATAMENTE ANTERIOR

#def Distancia(Primer_nodo,Segundo_nodo):
#	print "Calculando distancia"
#	Primer_nodo='0013a20041541017'
#	Segundo_nodo='0013a20041541016'
#	Segundo_nodo='0013a2004155f485'
#	Distancia = math.sqrt(((addresses_list[Primer_nodo][7]-addresses_list[Segundo_nodo][7])*10000000/90)**2+((addresses_list[Primer_nodo][6]-addresses_list[Segundo_nodo][6])*10000000/90)**2)
#	print Distancia
#	print addresses_list[Primer_nodo][7]	
#	print Primer_nodo
#	return Distancia
#dist_nodo = Distancia('s','a')
#print dist_nodo

def Promdia(instante):
#	print "Ejecutar Promedio dia 1 vez"
	global LunesP
	dfin= instante.day
#	dfin=4  #Probar lunes a inicio de mes
	LunesP=0
#	print LunesP
	dinit= dfin-7
	minit=instante.month
#	minit=1	
	ainit=instante.year
	afin=ainit
	mfin=minit
	tipinit=0
	if (dinit<1):	#Si el lunes anterior corresponde al mes anterior
		minit = minit-1 #Mes inicial - es el mes anterior
		tipinit=1
		if (minit==0): #Si el mes inicial corresponde al anio anterior
			minit=12 #Mes inicial = diciembre
			ainit=ainit-1 #Anio inicial = anio anterior
		cant_dias = 31 #Cantidad de dias inicial en 31
		if (minit==2):
			cant_dias=28 #Si es febrero
		else:
			if (minit<=7): 
				if(minit % 2==0):
					cant_dias=30 #Mes par
			else:
				if(minit % 2!=0):
					cant_dias=30 #Mes impar
		dinit=cant_dias+dinit
	calculopromedios(tipinit,dinit,minit,ainit,dfin,mfin,afin)

def Prommes(instante):
	#CALCULO DE PROMEDIO MENSUAL
	global MesP
	MesP=0
#	print "CALCULANDO MES"
#	print MesP
	Mesinit=instante.month-1
	Anioinit=instante.year
	if (Mesinit==0):
		Mesinit=12
		Anioinit=Anioinit-1
	calculopromedios(2,1,Mesinit,Anioinit,0,0,0)

def calculopromedios(tipo_prom,d_init,m_init,a_init,d_fin,m_fin,a_fin):
#	print "Ejecutar en db"
	global cant_nodos
#	print cant_nodos
#	L_sem= ["P_S_Temperatura","P_S_Humedad","P_S_Ruido","P_S_Nivel_UV","P_S_Intensidad_lm","P_S_Potencia","P_S_Intensidad","P_S_T_Nodo"]	
#	L_mes= ["P_M_Temperatura","P_M_Humedad","P_M_Ruido","P_M_Nivel_UV","P_M_Intensidad_lm","P_M_Potencia","P_M_Intensidad","P_M_T_Nodo"]	
	Lista_db=[]
#	print tipo_prom	
	print "CALCULANDO PROMEDIOS..."
#	print L_sem[0]
	for i in range(1,cant_nodos+1):
#		print i
		com_prom= ("SELECT avg(Temperatura),avg(Humedad),avg(Ruido),avg(Nivel_UV),avg(Intensidad_lm), avg(Potencia),"+
				"avg(Intensidad),avg(Tiempo_Nodo),avg(Try) FROM Variables WHERE id_nodo="+str(i))
		prom_t_serv = "SELECT avg(tiempo_servidor) FROM Tiempos_Servidor WHERE id_nodo="+str(i)
		prom_horas=" "
		if (tipo_prom==0):   #PROMEDIO SEMANAL CUANDO LA SEMANA SE ENCUENTRA EN EL MISMO MES
#			com_prom= com_prom+" AND Dia>="+str(d_init)+" AND Mes="+str(m_init)+" AND Anio="+str(a_init)
			Lista_db=["P_S_Temperatura","P_S_Humedad","P_S_Ruido","P_S_Nivel_UV","P_S_Intensidad_lm","P_S_Potencia","P_S_Intensidad","P_S_T_Nodo","P_S_T_Servidor"]
			condicion= (" AND ((Dia>="+str(d_init)+" AND Mes="+ str(m_init)+ " AND Anio="+str(a_init)+") AND (Dia<"+
					str(d_fin)+" AND Mes=" +str(m_fin)+ " AND Anio="+str(a_fin)+"))")
			com_prom = com_prom+condicion
			prom_t_serv=prom_t_serv + condicion
		elif (tipo_prom==1): #PROMEDIO SEMANAL CUANDO LA SEMANA SE ENCUETNRA ENTRE DOS MESES
#			print "TIPO 1"
			Lista_db=["P_S_Temperatura","P_S_Humedad","P_S_Ruido","P_S_Nivel_UV","P_S_Intensidad_lm","P_S_Potencia","P_S_Intensidad","P_S_T_Nodo","P_S_T_Servidor"]
			condicion= (" AND ((Dia>="+str(d_init)+" AND Mes="+ str(m_init)+ " AND Anio="+str(a_init)+") OR (Dia<"+
					str(d_fin)+" AND Mes=" +str(m_fin)+ " AND Anio="+str(a_fin)+"))")
			com_prom = com_prom + condicion
			prom_t_serv=prom_t_serv + condicion
		elif (tipo_prom==2): # PROMEDIO MENSUAL
#			print "TIPO 2"			
			Lista_db= ["P_M_Temperatura","P_M_Humedad","P_M_Ruido","P_M_Nivel_UV","P_M_Intensidad_lm","P_M_Potencia","P_M_Intensidad","P_M_T_Nodo","P_M_T_Servidor"]	
			condicion = " AND Mes="+str(m_init)+" AND Anio="+str(a_init)
			com_prom = com_prom+condicion
			prom_t_serv=prom_t_serv + condicion
			
		elif (tipo_prom==3): # PROMEDIO GENERAL ---- CREO QUE NO SE NECESITA HACER NADA ACA
#			print "TIPO 3"
			Lista_db= ["P_G_Temperatura","P_G_Humedad","P_G_Ruido","P_G_Nivel_UV","P_G_Intensidad_lm","P_G_Potencia","P_G_Intensidad","P_G_T_Nodo","P_G_T_Servidor"]
#		print "AJA"
#		print com_prom
		cur.execute(com_prom)
		datos=cur.fetchall()
		prom_sem_db="UPDATE NODOS_SENSORES SET "
#		print prom_t_serv
		cur.execute(prom_t_serv)
#		print "fun aca"
		tiempos_ser=cur.fetchall()
#		print "PROMEDIO TIEMPOS DE SERVIDOR******************************************"
		
#		print prom_t_serv
#		print "**********************************************************************"
		for cd in range (0,9):
#			print cd
			if ((datos[0][cd]==None) and (cd<8)):
				valor=0
			else:
				if cd<8:
					valor = round(datos[0][cd],3)

			if cd<8:
				prom_sem_db= prom_sem_db + Lista_db[cd]+"= "+ str(valor)+ ", "
#			print "entrando"
			else: 
#				print "aca va"
				if ((tiempos_ser[0][0]==None)):
					valor=0
				else:
					valor=round(tiempos_ser[0][0],3)
				prom_sem_db= prom_sem_db + Lista_db[cd]+"= "+ str(valor)+ " WHERE id_nodo="+str(i)
#			print prom_sem_db
#		print prom_sem_db
		cur.execute(prom_sem_db)
		prom_hora_db="UPDATE Tabla_horas SET "
		for hora in range (0,24):
			prom_horas = com_prom + " AND Hora = "+ str(hora)
			cur.execute(prom_horas)
			dato_hora= cur.fetchall()
			prom_horas = prom_t_serv+ " AND Hora = "+ str(hora)
			cur.execute(prom_horas)
			tiempos_ser = cur.fetchall()
#			print dato_hora
			prom_hora_db= "UPDATE Tabla_horas SET "
			for dh in range (0,9):
				if ((dato_hora[0][dh]==None) and (dh<8)):
					valor=0
				else:
					if dh<8:
						valor = round(datos[0][dh],3)
				if dh<8:
					prom_hora_db= prom_hora_db + Lista_db[dh]+"= "+ str(valor)+ ", "
				else: 
					if ((tiempos_ser[0][0]==None)):
						valor = 0
					else:
						valor=round(tiempos_ser[0][0],3)
					prom_hora_db= prom_hora_db + Lista_db[dh]+"= "+ str(valor)+ " WHERE id_nodo="+str(i) + " AND id_hora ="+ str(hora)
#			print prom_hora_db		
			cur.execute(prom_hora_db)
	print "FIN DE CALCULO DE PROMEDIOS"
 
def toHex(s):
    lst = [] #<- No se usa (Lista)
    direc64 = "" #<- se usa (String)
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
#        hv = '0x' + hv
	direc64 = direc64 + hv
        lst.append(hv) #<- No se usa
    return direc64 #<- se usa

#Funcion Para convertir a Decimal
def todec(param):
	for num in param:
		numero=hex(ord(num)).replace('0x','')
	return numero

#Pasar la informacion a la lista contenedora
def tolist(information):
	inicio = 0
	contador = 0
	bandera = 0
	variables = {}	
	variables["Tem"]="0"
	variables["Hum"]="0"
	variables["Rui"]="0"
	variables["Nuv"]="0"
	variables["Ilm"]="0"
	variables["Pot"]="0"
	variables["Int"]="0"
	variables["TNo"]="0"
	variables["Try"]="0"
	variables["TSe"]="0"
	#Separa la informacion basado en "+" y ":"
	otcontador=0
	for element in information:
		if element == "+":
			if bandera == 0:
				inicio= contador+1
				bandera = 1
			else:
				cadena = information[inicio:contador]
				if information[0]=="1":
					if otcontador == 0:
						variables["DIR"]=cadena
						otcontador = 1
					else:
						variables["RSSI"]=cadena
				else:
					ncontador = 0
					for nelem in cadena:
						if nelem == ":": 
							variables[cadena[0:ncontador]]=cadena[ncontador+1:len(cadena)]
						ncontador = ncontador +1
				inicio = contador +1
		contador = contador+1
	return variables

#Funcion para recibir la informacion por interrupcion del puerto serial en formato API del modulo XBee
def print_data(data):
    global horainicial
    global tiempoinicial
    global Fallo_end
    print "INICIANDO PROCESAMIENTO DE DATA"
#    print horainicial
#    horainicial=8
#    print horainicial
    tiempoactual=datetime.datetime.now()
    horaactual=tiempoactual.hour
    print horaactual
   # horaactual=8
    if horaactual==25:#!=horainicial:
		print "Cambio de hora"
		#tiempoinicial=datetime.datetime.now()
		horainicial=tiempoinicial.hour
		nodos_key=addresses_list.keys()
		Mes_E=  tiempoinicial.month
		Anio_E= tiempoinicial.year
		Dia_E= 	tiempoinicial.day
		for i in range(2,cant_nodos+1):
#			print i
			com_prom= ("SELECT Temperatura FROM Variables WHERE id_nodo="+str(i)+" AND Hora="+str(horainicial)
					+ " AND Dia="+str(Dia_E)+ " AND Mes="+str(Mes_E)+" AND Anio="+ str(Anio_E))
#			print com_prom
			
			cur.execute(com_prom)
			datos=cur.fetchall()
#			print datos
			if datos==():
#				print "No informacion en el nodo"+ str(i)
				cur.execute("SELECT DIR64 FROM NODOS_SENSORES WHERE id_nodo= "+str(i))
				dir64s=cur.fetchall()
				dir_key= dir64s[0][0]
				#dir_key='0013a2004155f489'
#				print addresses_list[dir_key][0]
				estado_actual=addresses_list[dir_key][8]
				#if addresses_list[dir_key][2]==1:
				#	print "ROUTER"
				#	if estado_actual==1:
				#		print "PASAR ESTADO A 0-NODO CON FALLO"
				#		cur.execute("UPDATE NODOS_SENSORES SET Estado=0 WHERE id_nodo="+str(i))

				#else:
				#	print "End device"
				if estado_actual==1 or estado_actual==2:
				#		print "Pasar a posible fallo ESTADO A 2"
						Fallo_end=2
						if estado_actual==1:
							cur.execute("UPDATE NODOS_SENSORES SET Estado=2 WHERE id_nodo="+str(i))
							addresses_list[dir_key][8]=2
				#elif estado_actual==2:#PREGUNTAR SI SE ESTA EN POSIBLE FALLO
				#		print "esta en posible fallo-no hacer nada"
						#Verificar nodos End device cercanos - Si hay cercanos con estado 1 o 2 o 3
						Nodos_dir64=addresses_list.keys()
						Nodos_cercanos = 0 # 0 No hay cercanos funcionales o con posibilidad de funcionar - 1 Si hay
#						print Nodos_dir64
						for nodo_dir64f in Nodos_dir64:
#							print nodo_dir64f
							if addresses_list[nodo_dir64f][8]!=0 and addresses_list[nodo_dir64f][2]==2 and nodo_dir64f!=dir_key:
								#Si no esta averiado totalmente  -  Si es un nodo sensor              - si es diferente al nodo averiado
								Dist_nodo=Distancia(nodo_dir64f,dir_key)
								if Dist_nodo<=101:
				#					print "Tiene solucion"
									Nodos_cercanos = 1
				#					print "Distancia Nodo cercano"
				#					print nodo_dir64f
				#					print "Es"
				#					print Dist_nodo
							#print "Buscando cercanos"
							################
##############################################################################
						if Nodos_cercanos==0:
							print "No tiene solucion pasar estado a 0"
						#Si no los hay - es decir entonces reportar al nodo como fallo
						Fallo_end=2
				elif estado_actual==3:#PREGUNTAR SI ESTA EN INTENTO DE REASOCIACION INNECESARIO
				#		print "Intentando Reestablecer comunicacion... Hacer nada"
						Fallo_end=3
				elif estado_actual==4: #INNECESARIO
				#		print "PASAR ESTADO A 0 Fallo en el nodo - no funciona"
						cur.execute("UPDATE NODOS_SENSORES SET Estado=0 WHERE id_nodo="+str(i))
						addresses_list[dir_key][8]=0
						Fallo_end=0
				#print "----"
		if Fallo_end!=0:
			Nodo_Fallo=[]
			Nodos_dir64=addresses_list.keys()
			for nodo_dir64f in Nodos_dir64:
				if addresses_list[nodo_dir64f][8]==2: #Si el nodo esta con estado de posible fallo
					print "Nodo con posible fallo" #Almacenar la dir64 del nodo con posible fallo... comenzar con 1
					Nodo_Fallo.append(nodo_dir64f)
			if Nodo_Fallo!=[]:
				orden_fallo=[]		
				cont_fallo=0				
				for nodo_Fal in Nodo_Fallo:
					#Nodo_FAIL= nodo_Fal	
					if cont_fallo==0:
						Nodo_FAIL=nodo_Fal
					else:
						if (addresses_list[nodo_Fal][9]<addresses_list[Nodo_FAIL][9]):
							Nodo_FAIL=nodo_Fal
#					Nodo_Fail=nod_Fal
#					orden_fallo.append(addresses_list[nodo_Fal][9])
#				orden_fallo.sort()
#				Nodo_Fail=
				#print Nodo_FAIL
				#print "Buscar"			
				for nodo_dir64f in Nodos_dir64:
					if addresses_list[nodo_dir64f][8]==1:
						print "imp"#Lista_ed_cercanos		
						 #Buscar por nodos cercanos
#						Nodo_keys=addresses_list.keys()
						#for nodos_k in Nodo_keys:
						#	print addresses_list[][1]
						
#				for dir_nodo in nodos_key:
#					print dir_nodo
		#print cant_nodos
 		#print Fallo_end
		tiempoinicial=datetime.datetime.now()
		horainicial=tiempoinicial.hour

    else:
			print "Diferente hora"

    print Fallo_end

    if data['id']=='rx':
#	print "-----------------------------------------------------------------------------------------------------"
	direccion   = toHex(data['source_addr_long']) #Convertir DIR 64 en hexadecimal formato string
	direccion16 = toHex(data['source_addr'])      #Convertir DIR 16 en hexadecimal formato string
#	print "DIRECCION:"
	global CAMBIO
	global Fallo_end
#	print direccion
	id_nodo = 0
#	print direccion16
#	print addresses_list[direccion][3]
	inform = data['rf_data']		      #Leer e payload 
	lista_datos = tolist(inform)		      #Pasar payload a lista procesada
	print lista_datos
	print inform[0]
	instante=datetime.datetime.now()
	if addresses_list.has_key(direccion):	      #Si la DIR 64 se encuentra en la bd
		id_nodo= addresses_list[direccion][0]
		if addresses_list[direccion][8]!=1 and addresses_list[direccion][8]!=5 and addresses_list[direccion][8]!=6:
			print "Ponerlo funcional ya se recibe info"
			cur.execute("UPDATE NODOS_SENSORES SET Estado=1 WHERE id_nodo="+str(id_nodo))
			addresses_list[direccion][8]=1

	#	if inform[0]== "0":		      #Si es informacion de un router
		if direccion16!=addresses_list[direccion][3]: #Si la DIR16 es diferente a la de la bd
				print "Diferente a"	
				print addresses_list[direccion][3]
				DIRO= "0"
				todb_16= ("UPDATE NODOS_SENSORES SET DIR16= '" +direccion16 +
					  "' WHERE id_nodo=" + str(id_nodo)) #Actualizar DIR 16 en bd
#				print todb_16
				cur.execute(todb_16)
				addresses_list[direccion][3]=direccion16     #Actualizar DIR 16 en la lista
		else:
				print "IGUAL DIR16"
		if inform[0]=="0":
			print addresses_list[direccion][4]
			print instante.hour
			if (addresses_list[direccion][4]!=instante.hour) and (CAMBIO=="05"): ##AGREGAR CONDICION EN CASO DE ESTAR REALIZANDO CAMBIOS A END DEVICES
				sen_nod=addresses_list.keys() ####cambiar minute por hour
#				print "entra"
				es_padre=0
				for ejnod in sen_nod:
#					print addresses_list[ejnod][1]
					if addresses_list[ejnod][1]==addresses_list[direccion][0]: #SI EL ID_NODO SE ENCUENTRA COMO PADRE DE CUALQUIER OTRO NODO
						print "***********************************************************************************************"
						print "ES UN PADRE"
						es_padre=1
				if es_padre==0:
#					print "NO ES UN PADRE"
					CAMBIO=direccion	       #ACTIVAR EL CAMBIO
					addresses_list[direccion][5]=2 #PASAR A END DEVICE
				addresses_list[direccion][4]=instante.hour
			
		if inform[0]!="1":		     #Si no es RSSI DESDE ROUTER
			if inform[0] =="0":	     #Si es router
				if addresses_list[direccion][2]!=1:
					print "NO ES ROUTER" 
					todb_type = "UPDATE NODOS_SENSORES SET Tipo=1 WHERE id_nodo="+ str(id_nodo) #Actualizar si no es router en bd
					cur.execute(todb_type)
					addresses_list[direccion][2]=1 #Actualizar Tipo en la lista
					todb_topad= "UPDATE NODOS_SENSORES SET Padre=1 WHERE id_nodo="+str(id_nodo)#Actualizar padre coordinador 1 en bd
					cur.execute(todb_topad)
					addresses_list[direccion][1]=1 #Actualizar padre en lista (coordinador 1)
				else:
					print "SI ES ROUTER COMO EN BD"
			elif ((inform[0] == "2") or (inform[0]=="3")):
				if addresses_list[direccion][2]!=2:
					todb_type = "UPDATE NODOS_SENSORES SET Tipo=2 WHERE id_nodo="+ str(id_nodo) #Actualizar si no es End Device en bd
					cur.execute(todb_type)
					addresses_list[direccion][2]=2 #Actualizar Tipo en la lista
					print "NO ES END DEVICE"
				#else:
				#	print "SI ES END DEVICE"
				if inform[0]=="3": #Si es End Device con router padre
					todb_pad = ("SELECT id_nodo FROM NODOS_SENSORES WHERE DIR16='"+
							lista_datos["Pad"]+"'")
					cur.execute (todb_pad) 
					for row in cur.fetchall():
						padnod=row[0]
					if padnod==addresses_list[direccion][1]: #Si es mismo padre que en db
						print "MISMO PADRE"
					else:					#Si es diferente padre
				#		print "OTRO PADRE"
						todb_topad= "UPDATE NODOS_SENSORES SET Padre="+str(padnod)+" WHERE id_nodo="+str(id_nodo)#Actualizar padre en bd
						cur.execute(todb_topad)
						addresses_list[direccion][1]=padnod #Actualizar padre en la lista
				elif inform[0]=="2": #Si es End Device con coordinador padre
					if addresses_list[direccion][1]!=0:
						print "PONER PADRE BD"
						todb_topad= "UPDATE NODOS_SENSORES SET Padre=1 WHERE id_nodo="+str(id_nodo)#Actualizar padre coordinador 1 en bd
						cur.execute(todb_topad)
						addresses_list[direccion][1]=1 #Actualizar padre en lista (coordinador 1)
#				print instante.hour
#				print addresses_list[direccion][4]
#				print "**************************************************************************************"
				print "****************************************************************************************"
				if Fallo_end==6 or Fallo_end==7:#Si existe posible fallo en un end device
														    #Tambien agregar si Fallo_end es 3 entre
#				if Fallo_end==2 or Fallo_end==3: #COMENTAR##############################################################################
					addresses_list[direccion][4]=instante.hour
#					addresses_list[direccion][4]=12
					print "Posible fallo"#Verificar si el end device se encuentra cerca basado en la ubicacion calcular distancia basado en Lat-Long
					#print "Transformar a ROUTER"
					# Esto hara transformar todos los end device cercanos a router... Es viable o solo el mas cercano
					# Puede que el mas cercano tenga obstaculos alredor... y uno un poco mas lejos tenga mejor linea de vista
					#0 - Si no intenta arreglar
#					print addresses_list[]
					if addresses_list[direccion][8]!=5: #Si el estado del end device es diferente a 5 (End device que se habia transformado a router)
					#1- Buscar el end device con posible Fallo					
						nodos_dir64=addresses_list.keys() #Direcciones de 64bits de todos los nodos
						Nodo_Fallo=[]
						for nodo_dir64f in nodos_dir64:
							if addresses_list[nodo_dir64f][8]==2 or addresses_list[nodo_dir64f][8]==3: #Si el nodo esta con estado de posible fallo
								print "Nodo con posible fallo" #Almacenar la dir64 del nodo con posible fallo... comenzar con 1
								Nodo_Fallo.append(nodo_dir64f)
						print Nodo_Fallo
						cantidad_fallos=len(Nodo_Fallo)
						for i in range (0,cantidad_fallos):
							#Analizar cada nodo
							Distancia_nodo=Distancia(direccion,Nodo_Fallo[i])
							if Distancia_nodo<=101:
								print "Cercano"
								#Transformar a router PONER VARIABLE DE CAMBIO PARA ETR
								addresses_list[direccion][5]=1 #Activar cambio a router
								CAMBIO=direccion
								cur.execute("UPDATE NODOS_SENSORES SET Estado=3 WHERE id_nodo="+str(addresses_list[Nodo_Fallo[i]][0]))
								addresses_list[Nodo_Fallo[i]][8]=3
								cur.execute("UPDATE NODOS_SENSORES SET Estado=5 WHERE id_nodo="+str(addresses_list[direccion][0]))
								addresses_list[direccion][8]=5
								
								#Pasar ESTADO Nodo_Fallo[i] a 3
							else:
								print "Lejano"
							print Nodo_Fallo[i]
							print Distancia_nodo
						#PASO 2
#						if Realizar_cambio==1:
#							print "Transformar a Router"
						#Distancia_nodos=Distancia(direccion,Nodo_Fallo)
						#print Distancia_nodos
					else:
						#BUSCAR EL NODO CERCANO QUE INTENTABA ASOCIARSE... OTRA VEZ BUSCAR EL NODO CERCANO? A LO MEJOR PERO AHORA NO ES CON POSIBLE FALLO
						#SINO CON EL ESTADO = 3 INTENTANDO... PASARLO A 0 DE GOLPE
						nodos_dir64=addresses_list.keys() #Direcciones de 64bits de todos los nodos
						for nodo_dir64f in nodos_dir64:
							if addresses_list[nodo_dir64f][8]==3: #Si el nodo esta intentando reasociarse a la red y es cercano
								print "Nodo intentando reasociarse" #Almacenar la dir64 del nodo con posible fallo... comenzar con 1
								Distancia_nodo=Distancia(direccion,nodo_dir64f)
								if Distancia_nodo<=101:
									#Pasar Estado de nodo_dir64f a 0 - Pasar Estado de direccion a 1 nuevamente
									cur.execute("UPDATE NODOS_SENSORES SET Estado=0 WHERE id_nodo="+str(addresses_list[nodo_dir64f][0]))
									addresses_list[nodo_dir64f][8]=0
									cur.execute("UPDATE NODOS_SENSORES SET Estado=1 WHERE id_nodo="+str(addresses_list[direccion][0]))								
									addresses_list[direccion][8]=1
									print "Retornando a estados anteriores"
						print "No sirvio, mantengase como end device y ponga estado=4 o.... estado=0 de una vez... para darle mas tiempo de unirse"
						#Paso 7 
					#2- Comparar las distancias del nodo con posible fallo y el nodo actual
					#3- Si se encuentran a menos de 100m transformar a router
					#4- Actualizar estado del nodo actual a 5 en la bd
					#5- Actualizar estado del nodo actual a 5 en addresses_list
					#6- Actualizar estado del nodo con posible fallo a 3 (Intentando arreglar)
					#7- La proxima vez que entre aca si no es padre ya sera end device nuevamente.
					#   Si el estado es 5 y el end device sigue sin funcionar entonces pasar estado del end device(actual 3) a Estado=0 en bd y en diccionario
					#cur.execute("UPDATE NODOS_SENSORES SET Estado=5 WHERE id_nodo="+str(i))
					#addresses_list[direccion][4]=instante.hour
					
	print "DIRECCION"
	print "**********************************"
	print "Information: "+ inform
	print "Adress long:"
	print direccion
	print "Adress 16 bit"
	print direccion16
	print data
	print "**********************************"
#	INNECESARIO
	if inform[0]=="0":
		print "Router"
	elif inform[0] == "1":
		print "RSSI END DEVICE DESDE EL ROUTER"
	elif inform[0] == "2":
		print "END DEVICE - COORDINADOR PADRE"
	elif inform[0] == "3":
		print "END DEVICE - ROUTER PADRE"
	else:
		print "Trama de datos invAlida"

#	lista_datos = tolist(inform)
	print lista_datos
	print "SENTENCIA SQL"
#	to_db = "INSERT into Variables (id_nodo,Temperatura) values(2,"+lista_datos["Tem"]+")"
	print id_nodo
#	instante=datetime.datetime.now()
	#Si es "Mon" Ejecutar promedios semanales #Si es 1 Ejecutar promedios mensuales #Activar 
	if (instante.strftime('%a')=="Mon"):#Pasar a "Mon"
		print "ES LUNES"
		print LunesP
		if (LunesP==1):
			print "Ejecutar promedio semanal"
			Promdia(instante)
	else:
		print "NO ES LUNES"
		print instante.strftime('%a')
		LunesP==1
	if (instante.day==1) : #PASAR A 1 (DIA 1 DEL MES)
		print "EJECUTAR PROMEDIO MENSUAL"
		if (MesP==1):
			print "Primera Vez MES"
			Prommes(instante)
	if (instante.day!=DiaP): #Pasar a !=DiaP
		print "EJECUTAR PROMEDIO GENERAL"
		global DiaP
		DiaP=instante.day
		calculopromedios(3,0,0,0,0,0,0)
	print "EMPEZAR ACTUALIZADA"
	print inform[0]
	if ((inform[0]=="0") or (inform[0]=="2")): #Router o End Device con coordinador padre
		xbee.at(command='DB')
		resp = xbee.wait_read_frame()
		nivelint=todec(resp['parameter'])
		nuevoint = int(nivelint,16)
		print "ENTRA..."
		print "Intensity: "+ str(nuevoint)+"dbm" #Leer nivel de intensidad en dbm mediante comandos AT
		lista_datos["Int"]=str(nuevoint)
		time_bd= "UPDATE Variables SET Tiempo_Nodo="+lista_datos["TNo"]+", Tiempo_Servidor="+lista_datos["TSe"]+" WHERE id_nodo="+str(id_nodo)+ " ORDER BY id_variable DESC LIMIT 1"
		print time_bd
#		print time_db
		cur.execute (time_bd)
		to_db =("INSERT into Variables (id_nodo, Temperatura, Humedad, Ruido, Nivel_UV, Intensidad_lm, Potencia, Intensidad,"
			+"Try,Anio,Mes,Dia,Hora,Minuto,Tipo_Nodo) values (" +str(id_nodo)+"," +  lista_datos["Tem"]+ "," + lista_datos["Hum"] + "," 
			+ lista_datos["Rui"] + "," + lista_datos["Nuv"]+ "," + lista_datos["Ilm"] + "," + lista_datos["Pot"] + "," 
			+ lista_datos["Int"]+ ","  + lista_datos["Try"] + "," + str(instante.year)+ "," 
			+ str(instante.month) + "," + str(instante.day) + "," + str(instante.hour) + "," +str(instante.minute)+","+inform[0]+")")
	
	elif inform[0]=="3": # End Device con router padre
#		print "Entra aca"
		time_bd= "UPDATE Variables SET Tiempo_Nodo="+lista_datos["TNo"]+", Tiempo_Servidor="+lista_datos["TSe"]+" WHERE id_nodo="+str(id_nodo)+ " ORDER BY id_variable DESC LIMIT 1"
		print time_bd
#		print time_db
		cur.execute (time_bd)
		
		to_db =("INSERT into Variables (id_nodo, Temperatura, Humedad, Ruido, Nivel_UV, Intensidad_lm, Potencia"
			+",Try,Anio,Mes,Dia,Hora,Minuto,Tipo_Nodo) values ("+str(id_nodo)+"," +  lista_datos["Tem"]+ "," + lista_datos["Hum"] + "," 
			+ lista_datos["Rui"] + "," + lista_datos["Nuv"] + "," + lista_datos["Ilm"]   + "," + lista_datos["Pot"] + "," 
			+ lista_datos["Try"] + "," + str(instante.year) + "," + str(instante.month)  + "," 
			+ str(instante.day)  + "," + str(instante.hour) + "," + str(instante.minute) + ","+inform[0]+")")

	elif inform[0]=="1":
		lista_datos["DIR"]="0013a200"+lista_datos["DIR"]
		to_db= "UPDATE Variables SET Intensidad="+lista_datos["RSSI"]+" WHERE id_nodo="+str(addresses_list[lista_datos["DIR"]][0])+ " ORDER BY id_variable DESC LIMIT 1"
	print to_db
	cur.execute(to_db)
	print "-----------------------------------------------------------------------------------------------------------------------------------------"
    elif (data['id'])=='tx_status':
	global cont_succ
	global CAMBIO
	global Band1
	print "ENVIANDO DATO..."
	if data['deliver_status']=='\x00':
		cont_succ=cont_succ+1		
		if cont_succ==3:
			addresses_list[CAMBIO][5]=0
			CAMBIO="01"
			cont_succ=0
	print data	
xbee = ZigBee(ser,escaped=True,callback=print_data)
DIR64_ENV='-'

while True:
	try:
		if (CAMBIO=="01"):
			time.sleep(5)
			print horainicial
			print "Pasaron 5 segundos"
			
		else:
			print "EJECUTAR CAMBIO" 
			print CAMBIO
			DIR64_ENV=CAMBIO.decode("hex")
			if addresses_list.has_key(CAMBIO):
			 if addresses_list[CAMBIO][5]==2:#HASTA ESTA FUNCION SIRVE
				print "ENVIAR RTE"
				xbee.send('tx',dest_addr_long = DIR64_ENV,data="RTE")
			 elif addresses_list[CAMBIO][5]==1:
				print "ENVIAR ETR"
				xbee.send('tx',dest_addr_long = DIR64_ENV,data="ETR")
			time.sleep(2)			
#			print addresses_list
	except KeyboardInterrupt:
		ser.close()
		break


