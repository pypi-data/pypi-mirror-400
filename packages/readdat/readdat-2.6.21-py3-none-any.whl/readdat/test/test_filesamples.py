import os
from readdat.read import autodetect_file_format
from readdat.read import read
import obspy

HERE = os.path.dirname(__file__)
FILESAMPLES = {
    "SEG2FILE": os.path.join(HERE, "..", 'filesamples', 'seg2file.sg2'),
    "SEG2FILE_MUSC": os.path.join(HERE, "..", 'filesamples', 'seg2file_musc.sg2'),
    "SEG2FILE_MUSC1": os.path.join(HERE, "..", 'filesamples', 'seg2file_musc1.sg2'),
    "SEG2FILE_ONDULYS": os.path.join(HERE, "..", 'filesamples', 'seg2file_ondulys.sg2'),
    "SEG2FILE_CODA": os.path.join(HERE, "..", 'filesamples', 'seg2file_coda.sg2'),
    "SEG2FILE_CODA1": os.path.join(HERE, "..", 'filesamples', 'seg2file_coda1.sg2'),
    "SEG2FILE_MUST": os.path.join(HERE, "..", "filesamples", "seg2file_must.sg2"),
    # "SEG2FILE_CDZ": os.path.join(HERE, "..", "filesamples", "seg2file_cdz.sg2"),  # ignored => not tested on server
    "SEG2FILE_TOMAG": os.path.join(HERE, "..", "filesamples", "seg2file_tomag.sg2"),
    "TUSMUSFILE": os.path.join(HERE, "..", "filesamples", "tusmusfile.tus"),
    "MSEEDFILE": os.path.join(HERE, "..", "filesamples", "mseedfile.mseed"),
    "BINFILE": os.path.join(HERE, "..", "filesamples", "RDP_Wenner_2.bin"),
    "MATFILE_QUANTUM": os.path.join(HERE, "..", "filesamples", "matfile_quantum.mat"),
    "SIGFILE": os.path.join(HERE, "..", "filesamples", "sigfile.sig"),
    "SEGDFILE": os.path.join(HERE, "..", "filesamples", "segdfile.segd"),
    "SEGDFILE_30": os.path.join(HERE, "..", "filesamples", "segdfile_rev3_0.segd"),
    "SEISCODFILE": os.path.join(HERE, "..", "filesamples", "npzfile.seiscodstream.npz"),
    "CSVFILE": os.path.join(HERE, "..", "filesamples", "csvfile.csv"),
    "ARBFILE": os.path.join(HERE, "..", "filesamples", "arbfile.arb"),
    }


def test_filesamples_exist():
    for name, filename in FILESAMPLES.items():
        assert os.path.isfile(filename), filename


def test_autodetect_file_format():

    assert autodetect_file_format(FILESAMPLES['SEG2FILE']) == "SEG2"
    assert autodetect_file_format(FILESAMPLES['SEG2FILE_MUSC']) == "SEG2"
    assert autodetect_file_format(FILESAMPLES['SEG2FILE_MUSC1']) == "SEG2"
    assert autodetect_file_format(FILESAMPLES['SEG2FILE_ONDULYS']) == "SEG2"
    assert autodetect_file_format(FILESAMPLES['SEG2FILE_CODA']) == "SEG2"
    assert autodetect_file_format(FILESAMPLES['SEG2FILE_CODA1']) == "SEG2"
    # assert autodetect_file_format(FILESAMPLES['SEG2FILE_CDZ']) == "SEG2"
    assert autodetect_file_format(FILESAMPLES['SEG2FILE_TOMAG']) == "SEG2"
    assert autodetect_file_format(FILESAMPLES['SEG2FILE_MUST']) == "SEG2"
    assert autodetect_file_format(FILESAMPLES['TUSMUSFILE']) == "TUS"
    assert autodetect_file_format(FILESAMPLES['MSEEDFILE']) == "MSEED"
    assert autodetect_file_format(FILESAMPLES['BINFILE']) == "BIN"
    assert autodetect_file_format(FILESAMPLES['MATFILE_QUANTUM']) == "MAT"
    assert autodetect_file_format(FILESAMPLES['SIGFILE']) == "SIG"
    assert autodetect_file_format(FILESAMPLES['SEGDFILE']) == "SEGD"
    assert autodetect_file_format(FILESAMPLES['SEGDFILE_30']) == "SEGD"
    assert autodetect_file_format(FILESAMPLES['SEISCODFILE']) == "SEISCOD"
    assert autodetect_file_format(FILESAMPLES['CSVFILE']) == "CSV"
    assert autodetect_file_format(FILESAMPLES['ARBFILE']) == "ARB"


def test_read():
    for name, filename in FILESAMPLES.items():
        if name == "BINFILE":
            # not handled by read
            continue

        # AUTO Mode must work for all files
        st = read(filename, format="AUTO", acquisition_system="AUTO")

        assert isinstance(st, obspy.core.stream.Stream)

        assert len(st)
        for tr in st:
            # all filesamples have traces with at least few samples
            assert tr.stats.npts > 0

            # all traces are supposed to have a _format field
            assert hasattr(tr.stats, "_format")

            # check the name and case of the "_format" dectected,
            assert tr.stats._format == name.split('FILE')[0]
            assert tr.stats._format == tr.stats._format.upper()

            assert hasattr(tr.stats, tr.stats._format.lower())

            assert isinstance(
                    tr.stats[tr.stats._format.lower()],
                    (dict, obspy.core.AttribDict)), \
                        (filename, type(tr.stats[tr.stats._format.lower()]))

