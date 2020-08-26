import threading
import time
import datetime
import os
import csv
import numpy as np

class Record:

    def __init__(self, values, extension='csv'):
        self.ext = extension
        self.values = values
        self.stopped = True
        self.fields  = ['time', 'h1', 'h2', 'h3', 'h4', 'v1', 'v2', 'r1', 'r2']
        self.t = None
        self.name = 'RecordData'
        self.namenpy = None


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
                    rows = ["{:.5f}".format(value.get_value()) for value in self.values]
                    rows.insert(0, datetime.datetime.now().strftime("%m/%d/%Y; %H:%M:%S"))

                    csvwriter.writerows([rows])
                    time.sleep(1)

        elif self.ext == 'txt':
            separator = ','
            with open('RecordData.txt', 'a', newline='') as txtfile:
                if 'RecordData.txt' not in dir:
                    txtfile.write(separator.join(self.fields)+'\n')
                while not self.stopped:
                    rows = ["{:.5f}".format(value.get_value()) for value in self.values]
                    rows.insert(0, datetime.datetime.now().strftime("%m/%d/%Y; %H:%M:%S"))
                    txtfile.write(separator.join(rows)+'\n')
                    time.sleep(1)

        elif self.ext == 'npy':
            self.namenpy = datetime.datetime.now().strftime("%m-%d-%Y_%H%M%S")
            with open(self.namenpy+'.npy', 'wb') as f:
                while not self.stopped:
                    rows = np.round(np.array([value.get_value() for value in self.values]), 4)
                    np.save(f, rows)
                    time.sleep(1)
                    
