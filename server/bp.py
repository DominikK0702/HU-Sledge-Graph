from flask import Blueprint, jsonify, request, abort
import flask_restful
import os
import csv
import json

import datetime

import snap7, time


class s7Com:
    IP = '192.168.0.4'
    RACK = 0
    SLOT = 0

    s7connected = False

    def __init__(self):
        self.s7 = snap7.client.Client()

        while not self.s7connected:
            try:
                print("Verbindung wird aufgebaut...")
                self.s7.connect(self.IP, self.RACK, self.SLOT)
                self.s7connected = True
                print("Verbindung mit S7 hergestellt.")
            except:
                print("Konnte nicht mit S7 verbinden... wiederholen")
                time.sleep(2)

    def readReal(self, db, start, offset):
        reading = self.s7.read_area(snap7.snap7types.S7AreaDB, db, start, 4)
        return snap7.util.get_real(reading, 0)

    def writeReal(self, db, start, value):
        reading = self.s7.db_read(db, start, 4)
        snap7.util.set_real(reading, 0, value)
        self.s7.db_write(db, start, reading)

    def readBool(self, db, start, offset):
        reading = self.s7.read_area(snap7.snap7types.S7AreaDB, db, start, 1)
        return snap7.util.get_bool(reading, 0, offset)

    def writeBool(self, db, start, offset, value):
        reading = self.s7.db_read(db, start, 1)
        snap7.util.set_bool(reading, 0, offset, value)
        self.s7.db_write(db, start, reading)

    def readInt(self, db, start):
        reading = self.s7.read_area(snap7.snap7types.S7AreaDB, db, start, 2)
        return snap7.util.get_int(reading, 0)

    def writeInt(self, db, start, value):
        reading = self.s7.db_read(db, start, 2)
        snap7.util.set_int(reading, 0, value)
        self.s7.db_write(db, start, reading)

    def readString(self, db, start,len=255):
        reading = self.s7.read_area(snap7.snap7types.S7AreaDB, db, start, len)
        return snap7.util.get_string(reading, 0, len)

    def writeString(self, db, start, value):
        reading = self.s7.read_area(snap7.snap7types.S7AreaDB, db, start, 255)
        snap7.util.set_string(reading, 0, value, 255)
        self.s7.db_write(db, start, reading)

    def disconnect(self):
        self.s7.disconnect()
        self.s7connected = False

s7 = s7Com()


# Config
API_NAME = 'graph'.lower()

# Init Blueprint
graph_bp = Blueprint(API_NAME, __name__, url_prefix=f'/{API_NAME}')
graph = flask_restful.Api(graph_bp)

current_data = []



# Resources
class SetData(flask_restful.Resource):
    routes = ('/setdata',)
    privilege_name = f'{API_NAME}-{__qualname__.lower()}'


    def get(self):
        data = []
        file = s7.readString(813,0)
        with open(file,'r') as f:
            reader = csv.reader(f,delimiter=';')

            return jsonify([[float(row[0]),float(row[1])] for row in reader])

    def post(self):

        global current_data
        current_data = json.loads(request.data.decode())
        global s7
        reading = s7.s7.db_read(811, 0, 12004)
        for e,i in enumerate(current_data):
            snap7.util.set_real(reading, e*4, i[1])
        s7.s7.db_write(811, 0, reading)
        return ''

class SaveCsv(flask_restful.Resource):
    routes = ('/savecsv',)
    privilege_name = f'{API_NAME}-{__qualname__.lower()}'

    def post(self):
        # Save current data w filename
        rootdir = 'C:\\Users\\Dominik\\PycharmProjects\\HU-Sledge-Graph'
        filename = s7.readString(813,258)
        filetype = 'csv'
        with open(os.path.join(rootdir,f"{filename}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{filetype}"),'w', newline='') as f:
            writer = csv.writer(f,delimiter=';')
            global current_data
            writer.writerows(current_data)
        return ''




# Add the resources to the Blueprint
graph.add_resource(SetData, *SetData.routes)
graph.add_resource(SaveCsv, *SaveCsv.routes)
