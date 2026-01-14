#!/usr/bin/env python

from typing import Union, Optional, Literal
import datetime
import sys, os, platform
import obspy
import warnings
import numpy as np

# # import obspy seg2 plugin explicitly or plugin might not be detected by pyinstaller
# from obspy.io.seg2 import seg2 as _obspy_seg2
# print('***************************************')
# print('***', _obspy_seg2.__file__, '***')
# print('***************************************')

from pyseg2.seg2file import Seg2File
from pyseg2.toobspy import pyseg2_to_obspy_stream

from readdat.seg2.read_seg2default import default_to_seg2obspy, is_seg2_written_by_readdat
from readdat.seg2.read_seg2musc import seg2musc_to_seg2obspy, is_seg2musc
from readdat.seg2.read_seg2coda import seg2coda_to_seg2obspy, is_seg2coda
from readdat.seg2.read_seg2ondulys import seg2ondulys_to_seg2obspy, is_seg2ondulys
from readdat.seg2.read_seg2cdz import seg2cdz_to_seg2obspy, is_seg2cdz, guess_starttime_from_file
from readdat.seg2.read_seg2tomag import seg2tomag_to_seg2obspy, is_seg2tomag
from readdat.seg2.read_seg2must import seg2must_to_seg2obspy, is_seg2must


from readdat.utils.waveforms import print_stream
from readdat.utils.timeconversion import convert_starttime_from_naive_to_utc

ACQUISITION_SYSTEMS = [None, 'AUTO', 'MUSC', 'CODA', 'ONDULYS', 'CDZ', 'MONA', 'TOMAG', 'MUST']

def _read_seg2_without_obspy_warning(filename: str, **kwargs):

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        stream = obspy.read(filename, format="SEG2", **kwargs)

    if not hasattr(stream.stats, "seg2"):
        raise Exception('not a seg2 file')

    return stream


def autodetect_seg2_acquisition_system(stream: obspy.core.stream.Stream) \
        -> Optional[str]:

    if is_seg2_written_by_readdat(stream=stream):
        # for seg2 files written by readdat
        # the "AUTO" mode must not try to detetect the acquisition_system
        acquisition_system = None

    elif is_seg2coda(stream=stream):
        acquisition_system = "CODA"

    elif is_seg2musc(stream=stream):
        acquisition_system = "MUSC"

    elif is_seg2ondulys(stream=stream):
        acquisition_system = "ONDULYS"

    elif is_seg2cdz(stream=stream):
        acquisition_system = "CDZ"

    elif is_seg2tomag(stream=stream):
        acquisition_system = "TOMAG"

    elif is_seg2must(stream=stream):
        acquisition_system = "MUST"

    else:
        warnings.warn(
            f"could not detect acquisition system "
            f"=> using obspy defaults")
        acquisition_system = None

    assert acquisition_system in ACQUISITION_SYSTEMS
    return acquisition_system


def setstats(stats, path: str, value: object):
    keys = path.split('.')
    item = stats
    for key in keys[:-1]:
        try:
            item[key]
        except KeyError:
            item[key] = {}
        item = item[key]
    item[keys[-1]] = value


def move_noseg2_items(stream):
    # "noseg2" attributes correspond to items that where placed in stats['seg2'] by obspy
    # move these attributes like seg2.noseg2.toto.tata.titi=1 in stats['toto']["tata"]["titi"]=1
    # at the stream level
    try:
        items = list(stream.stats["seg2"].items())
        for key, val in items:
            if key.startswith('noseg2'):
                setstats(stream.stats, key.split('noseg2.')[-1], val)
                del stream.stats["seg2"][key]

    except (AttributeError, KeyError):
        pass
    # at the trace level
    for trace in stream:
        try:
            items = list(trace.stats["seg2"].items())
            for key, val in items:
                if key.startswith('noseg2'):
                    setstats(trace.stats, key.split('noseg2.')[-1], val)
                    del trace.stats["seg2"][key]

        except (AttributeError, KeyError):
            pass


