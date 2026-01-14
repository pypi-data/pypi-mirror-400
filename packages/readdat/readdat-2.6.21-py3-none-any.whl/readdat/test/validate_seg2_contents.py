import os
import numpy as np
from obspy import Stream

HERE = os.path.dirname(__file__)


def validate_seg2file_content(stream):
    assert isinstance(stream, Stream)
    assert hasattr(stream, "stats")
    assert hasattr(stream.stats, "seg2")

    assert len(stream) == 20, len(stream)
    for trace in stream:
        assert hasattr(trace.stats, "seg2")
        assert hasattr(trace.stats, "receiver_x")
        assert hasattr(trace.stats, "receiver_y")
        assert hasattr(trace.stats, "receiver_z")
        assert hasattr(trace.stats, "source_x")
        assert hasattr(trace.stats, "source_y")
        assert hasattr(trace.stats, "source_z")
        assert hasattr(trace.stats, "temperature_degc")
        assert hasattr(trace.stats, "relative_humidity_percent")
        assert trace.stats.npts == 8176
        assert trace.stats.sampling_rate == 2000000.
        assert str(trace.stats.starttime) == "2020-02-18T19:08:53.000000Z"


def validate_seg2file_musc_content(stream):
    assert isinstance(stream, Stream)
    # assert hasattr(stream, "stats")  # must work also to save/reload to su
    # assert hasattr(stream.stats, "seg2")  # must work also after save/reload to segy

    assert len(stream) == 192
    for ntrace, trace in enumerate(stream):
        # assert hasattr(trace.stats, "seg2")  # must work also after save/reload to segy

        assert trace.stats.station == "MUSC"
        assert trace.stats.npts == 14000
        assert trace.stats.sampling_rate == 10000000.0
        assert str(trace.stats.starttime) == "2022-03-25T12:11:46.000000Z"

        # RECEIVER LOCATIONS
        assert hasattr(trace.stats, "receiver_x")
        assert hasattr(trace.stats, "receiver_y")
        assert hasattr(trace.stats, "receiver_z")

        assert not np.isnan(trace.stats.receiver_x)
        assert not np.isnan(trace.stats.receiver_y)
        assert not np.isnan(trace.stats.receiver_z)

        # expected = np.asarray(trace.stats.seg2['RECEIVER_LOCATION'].split(), float)
        # assert trace.stats.receiver_x == expected[0]
        # assert trace.stats.receiver_y == expected[1]
        # assert trace.stats.receiver_z == expected[2]

        assert abs(trace.stats.receiver_x - (0.379 + ntrace * 0.001)) < 1e-15
        assert trace.stats.receiver_y == 0.4275
        assert trace.stats.receiver_z == 0.0

        # SOURCE LOCATIONS
        assert hasattr(trace.stats, "source_x")
        assert hasattr(trace.stats, "source_y")
        assert hasattr(trace.stats, "source_z")

        assert not np.isnan(trace.stats.source_x), trace.stats.source_x
        assert np.isnan(trace.stats.source_y), trace.stats.source_y
        assert np.isnan(trace.stats.source_z), trace.stats.source_z

        # expected = float(trace.stats.seg2['SOURCE_LOCATION'])
        # assert trace.stats.source_x == expected
        assert trace.stats.source_x == 0.370

        # DELTA LASER SOURCE
        assert hasattr(trace.stats, "delta_source_laser")
        # assert trace.stats.seg2['NOTE'][3] == "DELTA_SOURCE_LASER -10.75"
        assert trace.stats.delta_source_laser == -0.01075, trace.stats.delta_source_laser  # must be converted to meters for consistency with others

        # TEMPERATURE / HUMIDITY
        assert hasattr(trace.stats, "temperature_degc")
        assert hasattr(trace.stats, "relative_humidity_percent")

        assert np.isnan(trace.stats["temperature_degc"])
        assert np.isnan(trace.stats["relative_humidity_percent"])


