import csv
import os
from loguru import logger


class OSGPulseData:
    def __init__(self):
        self.x = []
        self.y = []
        self._current_file = None
        self._data_avliable = False

    def __repr__(self):
        return f"PulseData: {self.get_datapoint_count()} | {self.get_resolution()} Hz | {self.get_current_file()}"

    def clear(self):
        self.x = []
        self.y = []
        self._current_file = None
        self._data_avliable = False

    def get_current_file(self):
        return self._current_file

    def get_name(self):
        if self._current_file:
            return os.path.split(self._current_file)[1]

    def get_max(self):
        return max(self.y)

    def get_min(self):
        return min(self.y)

    def get_durationms(self):
        # In Ms
        return self.x[-1]*1000

    def get_datapoint_count(self):
        return len(self.x), len(self.y)

    def get_resolution(self):
        if self._data_avliable:
            samples = []
            length = len(self.x)
            for cnt, i in enumerate(self.x):
                if (cnt+1) >= length:
                    break
                samples.append(1/(self.x[cnt+1]-i))

            return int(sum(samples)/len(samples)) # Average

    def load_from_file(self, filename, delimiter=';'):
        self.clear()
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                self.x.append(float(row[0].replace(',','.')))
                self.y.append(float(row[1].replace(',','.')))
        self._current_file = filename
        self._data_avliable = True


    def save_to_file(self, filename, delimiter=';'):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=delimiter)
            for x,y in zip(self.x, self.y):
                writer.writerow(['{:.10f}'.format(x),'{:.10f}'.format(y)])






