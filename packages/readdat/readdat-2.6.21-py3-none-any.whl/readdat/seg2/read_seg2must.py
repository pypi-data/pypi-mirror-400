import os, platform, warnings
import obspy
from readdat.seg2.read_seg2coda import extract_receiver_location  # it is the same for now


def is_seg2must(stream: obspy.core.stream.Stream) -> bool:
    """
    tries to detect MUST data files
    """
    try:
        ans = stream.stats['seg2']['COMPANY'] == "UGE_GeoEND"

        notes = stream.stats['seg2']['NOTE']
        ans &= any([note.startswith("UNIV. G.EIFFEL PICO4824 ") for note in notes])
    except KeyError:
        ans = False

    return ans


def _convert_time_units_in_seg2must_header(trace: obspy.core.trace.Trace, verbose: bool=True) -> None:
    """
    Time is expressed in milliseconds, but obspy assumes seconds => convert all times to seconds
    # => multiply sampling rate by 1000
    """
    if verbose:
        #chiant warnings.warn('convert SAMPLE_INTERVAL from milliseconds (MUST) to seconds (OBSPY)')
        pass

    trace.stats.sampling_rate *= 1000.  # NOTE trace.stats.delta is devided by 1000 accordingly
    trace.stats.seg2["SAMPLE_INTERVAL"] = str(trace.stats.delta)  # preserve the str type

    # NO : delay is already in seconds
    # delay = float(trace.stats.seg2["DELAY"]) / 1000.  # in seconds
    # trace.stats.seg2["DELAY"] = str(delay)  # preserve the str type

    return None

def seg2must_to_seg2obspy(stream: obspy.core.stream.Stream, verbose: bool=True) -> obspy.core.stream.Stream:
    """
    """
    for trace in stream:
        trace.stats.station = "MUST"


        # ==== header conversions
        _convert_time_units_in_seg2must_header(trace=trace, verbose=verbose)


        # coordinates
        extract_receiver_location(trace=trace)

    return stream
