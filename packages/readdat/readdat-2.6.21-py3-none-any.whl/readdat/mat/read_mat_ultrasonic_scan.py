import obspy
from obspy.core import UTCDateTime, AttribDict, Stream
from parse import parse

import numpy as np


"""
P.Mora 2025/05/02
"""

date_format = \
    '{day:02d}/{month:02d}/{year:04d} {hour:02d}:{minute:02d}:{second:02d}'


def is_mat_ultrasonic_scan(mat: dict) -> bool:
    """
    Check if the file is a Ultrasonic Scan .mat file
    """
    if 'DX' in mat and 'DY' in mat and 'YOri' in mat and 'XOri' in mat:
        return True

    return False


def _read_mat_ultrasonic_scan(mat: dict) -> Stream:

    stream = obspy.core.stream.Stream()

    stream_metadata = {}

    for key in mat.keys():
        if "ch" not in key.lower():
            stream_metadata[key] = mat[key]

    stream.stats = AttribDict(dict(ultrasonic_scan=stream_metadata))

    sample_frequency = 1. / mat['DX']
    DY = mat['DY']
    YOri = mat['YOri']
    XOri = mat['XOri']
    number_of_channels = DY.size
    date = UTCDateTime(**
        parse(date_format, str(mat['DATE_ORDI'] + ' ' + mat['TIME_ORDI'])).named)

    for ntrace in range(1, 1 + number_of_channels):

        # ## header_channel = _extract_quantum_trace_header(mat, ntrace)
        header_channel = {}  # TODO!
        k = f'CH{ntrace}'

        if k in mat:
            data = mat[f'CH{ntrace}'].flat[:] * DY[ntrace - 1] + YOri[ntrace - 1]
            npts = len(data)
        else:
            continue

        trace = obspy.core.trace.Trace(
            data=data,
            header={
                "sampling_rate": sample_frequency,
                "starttime": date - (npts - 1) / sample_frequency,
                "channel": f"{ntrace:d}",
                "_format": "ULTRASONIC_SCAN",
                "ultrasonic_scan": header_channel,
                },
            )
        stream.append(trace)
    return stream
