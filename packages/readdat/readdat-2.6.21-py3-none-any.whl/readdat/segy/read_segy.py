#!/usr/bin/env python
from typing import Union, Optional, Literal
import warnings
import obspy
import numpy as np

from readdat.segy.read_segymusc import segymusc_to_obspy, is_segymusc
from obspy.io.segy.header import TRACE_HEADER_KEYS


def autodetect_segy_acquisition_system(stream: obspy.core.stream.Stream) \
        -> Union[None, Literal["MUSC"]]:

    if is_segymusc(stream=stream):
        acquisition_system = "MUSC"

    else:
        warnings.warn(f"could not detect acquisition system => using obspy defaults")
        acquisition_system = None

    return acquisition_system


def _extract_segy_coordinates_from_trace(trace):

    sz = \
        trace.stats['segy']['trace_header']['scalar_to_be_applied_to_all_elevations_and_depths']
    if sz == 0:
        sz = 1.0
    elif sz > 0:
        sz = float(sz)
    else:
        sz = -1. / float(sz)

    sxy = \
        trace.stats['segy']['trace_header']['scalar_to_be_applied_to_all_coordinates']
    if sxy == 0:
        sxy = 1.0
    elif sxy > 0:
        sxy = float(sxy)
    else:
        sxy = -1. / float(sxy)

    receiver_x = trace.stats['segy']['trace_header']['group_coordinate_x'] * sxy
    receiver_y = trace.stats['segy']['trace_header']['group_coordinate_y'] * sxy
    receiver_z = trace.stats['segy']['trace_header']['receiver_group_elevation'] * sz
    source_x = trace.stats['segy']['trace_header']['source_coordinate_x'] * sxy
    source_y = trace.stats['segy']['trace_header']['source_coordinate_y'] * sxy
    source_z = (+trace.stats['segy']['trace_header']['surface_elevation_at_source']
                            - trace.stats['segy']['trace_header']['source_depth_below_surface']) * sz

    # there is no nan in segy header, assume 0 means undefined
    if receiver_x != 0.: trace.stats.receiver_x = receiver_x
    if receiver_y != 0.: trace.stats.receiver_y = receiver_y
    if receiver_z != 0.: trace.stats.receiver_z = receiver_z
    if source_x != 0.:   trace.stats.source_x = source_x
    if source_y != 0.:   trace.stats.source_y = source_y
    if source_z != 0.:   trace.stats.source_z = source_z


def read_segy(
        filename: str,
        acquisition_system: Optional[Literal["AUTO", "MUSC"]],
        verbose: bool=False,
        **kwargs) -> obspy.core.stream.Stream:
    """
    :param filename: name of the segy file to read
    :param acquisition_system:
        "MUSC", ..., None = default
    :param kwargs: all other keyword arguments are passed to the default obspy.read function

    :return stream: an obspy.core.stream.Stream object, containing the traces
    """

    stream: obspy.core.stream.Stream
    trace: obspy.core.trace.Trace

    # ================ READ THE DATA USING OBSPY
    stream = obspy.core.read(filename, **kwargs)

    # for unpacking the LazyTraceHeader by looping over the header keys
    # TODO: must be tested
    for trace in stream:
        for key in TRACE_HEADER_KEYS:
            trace.stats['segy']['trace_header'][key] = \
                trace.stats['segy']['trace_header'][key]

    # ============ DEFAULTS ATTRIBUTES
    # set defaults coordinates, to be filled depending on header conventions
    for trace in stream:
        trace.stats.receiver_x = np.nan
        trace.stats.receiver_y = np.nan
        trace.stats.receiver_z = np.nan
        trace.stats.source_x = np.nan
        trace.stats.source_y = np.nan
        trace.stats.source_z = np.nan
        trace.stats.temperature_degc = np.nan
        trace.stats.relative_humidity_percent = np.nan

    for trace in stream:
        # TODO: must be tested
        _extract_segy_coordinates_from_trace(trace)

    # ============ FILL ATTRIBUTES FROM HEADERS

    # ===== SPECIFIC CASES
    if acquisition_system == "AUTO":
        acquisition_system = autodetect_segy_acquisition_system(stream=stream)

    if acquisition_system == "MUSC":
        # NO autodetect, if the user wants the obspy standard => acquisition_system=None
        stream = segymusc_to_obspy(stream=stream, verbose=verbose)

    elif acquisition_system is None:
        # obspy defautls
        pass

    else:
        raise ValueError(f'unknown acquisition_system {acquisition_system}, use MUSC or None')

    if verbose:
        print(filename)
        for key, val in stream.stats.segy.items():
            print(f'\t{key}: {val}')

        for trace in stream:
            print(trace)
            for key, val in trace.stats.segy.items():
                print(f'\t{key}: {val}')

    return stream



