from readdat.read import read
from readdat.su.write_obspymusc_as_sumusc import write_obspymusc_as_sumusc


from readdat.test.test_filesamples import FILESAMPLES
from readdat.test.validate_seg2_contents import \
    validate_seg2file_musc_content

from obspy.core.stream import Stream
import numpy as np
import os

HERE = os.path.dirname(__file__)
SEG2FILE_MUSC_INPUT = FILESAMPLES['SEG2FILE_MUSC']
SUFILE_MUSC_OUTPUT = os.path.join(HERE, "..", 'filesamples', 'conversions', 'seg2musc_to_sumusc', 'output.su')  # WILL BE REMOVED !!!


def test_seg2musc_to_sumusc_files():
    """
    make sure that the test files exits
    """
    assert os.path.isfile(SEG2FILE_MUSC_INPUT)

    if os.path.isfile(SUFILE_MUSC_OUTPUT):
        assert SUFILE_MUSC_OUTPUT.endswith('output.su')
        os.remove(SUFILE_MUSC_OUTPUT)
    assert not os.path.isfile(SUFILE_MUSC_OUTPUT)
    d = os.path.dirname(SUFILE_MUSC_OUTPUT)
    os.makedirs(d, exist_ok=True)
    assert os.path.isdir(d)


def test_seg2musc_to_sumusc():
    """
    compare a su file converted from seg2 by this program with file converted by another source (unknown)
    """

    original_stream = read(SEG2FILE_MUSC_INPUT, format="SEG2", acquisition_system="MUSC")
    validate_seg2file_musc_content(original_stream)

    write_obspymusc_as_sumusc(
        stream_in=original_stream,
        filename_out=SUFILE_MUSC_OUTPUT,
        endian="big")
    assert os.path.isfile(SUFILE_MUSC_OUTPUT)

    # test after
    stream = read(SUFILE_MUSC_OUTPUT, format="SU", acquisition_system="MUSC", endian="big")
    validate_seg2file_musc_content(stream)
