from typing import Union
import os
import numpy as np
from obspy.core import Trace, Stream
import warnings

"""
Original file format from O. Durand, GeoEND
Reading program modified after Tom Druet, CEA
"""


class TusFormatError(Exception):
    pass


class MusChannelError(Exception):
    pass


def get_tus_mus(tus_file: str, mus_file: Union[str, None] = None):
    """
    infer mus file name from tus file name and check file existence
    """

    # ==== check tus fil
    if not tus_file.lower().endswith('.tus'):
        raise IOError(f"{tus_file} is not a .tus file")

    if not os.path.isfile(tus_file):
        raise IOError(f"{tus_file} not found")

    # ==== find corresponding mus file
    if mus_file is None:
        # assume mus has same name than tus file except the extension
        mus_file = tus_file.replace('.tus', ".mus")

    if not os.path.isfile(mus_file):
        raise IOError(f'could not find corresponding mus file {mus_file}')

    return tus_file, mus_file


def load_tus_header(tus_file: str) -> (int, int, float):
    """
    :return (npts, nb_trace, delta):
        npts = number of samples
        nb_traces = number of traces in file
        delta = sampling interval in seconds
    """
    with open(tus_file, 'r') as fid:
        line1 = fid.readline()
        line2 = fid.readline()
        line3 = fid.readline()

    if not line1.startswith('NB_DATA_PER_TRACE :'):
        raise TusFormatError('key NB_DATA_PER_TRACE not found is it a tus file?')

    if not line2.startswith('NB_TRACE :'):
        raise TusFormatError('key NB_TRACE not found is it a tus file?')

    if not line3.startswith('SAMPLING_INTERVAL :'):
        raise TusFormatError('key SAMPLING_INTERVAL not found is it a tus file?')

    npts = int(line1.split(':')[1])  # .replace("NB_DATA_PER_TRACE : ", ""))
    nb_trace = int(line2.split(':')[1])  # '.replace(" : ", ""))
    delta = float(line3.split(':')[1])  # '.replace("SAMPLING_INTERVAL : ", ""))
    return npts, nb_trace, delta


def read_tus_mus(tus_file: str, channel: int = 0,
                 mus_file: Union[str, None] = None, **ignored) -> Trace:
    """
    :param tus_file: .tus file name
    :type tus_file: str
    :param channel: channel number to load
    :type channel: int
    :param mus_file: .mus file name, (None means infer from tus name)
    :type mus_file: Union[str, int]
    :return tr: the loaded trace
    :rtype tr: [stats, data]
        can be packed into a obspy.core.trace.Trace object if needed
        I don't want a dependecy to obspy here
    """

    tus_file, mus_file = get_tus_mus(tus_file=tus_file, mus_file=mus_file)

    npts, _, delta = load_tus_header(tus_file=tus_file)

    # ==== load data from mus
    data_type = np.dtype('float32')
    data_type_max = np.finfo(dtype=data_type).max

    with open(mus_file, 'rb') as fid:
        data = np.fromfile(fid, dtype=data_type, count=4*npts, offset=channel * npts * 4)

    if not len(data):
        raise MusChannelError(f"no data found for channel {channel} in {mus_file}")

    data_abs_max = np.abs(data).max()
    if data_abs_max >= 0.99 * data_type_max:
        warnings.warn(f'overflow, max(|data|) ({data_abs_max}) exceeds 99% of max({data_type}) ({data_type_max})')

    stats = {
        "starttime": 0.,
        "channel": "CH%02d" % channel,
        "delta": delta,
        "_format": "TUSMUS",
        "tusmus": {}}

    trace = Trace(
        header=stats,
        data=data
        )
    stream = Stream([trace])
    return stream
