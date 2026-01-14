import os
from readdat.read import read, Stream

HERE = os.path.dirname(__file__)
SEGDFILE = os.path.join(HERE, "..", 'filesamples', 'segdfile.segd')
SEGDFILE30 = os.path.join(HERE, "..", 'filesamples', 'segdfile_rev3_0.segd')


def test_segd_file_exist():
    assert os.path.isfile(SEGDFILE)
    assert os.path.isfile(SEGDFILE30)


def test_read_segd():
    stream = read(SEGDFILE, format="SEGD")
    assert isinstance(stream, Stream)

    assert len(stream) == 36
    for trace in stream:
        assert trace.stats.npts == 2001
        assert trace.stats.sampling_rate == 1000.
        # assert str(trace.stats.starttime) == "2020-06-04T11:33:13.000000Z" <= time in the general header
        assert str(trace.stats.starttime) == "2020-06-04T11:33:30.094301Z"  # <= gps_time_of_acquisition, the right one
        assert hasattr(trace.stats, "segd")


def test_read_segd_rev3_0():
    stream = read(SEGDFILE30, format="SEGD")
    assert isinstance(stream, Stream)

    assert len(stream) == 46
    for trace in stream:
        assert trace.stats.npts == 4000
        assert trace.stats.sampling_rate == 2000.
        # assert str(trace.stats.starttime) == "2020-06-04T11:33:13.000000Z" <= time in the general header
        assert str(trace.stats.starttime) == "2022-09-08T14:37:41.303000Z"  # <= gps_time_of_acquisition, the right one
        assert hasattr(trace.stats, "segd")
