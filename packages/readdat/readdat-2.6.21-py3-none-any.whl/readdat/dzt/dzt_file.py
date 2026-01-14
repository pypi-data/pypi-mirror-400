"""
Read/Write binary DZT file in python 
Devie Thibaud, 23/09/2022
"""

import struct
import numpy as np
import os
from dataclasses import dataclass


@dataclass
class HeaderDzt:
    tag: int = 0x00ff
    data: int = 1024
    nsamp: int = 0
    bits: int = 0
    zero: int = 0x0000
    sps: float = 1.0
    spm: float = 0
    mpp: float = 0
    position: float = 0
    range: float = 0
    spp: int = 1
    rgain: int = 0
    nrgain: int = 0
    text: int = 0
    ntext: int = 0
    proc: int = 0
    nproc: int = 0
    nchan: int = 1
    epsr: int = 1
    top: int = 0
    depth: int = 0
    npass: int = 0
    reserved: str = 'x' * 60
    variable: str = 'x' * 384
    timestamp_create: bytes = b'x00'
    timestamp_modif: bytes = b'x00'
    second: int = 0
    minute: int = 0
    hour: int = 0
    day: int = 0
    month: int = 0
    year: int = 0

    def unpack(self, header_bin: bytes):
        self.tag = struct.unpack('<h', header_bin[0:2])[0]
        self.data = struct.unpack('<h', header_bin[2:4])[0]
        self.nsamp = struct.unpack('<h', header_bin[4:6])[0]
        self.bits = struct.unpack('<h', header_bin[6:8])[0]
        self.zero = struct.unpack('<h', header_bin[8:10])[0]
        self.sps = struct.unpack('<f', header_bin[10:14])[0]
        self.spm = struct.unpack('<f', header_bin[14:18])[0]
        self.mpp = struct.unpack('<f', header_bin[18:22])[0]
        self.position = struct.unpack('<f', header_bin[22:26])[0]
        self.range = struct.unpack('<f', header_bin[26:30])[0]
        self.spp = struct.unpack('<h', header_bin[30:32])[0]
        self.timestamp_create = header_bin[32:36]
        self.timestamp_modif = header_bin[36:40]
        self.rgain = struct.unpack('<h', header_bin[40:42])[0]
        self.nrgain = struct.unpack('<h', header_bin[42:44])[0]
        self.text = struct.unpack('<h', header_bin[44:46])[0]
        self.ntext = struct.unpack('<h', header_bin[46:48])[0]
        self.proc = struct.unpack('<h', header_bin[48:50])[0]
        self.nproc = struct.unpack('<h', header_bin[50:52])[0]
        self.nchan = struct.unpack('<h', header_bin[52:54])[0]
        self.epsr = struct.unpack('<f', header_bin[54:58])[0]
        self.top = struct.unpack('<f', header_bin[58:62])[0]
        self.depth = struct.unpack('<f', header_bin[62:66])[0]
        self.npass = struct.unpack('<h', header_bin[66:68])[0]
        self.reserved = struct.unpack('<' + 'c'*60, header_bin[68:128])[0].decode('ascii')
        self.variable = struct.unpack('<' + 'c'*384, header_bin[128:512])[0].decode('ascii')

        mask_second = 0x0000001f
        mask_minute = 0x000007e0
        mask_hour = 0x0000f800
        mask_day = 0x001f0000
        mask_month = 0x01e00000
        mask_year = 0xfe000000

        time_int = int.from_bytes(self.timestamp_create, byteorder="little", signed=False)
        self.second = (time_int & mask_second) * 2
        self.minute = (time_int & mask_minute) >> 5
        self.hour = (time_int & mask_hour) >> 11
        self.day = (time_int & mask_day) >> 16
        self.month = (time_int & mask_month) >> 21
        self.year = (time_int & mask_year) >> 25

    def pack(self) -> bytes:
        timestamp_create = 0x00000000
        timestamp_modif = 0x00000000

        timestamp_create = timestamp_create | self.second // 2 | self.minute << 5 | self.hour << 11 | self.day << 16 | self.month << 21 | self.year << 25

        header_bin = struct.pack('<hhhhh', self.tag, self.data, self.nsamp, self.bits, self.zero)
        header_bin += struct.pack('<fffff', self.sps, self.spm, self.mpp, self.position, self.range)
        header_bin += struct.pack('<h', self.spp)
        header_bin += struct.pack('<I', timestamp_create)
        header_bin += struct.pack('<I', timestamp_modif)
        header_bin += struct.pack('<hhhhhhh', self.rgain, self.nrgain, self.text, self.ntext, self.proc, self.nproc, self.nchan)
        header_bin += struct.pack('<fff', self.epsr, self.top, self.depth)
        header_bin += struct.pack('<h', self.npass)
        header_bin += struct.pack('<60s', self.reserved.encode('UTF-8'))
        header_bin += struct.pack('<384s', self.variable.encode('UTF-8'))

        return header_bin


@dataclass
class DataDzt:
    nsamp: int = 0
    nscan: int = 0
    data: np.ndarray = ()

    def unpack(self, data_bin: bytes, data_size, nb_samp, values_format):
        self.nsamp = nb_samp
        self.nscan = int(data_size / (self.nsamp * (values_format / 8)))
        self.data = struct.unpack('H' * int(data_size / 2), data_bin)
        self.data = np.reshape(self.data, (self.nscan, self.nsamp))

    def pack(self):
        data_bin = struct.pack(f"<{self.data.size:d}H", *self.data.flat[:])
        return data_bin


def read_dzt(filename: str) -> (HeaderDzt, DataDzt):
    headerdzt = HeaderDzt()
    datadzt = DataDzt()
    file_size = os.path.getsize(filename)
    print(file_size)
    with open(filename, 'rb') as f:
        header_bin = f.read(512)
        headerdzt.unpack(header_bin)
        unused = f.read(512)
        data_size = file_size - headerdzt.data
        data_bin = f.read(data_size)
        datadzt.unpack(data_bin, data_size, headerdzt.nsamp, headerdzt.bits)
    return headerdzt, datadzt


def write_dzt(filename: str, headerdzt: HeaderDzt, datadzt: DataDzt):
    header_bin = headerdzt.pack()
    data_bin = datadzt.pack()
    with open(filename, 'wb') as f:
        f.write(header_bin)
        f.write(bytes(512))
        f.write(data_bin)
