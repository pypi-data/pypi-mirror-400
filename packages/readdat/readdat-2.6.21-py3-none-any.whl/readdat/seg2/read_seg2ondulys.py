from typing import List
import obspy
import warnings
from readdat.seg2.read_seg2default import extract_receiver_location


KNOWN_ONDULYS_VERSIONS = [
    'V5.6 02/06/2021']


def is_seg2ondulys(stream: obspy.core.stream.Stream) -> bool:
    """
    determines whether a stream read from seg2 file is from ONDULYS or not
    :return answer: True or False
    """

    assert isinstance(stream, obspy.core.stream.Stream), TypeError(type(stream))

    if not hasattr(stream.stats, "seg2"):
        # probably not even a seg2 file
        return False

    if not hasattr(stream.stats.seg2, "NOTE"):
        return False

    notes: List[str] = stream.stats.seg2['NOTE']
    version_string = notes[-1].strip()

    if version_string in KNOWN_ONDULYS_VERSIONS:
        return True

    elif "ONDULYS" in version_string:
        return True

    elif len(stream) and "Universite G.EIFFEL IFSTTAR-Sciencia" in stream[0].stats.seg2['COMPANY']:
        return True

    else:
        return False


def seg2ondulys_to_seg2obspy(stream: obspy.core.stream.Stream, verbose: bool=True) -> obspy.core.stream.Stream:
    """
    Extract information for ondulys files,
    private, do not call directly
    """
    # TODO : assert that this is indeed a file from ONDULYS

    for trace in stream:
        trace.stats.station = "ONDULYS"

        # coordinates
        extract_receiver_location(trace=trace)

        # fix year issue 22 => 2022 // 75 => 1975
        if trace.stats.starttime.year < 50.:
            warnings.warn('modify year : +2000. ')
            trace.stats.starttime = obspy.core.UTCDateTime(
                year=trace.stats.starttime.year + 2000,
                month=trace.stats.starttime.month,
                day=trace.stats.starttime.day,
                hour=trace.stats.starttime.hour,
                minute=trace.stats.starttime.minute,
                second=trace.stats.starttime.second,
                microsecond=trace.stats.starttime.microsecond
                )

        elif trace.stats.starttime.year < 100.:
            warnings.warn('modify year : +1900. ')
            trace.stats.starttime = obspy.core.UTCDateTime(
                year=trace.stats.starttime.year + 1900,
                month=trace.stats.starttime.month,
                day=trace.stats.starttime.day,
                hour=trace.stats.starttime.hour,
                minute=trace.stats.starttime.minute,
                second=trace.stats.starttime.second,
                microsecond=trace.stats.starttime.microsecond
                )

    return stream
