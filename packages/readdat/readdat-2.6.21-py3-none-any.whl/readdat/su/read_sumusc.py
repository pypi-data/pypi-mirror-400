import warnings
import numpy as np
import obspy
from readdat.segy.write_obspymusc_as_segymusc import MUSC_CODE, DELTA_SOURCE_LASER_FACTOR


def is_sumusc(
        stream: obspy.core.stream.Stream) -> bool:
    """
    determines whether a stream read from su file is from MUSC or not
    :return answer: True or False
    """

    weathering_velocities = np.asarray([trace.stats.su['trace_header']['weathering_velocity'] for trace in stream])
    if (weathering_velocities != MUSC_CODE).any():
        # boolshit convention to say that this file was from MUSC
        return False

    return True



def _convert_time_units_in_sumusc_header(
        trace: obspy.core.trace.Trace, verbose: bool=True) -> None:
    """
    Time is expressed in milliseconds, but obspy assumes seconds => convert all times to seconds
    # => multiply sampling rate by 1000
    """
    if verbose:
        warnings.warn('convert SAMPLE_INTERVAL from nanoseconds (SU-MUSC) to seconds (OBSPY)')

    # the field sampling_intervale_in_ms_for_this_trace was supposed to receive microseconds (SEGY convention)
    # but for MUSC we saved nanoseconds for numerical reasons
    # when reading, obspy tries to convert microseconds to seconds with a x1e-6 factor
    # so we end up with nanoseconds x1e-6 = milliseconds => we need to convert to seconds
    # to meet the obspy convention
    trace.stats.sampling_rate *= 1e3  # NOTE trace.stats.delta is devided by 1000 accordingly

    return None


def _extract_receiver_location_from_sumusc_header(trace):
    try:
        # ========
        scalar_to_be_applied_to_all_coordinates = \
            trace.stats.su['trace_header']['scalar_to_be_applied_to_all_coordinates']

        if scalar_to_be_applied_to_all_coordinates < 0:
            k = -1. / scalar_to_be_applied_to_all_coordinates

        elif scalar_to_be_applied_to_all_coordinates > 0:
            k = scalar_to_be_applied_to_all_coordinates

        else:
            k = 1.
            warnings.warn(
                f'{scalar_to_be_applied_to_all_coordinates=}, '
                f'no correction applied')

        trace.stats.receiver_x = \
            trace.stats.su['trace_header']['group_coordinate_x'] * k / 1000.

        trace.stats.receiver_y = \
            trace.stats.su['trace_header']['group_coordinate_y'] * k / 1000.

        # ========
        scalar_to_be_applied_to_all_elevations_and_depths = \
            trace.stats.su['trace_header']['scalar_to_be_applied_to_all_elevations_and_depths']

        if scalar_to_be_applied_to_all_elevations_and_depths < 0:
            k = 1. / scalar_to_be_applied_to_all_elevations_and_depths

        elif scalar_to_be_applied_to_all_elevations_and_depths > 0:
            k = scalar_to_be_applied_to_all_elevations_and_depths

        else:
            k = 1.
            warnings.warn(
                f'{scalar_to_be_applied_to_all_elevations_and_depths=}, '
                f'no correction applied')

        trace.stats.receiver_z = \
            trace.stats.su['trace_header']['receiver_group_elevation'] * k / 1000.

    except KeyError as err:
        warnings.warn(str(err))


def _extract_source_location_from_sumusc_header(trace):
    try:
        # ========
        scalar_to_be_applied_to_all_coordinates = \
            trace.stats.su['trace_header']['scalar_to_be_applied_to_all_coordinates']

        if scalar_to_be_applied_to_all_coordinates < 0:
            k = -1. /scalar_to_be_applied_to_all_coordinates

        elif scalar_to_be_applied_to_all_coordinates > 0:
            k = scalar_to_be_applied_to_all_coordinates

        else:
            k = 1.
            warnings.warn(
                f'{scalar_to_be_applied_to_all_coordinates=}, '
                f'no correction applied')

        trace.stats.source_x = \
            trace.stats.su['trace_header']['source_coordinate_x'] * k / 1000.

    except KeyError as err:
        warnings.warn(str(err))


def _extract_delta_source_laser_from_header(trace):

    assert trace.stats.su['trace_header']['weathering_velocity'] == 12345  # (means MUSC data)
    return float(trace.stats.su['trace_header']['subweathering_velocity']) / DELTA_SOURCE_LASER_FACTOR  #


def sumusc_to_obspy(stream: obspy.core.stream.Stream, verbose: bool=True) -> obspy.core.stream.Stream:
    """
    Extract information from seg2 header assuming that the file has been acquired by MUSC,
    Convert times from milliseconds to seconds (FIELDS WILL BE CORRECTED)

    NOTE: trace.stats.starttime must not be set to float(trace.stats.seg2["DELAY"])

    :param stream: the stream provided by obspy
    :param verbose: allow informative warnings
    """

    if not is_sumusc(stream):
        raise Exception(
            'This data file does not look like '
            'a su file from MUSC, try debugging with acquisition_system=None to use obspy standards'
            'is it?')

    # ============= MUSC DATA

    for trace in stream:
        trace.stats.station = "MUSC"

        # ==== defaults that exist only form MUSC files
        trace.stats.delta_source_laser = \
            _extract_delta_source_laser_from_header(trace)

        # ==== header conversions
        _convert_time_units_in_sumusc_header(trace=trace, verbose=verbose)

        # ==== extract data from variable header
        _extract_receiver_location_from_sumusc_header(trace=trace)

        _extract_source_location_from_sumusc_header(trace=trace)

        # what else ?

    return stream

