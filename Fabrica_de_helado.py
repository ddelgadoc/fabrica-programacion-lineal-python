# -*- coding: utf-8 -*-
"""


@author: deyli
"""

from pulp import *

##Conjuntos
Sabor = ["V","F","CH","Valmendra"] #V:Vainilla,F:Fresa,CH:Chocolate,Valmendra:vainilla con almendra
Tam = ["P","M","G"]  #P:pequeño,M:mediano,G:grande
Maq =["1","2"] #Máquinas del tratamiento de helado
Material = [] #1-leche,2-Azucar,3-agua destilada,4-Saborizantes
for i in range(1,5):
    Material.append(str(i))


##Parametros
cantidad=[[1.5,2.5,3],[0.8,1.8,2.3],[1.7,2,2.7],[0.5,0.9,1.2]] #cantidades por tipo de ingrediente [[P,M,G],[P,M,G]...]  (litros/u)
L = dict(zip(Material,[cantidad[0],cantidad[1],cantidad[2],cantidad[3]]))
Precio ={"P":25,"M":45,"G":75}  #Precio de venta según tamaño ($/u)
Costo ={"P":11,"M":19.25,"G":24.95}  #Coste de fabricación variable de una unidad de pote de helado para cada tamaño ($/u)
Dem =dict(zip(Tam,[5000,2000,3000])) #Demanda de helado para el mes de mayo (unidades)
Dip = dict(zip(Material,[50000,20000,25000,15000]))  #Diponibilidad de materiales para la fabricación de los helados para el mes de mayo(litros)
Maq_d=dict(zip(Maq,[[7500,5000,4000],[6000,5110,3500]])) #Capacidad de producción de cada máquina según el tamaño del pote(unidades) [[P,M,G],[P,M,G]]
A=dict(zip(Tam,[0.5,0.7,1])) #Gramos de almendra para el sabor Valmendra según tamaño del pote(g/u)
CosteV={"P":1.5,"M":2.1,"G":3} #Coste de los gramos de almendra según tamaño ($/u)

##Problema
prob = LpProblem("Fabrica de helado",LpMaximize)

##Variables, decisiones a tomar
x = LpVariable.dicts("Cantidad_Potes_de_helado",(Tam,Sabor),0,cat="Integer")  #Cantidades de potes de helados para fabricar para el mes de mayo
y = LpVariable.dicts("Utilizar_maquina",Maq,0,1,cat="Integer")
k = LpVariable("Cantidad_de_neveras_adquirir",0,cat="Integer")
R = LpVariable("Realizar_ajustes_economicos",0,1,cat="Integer")  #Decidir si comprar alguna nevera nueva
u = LpVariable("Usar_nuevo_sabor_vainilla_almendra",0,1,cat="Integer")
##FO
prob += lpSum([x[i][j]*Precio[i] for i in Tam for j in Sabor]) - lpSum([x[i][j]*Costo[i] for i in Tam for j in Sabor]) - 500*k - lpSum([x[i][j]*CosteV[i] for i in Tam for j in Sabor if j == "Valmendra"]) + lpSum(5*x[i][j]  for i in Tam for j in Sabor if j == "Valmendra") #5 pesos adicionales sobre el precio unitario de venta si el sabor es Valmendra

##Restricciones
for i in Tam:
    prob += lpSum([x[i][j] for j in Sabor]) <= Dem[i] #Restriccion satisfacer la demanda de helado,es <= porque la FO es Max la ganancia, si fuera MIN costo fuera >=,es se podría incluir una restricción de penalización por vender más de la demanda con max ganancia 
    
#Restriccion capacidad nevera
prob += lpSum([x[i][j] for i in Tam for j in Sabor if i == "P"])/7000 + lpSum([x[i][j] for i in Tam for j in Sabor if i == "M"])/5000 + lpSum([x[i][j] for i in Tam for j in Sabor if i == "G"])/4000 <= 1 + k
    
#Restricciones comprar neveras nuevas
prob += k <= 4*R

#Restrccion chocolate helado más vendido
prob += lpSum([x[i][j] for i in Tam for j in Sabor if j == "CH"]) -3*lpSum([x[i][j] for i in Tam for j in Sabor if j != "CH"]) >= 0

#Restriccion ingredientes y disponibilidad
for n in Material:
    prob += lpSum([x[i][j] for i in Tam for j in Sabor if i == "P"])*L[n][0] + lpSum([x[i][j] for i in Tam for j in Sabor if i == "M"])*L[n][1] + lpSum([x[i][j] for i in Tam for j in Sabor if i == "G"])*L[n][2] <= Dip[n]

#restriccion Maquina que usar
prob += lpSum([y[i] for i in Maq]) == 1
    
for i in Tam:
    prob += lpSum([x[i][j] for j in Sabor if i == "P"]) <= Maq_d["1"][0]*y["1"] + Maq_d["2"][0]*y["2"]
    prob += lpSum([x[i][j] for j in Sabor if i == "M"]) <= Maq_d["1"][1]*y["1"] + Maq_d["2"][1]*y["2"]    
    prob += lpSum([x[i][j] for j in Sabor if i == "G"]) <= Maq_d["1"][2]*y["1"] + Maq_d["2"][2]*y["2"]
    
#restriccion nuevo sabor de helado Vainilla con almendra
prob += lpSum([x[i][j]*A[i] for i in Tam for j in Sabor if j == "Valmendra"]) <= 50000*u


prob.solve()

prob.writeLP("exa.txt")


print("Estado:",LpStatus[prob.status])

print("FO",value(prob.objective))


for v in prob.variables():
    print(v.name,":",v.value())
    
