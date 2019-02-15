resultados=['1, 4', '2, 4', '1, 6', '3, 3', '4, 3', '1, 9', '1, 1', '6, 7', '7, 1', '8, 1','9, 2','5, 5','3, 5','2, a','1, 4','7, b','1, b','1, 9']
a=resultados*1

while True:
    bandera=0
    cuenta=0
    recuerdo =resultados[0][-1]
    for valores in resultados:
        if recuerdo!=valores[-1] and bandera==1:
            bandera=2
            recuerdo2=recuerdo
            recuerdo=valores[-1]
        elif bandera==2 and recuerdo2!=recuerdo and recuerdo!=valores:
            resultados.pop(cuenta-2)
            break
        elif recuerdo==valores[-1]:
            bandera=0
            recuerdo=valores[-1]
        else:
            bandera=1
            recuerdo=valores[-1]
        cuenta+=1
    if cuenta==len(resultados):
        break
print(resultados)

count=0
for f in resultados:
    if count+1<len(resultados):
        if f[0]!=resultados[count+1][0]:
            print(resultados[count])
            count+=1
