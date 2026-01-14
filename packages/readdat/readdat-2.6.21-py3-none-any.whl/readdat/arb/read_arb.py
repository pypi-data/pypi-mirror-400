import sys

import numpy as np

from obspy.core import Stream, Trace



def is_arb(filename: str) -> bool:
    ans = False

    with open(filename, 'r') as fid:
        if fid.readline().startswith('Copyright: © 2010 Keysight Technologies, Inc.'):
            ans = True

    return ans



def read_arb(filename: str, **ignored) -> Stream:
    """read arbitrary generation file .arb"""
    header = {}
    data = None

    with open(filename, 'r') as fid:
        first_line = fid.readline().split('\n')[0]
        if not (first_line.startswith('Copyright: ')
                and '2010 Keysight Technologies, Inc.' in first_line):
            raise ValueError(f"File {filename} is not a valid .arb file.")

        for l in fid:
            l = l.split('\n')[0]
            key = l.split(':')[0]
            key = ("_".join(key.split())).lower()

            if key in ["file_format", "filter"]:
                # str
                header[key] = l.split(':')[1].strip()

            elif key in ["channel_count", "data_points"]:
                # int
                header[key] = int(l.split(':')[1].strip())

            elif key in ["sample_rate", "high_level", "low_level", ]:
                # float
                header[key] = float(l.split(':')[1].strip())

            elif key == "data":
                data = np.asarray([
                    fid.readline().split('\n')[0]
                    for _ in range(header['data_points'])], dtype=float)

                # back to voltage data
                data /= 32767.0

    tr = Trace(
        header={
            # obspy header
            "delta": 1./header['sample_rate'],
            "starttime": 0.,
            "_format": "ARB",
            "receiver_x": np.nan,
            "receiver_y": np.nan,
            "receiver_z": np.nan,
            "source_x": np.nan,
            "source_y": np.nan,
            "source_z": np.nan,
            # arb file header
            "arb": header,
            },
        data=data,
        )
    assert tr.stats.npts == len(data) == tr.stats['arb']['data_points']

    st = Stream([tr])

    return st


if __name__ == '__main__':

    filename = sys.argv[1]
    if is_arb(filename):
        st = read_arb(filename)


    print(st)