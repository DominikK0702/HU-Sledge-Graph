import csv
from loguru import logger

class OSGPulse:
    def __init__(self):
        self.delimiter = ';'
        self.axis_x = []
        self.axis_y = []
        self.resolution_hz = None
        self.current_file = None

    def __repr__(self):
        return f"{self.resolution_hz} Hz | {self.current_file}"

    def clear(self):
        self.axis_x = []
        self.axis_y = []

    def get_resolution(self):
        samples = []
        length = len(self.axis_x)
        for cnt, i in enumerate(self.axis_x):
            if (cnt+1) >= length:
                break
            samples.append(1/(self.axis_x[cnt+1]-i))

        return int(sum(samples)/len(samples)) # Average

    def load_from_file(self, filename):
        self.clear()
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            for row in reader:
                self.axis_x.append(float(row[0].replace(',','.')))
                self.axis_y.append(float(row[1].replace(',','.')))
        self.current_file = filename
        self.resolution_hz = self.get_resolution()


    def save_to_file(self, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            for x,y in zip(self.axis_x, self.axis_y):
                print('{:.10f}'.format(x),'{:.10f}'.format(y))



if __name__ == '__main__':
    x = OSGPulse()
    x.load_from_file('.\\PulsDaten\\Crash_1_40_2019-10-29_16kHz_15g.pcsv')
    res = x.get_resolution()
    x.save_to_file('test.pcsv')