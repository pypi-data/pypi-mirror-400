"""
convert seg2 from SEG2MUSC to SUMUSC or SEGYMUSC
"""
import os
import datetime
import parse
import numpy as np
import obspy

from readdat.segy.createsegy import \
    create_empty_segy_stream, create_empty_segy_trace, ENDIAN

MUSC_CODE = 12345
DELTA_SOURCE_LASER_FACTOR = 100000  # the delta source laser must be stored as integers, it is provided in meters

def _write_obspymusc_as_sumusc_or_segymusc(
        stream_in: obspy.core.stream.Stream, filename_out: str,
        format_out: str, endian: str = ENDIAN):

    """
    stream_in has been converted from SEG2MUSC (time in milliseconds) to OBSPY (time in seconds)
    Save it as SEGYMUSC or SUMUSC  (time in nanoseconds)

    :param stream_in: a stream of traces converted from seg2musc to obspy with option acquisition_system="MUSC"
    :param filename_out: name of the su file to write out
    :param endian: endianess "big" or "little", default is the endianess of the current system
    """
    assert endian in ['big', "little"], ValueError(endian)
    for trace in stream_in:
        if not trace.stats.station == "MUSC":
            # it is important to load the data using acquisition_system="MUSC"
            # to convert the time fields
            raise Exception(
                'please mention acquisition_system="MUSC" in the readdat.read function')

    if format_out not in ['SU', 'SEGY']:
        raise NotImplementedError('this function can only write SU or SEGY files for now')

    if os.path.isfile(filename_out):
        assert input(f'{filename_out} exists already, overwrite ? y/[n]') == "y"

    textual_file_header = f"C MUSC DATA CONVERTED FROM SEG2 TO {format_out}\n"

    # delta_source_laser = np.unique([tr.stats.delta_source_laser for tr in stream_in])
    # if len(delta_source_laser) == 1:
    #     textual_file_header += f"C delta_source_laser={delta_source_laser[0]}\n"
    # else:
    #     warnings.warn('MORE THAN ONE DELTA_LASER_SOURCE FOUND IN THIS FILE => Not Stored in Textual Header')

    sampling_interval_sec = stream_in[0].stats.delta
    number_of_samples = stream_in[0].stats.npts
    for trace in stream_in[1:]:
        assert trace.stats.delta == sampling_interval_sec, "inconsistent sampling detected"
        assert trace.stats.npts == number_of_samples, "inconsistent sampling detected"

    sample_interval_in_nanoseconds = int(round(sampling_interval_sec * 1e9))

    # CREATE AN EMPTY STREAM FOR OUTPUT, FILL THE FILE HEADER
    stream_out = create_empty_segy_stream(
        endian=endian,
        # :param data_encoding: code for data encoding
        #        1: 4 byte IBM floating point
        #        2: 4 byte Integer, two's complement
        #        3: 2 byte Integer, two's complement
        #        4: 4 byte Fixed point with gain
        #        5: 4 byte IEEE floating point
        #        8: 1 byte Integer, two's complement
        data_encoding=4,
        textual_file_header=textual_file_header.encode('ASCII'),
        textual_file_header_encoding="ASCII",
        # job_identification_number=0,
        # line_number=0,
        # reel_number=0,
        number_of_data_traces_per_ensemble=len(stream_in),
        # number_of_auxiliary_traces_per_ensemble=0,
        # WARNING !!! sample_interval should be in microseconds, but for musc data, we must use nanoseconds, no choice
        sample_interval_in_microseconds=sample_interval_in_nanoseconds,  # !!!!!!!!!!
        # sample_interval_in_microseconds_of_original_field_recording=0,
        number_of_samples_per_data_trace=number_of_samples,
        # number_of_samples_per_data_trace_for_original_field_recording=0,
        # data_sample_format_code=1,
        # ensemble_fold=0,
        # trace_sorting_code=0,
        # vertical_sum_code=0,
        # sweep_frequency_at_start=0,
        # sweep_frequency_at_end=0,
        # sweep_length=0,
        # sweep_type_code=0,
        # trace_number_of_sweep_channel=0,
        # sweep_trace_taper_length_in_ms_at_start=0,
        # sweep_trace_taper_length_in_ms_at_end=0,
        # taper_type=0,
        # correlated_data_traces=0,
        # binary_gain_recovered=0,
        # amplitude_recovery_method=0,
        measurement_system=1,  # 1 = meters  # !!!!!!!!!!!!!!! #
        # impulse_signal_polarity=0,
        # vibratory_polarity_code=0,
        # seg_y_format_revision_number=256,
        # fixed_length_trace_flag=0,
        # number_of_3200_byte_ext_file_header_records_following=0,
        )

    # LOOP OVER TRACES
    for n_trace, trace_in in enumerate(stream_in):
        sample_interval_in_nanoseconds = int(round(trace_in.stats.delta * 1e9))
        delay_recording_time_in_microseconds = +int(round(float(trace_in.stats.seg2['DELAY']) * 1e6))

        assert trace_in.data.dtype == np.dtype('float32'), "type error"

        acquisition_date = parse.parse("{day:02d}/{month:02d}/{year:d}", trace_in.stats.seg2['ACQUISITION_DATE'])
        acquisition_time = parse.parse("{hour:02d}:{minute:02d}:{second:02d}", trace_in.stats.seg2['ACQUISITION_TIME'])

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

        trace_out = create_empty_segy_trace(
            # tracl
            trace_sequence_number_within_line=n_trace + 1,
            # tracr
            trace_sequence_number_within_segy_file=n_trace + 1,
            # # fldr
            # original_field_record_number=: int = 0,
            # # tracf
            trace_number_within_the_original_field_record=n_trace + 1,
            # # ep
            energy_source_point_number=1,  # ML : unsure, only in the test example or always??
            # # cdp
            # ensemble_number: int = 0,
            # # cdpt
            # trace_number_within_the_ensemble: int = 0,
            # # trid
            #     # –1 = Other
            #     # 0 = Unknown
            #     # 1 = Time domain seismic data
            #     # 2 = Dead
            #     # 3 = Dummy
            #     # 4 = Time break
            #     # 5 = Uphole
            #     # 6 = Sweep
            #     # 7 = Timing
            #     # 8 = Waterbreak
            #     # 9 = Near-field gun signature
            #     # 10 = Far-field gun signature
            #     # 11 = Seismic pressure sensor
            #     # 12 = Multicomponent seismic sensor – Vertical component
            #     # 13 = Multicomponent seismic sensor – Cross-line component
            #     # 14 = Multicomponent seismic sensor – In-line component
            #     # 15 = Rotated multicomponent seismic sensor – Vertical component
            #     # 16 = Rotated multicomponent seismic sensor – Transverse component
            #     # 17 = Rotated multicomponent seismic sensor – Radial component
            #     # 18 = Vibrator reaction mass
            #     # 19 = Vibrator baseplate
            #     # 20 = Vibrator estimated ground force
            #     # 21 = Vibrator reference
            #     # 22 = Time-velocity pairs
            #     # 23 = Time-depth pairs
            #     # 24 = Depth-velocity pairs
            #     # 25 = Depth domain seismic data
            #     # 26 = Gravity potential
            #     # 27 = Electric field – Vertical component
            #     # 28 = Electric field – Cross-line component
            #     # 29 = Electric field – In-line component
            #     # 30 = Rotated electric field – Vertical component
            #     # 31 = Rotated electric field – Transverse component
            #     # 32 = Rotated electric field – Radial component
            #     # 33 = Magnetic field – Vertical component
            #     # 34 = Magnetic field – Cross-line component
            #     # 35 = Magnetic field – In-line component
            #     # 36 = Rotated magnetic field – Vertical component
            #     # 37 = Rotated magnetic field – Transverse component
            #     # 38 = Rotated magnetic field – Radial component
            #     # 39 = Rotational sensor – Pitch
            #     # 40 = Rotational sensor – Roll
            #     # 41 = Rotational sensor – Yaw
            #     # 42 ... 255 = Reserved
            #     # 256 ... N = optional use (maximum N = 16.383)
            #     # N+16;384 = Interpolated i.e. not original; seismic trace.
            # trace_identification_code: int = 0,
            # # nvs
            # number_of_vertically_summed_traces_yielding_this_trace: int = 0,
            # # nhs
            # number_of_horizontally_stacked_traces_yielding_this_trace: int = 0,
            # # duse
            #      # 1 = production
            #      # 2 = test
            data_use=1,
            # offset
            # distance_from_center_of_the_source_point_to_the_center_of_the_receiver_group: int = 0,
            # # gelev
            receiver_group_elevation=int(round(trace_in.stats.receiver_z * 1000 * 10)),
            # # selev
            # surface_elevation_at_source: int = 0,
            # # sdepth
            # source_depth_below_surface: int = 0,
            # # gdel
            # datum_elevation_at_receiver_group: int = 0,
            # # sdel
            # datum_elevation_at_source: int = 0,
            # # swdep
            # water_depth_at_source: int = 0,
            # # gwdep
            # water_depth_at_group: int = 0,
            # # scalel
            scalar_to_be_applied_to_all_elevations_and_depths=-10,  # means elevations are *10 => must be divieded by 10
            # # scalco
            scalar_to_be_applied_to_all_coordinates=-10,  # means coordinates are *10 => must be divided by 10
            # # sx
            source_coordinate_x=int(round(trace_in.stats.source_x * 1000 * 10)),  # in tenth of millimeters
            # # sy
            # source_coordinate_y: int = 0,
            # # gx
            group_coordinate_x=int(round(trace_in.stats.receiver_x * 1000 * 10)),  # in tenth of millimeters
            # # gy
            group_coordinate_y=int(round(trace_in.stats.receiver_y * 1000 * 10)),  # in tenth of millimeters
            # # counit
            # #  1 = Length (meters or feet as specified in Binary File Header bytes)
            # #  3 = Decimal degrees (preferred degree representation)
            coordinate_units=1,
            # # wevel
            weathering_velocity=MUSC_CODE,  # TRICK TO MENTION THAT THIS IS A FILE FROM MUSC
            # # swevel
            subweathering_velocity=int(trace.stats.delta_source_laser * DELTA_SOURCE_LASER_FACTOR),  # HIDE THE DELTA_LASER_SOURCE THERE
            # # sut
            # uphole_time_at_source_in_ms: int = 0,
            # # gut
            # uphole_time_at_group_in_ms: int = 0,
            # # sstat
            # source_static_correction_in_ms: int = 0,
            # # gstat
            # group_static_correction_in_ms: int = 0,
            # # tstat
            # total_static_applied_in_ms: int = 0,
            # # laga
            # lag_time_A: int = 0,
            # # lagb
            # lag_time_B: int = 0,
            # delrt
            # WARNING !!! delay_recording_time should be in milliseconds,
            # but for musc data, we must use microseconds, no choice
            delay_recording_time=delay_recording_time_in_microseconds,
            # # muts
            # mute_time_start_time_in_ms: int = 0,
            # # mute
            # mute_time_end_time_in_ms: int = 0,
            # # ns
            number_of_samples_in_this_trace=trace_in.stats.npts,
            # # dt
            # WARNING !!! sample_interval should be in microseconds,
            # but for musc data, we must use nanoseconds, no choice
            sample_interval_in_ms_for_this_trace=sample_interval_in_nanoseconds,  # WARNING !!
            # # gain
            gain_type_of_field_instruments=1,  # trace_in.stats.seg2["DESCALING_FACTOR"]),  # ML UNSURE???
            # # igc
            # instrument_gain_constant: int = 0,
            # # igi
            # instrument_early_or_initial_gain: int = 0,
            # # corr
            # #   0: no idea
            # #   1: no
            # #   2: yes
            correlated=1,
            # # sfs
            # sweep_frequency_at_start: int = 0,
            # # sfe
            # sweep_frequency_at_end: int = 0,
            # # slen  # here ms is MILISECONDS
            # sweep_length_in_ms: int = 0,
            # # styp
            # # 1 = linear
            # # 2 = parabolic
            # # 3 = exponential
            # # 4 = other
            # sweep_type: int = 0,
            # # stas
            # sweep_trace_taper_length_at_start_in_ms: int = 0,
            # # stae
            # sweep_trace_taper_length_at_end_in_ms: int = 0,
            # # tatyp
            # taper_type: int = 0,
            # # afilf
            # alias_filter_frequency: int = 0,
            # # afils
            # alias_filter_slope: int = 0,
            # # nofilf
            # notch_filter_frequency: int = 0,
            # # nofils
            # notch_filter_slope: int = 0,
            # # lcf
            # low_cut_frequency: int = 0,
            # # hcf
            # high_cut_frequency: int = 0,
            # # lcs
            # low_cut_slope: int = 0,
            # # hcs
            # high_cut_slope: int = 0,
            # year
            year_data_recorded=acquisition_timetuple.tm_year,
            # day
            day_of_year=acquisition_timetuple.tm_yday,  # julian day
            # hour
            hour_of_day=acquisition_timetuple.tm_hour,
            # minute
            minute_of_hour=acquisition_timetuple.tm_min,
            # sec
            second_of_minute=acquisition_timetuple.tm_sec,
            # # timbas
            # #    1 = Local
            # #    2 = GMT (Greenwich Mean Time)
            # #    3 = Other, should be explained in a user defined stanza in the Extended
            # #    Textual File Header
            # #    4 = UTC (Coordinated Universal Time)
            # #    5 = GPS (Global Positioning System Time)
            time_basis_code=1,
            # # trwf
            # trace_weighting_factor: int = 0,
            # # grnors
            # geophone_group_number_of_roll_switch_position_one: int = 0,
            # geophone_group_number_of_trace_number_one: int = 0,
            # geophone_group_number_of_last_trace: int = 0,
            # gap_size: int = 0,
            # over_travel_associated_with_taper: int = 0,
            # x_coordinate_of_ensemble_position_of_this_trace: int = 0,
            # y_coordinate_of_ensemble_position_of_this_trace: int = 0,
            # for_3d_poststack_data_this_field_is_for_in_line_number: int = 0,
            # for_3d_poststack_data_this_field_is_for_cross_line_number: int = 0,
            # shotpoint_number: int = 0,
            # scalar_to_be_applied_to_the_shotpoint_number: int = 0,
            # trace_value_measurement_unit: int = 0,
            # transduction_constant_mantissa: int = 0,
            # transduction_constant_exponent: int = 0,
            # transduction_units: int = 0,
            # device_trace_identifier: int = 0,
            # scalar_to_be_applied_to_times: int = 0,
            # # source_type_orientation
            # #   0: unknown
            # #   2: cross line
            # #   3: in line
            # #   4: impulsive vertical
            # source_type_orientation: int = 0,
            # source_energy_direction_mantissa: int = 0,
            # source_energy_direction_exponent: int = 0,
            # source_measurement_mantissa: int = 0,
            # source_measurement_exponent: int = 0,
            # source_measurement_unit: int = 0
            )
        # please do not modify trace_out.stats.delta from now

        # attach the data to the current trace
        trace_out.data = np.asarray(
            trace_in.data,
            # please make sure dtype is consistent with data_encoding, here float32, because data encoding is 4
            dtype=np.float32)

        # add the trace to the output stream
        stream_out.append(trace_out)

    # del stream_out.stats.segy
    for trace in stream_out:
        if format_out == "SU":
            trace.stats._format = "SU"
            trace.stats.su = trace.stats.segy
        elif format_out == "SEGY":
            trace.stats._format = "SEGY"
        else:
            raise Exception(format_out)

    print(f'writing {filename_out}')
    stream_out.write(
        filename=filename_out,
        format=format_out,
        byteorder={"big": ">", "little": "<"}[endian],  # <= otherwise obspy ignore endian and use the system byteorder
        )
    return stream_out


def write_obspymusc_as_segymusc(
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
        endian=endian, format_out="SEGY")
