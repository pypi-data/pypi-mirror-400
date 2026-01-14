import os
import obspy
import pytest

from readdat.read import read
from readdat.test.test_filesamples import FILESAMPLES
from readdat.seg2.read_seg2 import _read_seg2_without_obspy_warning, autodetect_seg2_acquisition_system
from readdat.seg2.read_seg2musc import is_seg2musc
from readdat.seg2.read_seg2coda import is_seg2coda
from readdat.seg2.read_seg2ondulys import is_seg2ondulys
from readdat.seg2.read_seg2cdz import is_seg2cdz
from readdat.seg2.read_seg2tomag import is_seg2tomag
from readdat.seg2.read_seg2must import is_seg2must


from readdat.test.validate_seg2_contents import \
    validate_seg2file_content, \
    validate_seg2file_musc_content, \
    validate_seg2file_ondulys_content, \
    validate_seg2file_coda_content_naive, \
    validate_seg2file_coda_content_utc

# ==================== file existence tested in filesamples

# ==================== Format detection
def test_is_seg2musc():

    for key, filesample in FILESAMPLES.items():
        if not key.startswith('SEG2FILE'):
            continue

        if key == "SEG2FILE_CDZ":
            continue

        if key.startswith("SEG2FILE_MUSC"):
            assert is_seg2musc(_read_seg2_without_obspy_warning(filesample)), filesample
        else:
            print(filesample)
            assert not is_seg2musc(_read_seg2_without_obspy_warning(filesample)), filesample


def test_is_seg2coda():
    for key, filesample in FILESAMPLES.items():
        if not key.startswith('SEG2FILE'):
            continue

        if key == "SEG2FILE_CDZ":
            continue

        if key.startswith("SEG2FILE_CODA") or key=="SEG2FILE":
            assert is_seg2coda(_read_seg2_without_obspy_warning(filesample)), filesample
        else:
            assert not is_seg2coda(_read_seg2_without_obspy_warning(filesample)), filesample


def test_is_seg2ondulys():
    for key, filesample in FILESAMPLES.items():
        if not key.startswith('SEG2FILE'):
            continue

        if key == "SEG2FILE_CDZ":
            continue

        if key=="SEG2FILE_ONDULYS":
            assert is_seg2ondulys(_read_seg2_without_obspy_warning(filesample)), filesample
        else:
            assert not is_seg2ondulys(_read_seg2_without_obspy_warning(filesample)), filesample


def test_is_seg2tomag():
    for key, filesample in FILESAMPLES.items():
        if not key.startswith('SEG2FILE'):
            continue

        if key == "SEG2FILE_CDZ":
            continue

        if key == "SEG2FILE_TOMAG":
            assert is_seg2tomag(_read_seg2_without_obspy_warning(filesample)), filesample
        else:
            assert not is_seg2tomag(_read_seg2_without_obspy_warning(filesample)), filesample

# def test_is_seg2cdz():
#     for key, filesample in FILESAMPLES.items():
#         if not key.startswith('SEG2FILE'):
#             continue
#
#         if key == "SEG2FILE_CDZ":
#             assert is_seg2cdz(_read_seg2_without_obspy_warning(filesample)), filesample
#         else:
#             assert not is_seg2cdz(_read_seg2_without_obspy_warning(filesample)), filesample


def test_is_seg2must():
    for key, filesample in FILESAMPLES.items():
        if not key.startswith('SEG2FILE'):
            continue

        if key == "SEG2FILE_CDZ":
            continue

        if key == "SEG2FILE_MUST":
            assert is_seg2must(_read_seg2_without_obspy_warning(filesample)), filesample
        else:
            assert not is_seg2must(_read_seg2_without_obspy_warning(filesample)), filesample


def test_autodetect_seg2_acquisition_system():
    #with pytest.warns(UserWarning):
    #    # standard seg2 files are supposed to produce a user warning
    assert autodetect_seg2_acquisition_system(_read_seg2_without_obspy_warning(FILESAMPLES['SEG2FILE'])) == "CODA"
    assert autodetect_seg2_acquisition_system(_read_seg2_without_obspy_warning(FILESAMPLES['SEG2FILE_MUSC'])) == "MUSC"
    assert autodetect_seg2_acquisition_system(_read_seg2_without_obspy_warning(FILESAMPLES['SEG2FILE_MUSC1'])) == "MUSC"
    assert autodetect_seg2_acquisition_system(_read_seg2_without_obspy_warning(FILESAMPLES['SEG2FILE_ONDULYS'])) == "ONDULYS"
    assert autodetect_seg2_acquisition_system(_read_seg2_without_obspy_warning(FILESAMPLES['SEG2FILE_CODA'])) == "CODA"
    assert autodetect_seg2_acquisition_system(_read_seg2_without_obspy_warning(FILESAMPLES['SEG2FILE_CODA1'])) == "CODA"
    assert autodetect_seg2_acquisition_system(_read_seg2_without_obspy_warning(FILESAMPLES['SEG2FILE_TOMAG'])) == "TOMAG"
    # assert autodetect_seg2_acquisition_system(_read_seg2_without_obspy_warning(FILESAMPLES['SEG2FILE_CDZ'])) == "CDZ"
    assert autodetect_seg2_acquisition_system(_read_seg2_without_obspy_warning(FILESAMPLES['SEG2FILE_MUST'])) == "MUST"

# =================== File contents
def test_read_seg2():

    stream = read(FILESAMPLES['SEG2FILE'], format="SEG2", acquisition_system=None)
    validate_seg2file_content(stream)

def test_read_seg2musc():

    stream = read(FILESAMPLES['SEG2FILE_MUSC'], format="SEG2", acquisition_system="MUSC")
    validate_seg2file_musc_content(stream)

def test_read_seg2musc_auto():

    stream = read(FILESAMPLES['SEG2FILE_MUSC'], format="AUTO", acquisition_system="AUTO")
    validate_seg2file_musc_content(stream)


def test_read_seg2ondulys():

    with pytest.warns(UserWarning):
        stream = read(FILESAMPLES['SEG2FILE_ONDULYS'], format="SEG2", acquisition_system="ONDULYS")

    validate_seg2file_ondulys_content(stream)

def test_read_seg2ondulys_auto():

    with pytest.warns(UserWarning):
        stream = read(FILESAMPLES['SEG2FILE_ONDULYS'], format="AUTO", acquisition_system="AUTO")

    validate_seg2file_ondulys_content(stream)

def test_read_seg2coda_naive():

    stream = read(FILESAMPLES['SEG2FILE_CODA'], format="SEG2", acquisition_system="CODA")
    validate_seg2file_coda_content_naive(stream)

    stream = read(FILESAMPLES['SEG2FILE_CODA'], format="SEG2", acquisition_system="CODA", timezone=None)
    validate_seg2file_coda_content_naive(stream)

def test_read_seg2coda_utc():

    stream = read(FILESAMPLES['SEG2FILE_CODA'], format="SEG2", acquisition_system="CODA", timezone="Europe/Paris")
    validate_seg2file_coda_content_utc(stream)

def test_read_seg2coda_auto():

    stream = read(FILESAMPLES['SEG2FILE_CODA'], format="AUTO", acquisition_system="AUTO", timezone="Europe/Paris")
    validate_seg2file_coda_content_utc(stream)
