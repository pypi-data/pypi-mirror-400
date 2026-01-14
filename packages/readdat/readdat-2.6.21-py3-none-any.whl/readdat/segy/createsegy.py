from typing import Optional
import sys

from obspy.core import Stream, Trace, AttribDict, UTCDateTime
from obspy.io.segy.segy import SEGYBinaryFileHeader, SEGYTraceHeader
from obspy.io.segy.header import DATA_SAMPLE_FORMAT_CODE_DTYPE

"""
some dummy functions to guide user on creating segy files from scratch
extracted from seiscod 3.0.1 tag 481c351
"""

ENDIAN: str = sys.byteorder  # "big" or "little"
TEXTUAL_FILE_HEADER: bytes = b' ' * 3200


def create_empty_segy_stream(
    endian: Optional[str] = None,
    data_encoding: int = 4,
    textual_file_header: bytes = TEXTUAL_FILE_HEADER,
    textual_file_header_encoding: str = "ASCII",
    job_identification_number: int = 0,
    line_number: int = 0,
    reel_number: int = 0,
    number_of_data_traces_per_ensemble: int = 1,
    number_of_auxiliary_traces_per_ensemble: int = 0,
    sample_interval_in_microseconds: int = 10000,
    sample_interval_in_microseconds_of_original_field_recording: int = 0,
    number_of_samples_per_data_trace: int = 10,
    number_of_samples_per_data_trace_for_original_field_recording: int = 0,
    data_sample_format_code: int = 1,
    ensemble_fold: int = 0,
    trace_sorting_code: int = 0,
    vertical_sum_code: int = 0,
    sweep_frequency_at_start: int = 0,
    sweep_frequency_at_end: int = 0,
    sweep_length: int = 0,
    sweep_type_code: int = 0,
    trace_number_of_sweep_channel: int = 0,
    sweep_trace_taper_length_in_ms_at_start: int = 0,
    sweep_trace_taper_length_in_ms_at_end: int = 0,
    taper_type: int = 0,
    correlated_data_traces: int = 0,
    binary_gain_recovered: int = 0,
    amplitude_recovery_method: int = 0,
    measurement_system: int = 0,
    impulse_signal_polarity: int = 0,
    vibratory_polarity_code: int = 0,
    seg_y_format_revision_number: int = 256,
    fixed_length_trace_flag: int = 0,
    number_of_3200_byte_ext_file_header_records_following: int = 0):

    """
    :param endian:
    :param data_encoding: code for data encoding
           1: 4 byte IBM floating point
           2: 4 byte Integer, two's complement
           3: 2 byte Integer, two's complement
           4: 4 byte Fixed point with gain
           5: 4 byte IEEE floating point
           8: 1 byte Integer, two's complement
    :param textual_file_header:  textual header, use "my text".encode('utf8')
    :param textual_file_header_encoding:

    # =================================== STREAM.STATS.BINARY_FILE_HEADER (obspy defaults)
    :param job_identification_number:
    :param line_number:
    :param reel_number:
    :param number_of_data_traces_per_ensemble:
    :param number_of_auxiliary_traces_per_ensemble:
    :param sample_interval_in_microseconds:
    :param sample_interval_in_microseconds_of_original_field_recording:
    :param number_of_samples_per_data_trace:
    :param number_of_samples_per_data_trace_for_original_field_recording:
    :param data_sample_format_code:
    :param ensemble_fold:
    :param trace_sorting_code:
            –1 = Other (should be explained in a user Extended Textual File Header stanza)
            0 = Unknown
            1 = As recorded (no sorting)
            2 = CDP ensemble
            3 = Single fold continuous profile
            4 = Horizontally stacked
            5 = Common source point
            6 = Common receiver point
            7 = Common offset point
            8 = Common mid-point
            9 = Common conversion point
    :param vertical_sum_code:
            1 = no sum,
            2 = two sum,
            ...,
            N = M–1 sum (M = 2 to 32,767)
    :param sweep_frequency_at_start: in Hz
    :param sweep_frequency_at_end: in Hz
    :param sweep_length: in milisecond
    :param sweep_type_code:
            1 = linear
            2 = parabolic
            3 = exponential
            4 = other
    :param trace_number_of_sweep_channel:
    :param sweep_trace_taper_length_in_ms_at_start:
    :param sweep_trace_taper_length_in_ms_at_end:
    :param taper_type:
    :param correlated_data_traces:
              1 = no
              2 = yes
    :param binary_gain_recovered:
    :param amplitude_recovery_method:
    :param measurement_system:
        If Location Data stanzas are included in the file, this
        entry would normally agree with the Location Data stanza. If there is a
        disagreement, the last Location Data stanza is the controlling authority. If units
        are mixed, e.g. meters on surface, feet in depth, then a Location Data stanza is
        mandatory.
          1 = Meters
          2 = Feet
    :param impulse_signal_polarity:
           1 = Increase in pressure or upward geophone case movement gives negative number on trace.
           2 = Increase in pressure or upward geophone case movement gives positive number on trace.
    :param vibratory_polarity_code:
    :param seg_y_format_revision_number:
    :param fixed_length_trace_flag:
    :param number_of_3200_byte_ext_file_header_records_following:
    :return:
    """

    # ========================================================
    # ========================================================
    # ========================================================

    """
    the goal of this function is to provide a tool to create a segy
    stream with complete list of attributes with their defaults values
    as defined in obspy
    """
    if endian is None:
        endian = ENDIAN
    assert endian in ['big', "little"], ValueError(endian)

    # ========== create the stream
    stsegy = Stream()
    stsegy.stats = AttribDict()

    # ========== set basis attributes
    stsegy.stats.endian = {"big": ">", "little": "<"}[endian]
    stsegy.stats.data_encoding = data_encoding
    stsegy.stats.textual_file_header = textual_file_header
    stsegy.stats.textual_file_header_encoding = textual_file_header_encoding

    # ========== fill and attach binary file header
    bf = SEGYBinaryFileHeader(endian={"big": ">", "little": "<"}[endian])
    bf.job_identification_number = job_identification_number
    bf.line_number = line_number
    bf.reel_number = reel_number
    bf.number_of_data_traces_per_ensemble = number_of_data_traces_per_ensemble
    bf.number_of_auxiliary_traces_per_ensemble = number_of_auxiliary_traces_per_ensemble
    bf.sample_interval_in_microseconds = sample_interval_in_microseconds
    bf.sample_interval_in_microseconds_of_original_field_recording = sample_interval_in_microseconds_of_original_field_recording
    bf.number_of_samples_per_data_trace = number_of_samples_per_data_trace
    bf.number_of_samples_per_data_trace_for_original_field_recording = number_of_samples_per_data_trace_for_original_field_recording
    bf.data_sample_format_code = data_sample_format_code
    bf.ensemble_fold = ensemble_fold
    bf.trace_sorting_code = trace_sorting_code
    bf.vertical_sum_code = vertical_sum_code
    bf.sweep_frequency_at_start = sweep_frequency_at_start
    bf.sweep_frequency_at_end = sweep_frequency_at_end
    bf.sweep_length = sweep_length
    bf.sweep_type_code = sweep_type_code
    bf.trace_number_of_sweep_channel = trace_number_of_sweep_channel
    bf.sweep_trace_taper_length_in_ms_at_start = sweep_trace_taper_length_in_ms_at_start
    bf.sweep_trace_taper_length_in_ms_at_end = sweep_trace_taper_length_in_ms_at_end
    bf.taper_type = taper_type
    bf.correlated_data_traces = correlated_data_traces
    bf.binary_gain_recovered = binary_gain_recovered
    bf.amplitude_recovery_method = amplitude_recovery_method
    bf.measurement_system = measurement_system
    bf.impulse_signal_polarity = impulse_signal_polarity
    bf.vibratory_polarity_code = vibratory_polarity_code
    bf.seg_y_format_revision_number = seg_y_format_revision_number
    bf.fixed_length_trace_flag = fixed_length_trace_flag
    bf.number_of_3200_byte_ext_file_header_records_following = number_of_3200_byte_ext_file_header_records_following

    stsegy.stats.binary_file_header = bf

    return stsegy


