from opcua import Client
from opcua import ua
from Server_Modified.PID import PID
import time
import threading
from math import sqrt


class RunPID:

    def __init__(self, values, debug=False):
        self.debug = debug
        # self.client = Client('opc.tcp://localhost:4840/freeopcua/server/')
        # self.client.connect()
        #
        # self.objects_node = self.client.get_objects_node()
        #
        # self.h1 = self.objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque1', '2:h'])
        # self.h2 = self.objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque2', '2:h'])
        # self.h3 = self.objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque3', '2:h'])
        # self.h4 = self.objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque4', '2:h'])
        #
        # self.v1 = self.objects_node.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula1', '2:u'])
        # self.v2 = self.objects_node.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula2', '2:u'])
        #
        # self.r1 = self.objects_node.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon1', '2:gamma'])
        # self.r2 = self.objects_node.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon2', '2:gamma'])
        h1, h2, h3, h4, v1, v2, r1, r2 = values

        self.h = [h1, h2, h3, h4]
        self.v = [v1, v2]
        self.r = [r1, r2]

        # PID
        self.Kp1 = 5
        self.Kp2 = 5
        self.Ki1 = 0.5
        self.Ki2 = 0.5
        self.Kd1 = 0.1
        self.Kd2 = 0.1
        self.Kw1 = 0.02
        self.Kw2 = 0.02
        self.H1 = PID(Kp=self.Kp1, Ki=self.Ki1, Kd=self.Kd1, Kw=self.Kw1, Imax=0.75, debug=debug)
        self.H2 = PID(Kp=self.Kp2, Ki=self.Ki2, Kd=self.Kd2, Kw=self.Kw2, Imax=0.8, debug=debug)

        self.H1.name = 'T1'
        self.H2.name = 'T2'

        # Set point
        self.setpoint1 = 15
        self.setpoint2 = 15
        self.h3_set = 0
        self.h4_set = 0

        # variables for threading
        self.stopped = True
        self.t = None



    def imprimir_lista(self, lista):
        for it in lista:
            print(int(it.get_value()), end=' ')
        print()


    def setPoint_pid(self):

        self.H1.setPoint = self.setpoint1
        self.H2.setPoint = self.setpoint2

    def stop(self):
        if not self.stopped:
            print('PID is stopping')
        self.stopped = True

    def start(self):
        self.t = threading.Thread(target=self.run_pid)
        self.stopped = False
        print('PID running')
        self.t.start()


    def run_pid(self):
        self.setPoint_pid()
        while not self.stopped:
            self.H1.update(self.h[0].get_value())
            self.H2.update(self.h[1].get_value())

            # self.v1ff = (sqrt(2*g*h3_set)*a3)/((1-y2)*k2)
            # self.v2ff = (sqrt(2*g*h4_set)*a4)/((1-y1)*k1)

            V1 = self.H1.u
            V2 = self.H2.u

            if self.debug:
                print('######PID########')

            self.H1.status()
            self.H2.status()

            if self.debug:
                print('V_PID', '{:.4f}'.format(V1), '{:.4f}'.format(V2))

                print('######PLANT########')
                print('hs', '{:.2f}'.format(self.h[2].get_value()), '{:.2f}'.format(self.h[3].get_value()))
                print('hi', '{:.2f}'.format(self.h[0].get_value()), '{:.2f}'.format(self.h[1].get_value()))


                print('######SET########')
                print('h: ', end='')
                print('{:.4f}'.format(self.H1.setPoint),'{:.4f}'.format(self.H2.setPoint))

                print()

            if abs(V1) <= 1:
                self.v[0].set_value(V1)
            else:
                self.v[0].set_value(V1 / abs(V1))

            if abs(V2) <= 1:
                self.v[1].set_value(V2)
            else:
                self.v[1].set_value(V2/abs(V2))