def validate_seg2file_ondulys_content(stream):
    assert isinstance(stream, Stream)

    assert len(stream) == 44
    for ntrace, trace in enumerate(stream):
        assert hasattr(trace.stats, "seg2")

        assert trace.stats.station == "ONDULYS"
        assert trace.stats.npts == 2000
        assert trace.stats.delta == 6.024e-07
        assert trace.stats.seg2['ACQUISITION_DATE'] == "07/06/21"
        # verify that time issue has been fixed 21->2021
        assert str(trace.stats.starttime) == "2021-06-07T17:13:28.000000Z"

        # RECEIVER LOCATIONS
        assert hasattr(trace.stats, "receiver_x")
        assert hasattr(trace.stats, "receiver_y")
        assert hasattr(trace.stats, "receiver_z")

        assert not np.isnan(trace.stats.receiver_x)
        assert not np.isnan(trace.stats.receiver_y)
        assert not np.isnan(trace.stats.receiver_z)

        expected = np.asarray(trace.stats.seg2['RECEIVER_LOCATION'].split(), float)
        assert trace.stats.receiver_x == expected[0]
        assert trace.stats.receiver_y == expected[1]
        assert trace.stats.receiver_z == expected[2]

        assert abs(trace.stats.receiver_x - (0.025 + ntrace * 0.005)) < 1e-15
        assert trace.stats.receiver_y == 0.
        assert trace.stats.receiver_z == 0.

        # SOURCE LOCATIONS
        assert hasattr(trace.stats, "source_x")
        assert hasattr(trace.stats, "source_y")
        assert hasattr(trace.stats, "source_z")

        assert np.isnan(trace.stats.source_x)
        assert np.isnan(trace.stats.source_y)
        assert np.isnan(trace.stats.source_z)

        # TEMPERATURE / HUMIDITY
        assert hasattr(trace.stats, "temperature_degc")
        assert hasattr(trace.stats, "relative_humidity_percent")

        assert np.isnan(trace.stats["temperature_degc"])
        assert np.isnan(trace.stats["relative_humidity_percent"])


def validate_seg2file_coda_content_naive(stream):
    assert isinstance(stream, Stream)

    assert len(stream) == 50
    for ntrace, trace in enumerate(stream):
        assert hasattr(trace.stats, "seg2")

        assert trace.stats.station == "CODA"
        assert trace.stats.npts == 8176
        assert trace.stats.delta == 2e-7

        assert trace.stats.seg2['ACQUISITION_DATE'] == "01/07/2022", trace.stats.seg2['ACQUISITION_DATE']
        assert trace.stats.seg2['ACQUISITION_TIME'] == "16:17:45", trace.stats.seg2['ACQUISITION_TIME']

        # starttime must be from the NOTE fields, one different time per trace
        if ntrace == 0:
            assert trace.stats.seg2['NOTE'][2] == "DATE 01/07/2022", trace.stats.seg2['NOTE'][2]
            assert trace.stats.seg2['NOTE'][3] == "TIME 16:13:35", trace.stats.seg2['NOTE'][3]
            assert str(trace.stats.starttime) == "2022-07-01T16:13:35.000000Z", str(trace.stats.starttime)
        elif ntrace == 10:
            assert trace.stats.seg2['NOTE'][2] == "DATE 01/07/2022", trace.stats.seg2['NOTE'][2]
            assert trace.stats.seg2['NOTE'][3] == "TIME 16:14:26", trace.stats.seg2['NOTE'][3]
            assert str(trace.stats.starttime) == "2022-07-01T16:14:26.000000Z", str(trace.stats.starttime)

        # RECEIVER LOCATIONS
        assert hasattr(trace.stats, "receiver_x")
        assert hasattr(trace.stats, "receiver_y")
        assert hasattr(trace.stats, "receiver_z")

        assert not np.isnan(trace.stats.receiver_x)
        assert not np.isnan(trace.stats.receiver_y)
        assert not np.isnan(trace.stats.receiver_z)

        expected = np.asarray(trace.stats.seg2['RECEIVER_LOCATION'].split(), float)
        assert trace.stats.receiver_x == expected[0]
        assert trace.stats.receiver_y == expected[1]
        assert trace.stats.receiver_z == expected[2]

        assert abs(trace.stats.receiver_x - (0.0 + ntrace * 0.001)) < 1e-15
        assert trace.stats.receiver_y == 7.0  # ???
        assert trace.stats.receiver_z == 0.

        # SOURCE LOCATIONS
        assert hasattr(trace.stats, "source_x")
        assert hasattr(trace.stats, "source_y")
        assert hasattr(trace.stats, "source_z")

        assert np.isnan(trace.stats.source_x)
        assert np.isnan(trace.stats.source_y)
        assert np.isnan(trace.stats.source_z)

        # TEMPERATURE / HUMIDITY
        assert hasattr(trace.stats, "temperature_degc")
        assert hasattr(trace.stats, "relative_humidity_percent")

        assert np.isnan(trace.stats["temperature_degc"])
        assert np.isnan(trace.stats["relative_humidity_percent"])


