import json

class OSGPulse:
    def __init__(self, json):
        for key, value in json.items():
            self.__setattr__(key,value)

    def get_datapoints(self):
        return self.datapoints

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_x(self):
        return self.data['x']

    def get_y(self):
        return self.data['y']

    def get_data(self):
        return [list(i) for i in zip(self.get_x(),self.get_y())]

    def get_branch_count(self):
        return len(self.branches)

    def get_branches(self):
        return [OSGPulse(i) for i in self.branches]



class OSGPulseLibrary:
    def __init__(self):
        self.json = None

    def load(self, filename):
        with open('puls.opl', 'r', encoding='utf-8') as f:
            self.json = OSGPulse(json.loads(f.read()))

    def get_branch(self, index):
        return OSGPulse(self.json.branches[0])





def main():

    x = OSGPulseLibrary()
    x.load('puls.opl')
    puls = x.get_branch(0)





    print(1)


if __name__ == '__main__':
    main()
