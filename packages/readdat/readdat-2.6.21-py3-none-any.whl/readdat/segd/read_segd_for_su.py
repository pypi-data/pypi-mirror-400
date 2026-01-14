#/usr/bin/env python

HELP = """
A simple approach to read segdfile and pipe it to seismic unix

Usage 
    # prompt help message and exits 
    python read_segd_for_su.py -h   
    python read_segd_for_su.py --help    

    # load segd data and show it with seismic unix
    python read_segd_for_su.py <filename.segd> | suxwigb

WARNING : do NOT use 
    python read_segd_for_su.py <filename.segd>
    because it will prompt binary data to your terminal
    
"""
import sys, glob, os
from obspy.core import Stream
from readdat.segd.read_segd2X import read_segd_rev2_X
from readdat.segd.read_segd30 import read_segd_rev3_0 # not ready
import numpy as np


if __name__ == "__main__":
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        print(HELP)
        sys.exit(1)

    stream_all = Stream()        
    for filename in sys.argv[1:]:
        if filename.endswith('.segd'):
            try:
                stream_i = read_segd_rev2_X(filename)
            except Exception as err:
                try:
                    stream_i = read_segd_rev3_0(filename, verbose=False).copy()
                except Exception as err1:
                    raise err1
                    
            for trace in stream_i:
                stream_all.append(trace)
                    
    for trace in stream_all:
        # trace.detrend(type="simple")
        # trace.data /= np.std(trace.data)
        # force data type for seismic unix
        trace.data = trace.data.astype(np.dtype('float32'))

    # write to stdout as binary SU data to pipe it to seismic unix programs
    stream_all.write(sys.stdout.buffer, format="SU")
    # stream.write("toto.su", format="SU")

