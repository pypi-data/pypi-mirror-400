import os
import numpy
from readdat.read import read, Stream

HERE = os.path.dirname(__file__)
MSEEDFILE = os.path.join(HERE, "..", 'filesamples', 'mseedfile.mseed')


def test_mseed_file_exist():
    assert os.path.isfile(MSEEDFILE)


def test_read_mseed():
    stream = read(MSEEDFILE, format="mseed")
    assert isinstance(stream, Stream)

    assert len(stream) == 3
    for trace in stream:
        assert trace.stats.npts == 4200
        assert trace.stats.sampling_rate == 1.
        assert str(trace.stats.starttime) == "2010-02-27T06:50:00.069539Z"
        assert hasattr(trace.stats, "mseed")
