#!/usr/bin/env python

"""
convert seg2 file acquired by MUSC into su file
"""

import sys, os
from readdat.seg2.read_seg2 import read_seg2
from readdat.segy.write_obspymusc_as_segymusc import write_obspymusc_as_segymusc


if __name__ == "__main__":

    if not len(sys.argv) == 4:
        raise Exception(
            'Usage: \n\t'
            'seg2musc_to_segymusc.py seg2file_musc.sg2 segyfile_musc.segy <big|little>')

    filename_in = sys.argv[1]
    filename_out = sys.argv[2]
    endian = sys.argv[3]

    assert os.path.isfile(filename_in)
    assert filename_out.endswith('.segy')

    if os.path.isfile(filename_out):
        assert input(f'{filename_out} exists already, replace? y/[n]') == "y"

    assert endian in ["big", "little"]

    stream_in = read_seg2(filename=filename_in, acquisition_system="MUSC", timezone=None, verbose=True)
    write_obspymusc_as_segymusc(stream_in=stream_in, filename_out=filename_out, endian=endian)
