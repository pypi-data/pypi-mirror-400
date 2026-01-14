#!/usr/bin/env python
import sys, glob, os
import struct
import numpy as np
import matplotlib.pyplot as plt
import obspy

"""
read a .sig acoustic data file 
after GageScope user's guide for version 3.1 : 
http://www.egmont.com.pl/gage/instrukcje/GageScope3.1.pdf
M.L. 12/01/2022
"""

SAMPLE_RATE_INDEX_HZ = {
    'GS V.3.00': {
         0: 1.0,      1: 2.0,     3: 10.,     4: 20.,
         5: 50.,      6: 100.,    7: 200.,    8: 500.,
         9: 1e3,     10: 2e3,    11: 5e3,    12: 10e3,
        13: 20e3,    14: 50e3,   15: 100e3,  16: 200e3,
        17: 500.e3,  18: 1.e6,   19: 2.e6,   20: 2.5e6,
        21: 5e6,     22: 10e6,   23: 12.5e6, 24: 20e6,
        25: 25e6,    26: 30e6,   27: 40e6,   28: 50e6,
        29: 60e6,    30: 65e6,   31: 80e6,   32: 100e6,
        33: 120e6,   34: 125e6,  35: 130e6,  36: 150e6,
        37: 200e6,   38: 250e6,  39: 300e6,  40: 500e6,
        41: 1e9,     42: 2e9,    43: 4e9,    44: 5e9,
        45: 8e9,     46: 10e9,
        }}

GAIN = {
    'GS V.3.00': {
        0: 10.,  1: 5.,  2: 2.,  3: 1.,
        4: 0.5,  5: 0.2, 6: 0.1,
        }}


PROBE_MULTIPLIER = {
    'GS V.3.00': {
        0: 1.,    1: 10.,   2: 20.,   3: 50.,
        4: 100.,  5: 200.,  6: 500.,  7: 1000.,
        }}


COUPLING = {
    'GS V.3.00': {
        1: "DC",
        2: "AC"}}