def create_empty_segy_trace(
    # tracl
    trace_sequence_number_within_line: int = 0,
    # tracr
    trace_sequence_number_within_segy_file: int = 0,
    # fldr
    original_field_record_number: int = 0,
    # tracf
    trace_number_within_the_original_field_record: int = 0,
    # ep
    energy_source_point_number: int = 0,
    # cdp
    ensemble_number: int = 0,
    # cdpt
    trace_number_within_the_ensemble: int = 0,
    # trid
        # –1 = Other
        # 0 = Unknown
        # 1 = Time domain seismic data
        # 2 = Dead
        # 3 = Dummy
        # 4 = Time break
        # 5 = Uphole
        # 6 = Sweep
        # 7 = Timing
        # 8 = Waterbreak
        # 9 = Near-field gun signature
        # 10 = Far-field gun signature
        # 11 = Seismic pressure sensor
        # 12 = Multicomponent seismic sensor – Vertical component
        # 13 = Multicomponent seismic sensor – Cross-line component
        # 14 = Multicomponent seismic sensor – In-line component
        # 15 = Rotated multicomponent seismic sensor – Vertical component
        # 16 = Rotated multicomponent seismic sensor – Transverse component
        # 17 = Rotated multicomponent seismic sensor – Radial component
        # 18 = Vibrator reaction mass
        # 19 = Vibrator baseplate
        # 20 = Vibrator estimated ground force
        # 21 = Vibrator reference
        # 22 = Time-velocity pairs
        # 23 = Time-depth pairs
        # 24 = Depth-velocity pairs
        # 25 = Depth domain seismic data
        # 26 = Gravity potential
        # 27 = Electric field – Vertical component
        # 28 = Electric field – Cross-line component
        # 29 = Electric field – In-line component
        # 30 = Rotated electric field – Vertical component
        # 31 = Rotated electric field – Transverse component
        # 32 = Rotated electric field – Radial component
        # 33 = Magnetic field – Vertical component
        # 34 = Magnetic field – Cross-line component
        # 35 = Magnetic field – In-line component
        # 36 = Rotated magnetic field – Vertical component
        # 37 = Rotated magnetic field – Transverse component
        # 38 = Rotated magnetic field – Radial component
        # 39 = Rotational sensor – Pitch
        # 40 = Rotational sensor – Roll
        # 41 = Rotational sensor – Yaw
        # 42 ... 255 = Reserved
        # 256 ... N = optional use (maximum N = 16.383)
        # N+16;384 = Interpolated i.e. not original; seismic trace.
    trace_identification_code: int = 0,
    # nvs
    number_of_vertically_summed_traces_yielding_this_trace: int = 0,
    # nhs
    number_of_horizontally_stacked_traces_yielding_this_trace: int = 0,
    # duse
         # 1 = production
         # 2 = test
    data_use: int = 0,
    # offset
    distance_from_center_of_the_source_point_to_the_center_of_the_receiver_group: int = 0,
    # gelev
    receiver_group_elevation: int = 0,
    # selev
    surface_elevation_at_source: int = 0,
    # sdepth
    source_depth_below_surface: int = 0,
    # gdel
    datum_elevation_at_receiver_group: int = 0,
    # sdel
    datum_elevation_at_source: int = 0,
    # swdep
    water_depth_at_source: int = 0,
    # gwdep
    water_depth_at_group: int = 0,
    # scalel
    scalar_to_be_applied_to_all_elevations_and_depths: int = 0,
    # scalco
    # Scalar = 1, +10, +100, +1000, or +10,000.
    # If positive, scalar is used as a multiplier;
    # if negative, scalar isused as divisor.
    scalar_to_be_applied_to_all_coordinates: int = 0,
    # sx
    source_coordinate_x: int = 0,
    # sy
    source_coordinate_y: int = 0,
    # gx
    group_coordinate_x: int = 0,
    # gy
    group_coordinate_y: int = 0,
    # counit
    #  1 = Length (meters or feet as specified in Binary File Header bytes)
    #  3 = Decimal degrees (preferred degree representation)
    coordinate_units: int = 0,
    # wevel
    weathering_velocity: int = 0,
    # swevel
    subweathering_velocity: int = 0,
    # sut
    uphole_time_at_source_in_ms: int = 0,
    # gut
    uphole_time_at_group_in_ms: int = 0,
    # sstat
    source_static_correction_in_ms: int = 0,
    # gstat
    group_static_correction_in_ms: int = 0,
    # tstat
    total_static_applied_in_ms: int = 0,
    # laga
    lag_time_A: int = 0,
    # lagb
    lag_time_B: int = 0,
    # delrt
    # delay_recording_time must be in milliseconds,
    # negative means => first sample before time 0, note suxwigb only reads the delrt of the first trace displayed
    delay_recording_time: int = 0,
    # muts
    mute_time_start_time_in_ms: int = 0,
    # mute
    mute_time_end_time_in_ms: int = 0,
    # ns
    number_of_samples_in_this_trace: int = 10,
    # dt
    #    WARNING ms means MICROSECOND !!!!
    sample_interval_in_ms_for_this_trace: int = 10000,
    # gain
    gain_type_of_field_instruments: int = 0,
    # igc
    instrument_gain_constant: int = 0,
    # igi
    instrument_early_or_initial_gain: int = 0,
    # corr
    #   0: no idea
    #   1: no
    #   2: yes
    correlated: int = 0,
    # sfs
    sweep_frequency_at_start: int = 0,
    # sfe
    sweep_frequency_at_end: int = 0,
    # slen  # here ms is MILISECONDS
    sweep_length_in_ms: int = 0,
    # styp
    # 1 = linear
    # 2 = parabolic
    # 3 = exponential
    # 4 = other
    sweep_type: int = 0,
    # stas
    sweep_trace_taper_length_at_start_in_ms: int = 0,
    # stae
    sweep_trace_taper_length_at_end_in_ms: int = 0,
    # tatyp
    taper_type: int = 0,
    # afilf
    alias_filter_frequency: int = 0,
    # afils
    alias_filter_slope: int = 0,
    # nofilf
    notch_filter_frequency: int = 0,
    # nofils
    notch_filter_slope: int = 0,
    # lcf
    low_cut_frequency: int = 0,
    # hcf
    high_cut_frequency: int = 0,
    # lcs
    low_cut_slope: int = 0,
    # hcs
    high_cut_slope: int = 0,
    # year
    year_data_recorded: int = 0,
    # day
    day_of_year: int = 0,
    # hour
    hour_of_day: int = 0,
    # minute
    minute_of_hour: int = 0,
    # sec
    second_of_minute: int = 0,
    # timbas
    #    1 = Local
    #    2 = GMT (Greenwich Mean Time)
    #    3 = Other, should be explained in a user defined stanza in the Extended
    #    Textual File Header
    #    4 = UTC (Coordinated Universal Time)
    #    5 = GPS (Global Positioning System Time)
    time_basis_code: int = 0,
    # trwf
    trace_weighting_factor: int = 0,
    # grnors
    geophone_group_number_of_roll_switch_position_one: int = 0,
    geophone_group_number_of_trace_number_one: int = 0,
    geophone_group_number_of_last_trace: int = 0,
    gap_size: int = 0,
    over_travel_associated_with_taper: int = 0,
    x_coordinate_of_ensemble_position_of_this_trace: int = 0,
    y_coordinate_of_ensemble_position_of_this_trace: int = 0,
    for_3d_poststack_data_this_field_is_for_in_line_number: int = 0,
    for_3d_poststack_data_this_field_is_for_cross_line_number: int = 0,
    shotpoint_number: int = 0,
    scalar_to_be_applied_to_the_shotpoint_number: int = 0,
    trace_value_measurement_unit: int = 0,
    transduction_constant_mantissa: int = 0,
    transduction_constant_exponent: int = 0,
    transduction_units: int = 0,
    device_trace_identifier: int = 0,
    scalar_to_be_applied_to_times: int = 0,
    # source_type_orientation
    #   0: unknown
    #   2: cross line
    #   3: in line
    #   4: impulsive vertical
    source_type_orientation: int = 0,
    source_energy_direction_mantissa: int = 0,
    source_energy_direction_exponent: int = 0,
    source_measurement_mantissa: int = 0,
    source_measurement_exponent: int = 0,
    source_measurement_unit: int = 0):

    """
    :param trace_sequence_number_within_line:
    :param trace_sequence_number_within_segy_file:
    :param original_field_record_number:
    :param trace_number_within_the_original_field_record:
    :param energy_source_point_number:
    :param ensemble_number:
    :param trace_number_within_the_ensemble:
    :param trace_identification_code:
    :param number_of_vertically_summed_traces_yielding_this_trace:
    :param number_of_horizontally_stacked_traces_yielding_this_trace:
    :param data_use:
    :param distance_from_center_of_the_source_point_to_the_center_of_the_receiver_group:
    :param receiver_group_elevation:
    :param surface_elevation_at_source:
    :param source_depth_below_surface:
    :param datum_elevation_at_receiver_group:
    :param datum_elevation_at_source:
    :param water_depth_at_source:
    :param water_depth_at_group:
    :param scalar_to_be_applied_to_all_elevations_and_depths:
    :param scalar_to_be_applied_to_all_coordinates:
    :param source_coordinate_x:
    :param source_coordinate_y:
    :param group_coordinate_x:
    :param group_coordinate_y:
    :param coordinate_units:
    :param weathering_velocity:
    :param subweathering_velocity:
    :param uphole_time_at_source_in_ms:
    :param uphole_time_at_group_in_ms:
    :param source_static_correction_in_ms:
    :param group_static_correction_in_ms:
    :param total_static_applied_in_ms:
    :param lag_time_A:
    :param lag_time_B:
    :param delay_recording_time:
    :param mute_time_start_time_in_ms:
    :param mute_time_end_time_in_ms:
    :param number_of_samples_in_this_trace:
    :param sample_interval_in_ms_for_this_trace:
    :param gain_type_of_field_instruments:
    :param instrument_gain_constant:
    :param instrument_early_or_initial_gain:
    :param correlated:
    :param sweep_frequency_at_start:
    :param sweep_frequency_at_end:
    :param sweep_length_in_ms:
    :param sweep_type:
    :param sweep_trace_taper_length_at_start_in_ms:
    :param sweep_trace_taper_length_at_end_in_ms:
    :param taper_type:
    :param alias_filter_frequency:
    :param alias_filter_slope:
    :param notch_filter_frequency:
    :param notch_filter_slope:
    :param low_cut_frequency:
    :param high_cut_frequency:
    :param low_cut_slope:
    :param high_cut_slope:
    :param year_data_recorded:
    :param day_of_year:
    :param hour_of_day:
    :param minute_of_hour:
    :param second_of_minute:
    :param time_basis_code:
    :param trace_weighting_factor:
    :param geophone_group_number_of_roll_switch_position_one:
    :param geophone_group_number_of_trace_number_one:
    :param geophone_group_number_of_last_trace:
    :param gap_size:
    :param over_travel_associated_with_taper:
    :param x_coordinate_of_ensemble_position_of_this_trace:
    :param y_coordinate_of_ensemble_position_of_this_trace:
    :param for_3d_poststack_data_this_field_is_for_in_line_number:
    :param for_3d_poststack_data_this_field_is_for_cross_line_number:
    :param shotpoint_number:
    :param scalar_to_be_applied_to_the_shotpoint_number:
    :param trace_value_measurement_unit:
    :param transduction_constant_mantissa:
    :param transduction_constant_exponent:
    :param transduction_units:
    :param device_trace_identifier:
    :param scalar_to_be_applied_to_times:
    :param source_type_orientation:
    :param source_energy_direction_mantissa:
    :param source_energy_direction_exponent:
    :param source_measurement_mantissa:
    :param source_measurement_exponent:
    :param source_measurement_unit:
    :return:
    """

    # ========== Create an empty trace
    trace = Trace()
    trace.stats.segy = AttribDict()
    
    # ========== create and fill a segy trace header
    thf = SEGYTraceHeader()
    
    thf.trace_sequence_number_within_line = trace_sequence_number_within_line
    thf.trace_sequence_number_within_segy_file = trace_sequence_number_within_segy_file
    thf.original_field_record_number = original_field_record_number
    thf.trace_number_within_the_original_field_record = trace_number_within_the_original_field_record
    thf.energy_source_point_number = energy_source_point_number
    thf.ensemble_number = ensemble_number
    thf.trace_number_within_the_ensemble = trace_number_within_the_ensemble
    thf.trace_identification_code = trace_identification_code
    thf.number_of_vertically_summed_traces_yielding_this_trace = \
        number_of_vertically_summed_traces_yielding_this_trace
    thf.number_of_horizontally_stacked_traces_yielding_this_trace = \
        number_of_horizontally_stacked_traces_yielding_this_trace
    thf.data_use = data_use
    thf.distance_from_center_of_the_source_point_to_the_center_of_the_receiver_group = \
        distance_from_center_of_the_source_point_to_the_center_of_the_receiver_group
    thf.receiver_group_elevation = receiver_group_elevation
    thf.surface_elevation_at_source = surface_elevation_at_source
    thf.source_depth_below_surface = source_depth_below_surface
    thf.datum_elevation_at_receiver_group = datum_elevation_at_receiver_group
    thf.datum_elevation_at_source = datum_elevation_at_source
    thf.water_depth_at_source = water_depth_at_source
    thf.water_depth_at_group = water_depth_at_group
    thf.scalar_to_be_applied_to_all_elevations_and_depths = \
        scalar_to_be_applied_to_all_elevations_and_depths
    thf.scalar_to_be_applied_to_all_coordinates = scalar_to_be_applied_to_all_coordinates
    thf.source_coordinate_x = source_coordinate_x
    thf.source_coordinate_y = source_coordinate_y
    thf.group_coordinate_x = group_coordinate_x
    thf.group_coordinate_y = group_coordinate_y
    thf.coordinate_units = coordinate_units
    thf.weathering_velocity = weathering_velocity
    thf.subweathering_velocity = subweathering_velocity
    thf.uphole_time_at_source_in_ms = uphole_time_at_source_in_ms
    thf.uphole_time_at_group_in_ms = uphole_time_at_group_in_ms
    thf.source_static_correction_in_ms = source_static_correction_in_ms
    thf.group_static_correction_in_ms = group_static_correction_in_ms
    thf.total_static_applied_in_ms = total_static_applied_in_ms
    thf.lag_time_A = lag_time_A
    thf.lag_time_B = lag_time_B
    thf.delay_recording_time = delay_recording_time
    thf.mute_time_start_time_in_ms = mute_time_start_time_in_ms
    thf.mute_time_end_time_in_ms = mute_time_end_time_in_ms
    thf.number_of_samples_in_this_trace = number_of_samples_in_this_trace
    thf.sample_interval_in_ms_for_this_trace = sample_interval_in_ms_for_this_trace
    thf.gain_type_of_field_instruments = gain_type_of_field_instruments
    thf.instrument_gain_constant = instrument_gain_constant
    thf.instrument_early_or_initial_gain = instrument_early_or_initial_gain
    thf.correlated = correlated
    thf.sweep_frequency_at_start = sweep_frequency_at_start
    thf.sweep_frequency_at_end = sweep_frequency_at_end
    thf.sweep_length_in_ms = sweep_length_in_ms
    thf.sweep_type = sweep_type
    thf.sweep_trace_taper_length_at_start_in_ms = sweep_trace_taper_length_at_start_in_ms
    thf.sweep_trace_taper_length_at_end_in_ms = sweep_trace_taper_length_at_end_in_ms
    thf.taper_type = taper_type
    thf.alias_filter_frequency = alias_filter_frequency
    thf.alias_filter_slope = alias_filter_slope
    thf.notch_filter_frequency = notch_filter_frequency
    thf.notch_filter_slope = notch_filter_slope
    thf.low_cut_frequency = low_cut_frequency
    thf.high_cut_frequency = high_cut_frequency
    thf.low_cut_slope = low_cut_slope
    thf.high_cut_slope = high_cut_slope
    thf.year_data_recorded = year_data_recorded
    thf.day_of_year = day_of_year
    thf.hour_of_day = hour_of_day
    thf.minute_of_hour = minute_of_hour
    thf.second_of_minute = second_of_minute
    thf.time_basis_code = time_basis_code
    thf.trace_weighting_factor = trace_weighting_factor
    thf.geophone_group_number_of_roll_switch_position_one = \
        geophone_group_number_of_roll_switch_position_one
    thf.geophone_group_number_of_trace_number_one = \
        geophone_group_number_of_trace_number_one
    thf.geophone_group_number_of_last_trace = \
        geophone_group_number_of_last_trace
    thf.gap_size = gap_size
    thf.over_travel_associated_with_taper = over_travel_associated_with_taper
    thf.x_coordinate_of_ensemble_position_of_this_trace = \
        x_coordinate_of_ensemble_position_of_this_trace
    thf.y_coordinate_of_ensemble_position_of_this_trace = \
        y_coordinate_of_ensemble_position_of_this_trace
    thf.for_3d_poststack_data_this_field_is_for_in_line_number = \
        for_3d_poststack_data_this_field_is_for_in_line_number
    thf.for_3d_poststack_data_this_field_is_for_cross_line_number = \
        for_3d_poststack_data_this_field_is_for_cross_line_number
    thf.shotpoint_number = shotpoint_number
    thf.scalar_to_be_applied_to_the_shotpoint_number = scalar_to_be_applied_to_the_shotpoint_number
    thf.trace_value_measurement_unit = trace_value_measurement_unit
    thf.transduction_constant_mantissa = transduction_constant_mantissa
    thf.transduction_constant_exponent = transduction_constant_exponent
    thf.transduction_units = transduction_units
    thf.device_trace_identifier = device_trace_identifier
    thf.scalar_to_be_applied_to_times = scalar_to_be_applied_to_times
    thf.source_type_orientation = source_type_orientation
    thf.source_energy_direction_mantissa = source_energy_direction_mantissa
    thf.source_energy_direction_exponent = source_energy_direction_exponent
    thf.source_measurement_mantissa = source_measurement_mantissa
    thf.source_measurement_exponent = source_measurement_exponent
    thf.source_measurement_unit = source_measurement_unit
    
    trace.stats.segy.trace_header = thf
    # WARNING : segy_write uses stats info before trace_header
    trace.stats.delta = trace.stats.segy.trace_header.sample_interval_in_ms_for_this_trace * 1e-6

    trace.stats.starttime = UTCDateTime(
        year=year_data_recorded if year_data_recorded else 1970,
        julday=day_of_year if day_of_year else 1,
        hour=hour_of_day,
        minute=minute_of_hour,
        second=second_of_minute)

    return trace


