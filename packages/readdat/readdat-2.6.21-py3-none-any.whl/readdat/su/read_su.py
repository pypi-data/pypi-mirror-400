#!/usr/bin/env python
from typing import Union, Optional, Literal
import warnings
import obspy
import numpy as np

from readdat.su.read_sumusc import sumusc_to_obspy, is_sumusc


def autodetect_su_acquisition_system(stream: obspy.core.stream.Stream) \
        -> Union[None, Literal["MUSC"]]:

    if is_sumusc(stream=stream):
        acquisition_system = "MUSC"

    else:
        warnings.warn(f"could not detect acquisition system => using obspy defaults")
        acquisition_system = None

    return acquisition_system


def read_su(
        filename: str,
        acquisition_system: Optional[Literal["AUTO", "MUSC"]],
        verbose: bool=False,
        **kwargs) -> obspy.core.stream.Stream:
    """
    :param filename: name of the segy file to read
    :param acquisition_system:
        "MUSC", None = default
    :param kwargs: all other keyword arguments are passed to the default obspy.read function

    :return stream: an obspy.core.stream.Stream object, containing the traces
    """

    stream: obspy.core.stream.Stream
    trace: obspy.core.trace.Trace

    # ================ READ THE DATA USING OBSPY
    print(kwargs, filename)

    stream = obspy.core.read(filename, **kwargs)

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

    # ============ FILL ATTRIBUTES FROM HEADERS

    # ===== SPECIFIC CASES
    if acquisition_system == "AUTO":
        acquisition_system = autodetect_su_acquisition_system(stream=stream)

    if acquisition_system == "MUSC":
        # NO autodetect, if the user wants the obspy standard => acquisition_system=None
        stream = sumusc_to_obspy(stream=stream, verbose=verbose)

    elif acquisition_system == "CODA":
        raise NotImplementedError('use defaults from obspy')

    elif acquisition_system == "ONDULYS":
        raise NotImplementedError('use defaults from obspy')

    elif acquisition_system is None:
        # obspy defautls
        pass

    else:
        raise ValueError(f'unknown acquisition_system {acquisition_system}, use MUSC, CODA, ONDULYS or None')

    if verbose:
        print(filename)
        for key, val in stream.stats.segy.items():
            print(f'\t{key}: {val}')

        for trace in stream:
            print(trace)
            for key, val in trace.stats.segy.items():
                print(f'\t{key}: {val}')

    return stream