def read_sig(filename: str, zero_at_trigger_time: bool = True, **ignored) -> obspy.core.trace.Trace:
    """
    :param filename: name of the .sig file to read
    :param zero_at_trigger_time: set the 0 time at trigg time, otherwise time 0 corresponds to the first sample
    :return header, data:
        header : a dictionnary including the header names and values
        data : a numpy array with the data
    """
    with open(filename, 'rb') as fid:
        file_version = fid.read(14).decode('ascii').replace('\x00', '')

        crlf1 = struct.unpack('h', fid.read(2))[0]

        channel_name = fid.read(9).decode('ascii').replace('\x00', '')

        crlf2 = struct.unpack('h', fid.read(2))[0]

        comment = fid.read(256).decode('ascii').replace('\x00', '')

        crlf3, control_z, sample_rate_index, operation_mode = \
            struct.unpack('4h', fid.read(4 * 2))

        trigger_depth = struct.unpack('i', fid.read(4))[0]

        trigger_slope, trigger_source, trigger_level = \
            struct.unpack('3h', fid.read(3 * 2))

        sample_depth = struct.unpack('i', fid.read(4))[0]

        captured_gain_index, captured_coupling_index = \
            struct.unpack('2h', fid.read(2*2))

        current_mem_ptr, starting_address, trigger_address, ending_address = \
            struct.unpack('4i', fid.read(4 * 4))

        trigger_time, trigger_date = \
            struct.unpack('2H', fid.read(2 * 2))  # uINT16 ????

        trigger_coupling_index, trigger_gain_index, \
            probe_multiplier_index, inverted_data = \
            struct.unpack('4h', fid.read(4*2))

        board_type = struct.unpack('1H', fid.read(2))[0]  # ???

        resolution_12_bits, multiple_record, trigger_probe, \
            sample_offset, sample_resolution, sample_bits = \
            struct.unpack('6h', fid.read(6 * 2))

        extended_trigger_time = struct.unpack('I', fid.read(4))[0]

        imped_a, imped_b = struct.unpack('2h', fid.read(2*2))

        external_tbs, external_clock_rate = \
            struct.unpack('2f', fid.read(2 * 4))

        file_options = struct.unpack('i', fid.read(4))[0]

        version = struct.unpack('H', fid.read(2))[0]

        eeprom_options, trigger_hardware, record_depth = \
            struct.unpack('3I', fid.read(3 * 4))

        padding = fid.read(127)  # 0 filled section to complete the 512 byte header
        assert fid.tell() == 512

        # ============================== INDEX TO VALUES
        try:
            probe_multiplier = PROBE_MULTIPLIER[file_version][probe_multiplier_index]
            captured_gain = GAIN[file_version][captured_gain_index]
            trigger_gain = GAIN[file_version][trigger_gain_index]
            sampling_rate = SAMPLE_RATE_INDEX_HZ[file_version][sample_rate_index]
            captured_coupling = COUPLING[file_version][captured_coupling_index]
            trigger_coupling = COUPLING[file_version][trigger_coupling_index]

        except KeyError:
            raise NotImplementedError(
                "The tables did not include the "
                "requested parameters, please check : "
                f"{file_version=} "
                f"{probe_multiplier_index=} " 
                f"{captured_gain_index=} " 
                f"{sample_rate_index=} " 
                f"{captured_coupling_index=} ")

        # ============================== DATA SECTION
        # =========== check
        if probe_multiplier != 1:
            raise NotImplementedError(probe_multiplier)

        if inverted_data != 0:
            raise NotImplementedError(inverted_data)

        # =========== data type
        if resolution_12_bits == 0:
            # If the "resolution_12_bits" flag equals zero then the data is stored as unsigned 8 bit bytes.
            dtype = np.dtype('uint8')

        elif resolution_12_bits == 1:

            # if the "resolution_12_bits" flag equals one then the data is in the 12/16 bit format
            # which is stored as 16 bit signed integers (in the 12 bit mode the sampled data is sign extended
            # to 16 bits). For the 12 bit boards, the smallest value (-2047) represents –1V while the largest
            # value (+2047) represents +1V for the trigger level whereas the smallest and the largest values
            # represent +1V and –1V respectively for the captured data.
            dtype = np.dtype('int16')

        else:
            raise ValueError(resolution_12_bits)

        # =========== load data array
        if operation_mode == 2:
            # dual channel
            # The data is stored contiguously as a binary image of the saved
            # channel's signal storage space (one-half the memory depth).
            data = np.fromfile(fid, count=sample_depth * dtype.itemsize, dtype=dtype)

        elif operation_mode == 1:
            # single channel
            # The data is interleaved as a binary image of the complete signal
            # storage space for the single channel mode (full memory depth).
            raise NotImplementedError(operation_mode)

        else:
            raise ValueError(operation_mode)

        # =========== unpack data array, type conversion
        if resolution_12_bits == 0:
            raise NotImplementedError

        elif resolution_12_bits == 1:
            assert probe_multiplier == 1.0  # I am unsure what to do otherwise
            # data = np.array(-1. * data / captured_gain / 2047., np.dtype('float32'))
            data = np.array(-1. * data * captured_gain / 2047., np.dtype('float32'))

        if zero_at_trigger_time:
            starttime = -trigger_address / sampling_rate
        else:
            starttime = 0.

        # ========================= OUTPUT
        header = {
            "channel": channel_name,
            "npts": sample_depth,  # "sample_depth": sample_depth,
            "delta": 1. / sampling_rate,
            "starttime": starttime,
            "_format": "SIG",
            "sig": {
                "file_version": file_version,
                "crlf1": crlf1,
                "name": channel_name,
                "crlf2": crlf2,
                "comment": comment,
                "crlf3": crlf3,
                "control_z": control_z,
                "sample_depth": sample_depth,
                "sample_rate_index": sample_rate_index,
                "operation_mode": operation_mode,
                "trigger_depth": trigger_depth,
                "trigger_slope": trigger_slope,
                "trigger_source": trigger_source,
                "trigger_level": trigger_level,
                "captured_gain_index": captured_gain_index,
                "captured_gain": captured_gain,
                "captured_coupling_index": captured_coupling_index,
                "captured_coupling": captured_coupling,
                "current_mem_ptr": current_mem_ptr,
                "starting_address": starting_address,
                "trigger_address": trigger_address,
                "ending_address": ending_address,
                "trigger_time": trigger_time,
                "trigger_date": trigger_date,
                "trigger_coupling_index": trigger_coupling_index,
                "trigger_coupling": trigger_coupling,
                "trigger_gain_index": trigger_gain_index,
                "trigger_gain": trigger_gain,
                "probe_multiplier_index": probe_multiplier_index,
                "probe_multiplier": probe_multiplier,
                "inverted_data": inverted_data,
                "board_type": board_type,
                "resolution_12_bits": resolution_12_bits,
                "multiple_record": multiple_record,
                "trigger_probe": trigger_probe,
                "sample_offset": sample_offset,
                "sample_resolution": sample_resolution,
                "sample_bits": sample_bits,
                "extended_trigger_time": extended_trigger_time,
                "imped_a": imped_a,
                "imped_b": imped_b,
                "external_tbs": external_tbs,
                "external_clock_rate": external_clock_rate,
                "file_options": file_options,
                "version": version,
                "eeprom_options": eeprom_options,
                "trigger_hardware": trigger_hardware,
                "record_depth": record_depth,
                }}

        trace = obspy.core.trace.Trace(
            data=data,
            header=header
            )

        return trace
