from typing import List
import datetime
import warnings
import numpy as np
import obspy
import parse
from readdat.seg2.read_seg2default import extract_receiver_location, extract_source_location


KNOWN_MUSC_VERSIONS = [
    # future versions are assumed to include "MUSC"
    "IFSTTAR MUSC V12.3 26/04/2016 TRIG FAST",
    "IFSTTAR MUSC V12.2 25/04/2016 TRIG FAST",
    "IFSTTAR MUSC V12.1 18/04/2016 TRIG FAST",
    "IFSTTAR MUSC V12.0 08/02/2016 TRIG FAST",
    "IFSTTAR MUSC V11.7 26/01/2016 TRIG FAST",
    "IFSTTAR MUSC V11.5 20/01/2016 TRIG FAST",
    "IFSTTAR MUSC V11.4 19/02/2015 TRIG FAST",
    "IFSTTAR MUSC V11.3 19/02/2015 TRIG FAST",
    "IFSTTAR MUSC V11.2 16/02/2015 TRIG FAST",
    "IFSTTAR MUSC V11.1 27/01/15 TRIG FAST",
    "IFSTTAR MUSC V11.0 14/01/15 TRIG FAST",
    "IFSTTAR MUSC V10.7 08/09/14 TRIG FAST",
    "IFSTTAR MUSC V10.5 21/07/14 TRIG FAST",
    "IFSTTAR MUSC V10.4 11/03/14 TRIG FAST",
    "IFSTTAR MUSC V10.3 19/02/14 TRIG FAST",
    "IFSTTAR MUSC V10.2 14/02/14 TRIG FAST",
    "IFSTTAR MUSC V10.1 21/01/14 TRIG FAST",
    "IFSTTAR MUSC V10.0 13/12/13 TRIG FAST",
    "IFSTTAR MUSC V9.5 02/12/13 TRIG FAST",
    "IFSTTAR MUSC V9.4 23/10/13 TRIG FAST",
    "IFSTTAR MUSC V9.3 22/10/13 TRIG FAST",
    "IFSTTAR MUSC V9.2 04/10/13 TRIG FAST",
    "IFSTTAR MUSC V9.1 02/10/13 TRIG FAST",
    "IFSTTAR MUSC V9.0 24/07/13 TRIG FAST",
    "IFSTTAR MUSC V8.8 18/06/13 TRIG FAST",
    "IFSTTAR MUSC V8.7 25/02/13 TRIG SLOW",
    "IFSTTAR MUSC V8.7 25/02/13 TRIG FAST",
    "IFSTTAR MUSC V8.6 28/01/13 TRIG FAST",
    "IFSTTAR MUSC V8.5 24/01/13 TRIG FAST",
    "8.4 06/11/12 TRIG FAST",
    "8.3 11/10/12 TRIG FAST",
    "8.2 12/07/12",
    "8.1 10/04/12",
    "8.0 03/04/12",
    "7.9 22/03/12",
    "7.8 19/03/12",
    "7.7 28/06/11",
    "7.6 24/06/11",
    "7.5 14/06/11",
    "7.4 31/05/11",
    "7.3 12/05/11",
    "7.2 03/03/11",
    "7.1 18/02/11",
    "7.0 24/01/11",
    "6.9 06/12/10",
    "6.8 18/11/10",
    "6.7 11/10/10",
    "6.6 29/09/10",
    "6.5 06/09/10",
    "6.4 02/08/10",
    "6.3 19/07/10",
    "6.2 08/07/10",
    "6.1 19/05/10",
    "6.0 30/03/10",
    "5.07 18/03/10",
    "5.06 01/03/10",
    "5.05 28/01/10",
    "5.04 13/01/10",
    "5.03 09/12/09",
    "5.02 08/12/09",
    "5.01 04/12/09",
    "5.00 03/12/09",
    "4.34 04/11/09",
    "4.31 02/09/09",
    "4.30 26/05/09",
    "4.29 18/06/09",
    "4.28 18/05/09",
    "4.27 30/04/09",
    "4.26 08/04/09",
    "4.25 06/04/09",
    "4.24 06/04/09",
    "4.23 24/02/09",
    "4.21 19/02/09",
    "4.20 16/02/09",
    "4.10 02/02/09",
    "4.09 27/01/09",
    "4.08 26/01/09",
    "4.07 21/01/09",
    "4.06 20/01/09",
    "4.05 19/01/09",
    "4.04 19/01/09",
    "4.02 14/01/09",
    "4.02 13/01/09",
    "4.01 17/12/08",
    ]


