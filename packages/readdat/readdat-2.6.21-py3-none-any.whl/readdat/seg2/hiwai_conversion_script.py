#!/usr/bin/env python3

"""
A python script to convert seg2 files into su files
WARNING : this script should not be used for other datasets

M. Lehujeur 24/08/2022, Univ Gustave Eiffel
"""


import os
import sys
import obspy
import datetime
import parse
import numpy as np
from obspy.io.segy.segy import SEGYBinaryFileHeader, SEGYTraceHeader
import warnings


ENDIAN = sys.byteorder

HELP = f"""Script to convert seg2 (Hiwai project) to su (nanoseconds, tenth-of-meters)
Install:
    python3 -m pip install numpy parse obspy 

Usage : 
    python3 {os.path.basename(__file__)} filename_in.seg2 filename_out.su [endianess<big|little>, default={ENDIAN}]
"""


def read_seg2(filename_in: str) -> obspy.core.stream.Stream:
    """
    convert times from miliseconds to seconds
    :param filename_in: name of the file to read in (seg2 from MUSC),
        time convention in milliseconds
        distances in meters!!
    :return stream: the loaded data
    """

    # verify input file name and existence
    assert os.path.isfile(filename_in), IOError(filename_in)
    assert filename_in.lower().endswith(".sg2") or filename_in.lower().endswith(".SG2"), \
        IOError(f'{filename_in} has no seg2 extension')

    # read the data, ignore obspy warning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        stream = obspy.read(filename_in, format="SEG2")

    # convert times to seconds
    for trace in stream:
        trace.stats.sampling_rate *= 1000.  # NOTE trace.stats.delta is divided by 1000 accordingly
        trace.stats.seg2["SAMPLE_INTERVAL"] = str(trace.stats.delta)  # preserve the str type
        delay = +float(trace.stats.seg2["DELAY"]) / 1000.
        trace.stats.seg2["DELAY"] = str(delay)  # preserve the str type

    return stream


