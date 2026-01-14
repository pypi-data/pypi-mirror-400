import obspy
from obspy.core import UTCDateTime, AttribDict, Stream
from parse import parse

import numpy as np


"""
P.Mora 2023/05/09
"""

header_format = \
    'MATLAB {mat_version:f} MAT-file, Platform: {platform:s}, Created on: {day:02d}/{month:02d}/{year:04d} {hour:02d}:{minute:02d}:{second:02d}'
date_format = \
    '{day:02d}/{month:02d}/{year:04d} {hour:02d}:{minute:02d}:{second:02d}'


def is_mat_quantum(mat: dict) -> bool:
    """
    Check if the file is a Quantum .mat file
    """
    try:
        mat['File_Header']['NumberOfChannels']
        ans = True
    except KeyError:
        ans = False

    return ans


def _extract_quantum_file_header(mat: dict) -> (int, float, UTCDateTime):
    # ======== Unpack File Header
    # print(mat['File_Header'].dtype)
    number_of_channels = int(
        mat['File_Header']['NumberOfChannels'])

    # number_of_samples_per_block = int(
    #     mat['File_Header']['NumberOfSamplesPerBlock'])

    sample_frequency = float(
        str(mat['File_Header']['SampleFrequency'])
        .replace(',', '.'))  # Hz

    date = UTCDateTime(**
        parse(date_format, str(mat['File_Header']['Date'])).named)

    # comment = str(
    #     mat['File_Header']['Comment'])

    # number_of_samples_per_channel = int(
    #     mat['File_Header']['NumberOfSamplesPerChannel'])

    return number_of_channels, sample_frequency, date


def _extract_quantum_metadata_field(mat: dict, key: str) -> dict:
    meta = {}

    for k in mat[key].dtype.fields:
        meta[k] = str(mat[key][k])

    return meta


def _extract_quantum_trace_header(mat: dict, ntrace: int) -> dict:
    # ======== Unpack Trace Header
    return _extract_quantum_metadata_field(mat, f'Channel_{ntrace}_Header')


def _read_mat_quantum(mat: dict) -> Stream:

    stream = obspy.core.stream.Stream()

    stream_metadata = {}

    for key in mat.keys():
        if "channel" not in key.lower():
            if isinstance(mat[key], np.ndarray):
                stream_metadata[key] = _extract_quantum_metadata_field(mat, key)
            else:
                stream_metadata[key] = mat[key]

    stream.stats = AttribDict(dict(mat=stream_metadata))

    number_of_channels, sample_frequency, date = \
        _extract_quantum_file_header(mat)

    for ntrace in range(1, 1 + number_of_channels):

        header_channel = _extract_quantum_trace_header(mat, ntrace)
        data = mat[f'Channel_{ntrace}_Data'].flat[:]
        npts = len(data)

        trace = obspy.core.trace.Trace(
            data=data,
            header={
                "sampling_rate": sample_frequency,
                "starttime": date - (npts - 1) / sample_frequency,
                "network": "QUANTUM",
                "channel": f"{ntrace:d}",
                "_format": "MAT",
                "mat": header_channel,
                },
            )
        stream.append(trace)
    return stream
