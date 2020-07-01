import csv
import subprocess
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter


def diff(array, td):
    result = []
    last = 0
    for i in array:
        result.append(((i - last) / (td / 1000)))
        last = i
    return result


def offset_x_soll(array, steps):
    return [i / 16000 for i in range(steps, len(array) + steps)]


class Trace:
    def __init__(self, filename=None):
        self.filename = filename
        self.datapoints = 0
        self.header = None
        self.axis_x = []
        self.axis_velocity = []
        self.axis_2 = []
        self.axis_voltage = []
        self.axis_acceleration = []

    def clear(self):
        self.filename = None
        self.datapoints = 0
        self.header = None
        self.axis_x = []
        self.axis_velocity = []
        self.axis_2 = []
        self.axis_voltage = []
        self.axis_acceleration = []

    def save_to_csv(self, filename):
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(self.header)
            for index, row in enumerate(self.axis_x):
                writer.writerow([row,
                                 self.axis_velocity[index],
                                 self.axis_2[index],
                                 self.axis_voltage[index],
                                 self.axis_acceleration[index]
                                 ])

    def load_trace_acx(self, filename=None):
        if filename: self.filename = filename
        temp_csv = './export/temp/trace.csv'
        subprocess.call(['./bin/Convert_SINAMICS_trace_CSV.exe',
                         filename,
                         '-sep', 'SEMICOLON',
                         '-out', './export/temp/trace.csv'])
        self.load_trace_csv(temp_csv)

    def load_trace_csv(self, filename=None, header=True):
        self.datapoints = 0
        self.axis_x = []
        self.axis_velocity = []
        self.axis_2 = []
        self.axis_voltage = []
        self.axis_acceleration = []
        if filename: self.filename = filename
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if header:
                    self.header = row
                    header = False
                    continue
                self.axis_x.append(float(row[0].replace(',', '.')) / 1000)  # Conver from ms to s
                self.axis_velocity.append(float(row[1].replace(',', '.'))/1000)
                self.axis_2.append(float(row[2].replace(',', '.'))*0.005)
                self.axis_voltage.append((float(row[3].replace(',', '.'))*25)-12000)
                self.axis_acceleration.append(float(row[4].replace(',', '.')))
        self.datapoints = len(self.axis_x)

    def get_axis_time(self):
        return self.axis_x

    def get_axis_velocity(self):
        return self.axis_velocity

    def get_axis_2(self):
        return self.axis_2

    def get_axis_voltage(self):
        return savgol_filter(self.axis_voltage,51,3)

    def get_axis_acceleration(self):
        return self.axis_acceleration

    def get_axis_acc_from_speed(self, filtered=False):
        if filtered:
            return savgol_filter(diff(self.axis_velocity, (self.axis_x[2] - self.axis_x[1])), 51, 3)
        else:
            return diff(self.axis_velocity, (self.axis_x[2] - self.axis_x[1]))
