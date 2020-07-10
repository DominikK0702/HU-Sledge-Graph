import datetime
import json


class ProtocolData:
    def __init__(self):
        self.data = {
            'versuchsnummer'    : '',
            'versuchstyp'       : '',
            'bediener'          : '',
            'kommentar'         : '',
            'startpos'          : '',
            'endpos'            : '',
            'zuladung'          : '',
            'trigger'           : {
                '01': {'enabled': False, 'name': '', 'zeit': 0},
                '02': {'enabled': False, 'name': '', 'zeit': 0},
                '03': {'enabled': False, 'name': '', 'zeit': 0},
                '04': {'enabled': False, 'name': '', 'zeit': 0},
                '05': {'enabled': False, 'name': '', 'zeit': 0},
                '06': {'enabled': False, 'name': '', 'zeit': 0},
                '07': {'enabled': False, 'name': '', 'zeit': 0},
                '08': {'enabled': False, 'name': '', 'zeit': 0},
                '09': {'enabled': False, 'name': '', 'zeit': 0},
                '10': {'enabled': False, 'name': '', 'zeit': 0},
                '11': {'enabled': False, 'name': '', 'zeit': 0},
                '12': {'enabled': False, 'name': '', 'zeit': 0},
                '13': {'enabled': False, 'name': '', 'zeit': 0},
                '14': {'enabled': False, 'name': '', 'zeit': 0},
                '15': {'enabled': False, 'name': '', 'zeit': 0}
            },
            'puls_x'            : [],
            'puls_y'            : [],
            'trace_vel'         : [],
            'trace_x'           : [],
            'trace_way'         : [],
            'trace_acc_way'     : [],
            'trace_acc_vel'     : [],
            'trace_acc_vel_filt': [],
            'trace_voltage'     : []
        }


class ProtocolJson:
    def __init__(self):
        self.json = ProtocolData()

    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            self.json.data = json.loads(f.read())

    def gen_filename(self, path):
        extension = '.pjson'
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return f'{path}\\{self.json.data["versuchstyp"]}_{timestamp}{extension}'

    def save(self, filepath):
        with open(self.gen_filename(filepath), 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.json.data))
