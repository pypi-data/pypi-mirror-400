import os, platform
import obspy


def is_seg2tomag(stream: obspy.core.stream.Stream) -> bool:
    """
    tries to detect TOMAG data files
    """
    try:
        ans = stream.stats['seg2']['OBSERVER'] == "TomoAcq"
        ans &= stream.stats['seg2']['COMPANY'] == "IFSTTAR_GeoEnd"
        for note in stream.stats['seg2']['NOTE']:
            if "TOMAG VERSION" in note:
                break
        else:
            ans = False
    except KeyError:
        ans = False

    return ans


def seg2tomag_to_seg2obspy(stream: obspy.core.stream.Stream, verbose: bool=True) -> obspy.core.stream.Stream:
    """
    """
    for trace in stream:
        trace.stats.station = "TOMAG"

    # no specificities yet, except that RECEIVER_LOCATION should be empty

    return stream
