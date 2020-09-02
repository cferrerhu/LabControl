import time
from scipy import signal

class PID:
    def __init__(self, Kp=0.2, Ki=0.1, Kd=0, Kw=0.3, voltmax=[0, 1], debug=False):
        self.name = ''
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.Kw = Kw

        self.umax = voltmax
        self.Imax = 1
        self.pastD = []
        self.max_D_len = 10

        self.sample_time = 0
        self.current_time = time.time()
        self.last_time = self.current_time

        self.setPoint = 0
        self.P = 0
        self.I = 0
        self.D = 0

        self.last_error = 0

        self.u = 0
        self.uOriginal = 0

        self.pole = 5

        self.debug = debug

    def status(self):
        if self.debug:
            print(self.name, end=': ')
            print('P I D U', '{:.2f}'.format(self.P), '{:.2f}'.format(self.I), '{:.2f}'.format(self.D), '{:.2f}'.format(self.uOriginal))
            #print('U Umod', '{:.2f}'.format(self.uOriginal), '{:.2f}'.format(self.u))
        state = [self.P, self.I, self.D, self.Kp, self.Ki, self.Kd, self.Kw, self.u, self.uOriginal, self.setPoint, self.pole]
        # state['e_P'] = self.P
        # state['e_I'] = self.I
        # state['e_D'] = self.D
        #
        # state['k_P'] = self.Kp
        # state['k_I'] = self.Ki
        # state['k_D'] = self.Kd
        # state['k_w'] = self.Kw
        #
        # state['u'] = self.u
        # state['uO'] = self.uOriginal
        #
        # state['set_p'] = self.setPoint
        # state['epoch'] = time.time()
        return state



    def LP_kd(self, lpf_val, sf):
        self.pastD.append(lpf_val)
        if len(self.pastD) > self.max_D_len:
            self.pastD = self.pastD[1:]

        # self.pole = 5
        if sf < 2*self.pole:
            self.pole = (sf - 0.001)/2


        iir_b, iir_a = signal.butter(2, self.pole, btype="lowpass", fs=sf)
        xs = signal.lfilter(iir_b, iir_a, self.pastD)

        return xs[-1]


    def update(self, value):

        error = self.setPoint - value # calcular error

        self.current_time = time.time()
        delta_time = self.current_time - self.last_time #calcular delta t, entre calls

        delta_error = error - self.last_error

        if delta_time < self.sample_time:
            time.sleep(self.sample_time - delta_time)

        self.P = self.Kp*error
        self.I += (self.Ki*error + self.Kw*(self.u - self.uOriginal))*delta_time

        if abs(self.I) > self.Imax: #limitar acción I a +-1
            self.I = self.I/abs(self.I)

        if delta_time > 0:
            self.D = self.LP_kd(self.Kd*delta_error/delta_time, 1/delta_time)

        self.uOriginal = self.P + self.I + self.D

        if self.uOriginal > self.umax[1]:
            self.u = self.umax[1]
        elif self.uOriginal < self.umax[0]:
            self.u = self.umax[0]
        else:
            self.u = self.uOriginal

        self.last_time = self.current_time
        self.last_error = error
        #print('{:.2f}'.format(self.u), end=' ')
        return self.u
