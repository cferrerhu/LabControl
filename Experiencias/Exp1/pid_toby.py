from opcua import Client
from opcua import ua
import time
from math import sqrt

client = Client('opc.tcp://localhost:4840/freeopcua/server/')
client.connect()

objects_node = client.get_objects_node()

h1 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque1', '2:h'])
h2 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque2', '2:h'])
h3 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque3', '2:h'])
h4 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque4', '2:h'])

v1 = objects_node.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula1', '2:u'])
v2 = objects_node.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula2', '2:u'])

r1 = objects_node.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon1', '2:gamma'])
r2 = objects_node.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon2', '2:gamma'])

h = {'H1': h1, 'H2': h2, 'H3': h3, 'H4': h4}
v = {'V1': v1, 'V2': v2}
r = {'R1': r1, 'R2': r2}
proceso = {'H': h, 'V': v, 'R': r}

h = [h1, h2, h3, h4]
v = [v1, v2]
r = [r1, r2]

def imprimir(pr):
    print('######PLANT########')
    for tipo in pr:
        for var in pr[tipo]:
            print(var, pr[tipo][var].get_value())
    print()

def imprimir_lista(lista):
    for it in lista:
        print(int(it.get_value()), end=' ')
    print()



########################################################################
########################################################################

y1 = 0.4 #0.7
y2 = 0.4 #0.6

A1 = 28
A2 = 32
A3 = 28
A4 = 32

a1 = 0.071
a2 = 0.057
a3 = 0.071
a4 = 0.057

k1 = 3.33
k2 = 3.33

g = 981

#v1 = 3
#v2 = 3


imprimir(proceso)
r1.set_value(y1)
r2.set_value(y2)
imprimir(proceso)


from Server_Modified.PID import PID


H1 = PID(Kp=5, Ki=0, Kd=0, Kw=0)
H2 = PID(Kp=5, Ki=0, Kd=0, Kw=0)


H = [H1, H2]

H1.setPoint = 25
H2.setPoint = 25
h3_value = 0
h4_value = 0

while True:
    print('######PID########')
    print('H_PID: ', end='')
    H1.update(h1.get_value())
    H2.update(h2.get_value())

    h3_value = h3.get_value()
    h4_value = h4.get_value()
    v1cc = (sqrt(2*g*h3_value))*a3/A1
    v2cc = (sqrt(2*g*h4_value))*a4/A2

    v1ff = (sqrt(2*g*h3_value)*a3)/((1-y2)*k2)
    v2ff = (sqrt(2*g*h4_value)*a4)/((1-y1)*k1)

    print('')
    H1.status()
    H2.status()

    V1 = H1.u
    V2 = H2.u
    print('V_PID', 'V1:{:.4f}'.format(H1.u), 'V2:{:.4f}'.format(H2.u))
    print('Vcc', '1:{:.4f}'.format(v1cc), '2:{:.4f}'.format(v2cc))



    print('######PLANT########')
    print('h: ', end='')
    imprimir_lista([h1, h2, h3, h4])

    print('######SET########')
    print('h: ', end='')
    print('{:.4f}'.format(H1.setPoint),'{:.4f}'.format(H2.setPoint))




    if abs(V1) <= 1:
        v1.set_value(V1)
    else:
        v1.set_value(V1 / abs(V1))

    if abs(V2) <= 1:
        v2.set_value(V2)
    else:
        v2.set_value(V2/abs(V2))


    #time.sleep(1)
    print()



client.disconnect()