def create_segy_trace_from_trace(trace, **kwargs):
    # the attributes of stats.segy are not adjusted on tr.stats.delta and tr.stats.npts
    kwargs['sample_interval_in_ms_for_this_trace'] = int(trace.stats.delta * 1e6)
    kwargs['number_of_samples_in_this_trace'] = len(trace.data)

    assert trace.data.dtype in list(DATA_SAMPLE_FORMAT_CODE_DTYPE.values())

    new_trace = create_empty_segy_trace(**kwargs)
    new_trace.data = trace.data
    return new_trace


if __name__ == '__main__':
    import numpy as np

    # create an empty data stream
    st = create_empty_segy_stream(
        data_encoding=4,
        textual_file_header="dummy segy file".encode("UTF-8"),
        number_of_samples_per_data_trace=256)

    for n in range(10):
        # create an empty trace, with only the arguments that are not set to default
        tr = create_empty_segy_trace(
            trace_sequence_number_within_line=n,
            trace_identification_code=12,
            number_of_samples_in_this_trace=256,
            sample_interval_in_ms_for_this_trace=int(0.05 * 1e6),
            year_data_recorded=2020,
            day_of_year=1,
            hour_of_day=0,
            minute_of_hour=0,
            second_of_minute=0)
        # please do not modify tr.stats.delta from now

        # attach the data
        tr.data = np.asarray(
            np.random.randn(256) * 256,
            # please make sure dtype is consistent with data_encoding, here float32, because data encoding is 4
            dtype=np.float32)

        # add the trace to the stream
        st.append(tr)

    # write
    st.write('_testfile.segy', format="SEGY")
    st.write('_testfile.su', format="SU")

