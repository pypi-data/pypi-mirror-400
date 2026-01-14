import os, platform
import obspy
from readdat.seg2.read_seg2coda import extract_receiver_location  # it is the same for now


def guess_starttime_from_file(filename: str) -> obspy.core.UTCDateTime:
    """
    unfortunatly, the date was not stored in the files, try to get it from the file creation time
    the methods differs depending on the file system
    """
    file_stat = os.stat(filename)
    if platform.system() == 'Windows':
        creation_time = file_stat.st_ctime
    else:
        # linux
        if hasattr(file_stat, 'st_birthtime'):
            # if st_birthtime is available (recent ext4)
            creation_time = file_stat.st_birthtime
        else:
            # last modification time...
            creation_time = file_stat.st_mtime
    return obspy.core.UTCDateTime(creation_time)



def is_seg2cdz(stream: obspy.core.stream.Stream) -> bool:
    """
    tries to detect CDZ data files
    """
    ans = stream.stats['seg2']['COMPANY'] == "IFSTTAR_GER6AI"
    ans &= stream.stats['seg2']['ACQUISITION_DATE'] == "Unknown"
    ans &= stream.stats['seg2']['ACQUISITION_TIME'] == "Unknown"
    return ans


def seg2cdz_to_seg2obspy(stream: obspy.core.stream.Stream, verbose: bool=True) -> obspy.core.stream.Stream:
    """
    """
    for trace in stream:
        trace.stats.station = "CDZ"

        # coordinates
        extract_receiver_location(trace=trace)

    return stream
