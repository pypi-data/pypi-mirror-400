import os
from readdat.read import read
from readdat.mat.read_mat import autodetect_mat_acquisition_system, is_mat_quantum
from scipy.io import loadmat


HERE = os.path.dirname(__file__)
MATQUANTUMFILE = os.path.join(HERE, "..", 'filesamples', 'matfile_quantum.mat')


def test_mat_files_exist():

    assert os.path.isfile(MATQUANTUMFILE)


def test_load_mat():
    loadmat(file_name=MATQUANTUMFILE, squeeze_me=True)


def test_is_mat_quantum():
    """Check if the file is a Quantum .mat file"""
    mat = loadmat(file_name=MATQUANTUMFILE, squeeze_me=True)
    assert is_mat_quantum(mat=mat)


def test_autodetect_mat_acquisition_system():
    mat = loadmat(file_name=MATQUANTUMFILE, squeeze_me=True)
    assert autodetect_mat_acquisition_system(mat=mat) == "QUANTUM"


def test_read_matquantum():

    stream = read(MATQUANTUMFILE, format="MAT", acquisition_system="QUANTUM")

    assert len(stream) == 4

    assert hasattr(stream, "stats")

    assert stream.stats["mat"]["__header__"] == b'MATLAB 5.0 MAT-file, Platform: PCWIN, Created on: 02/05/2023 13:38:49'
    assert stream.stats["mat"]["__version__"] == "1.0"
    assert stream.stats["mat"]["__globals__"] == []
    assert stream.stats["mat"]["File_Header"]["NumberOfChannels"] == "4"
    assert stream.stats["mat"]["File_Header"]["NumberOfSamplesPerBlock"] == " "
    assert stream.stats["mat"]["File_Header"]["SampleFrequency"] == "600,00"
    assert stream.stats["mat"]["File_Header"]["Date"] == "02/05/2023 13:38:50"
    assert stream.stats["mat"]["File_Header"]["Comment"] == " "
    assert stream.stats["mat"]["File_Header"]["NumberOfSamplesPerChannel"] == "209600"

    for ntrace, trace in enumerate(stream):
        assert trace.stats.sampling_rate == 600.
        assert str(trace.stats.starttime) == "2023-05-02T13:33:00.668333Z"
        assert str(trace.stats.endtime) == "2023-05-02T13:38:50.000000Z"  # the "date" field of the file
        assert trace.stats.channel == "%d" % (ntrace + 1)
        assert trace.stats.npts == 209600

        assert (trace.stats.mat['Unit'] ==
                ["s", "V", "kN", "V"][ntrace])

        assert (trace.stats.mat['SignalName'] ==
                ["Temps__1_-_Vitesse_de_mesure_standard",
                "Volt.Acc1",
                "Peson",
                "PB_BU_100"][ntrace])

        assert trace.stats.mat['MaxLevel'] == ['349,33168', "0,08788", "0,04782", "0,08919"][ntrace]
        assert trace.stats.mat['Correction'] == ['0', "0", "0", "0"][ntrace]