def read_seg2(
        filename: str,
        acquisition_system: Optional[str],
        timezone: Optional[Literal['Europe/Paris']],
        verbose: bool=False,
        **kwargs) -> obspy.core.stream.Stream:
    """
    :param filename: name of the seg2 file to read
    :param acquisition_system:
        "MUSC", "CODA", "ONDULYS", "CDZ", ..., None = default
    :param timezone: interpret the absolute date/times as local times in a given time zone
            None (default) means "use the given times as if they where expressed in UTC+0"
                => pros : print(trace.stats.starttime) will look like the content of the header
                => cons : trace.stats.starttime.timestamp will be wrong by 3600s or 2*3600s depending on the season
                          this may bias the timeseries
            "Europe/Paris" means "subtract 1h or 2h to the starttimes depending on the season"
                => pros : timestamps are correct => ideal for time series
                => cons : printing the starttimes of each trace might look wrong and induce errors
    :param kwargs: all other keyword arguments are passed to the default obspy.read function
    :return stream: an obspy.core.stream.Stream object, containing the traces
    """

    stream: obspy.core.stream.Stream
    trace: obspy.core.trace.Trace
    if acquisition_system not in ACQUISITION_SYSTEMS:
        raise ValueError(f'{acquisition_system=} not allowed, should be among {ACQUISITION_SYSTEMS=}')
    # ================ READ THE DATA USING OBSPY
    try:
        stream = _read_seg2_without_obspy_warning(filename=filename, **kwargs)

    except IndexError as err:
        # this error was observed with cdz files
        if acquisition_system in ["AUTO", "CDZ"]:
            acquisition_system = "CDZ"  # this skips the auto detection

            # for these files, the obspy routines cannot be used
            seg2 = Seg2File()
            with open(filename, 'rb') as fid:
                seg2.load(fid)

            stream = seg2.to_obspy(**kwargs)

            starttime = guess_starttime_from_file(filename)

            if np.all([tr.stats.starttime.timestamp == 0 for tr in stream]):
                # probably not 1970.1.1 => try to read from the filetime ..bad option but no choice
                # NOTE : for CDZ Files the acquistion date was not set,
                # try to get it from the file creation time
                for trace in stream:
                    trace.stats.starttime = starttime
        else:
            raise Exception(err)

    # ============ DEFAULTS ATTRIBUTES COMMONT TO ALL SEG2 FILES
    # set defaults coordinates, to be filled depending on header conventions
    for trace in stream:
        trace.stats.receiver_x = np.nan  # METERS !!!
        trace.stats.receiver_y = np.nan  # METERS !!!
        trace.stats.receiver_z = np.nan  # METERS !!!
        trace.stats.source_x = np.nan  # METERS !!!
        trace.stats.source_y = np.nan  # METERS !!!
        trace.stats.source_z = np.nan  # METERS !!!
        trace.stats.temperature_degc = np.nan  # DEGC
        trace.stats.relative_humidity_percent = np.nan  # %

    # ============ FILL ATTRIBUTES FROM HEADERS
    # ===== COMMON TO ALL SEG2 FILES
    # channel
    try:
        for trace in stream:
            trace.stats.channel = f"{int(trace.stats.seg2['CHANNEL_NUMBER']):02d}"
    except KeyError as err:
        if verbose:
            warnings.warn('#no CHANNEL_NUMBER field was found in seg2 header')

    # if force_trig_to_zero: NO!!

    # ===== ACQUISITION SYSTEM
    if acquisition_system == "AUTO":
        acquisition_system = autodetect_seg2_acquisition_system(stream)

    # =====
    if acquisition_system is None:
        # use default seg2
        stream = default_to_seg2obspy(stream=stream)

    elif acquisition_system == "MUSC":
        # NO autodetect, if the user wants the obspy standard => acquisition_system=None
        stream = seg2musc_to_seg2obspy(
            stream=stream, verbose=verbose)

    elif acquisition_system == "CODA":
        stream = seg2coda_to_seg2obspy(
            stream=stream, verbose=verbose)

    elif acquisition_system == "ONDULYS":
        stream = seg2ondulys_to_seg2obspy(
            stream=stream)

    elif acquisition_system == "CDZ":
        stream = seg2cdz_to_seg2obspy(stream=stream)

    elif acquisition_system == "TOMAG":
        stream = seg2tomag_to_seg2obspy(stream=stream)

    elif acquisition_system == "MUST":
        stream = seg2must_to_seg2obspy(stream=stream)

    else:
        raise ValueError(
            f'unknown acquisition_system {acquisition_system}, '
            f'choices : {ACQUISITION_SYSTEMS=}')

    # convert the starttimes assuming a given time zone
    if timezone is not None:
        # warnings.warn("stream[*].stats.starttime and endtime converted to UTC+0")

        for trace in stream:

            # warnings.warn(
            #     '********** debug **********\n\t' +\
            #     str(timezone) + "\n\t" +\
            #     str(trace.stats.starttime) + "\n\t" +\
            #     str(convert_starttime_from_naive_to_utc(trace.stats.starttime, timezone=timezone)))

            trace.stats.starttime = \
                convert_starttime_from_naive_to_utc(
                    trace.stats.starttime, timezone=timezone)

            # trace.stats.endtime adjusted accordingly

    move_noseg2_items(stream)

    if verbose:
        print(filename)
        print_stream(stream)

    return stream



if __name__ == '__main__':

    if len(sys.argv[1:]) < 1 or ("-h" in sys.argv[1:]):
        print('''usage : 
        read_seg2.py [--<acquisition_system>] [--french] list.seg2 of.seg2 files.seg2
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
            verbose=True, headonly=True)
