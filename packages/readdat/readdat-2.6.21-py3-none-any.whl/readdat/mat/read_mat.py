import warnings
from typing import Optional, Literal

from scipy.io import loadmat
import obspy
from obspy.core.utcdatetime import UTCDateTime

from readdat.mat.read_mat_quantum import _read_mat_quantum, is_mat_quantum
from readdat.mat.read_mat_ultrasonic_scan import _read_mat_ultrasonic_scan, is_mat_ultrasonic_scan
from readdat.utils.timeconversion import convert_starttime_from_naive_to_utc


def autodetect_mat_acquisition_system(mat: dict) -> Optional[str]:
    """
    Check if the file is a Quantum or Ultrasonic Scan .mat file
    """
    if is_mat_quantum(mat):
        return "QUANTUM"

    elif is_mat_ultrasonic_scan(mat):
        return "ULTRASONICS_SCAN"

    else:
        raise Exception("Could not detect mat acquisition system automatically")


def read_mat(
        filename: str,
        acquisition_system: Optional[Literal["AUTO", "QUANTUM", "ULTRASONICS_SCAN", "USCAN"]],
        timezone: Optional[Literal["Europe/Paris"]],
        verbose: bool=False,
        **ignored) -> obspy.core.stream.Stream:
    """
    :param filename: name of the .mat file to read
    :param acquisition_system: AUTO, QUANTUM, ULTRASONICS_SCAN, USCAN
    :param timezone: interpret the absolute date/times as local times in a given time zone
        None (default) means "use the given times as if they were expressed in UTC+0"
            => pros : print(trace.stats.starttime) will look like the content of the header
            => cons : trace.stats.starttime.timestamp will be wrong by 3600s or 2*3600s depending on the season
                      this may bias the timeseries
        "Europe/Paris" means "subtract 1h or 2h to the starttimes depending on the season"
            => pros : timestamps are correct => ideal for time series
            => cons : printing the starttimes of each trace might look wrong and induce errors
    :param ignored: other arguments ignored
    :return stream: an obspy.core.stream.Stream object, containing the traces
    """

    stream: obspy.core.stream.Stream
    trace: obspy.core.trace.Trace

    # ================ READ THE DATA
    mat = loadmat(file_name=filename, squeeze_me=True)

    if acquisition_system == "AUTO":
        acquisition_system = autodetect_mat_acquisition_system(mat=mat)

    if acquisition_system == "QUANTUM":
        stream = _read_mat_quantum(mat=mat)

    elif acquisition_system in ["ULTRASONICS_SCAN", "USCAN"]:
        stream = _read_mat_ultrasonic_scan(mat=mat)

    else:
        raise NotImplementedError(
            f'unknown acquisition_system {acquisition_system}, '
            f'use QUANTUM, ULTRASONICS_SCAN, USCAN, or ...')

    if timezone is not None:
        warnings.warn('stream[*].stats.starttime and endtime converted to UTC+0')
        for trace in stream:
            trace.stats.starttime = \
                convert_starttime_from_naive_to_utc(
                    starttime=trace.stats.starttime, timezone=timezone)

    if verbose:
        print(filename)

        for trace in stream:
            print(trace)
            for key, val in trace.stats[acquisition_system.lower()].items():
                print(f'\t{key}: {val}')

    return stream


if __name__ == '__main__':
    read_mat('../filesamples/matquantum1.mat',
             acquisition_system="QUANTUM",
             verbose=True,
             timezone=None)
