import obspy

from readdat.segy.createsegy import ENDIAN
from readdat.segy.write_obspymusc_as_segymusc import _write_obspymusc_as_sumusc_or_segymusc


def write_obspymusc_as_sumusc(
        stream_in: obspy.core.stream.Stream, filename_out: str, endian=ENDIAN) \
        -> obspy.core.stream.Stream:
    """
    stream_in has been converted from SEG2MUSC (time in milliseconds) to OBSPY (time in seconds)
    Save it as SEGYMUSC  (time in nanoseconds)

    :param stream_in: a stream of traces converted from seg2musc to obspy with option acquisition_system="MUSC"
    :param filename_out: name of the su file to write out
    :param endian: endianess "big" or "little", default is the endianess of the current system
    """

    return _write_obspymusc_as_sumusc_or_segymusc(
        stream_in=stream_in, filename_out=filename_out,
        endian=endian, format_out="SU")
