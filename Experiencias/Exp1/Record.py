import threading
import time
import datetime
import os
import csv
import numpy as np

class Record:

    def __init__(self, values, pid, extension='csv'):
        self.ext = extension
        self.values = values
        self.stopped = True
        self.fields  = ['time', 'h_1', 'h_2', 'h_3', 'h_4', 'v_1', 'v_2', 'r_1', 'r_2', \
                        'e_P_1', 'e_I_1', 'e_D_1', 'k_P_1', 'k_I_1', 'k_D_1', 'k_w_1', 'u_sat_1', 'u0_1', 'setPoint_1', 'Pole_1',\
                        'e_P_2', 'e_I_2', 'e_D_2', 'k_P_2', 'k_I_2', 'k_D_2', 'k_w_2', 'u_sat_2', 'u0_2', 'setPoint_2', 'Pole_2']
        self.t = None
        self.name = 'RecordData'
        self.namenpy = None
        self.pid = pid


    def stop(self):
        print('Recording going to stop')
        self.stopped = True

    def start(self):
        self.t = threading.Thread(target=self.record_data)
        self.stopped = False
        self.t.start()
        print('Recording')

    def record_data(self):

        dir = os.listdir()
        if self.ext == 'csv':

            with open('RecordData.csv', 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=',')
                if 'RecordData.csv' not in dir:
                    csvwriter.writerow(self.fields)
                while not self.stopped:
                    # states1 = self.pid.H1.status(); print(["{:.5f}".format(i) for i in states1.values()][0:-2])
                    rows = ["{:.3f}".format(value.get_value()) for value in self.values]
                    rows.insert(0, datetime.datetime.now().strftime("%m/%d/%Y; %H:%M:%S"))
                    states1 = self.pid.H1.status()
                    rows.extend(["{:.3f}".format(i) for i in states1])
                    states2 = self.pid.H2.status()
                    rows.extend(["{:.3f}".format(i) for i in states2])

                    csvwriter.writerows([rows])
                    time.sleep(1)

        elif self.ext == 'txt':
            separator = ','
            with open('RecordData.txt', 'a', newline='') as txtfile:
                if 'RecordData.txt' not in dir:
                    txtfile.write(separator.join(self.fields)+'\n')
                while not self.stopped:
                    rows = ["{:.3f}".format(value.get_value()) for value in self.values]
                    rows.insert(0, datetime.datetime.now().strftime("%m/%d/%Y; %H:%M:%S"))
                    states1 = self.pid.H1.status()
                    rows.extend(["{:.3f}".format(i) for i in states1])
                    states2 = self.pid.H2.status()
                    rows.extend(["{:.3f}".format(i) for i in states2])
                    txtfile.write(separator.join(rows)+'\n')
                    time.sleep(1)

        elif self.ext == 'npy':
            self.namenpy = datetime.datetime.now().strftime("%m-%d-%Y_%H%M%S")
            with open(self.namenpy+'.npy', 'wb') as f:
                old_time = time.time()
                while not self.stopped:
                    l1 = [value.get_value() for value in self.values]
                    # print(l1)
                    l1.extend(self.pid.H1.status())
                    l1.extend(self.pid.H2.status())

                    l1.insert(0, time.time()-old_time)
                    rows = np.around(np.array(l1, dtype='f'), decimals=3)
                    np.save(f, rows)
                    time.sleep(1)