def validate_seg2file_coda_content_utc(stream):
    assert isinstance(stream, Stream)

    assert len(stream) == 50
    for ntrace, trace in enumerate(stream):
        assert hasattr(trace.stats, "seg2")

        assert trace.stats.station == "CODA"
        assert trace.stats.npts == 8176
        assert trace.stats.delta == 2e-7

        assert trace.stats.seg2['ACQUISITION_DATE'] == "01/07/2022", trace.stats.seg2['ACQUISITION_DATE']
        assert trace.stats.seg2['ACQUISITION_TIME'] == "16:17:45", trace.stats.seg2['ACQUISITION_TIME']

        # starttime must be from the NOTE fields, one different time per trace
        if ntrace == 0:
            assert trace.stats.seg2['NOTE'][2] == "DATE 01/07/2022", trace.stats.seg2['NOTE'][2]
            assert trace.stats.seg2['NOTE'][3] == "TIME 16:13:35", trace.stats.seg2['NOTE'][3]
            assert str(trace.stats.starttime) == "2022-07-01T14:13:35.000000Z", \
                str(trace.stats.starttime) + "is not 2022-07-01T14:13:35.000000Z"
        elif ntrace == 10:
            assert trace.stats.seg2['NOTE'][2] == "DATE 01/07/2022", trace.stats.seg2['NOTE'][2]
            assert trace.stats.seg2['NOTE'][3] == "TIME 16:14:26", trace.stats.seg2['NOTE'][3]
            assert str(trace.stats.starttime) == "2022-07-01T14:14:26.000000Z", str(trace.stats.starttime)

        # RECEIVER LOCATIONS
        assert hasattr(trace.stats, "receiver_x")
        assert hasattr(trace.stats, "receiver_y")
        assert hasattr(trace.stats, "receiver_z")

        assert not np.isnan(trace.stats.receiver_x)
        assert not np.isnan(trace.stats.receiver_y)
        assert not np.isnan(trace.stats.receiver_z)

        expected = np.asarray(trace.stats.seg2['RECEIVER_LOCATION'].split(), float)
        assert trace.stats.receiver_x == expected[0]
        assert trace.stats.receiver_y == expected[1]
        assert trace.stats.receiver_z == expected[2]

        assert abs(trace.stats.receiver_x - (0.0 + ntrace * 0.001)) < 1e-15
        assert trace.stats.receiver_y == 7.0  # ???
        assert trace.stats.receiver_z == 0.

        # SOURCE LOCATIONS
        assert hasattr(trace.stats, "source_x")
        assert hasattr(trace.stats, "source_y")
        assert hasattr(trace.stats, "source_z")

        assert np.isnan(trace.stats.source_x)
        assert np.isnan(trace.stats.source_y)
        assert np.isnan(trace.stats.source_z)

        # TEMPERATURE / HUMIDITY
        assert hasattr(trace.stats, "temperature_degc")
        assert hasattr(trace.stats, "relative_humidity_percent")

        assert np.isnan(trace.stats["temperature_degc"])
        assert np.isnan(trace.stats["relative_humidity_percent"])

