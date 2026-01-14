#!/usr/bin/env python
import sys, glob, os
import numpy as np
import matplotlib.pyplot as plt
from readdat.seg2.read_seg2 import read_seg2
from readdat import show_stream, shade_stream


if __name__ == '__main__':

    if len(sys.argv[1:]) < 1 or ("-h" in sys.argv[1:]):
        print('''usage : 
        show_seg2.py [--<acquisition_system>] [--french]  [--shade] list.seg2 of.seg2 files.seg2
        ''')
        exit(1)

    file_list = []
    acquisition_system = None
    timezone = None
    for arg in sys.argv[1:]:
        if arg == "--french":
            timezone = "Europe/Paris"
        elif arg.startswith('--'):
            acquisition_system = arg.split('--')[-1].upper()
        elif os.path.isfile(arg):
            file_list.append(arg)
        else:
            raise IOError(arg)

    for filename in file_list:
        stream = read_seg2(
            filename,
            acquisition_system=acquisition_system,
            timezone=timezone,
            verbose=True)

        for trace in stream:
            trace.detrend(type='simple')
            trace.stats.timestamp = trace.stats.starttime.timestamp # backup
            trace.stats.starttime = 0.  # for display
            # print(trace)

        if "--shade" in sys.argv[1:]:
            shade_stream(plt.gca(), stream, cmap=plt.get_cmap('seismic'), powergain=0.8)
        show_stream(plt.gca(), stream, color="k", alpha=0.3)
        plt.gca().set_ylabel('trace num.')
        plt.gca().set_xlabel('time (s)')
        plt.show()