def is_seg2musc(stream: obspy.core.stream.Stream) -> bool:
    """
    determines whether a stream read from seg2 file is from MUSC or not
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

    if version_string in KNOWN_MUSC_VERSIONS:
        # safest control
        return True

    elif "MUSC" in version_string:
        return True

    elif "/" in version_string:
        # old versions before 24/01/2013 are assumed to be formatted as follow
        version_format_before_8_4 = "{version_number:f} {day:02d}/{month:02d}/{year:02d}"

        ans = parse.parse(
            version_format_before_8_4,
            version_string.split('TRIG FAST')[0].strip())

        if ans is None:
            # version string is formatted at expected => not a MUSC File
            return False

        version_date = datetime.datetime(
            year=2000 + ans["year"], month=ans["month"], day=ans["day"])
        version_number = ans['version_number']

        if version_number <= 8.4 and (version_date - datetime.datetime(2013, month=1, day=24)).days <= 0:
            # version string is at the right format, version number and time
            # aggree with the fact that the keyword MUSC is missing
            return True

        return False


def _fix_distance_units_in_seg2musc_header(stream: obspy.core.stream.Stream, verbose: bool=True) -> None:
    """
    UNITS are labeled as MILLIMETERS but correspond to METERS
    Fix it at the stream and trace levels
    """
    if stream.stats.seg2['UNITS'] == "MILLIMETERS":
        if verbose:
            warnings.warn('fix typo : UNITS changed from MILLIMETERS to METERS at the stream level')
        stream.stats.seg2['UNITS'] = "METERS"

    for trace in stream:

        # fix header typo at the trace level
        if trace.stats.seg2['UNITS'] == "MILLIMETERS":
            if verbose:
                warnings.warn('fix typo : UNITS changed from MILLIMETERS to METERS at the traces level')
            trace.stats.seg2['UNITS'] = "METERS"

    return None


def _convert_time_units_in_seg2musc_header(trace: obspy.core.trace.Trace, verbose: bool=True) -> None:
    """
    Time is expressed in milliseconds, but obspy assumes seconds => convert all times to seconds
    # => multiply sampling rate by 1000
    """
    if verbose:
        warnings.warn('convert SAMPLE_INTERVAL from milliseconds (MUSC) to seconds (OBSPY)')
    trace.stats.sampling_rate *= 1000.  # NOTE trace.stats.delta is devided by 1000 accordingly
    trace.stats.seg2["SAMPLE_INTERVAL"] = str(trace.stats.delta)  # preserve the str type

    delay = float(trace.stats.seg2["DELAY"]) / 1000.  # in seconds
    trace.stats.seg2["DELAY"] = str(delay)  # preserve the str type

    return None


def _extract_delta_source_laser_from_seg2musc_header(trace: obspy.core.trace.Trace):
    try:
        # extract the delta source laser (the source position is already corrected !!!)
        # this is just an informative field
        for note in trace.stats.seg2['NOTE']:
            if "DELTA_SOURCE_LASER" in note:
                trace.stats.delta_source_laser = \
                    float(note.split("DELTA_SOURCE_LASER")[-1]) / 1000.  # millimeters to meters
                break
        else:
            warnings.warn('field DELTA_SOURCE_LASER not found')

    except KeyError as err:
        warnings.warn(str(err))


def seg2musc_to_seg2obspy(stream: obspy.core.stream.Stream, verbose: bool=True) -> obspy.core.stream.Stream:
    """
    Extract information from seg2 header assuming that the file has been acquired by MUSC,
    Convert times from milliseconds to seconds (FIELDS WILL BE CORRECTED)

    NOTE: trace.stats.starttime must not be set to float(trace.stats.seg2["DELAY"])

    :param stream: the stream provided by obspy
    :param verbose: allow informative warnings
    """

    if not is_seg2musc(stream):
        raise Exception(
            'This data file does not look like '
            'a seg2 file from MUSC, is it?')

    # ============= MUSC DATA
    # fix header typo at the stream level
    _fix_distance_units_in_seg2musc_header(stream=stream, verbose=verbose)

    for trace in stream:
        trace.stats.station = "MUSC"

        # ==== defaults that exist only for MUSC files
        trace.stats.delta_source_laser = np.nan

        # ==== header conversions
        _convert_time_units_in_seg2musc_header(trace=trace, verbose=verbose)

        # ==== extract data from variable header
        extract_receiver_location(trace=trace)

        extract_source_location(trace=trace)

        _extract_delta_source_laser_from_seg2musc_header(trace=trace)

    return stream
