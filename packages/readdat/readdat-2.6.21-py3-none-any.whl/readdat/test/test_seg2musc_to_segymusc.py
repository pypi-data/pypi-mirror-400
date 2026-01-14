import os

import obspy

from readdat.read import read
from readdat.segy.write_obspymusc_as_segymusc import write_obspymusc_as_segymusc
from readdat.segy.read_segymusc import is_segymusc

from readdat.test.test_filesamples import FILESAMPLES
from readdat.test.validate_seg2_contents import validate_seg2file_musc_content


HERE = os.path.dirname(__file__)
SEG2FILE_MUSC_INPUT = FILESAMPLES['SEG2FILE_MUSC']
SEGYFILE_MUSC_OUTPUT = os.path.join(
    HERE, "..", 'filesamples', 'conversions',
    'seg2musc_to_segymusc', 'output.segy')  # WILL BE REMOVED !!!


def test_seg2musc_to_segymusc_files_exist():
    """
    make sure that the test files exits
    """
    assert os.path.isfile(SEG2FILE_MUSC_INPUT)

    if os.path.isfile(SEGYFILE_MUSC_OUTPUT):
        assert SEGYFILE_MUSC_OUTPUT.endswith('output.segy')
        os.remove(SEGYFILE_MUSC_OUTPUT)
    assert not os.path.isfile(SEGYFILE_MUSC_OUTPUT)

    d = os.path.dirname(SEGYFILE_MUSC_OUTPUT)
    os.makedirs(d, exist_ok=True)
    assert os.path.isdir(d)


def test_seg2musc_to_segymusc():
    """
    compare a su file converted from seg2 by this program with file converted by another source (unknown)
    """

    original_stream = read(SEG2FILE_MUSC_INPUT, format="SEG2", acquisition_system="MUSC")
    validate_seg2file_musc_content(original_stream)

    write_obspymusc_as_segymusc(
        stream_in=original_stream,
        filename_out=SEGYFILE_MUSC_OUTPUT,
        endian="big")
    assert os.path.isfile(SEGYFILE_MUSC_OUTPUT)

    assert is_segymusc(stream=obspy.core.read(SEGYFILE_MUSC_OUTPUT))

    # test after
    stream = read(SEGYFILE_MUSC_OUTPUT, format="SEGY", acquisition_system="MUSC", endian="big")
    validate_seg2file_musc_content(stream)
