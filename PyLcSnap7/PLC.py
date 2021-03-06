import snap7
import math
import struct
import numpy
import datetime


class S7Conn:
    def __init__(self, ip='192.168.0.4', plcname='Default'):
        self.ip = ip
        self.plcname = plcname
        self.port = 102
        self.rack = 0
        self.slot = 0
        self.client = snap7.client.Client()

    def connect(self):
        if self.client.get_connected():
            return True
        else:
            try:
                self.client.connect(self.ip, self.rack, self.slot, self.port)
                return True
            except Exception as e:
                return False

    def readReal(self, db, start):
        if self.connect():
            reading = self.client.read_area(snap7.snap7types.S7AreaDB, db, start, 4)
            return snap7.util.get_real(reading, 0)
        else:
            return self.readReal(db, start)

    def readRealArray(self, db, start, lenght):
        if self.connect():
            bytelength = 4
            reading = self.client.read_area(snap7.snap7types.S7AreaDB, db, start, bytelength * (lenght + 1))
            array = [snap7.util.get_real(reading, i * bytelength) for i in range(0, lenght + 1)]
            return array
        else:
            return self.readRealArray(db, start, lenght)

    def writeReal(self, db, start, value):
        if self.connect():
            reading = self.client.db_read(db, start, 4)
            snap7.util.set_real(reading, 0, value)
            self.client.db_write(db, start, reading)
        else:
            return self.writeReal(db, start, value)

    def writeRealArray(self, db, start, data):
        if self.connect():
            bytelength = 4
            reading = self.client.read_area(snap7.snap7types.S7AreaDB, db, start * bytelength, bytelength * (len(data)))
            for index, d in enumerate(data):
                snap7.util.set_real(reading, index * bytelength, d)
            self.client.db_write(db, start * bytelength, reading)
        else:
            return self.writeRealArray(db, start, data)

    def readBool(self, db, start, offset):
        if self.connect():
            reading = self.client.read_area(snap7.snap7types.S7AreaDB, db, start, 1)
            return snap7.util.get_bool(reading, 0, offset)
        else:
            return self.readBool(db, start, offset)

    def readBoolArray(self, db, start, lenght):
        if self.connect():
            reading = self.client.read_area(snap7.snap7types.S7AreaDB, db, start, math.ceil(lenght/8)+1)
            data = []
            for b in range(math.ceil(lenght/8)+1):
                for x in range(0,8):
                    data.append(snap7.util.get_bool(reading, b, x))
            return data[:lenght+1]
        else:
            return self.readRealArray(db, start, lenght)

    def writeBool(self, db, start, offset, value):
        if self.connect():
            reading = self.client.db_read(db, start, 1)
            snap7.util.set_bool(reading, 0, offset, value)
            self.client.db_write(db, start, reading)
        else:
            return self.writeBool(db, start, offset, value)

    def readInt(self, db, start):
        if self.connect():
            reading = self.client.read_area(snap7.snap7types.S7AreaDB, db, start, 2)
            return snap7.util.get_int(reading, 0)
        else:
            return self.readInt(db, start)

    def writeInt(self, db, start, value):
        if self.connect():
            reading = self.client.db_read(db, start, 2)
            snap7.util.set_int(reading, 0, value)
            self.client.db_write(db, start, reading)
        else:
            return self.writeInt(db, start, value)

    def readString(self, db, start, len=255):
        if self.connect():
            reading = self.client.read_area(snap7.snap7types.S7AreaDB, db, start, len)
            return snap7.util.get_string(reading, 0, len)
        else:
            return self.readString(db, start, len)

    def writeString(self, db, start, value):
        if self.connect():
            reading = self.client.read_area(snap7.snap7types.S7AreaDB, db, start, 255)
            snap7.util.set_string(reading, 0, value, 255)
            self.client.db_write(db, start, reading)
        else:
            return self.writeString(db, start, value)

    def readLTime(self, db, start,getdt=False):
        if self.connect():
            reading = self.client.read_area(snap7.snap7types.S7AreaDB, db, start, 8)
            value = struct.unpack('>q', struct.pack('8B', *reading))[0]
            if getdt:
                td = numpy.timedelta64(value, 'ns')
                return datetime.timedelta(microseconds=td.tolist() / 1e3)
            else:
                return value

        else:
            return self.readLTime(db, start)


    def disconnect(self):
        self.client.disconnect()

    def __repr__(self):
        return f"{self.plcname if self.plcname else 'NoName'}@{self.ip}"
