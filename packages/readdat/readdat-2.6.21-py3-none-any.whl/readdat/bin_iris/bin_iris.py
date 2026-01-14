"""
Author: Thibaud Devie
Oct. 2023
"""

import struct
import numpy as np
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
from datetime import timedelta


@dataclass
class HeaderBin:
    version: int = 0x00000000
    typeofsyscal: int = 0x00
    comments: str = 'x' * 1024
    ColeCole: np.ndarray = ()
    ColeTau: np.ndarray = ()
    ColeM: np.ndarray = ()
    ColeRms: np.ndarray = ()


    def unpack(self, file):
        header_bin = file.read(1029)
        self.version = struct.unpack('<L', header_bin[0:4])[0]
        self.typeofsyscal = struct.unpack('<B', header_bin[4:5])[0]
        self.comments = struct.unpack('<1024c', header_bin[5:])[0].decode('ascii')
        if self.version == 2147483651:
            cole_bin = file.read(64000*3*4)
            self.ColeCole = np.frombuffer(cole_bin, dtype=float, count=-1)
            self.ColeTau = self.ColeCole[::3]
            self.ColeM = self.ColeCole[1::3]
            self.ColeRms = self.ColeCole[2::3]


@dataclass
class DataBin:
    df: pd.DataFrame = None  # (np.empty(0))
    g: np.ndarray = None  # ()
    Tm: np.ndarray = None  # ()
    Mx: np.ndarray = None  # ()
    el_array: int = 0
    MoreTMesure: int = 0
    time: float = 0
    m_dly: float = 0
    TypeCpXyz: int = 0
    Ignore: int = 0
    ps: float = 0
    vp: float = 0
    In: float = 0
    rho: float = 0
    m: float = 0
    e: float = 0
    Channel: int = 0
    NbChannel: int = 0
    Overload: int = 0
    ChannelValide: int = 0
    ChannelSync: int = 0
    GapFiller: int = 0
    unused: int = 0
    QuadNumber: int = 0
    Name: str = ''
    Latitude: float = 0
    Longitude: float = 0
    NbCren: float = 0
    RsChk: float = 0
    TxVab: float = 0
    TxBat: float = 0
    RxBat: float = 0
    Temperature: float = 0
    DateTime: int = 0
    second: int = 0
    minute: int = 0
    hour: int = 0
    day: int = 0
    month: int = 0
    year: int = 0

    def unpack(self, file):
        data1 = []  # Liste pour stocker les données
        data2 = []
        for i in range(64000):
            try:
                data_bin = file.read(280)
                self.el_array = struct.unpack('<h', data_bin[0:2])[0]
                self.MoreTMesure = struct.unpack('<h', data_bin[2:4])[0]
                self.time = struct.unpack('<f', data_bin[4:8])[0]
                self.m_dly = struct.unpack('<f', data_bin[8:12])[0]
                self.TypeCpXyz = struct.unpack('<h', data_bin[12:14])[0]
                self.Ignore = struct.unpack('<h', data_bin[14:16])[0]
                self.g = np.frombuffer(data_bin, dtype=np.dtype('float32'), count=12, offset=16)
                self.ps = struct.unpack('<f', data_bin[64:68])[0]
                self.vp = struct.unpack('<f', data_bin[68:72])[0]
                self.In = struct.unpack('<f', data_bin[72:76])[0]
                self.rho = struct.unpack('<f', data_bin[76:80])[0]
                self.m = struct.unpack('<f', data_bin[80:84])[0]
                self.e = struct.unpack('<f', data_bin[84:88])[0]
                self.Tm = np.frombuffer(data_bin, dtype=np.dtype('float32'), count=20, offset=88)
                self.Mx = np.frombuffer(data_bin, dtype=np.dtype('float32'), count=20, offset=168)
                channel_temp = struct.unpack('<B', data_bin[248:249])[0]
                self.Channel = channel_temp>>4 & 0b00001111
                self.NbChannel = channel_temp & 0b00001111
                miscel_temp = struct.unpack('<B', data_bin[249:250])[0]
                self.Overload = miscel_temp & 0b00000001
                self.ChannelValide = miscel_temp & 0b00000010
                self.ChannelSync = miscel_temp & 0b00000100
                self.GapFiller = miscel_temp & 0b00001000
                self.unused = miscel_temp & 0b11110000
                self.QuadNumber = struct.unpack('<H', data_bin[250:252])[0]
                self.Name = struct.unpack('<12s', data_bin[252:264])[0].decode('utf-8').rstrip('\x00')
                self.Latitude = struct.unpack('<f', data_bin[264:268])[0]
                self.Longitude = struct.unpack('<f', data_bin[268:272])[0]
                self.NbCren = struct.unpack('<f', data_bin[272:276])[0]
                self.RsChk = struct.unpack('<f', data_bin[276:])[0]

                data1.append({'Type_acq': self.el_array, 'time': self.time, 'm_delay': self.m_dly, 'TypeCpXyz':self.TypeCpXyz,
                             'Ignore':self.Ignore, 'g':self.g, 'ps':self.ps, 'vp':self.vp, 'in':self.In, 'rho': self.rho,
                             'm':self.m, 'Deviation':self.e, 'Tm':self.Tm, 'Mx':self.Mx, 'Channel':self.Channel, 'NbChannel':self.NbChannel,
                             'Overload':self.Overload, 'Channel_Valide':self.ChannelValide, 'Channel_Sync':self.ChannelSync,
                             'GapFiller':self.GapFiller, 'Name':self.Name, 'Latitude':self.Latitude, 'Longitude':self.Longitude,
                             'NbCren':self.NbCren, 'RsCheck':self.RsChk})

                if self.MoreTMesure == 2:
                    data_bin = file.read(16)
                    self.TxVab = struct.unpack('<f', data_bin[0:4])[0]
                    self.TxBat = struct.unpack('<f', data_bin[4:8])[0]
                    self.RxBat = struct.unpack('<f', data_bin[8:12])[0]
                    self.Temperature = struct.unpack('<f', data_bin[12:])[0]

                    data2.append({'TxVab':self.TxVab, 'TxBat':self.TxBat, 'RxBat':self.RxBat, 'Temperature':self.Temperature})

                if self.MoreTMesure == 3:
                    data_bin = file.read(24)
                    self.TxVab = struct.unpack('<f', data_bin[0:4])[0]
                    self.TxBat = struct.unpack('<f', data_bin[4:8])[0]
                    self.RxBat = struct.unpack('<f', data_bin[8:12])[0]
                    self.Temperature = struct.unpack('<f', data_bin[12:16])[0]
                    self.DateTime = struct.unpack('<d', data_bin[16:])[0]

                    ref_date = datetime(1899, 12, 30, 0, 0, 0)
                    date = ref_date + timedelta(days=self.DateTime)
                    self.second = date.second
                    self.minute = date.minute
                    self.hour = date.hour
                    self.day = date.day
                    self.month = date.month
                    self.year = date.year

                    data2.append(
                        {'TxVab': self.TxVab, 'TxBat': self.TxBat, 'RxBat': self.RxBat, 'Temperature': self.Temperature,
                         'seconds': self.second, 'minutes': self.minute, 'hour': self.hour, 'day': self.day,
                         'month': self.month, 'year': self.year})
            except struct.error:
                break
        df1 = pd.DataFrame(data1)
        if data2 is not None:
            df2 = pd.DataFrame(data2)
            self.df = pd.concat([df1, df2], axis=1)
        else:
            self.df = df1


def read_bin(filename: str):
    f = open(filename, 'rb')
    headerbin = HeaderBin()
    databin = DataBin()
    headerbin.unpack(f)
    databin.unpack(f)
    return headerbin, databin.df