def write_su(stream_in: obspy.core.stream.Stream, filename_out: str, endian=ENDIAN):
    """
    write su file with times in nanoseconds, distances in tenth of millimeters
    :param stream_in: loaded data from read_seg2 above, time in seconds, distances in meters
    :param filename_out: file to write, overwriten if exists !!
    :param endian: str, endianess of the data big or little
    """

    assert filename_out.lower().endswith('.su'), \
        IOError(f'{filename_out} must end with .su')

    # get sampling, make sure it is consistent between traces
    sampling_interval_sec = stream_in[0].stats.delta
    number_of_samples = stream_in[0].stats.npts
    for trace in stream_in[1:]:
        assert trace.stats.delta == sampling_interval_sec, "inconsistent sampling?"
        assert trace.stats.npts == number_of_samples, "inconsistent sampling?"

    sample_interval_in_nanoseconds = int(round(sampling_interval_sec * 1e9))

    # ========== create the stream
    stsegy = obspy.core.stream.Stream()
    stsegy.stats = obspy.core.AttribDict()

    # ========== set basis attributes
    stsegy.stats.endian = endian
    stsegy.stats.data_encoding = 4
    stsegy.stats.textual_file_header = b' ' * 3200
    stsegy.stats.textual_file_header_encoding = "ASCII"

    # ========== fill and attach binary file header
    bf = SEGYBinaryFileHeader(endian=endian)
    bf.number_of_data_traces_per_ensemble = len(stream_in)
    # WARNING !!! sample_interval should be in microseconds,
    # but for musc data, we here must use nanoseconds
    bf.sample_interval_in_microseconds = sample_interval_in_nanoseconds
    bf.number_of_samples_per_data_trace = number_of_samples
    bf.measurement_system = 1
    stsegy.stats.binary_file_header = bf
    stream_out = stsegy

    for n_trace, trace_in in enumerate(stream_in):
        sample_interval_in_nanoseconds = int(round(trace_in.stats.delta * 1e9))
        delay_recording_time_in_microseconds = \
            +int(round(float(trace_in.stats.seg2['DELAY']) * 1e6))

        assert trace_in.data.dtype == np.dtype('float32')

        # get the acquisition time from the seg2 header
        acquisition_date = parse.parse(
            "{day:02d}/{month:02d}/{year:d}",
            trace_in.stats.seg2['ACQUISITION_DATE'])
        acquisition_time = parse.parse(
            "{hour:02d}:{minute:02d}:{second:02d}",
            trace_in.stats.seg2['ACQUISITION_TIME'])

        if acquisition_date is None:
            raise Exception

        if acquisition_date['year'] < 100:
            # year on two digits : 19 => 2019 (obspy fails in this case)
            acquisition_date['year'] += 2000

        acquisition_timetuple = datetime.datetime(
            year=acquisition_date['year'],
            month=acquisition_date['month'],
            day=acquisition_date['day'],
            hour=acquisition_time['hour'],
            minute=acquisition_time['minute'],
            second=acquisition_time['second'],
            ).timetuple()

        # receiver coordinates, in meters
        receiver_x, receiver_y, _ = \
            np.asarray(trace_in.stats.seg2['RECEIVER_LOCATION'].split(), float)

        # source coordinates, in meters
        source_x = float(trace_in.stats.seg2['SOURCE_LOCATION'])

        # ========== Create an empty trace
        trace_out = obspy.core.Trace()
        trace_out.stats.segy = obspy.core.AttribDict()

        # ========== create and fill a segy trace header
        thf = SEGYTraceHeader()

        thf.trace_sequence_number_within_line = n_trace + 1
        thf.trace_sequence_number_within_segy_file = n_trace + 1
        thf.trace_number_within_the_original_field_record = n_trace + 1
        thf.energy_source_point_number = 1  # ML : unsure
        thf.data_use = 1  # production
        thf.scalar_to_be_applied_to_all_elevations_and_depths = 1  # means that coordinates are multiplied by 10
        thf.scalar_to_be_applied_to_all_coordinates = 1  # means that coordinates are multiplied by 10
        thf.source_coordinate_x = int(round(source_x * 1000 * 10))  # in tenth of millimeters
        thf.group_coordinate_x = int(round(receiver_x * 1000 * 10))  # in tenth of millimeters
        thf.group_coordinate_y = int(round(receiver_y * 1000 * 10))  # in tenth of millimeters
        thf.coordinate_units = 1  # meters
        # WARNING !!! delay_recording_time should be in milliseconds,
        # but for musc data, we must use microseconds, no choice
        thf.delay_recording_time = delay_recording_time_in_microseconds
        thf.number_of_samples_in_this_trace = trace_in.stats.npts
        # WARNING !!! sample_interval should be in microseconds,
        # but for musc data, we must use nanoseconds, no choice
        thf.sample_interval_in_ms_for_this_trace = sample_interval_in_nanoseconds
        thf.gain_type_of_field_instruments = 1  # ML unsure
        thf.correlated = 1  # means no
        thf.year_data_recorded = acquisition_timetuple.tm_year
        thf.day_of_year = acquisition_timetuple.tm_yday  # julian day
        thf.hour_of_day = acquisition_timetuple.tm_hour
        thf.minute_of_hour = acquisition_timetuple.tm_min
        thf.second_of_minute = acquisition_timetuple.tm_sec
        thf.time_basis_code = 1  # = local

        trace_out.stats.segy.trace_header = thf
        # WARNING : segy_write uses stats info before trace_header :
        # reproduce the segy header info here (as for standard convention in seconds)
        trace_out.stats.delta = \
            trace_out.stats.segy.trace_header.sample_interval_in_ms_for_this_trace * 1e-6

        trace_out.stats.starttime = obspy.core.UTCDateTime(
            year=thf.year_data_recorded,
            julday=thf.day_of_year,
            hour=thf.hour_of_day,
            minute=thf.minute_of_hour,
            second=thf.second_of_minute,
            )
        # Do not modify trace_out.stats.delta after this point

        # attach the data
        trace_out.data = np.asarray(
            trace_in.data,
            # make sure dtype is consistent with data_encoding,
            # here float32, because data encoding is 4
            dtype=np.float32)

        # add the trace to the stream
        stream_out.append(trace_out)

    for trace in stream_out:
        trace.stats._format = "SU"
        trace.stats.su = trace.stats.segy

    print(f'writing {filename_out}')
    stream_out.write(
        filename=filename_out,
        format="SU",
        byteorder={"big": ">", "little": "<"}[endian],
        )


if __name__ == '__main__':

    endian = ENDIAN

    if len(sys.argv) in [3, 4]:
        filename_in = sys.argv[1]
        filename_out = sys.argv[2]
        if len(sys.argv) == 4:
            endian = sys.argv[3]
            assert endian in ['big', 'little'], ValueError('endian must be big or little')

    else:
        print(HELP)
        sys.exit(1)

    stream_in = read_seg2(filename_in=filename_in)
    write_su(stream_in=stream_in, filename_out=filename_out, endian=endian)
