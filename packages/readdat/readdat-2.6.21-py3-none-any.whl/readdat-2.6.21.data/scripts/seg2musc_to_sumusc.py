#!python

"""
convert seg2 file acquired by MUSC into su file
"""

import sys, os
from readdat.seg2.read_seg2 import read_seg2
from readdat.su.write_obspymusc_as_sumusc import write_obspymusc_as_sumusc

if __name__ == "__main__":

    if not len(sys.argv) == 4:
        raise Exception(
            'Usage: \n\t'
            'seg2musc_to_sumusc.py seg2file_musc.sg2 sufile_musc.su <big|little>')

    filename_in = sys.argv[1]
    filename_out = sys.argv[2]
    endian = sys.argv[3]

    assert os.path.isfile(filename_in)
    assert filename_out.endswith('.su')
    if os.path.isfile(filename_out):
        assert input(f'{filename_out} exists already, replace? y/[n]') == "y"

    assert endian in ["big", "little"]

    stream_in = read_seg2(filename=filename_in, acquisition_system="MUSC", verbose=True)
    write_obspymusc_as_sumusc(stream_in=stream_in, filename_out=filename_out, endian=endian)
