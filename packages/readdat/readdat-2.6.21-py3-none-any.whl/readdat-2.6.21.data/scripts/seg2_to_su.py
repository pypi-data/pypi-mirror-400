#!python

"""
convert seg2 into su for seismic data (not MUSC)
and pipes it into stdout for direct use by seismic unix
"""

import sys, os
from readdat.seg2.read_seg2 import read_seg2


if __name__ == "__main__":

    if not len(sys.argv) == 3 or sys.stdout.isatty():
        raise Exception(
            'Usage: \n\t'
            'seg2_to_su.py seg2file.sg2 <big|little> > sufile.su\n\t'
            'seg2_to_su.py seg2file.sg2 <big|little> | suxwigb\n\t'
            'nb: output cannot be terminal'
            )

            
    filename_in = sys.argv[1]
    endian = sys.argv[2]

    assert os.path.isfile(filename_in)
    assert endian in ["big", "little"]

    stream_in = read_seg2(filename=filename_in, acquisition_system=None, verbose=False, timezone="Europe/Paris")

    stream_in.write(sys.stdout.buffer, format="SU", endian=endian)

