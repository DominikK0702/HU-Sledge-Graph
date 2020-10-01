import json

class OSGPulseData:
    def __init__(self):
        self.name = None
        self.description = None
        self.resolution = None
        self.datapoints = None
        self.data = {
            'x': [],
            'y': []
        }
        self.branches = []

    def add_branch(self, pulse):
        self.branches.append(pulse)



class OGSPulseJson:
    def __init__(self):
        self.pulse = OSGPulseData()

    def load(self, filename):
        with open('puls.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        if data:
            self.pulse.name = data.get('name')
            self.pulse.description = data.get('description')
            self.pulse.resolution = data.get('resolution')
            self.pulse.datapoints = data.get('datapoints')
            self.pulse.data = data.get('data')
            self.branches = data.get('branches')

def main():
    x = OGSPulseJson()
    x.load('puls.json')
    print(1)


if __name__ == '__main__':
    main()
