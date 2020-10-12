import json
import csv
from loguru import logger

class OSGPulseData(dict):
    def __int__(self, data):
        super(OSGPulseData, self).__int__(data)

    def __repr__(self):
        return f"{self.get_name()} | {self.get_resolution()} hz | {self.get_datapoints()} points | {self.get_branches_count()} branches"

    def get_name(self):
        return self.get('name')

    def get_duration(self):
        return self.get_x()[-1]

    def get_description(self):
        return self.get('description')

    def get_resolution(self):
        return self.get('resolution')

    def get_datapoints(self):
        return self.get('datapoints')

    def get_x(self):
        return self.get('data').get('x')

    def get_y(self):
        return self.get('data').get('y')

    def get_max(self):
        return max(self.get('data').get('y'))

    def get_min(self):
        return min(self.get('data').get('y'))

    def get_data(self):
        return self.get_x(), self.get_y()

    def get_branches_count(self):
        return len(self.get('branches'))

    def get_branches(self):
        return [OSGPulseData(i) for i in self.get('branches')]

    def get_json(self):
        return json.dumps(self)

    @classmethod
    def load_from_file(self, filename):
        return OSGPulseData(json.load(open(filename)))



class OSGPulseLibrary:
    def __init__(self):
        self._filetype = '.opl'
        self.current_pulse_data = None
        pass

    def load_from_csv(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    print(row)
                return True
        except Exception as e:
            logger.error('Loading Pulse CSV failed: ' + str(e))
            return False
        pass

    def save_to_csv(self, filename):

        pass

    def load_pulse_library(self, filename):
        try:
            self.current_pulse_data = OSGPulseData.load_from_file(filename)
            return True
        except Exception as e:
            logger.error('Loading Pulse Library failed: ' + str(e))
            return False

    def save_pulse_library(self, dir, name):
        pass




if __name__ == '__main__':
    test = OSGPulseLibrary()
    print(1)
