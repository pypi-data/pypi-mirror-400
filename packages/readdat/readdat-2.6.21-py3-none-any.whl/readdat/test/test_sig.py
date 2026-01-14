import os
from readdat.read import read, Stream

HERE = os.path.dirname(__file__)
SIGFILE = os.path.join(HERE, "..", 'filesamples', 'sigfile.sig')


def test_seg2_file_exist():
    assert os.path.isfile(SIGFILE)


def test_read_seg2():
    stream = read(SIGFILE, format="SIG")
    assert isinstance(stream, Stream)

    assert len(stream) == 1
    for trace in stream:
        assert trace.stats.npts == 82000
        assert trace.stats.sampling_rate == 1000000.0
        assert str(trace.stats.starttime) == "1969-12-31T23:59:59.998000Z"
        assert hasattr(trace.stats, "sig")
