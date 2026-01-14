import os
from readdat.bin_iris.bin_iris import read_bin, HeaderBin
from pandas import DataFrame

HERE = os.path.dirname(__file__)
BINIRISFILE = os.path.join(HERE, "..", 'filesamples', 'RDP_Wenner_2.bin')


def test_bin_iris_file_exist():
    assert os.path.isfile(BINIRISFILE)


def test_read_biniris():
    headerbin, dataframebin = read_bin(BINIRISFILE)
    assert isinstance(headerbin, HeaderBin)

    assert headerbin.version == 2147483650
    assert headerbin.typeofsyscal == 8
    assert headerbin.comments == 'T'
    assert headerbin.ColeCole == ()
    assert headerbin.ColeTau == ()
    assert headerbin.ColeM == ()
    assert headerbin.ColeRms == ()

    assert isinstance(dataframebin, DataFrame)

    assert all(dataframebin.Type_acq.array == 10)
    assert all(dataframebin.time.array == 500.)
    assert all(dataframebin.m_delay.array == 60.)

    # TODO add meaningful tests to check the content of the test file, values, number of items, data types...
    # assert all(dataframebin.TypeCpXyz.array == 1)
    # assert all(dataframebin.Ignore.array == 0)
    # assert all(dataframebin.g.array == 0)
    # assert all(dataframebin.ps.array == 0)
    # assert all(dataframebin.vp.array == 0)
    # assert all(dataframebin.In.array == 0)
    # assert all(dataframebin.rho.array == 0)
    # assert all(dataframebin.m.array == 0)
    # assert all(dataframebin.Deviation.array == 0)
    # assert all(dataframebin.Tm.array == 0)
    # assert all(dataframebin.Mx.array == 0)
    # assert all(dataframebin.Channel.array == 0)
    # assert all(dataframebin.NbChannel.array == 0)
    # assert all(dataframebin.Overload.array == 0)
    # assert all(dataframebin.Channel_Valide.array == 0)
    # assert all(dataframebin.Channel_Sync.array == 0)
    # assert all(dataframebin.GapFiller.array == 0)
    # assert all(dataframebin.Name.array == 0)
    # assert all(dataframebin.Latitude.array == 0)
    # assert all(dataframebin.Longitude.array == 0)
    # assert all(dataframebin.NbCren.array == 0)
    # assert all(dataframebin.RsCheck.array == 0)
    # assert all(dataframebin.TxVab.array == 0)
    # assert all(dataframebin.TxBat.array == 0)
    # assert all(dataframebin.RxBat.array == 0)
    # assert all(dataframebin.Temperature.array == 0)
    # assert all(dataframebin.seconds.array == 0)
    # assert all(dataframebin.minutes.array == 0)
    # assert all(dataframebin.hour.array == 0)
    # assert all(dataframebin.day.array == 0)
    # assert all(dataframebin.month.array == 0)
    # assert all(dataframebin.year.array == 0)

