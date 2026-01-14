import os
from readdat.read import read, Stream

HERE = os.path.dirname(__file__)
TUSFILE = os.path.join(HERE, "..", 'filesamples', 'tusmusfile.tus')
MUSFILE = os.path.join(HERE, "..", 'filesamples', 'tusmusfile.mus')


def test_tus_file_exist():
    assert os.path.isfile(TUSFILE)


def test_mus_file_exist():
    assert os.path.isfile(MUSFILE)


def test_read_tusmus():
    stream = read(TUSFILE, format="tusmus")
    assert isinstance(stream, Stream)

    assert len(stream) == 1
    for trace in stream:
        assert trace.stats.npts == 52080
        assert trace.stats.sampling_rate == 2500000.0
        assert str(trace.stats.starttime) == "1970-01-01T00:00:00.000000Z"
        assert hasattr(trace.stats, "tusmus")
