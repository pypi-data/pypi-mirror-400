from typing import Optional, Literal
import warnings
import glob

import numpy as np

from obspy.core import read as obspyread, Stream, Trace
from readdat.seg2.read_seg2 import read_seg2
from readdat.segy.read_segy import read_segy
from readdat.su.read_su import read_su
from readdat.segd.read_segd2X import read_segd_rev2_X
from readdat.segd.read_segd30 import read_segd_rev3_0

from readdat.sig.read_sig import read_sig
from readdat.tusmus.read_tusmus import read_tus_mus
from readdat.dzt.read_dzt import read_dzt_as_stream
from readdat.mat.read_mat import read_mat
from readdat.arb.read_arb import is_arb, read_arb

 
def autodetect_file_format(filename: str) -> str:
    """
    Detection of file format based on the extension
    TODO: improve with quick reading of first bytes
    """
    extension = filename.split('.')[-1].upper()
    
    if filename.endswith('.seiscodstream.npz') or filename.endswith('.seispystream.npz'):
        format = "SEISCOD"
   
    elif extension in ["MSEED", "SEGY", "SU", "SEG2", "SEGD", "SIG", "TUS", "MUS", "DZT", "BIN", "NPZ", "MAT", "CSV", "ARB"]:
        format = extension

    elif extension == 'DAT':
        format = "SEG2"

    elif extension == 'SG2':
        format = "SEG2"

    elif extension == 'SGY':
        format = "SEGY"
        
    else:
        raise ValueError(f'cound not detect file format from file extension {filename=}')

    return format


def read(filename: str, 
         format: Literal[
             "AUTO", "MSEED", "SEGY", "SU", "SEG2",
             "SEGD", "SIG", "TUS", "DZT", "NPZ",
             "MAT", "SEISCOD", "CSV", "ARB"],
         timezone: Optional[Literal['Europe/Paris']] = None,
         **kwargs) -> Stream:
    """
    A layer on top of obspy.core.read to include
    some formats not handled by obspy or to accout for some specific header conventions

    :param filename: name of the file to read
    :param format: file format
           can be one of  "AUTO", "MSEED", "SEGY", "SU", "SEG2", "SEGD", "SIG",
           "TUS", "DZT", "NPZ", "MAT", "SEISCOD", "CSV", "ARB"

    :param timezone: 
            this field allows you to interpret the absolute dates as local time in the given timezone
            if timezone is None, then the times are interpreted as UTC+0 Universal times
    :param kwargs:
           all other arguments are passed as is to the sub-reading functions
    """
    # =================
    if format.lower() == "auto":
        format = autodetect_file_format(filename=filename)

    # =================
    if format.lower() == "mseed":
        if timezone is not None:
            raise NotImplementedError(timezone)

        stream = obspyread(
            filename, format=format, **kwargs)

    elif format.lower() == "segy":
        if timezone is not None:
            raise NotImplementedError(timezone)

        stream = read_segy(
            filename, format=format, **kwargs)

    elif format.lower() == "su":
        if timezone is not None:
            raise NotImplementedError(timezone)

        stream = read_su(
            filename, format=format, **kwargs)

    elif format.lower() == 'seg2':

        stream = read_seg2(
            filename, 
            timezone=timezone,
            **kwargs)

    elif format.lower() == "segd":
        if timezone is not None:
            raise NotImplementedError(timezone)

        try:
            # try revision 3.0 by default
            stream = read_segd_rev3_0(
                    filename=filename,
                    **kwargs)

        except AssertionError:
            # try revision 2X
            stream = read_segd_rev2_X(
                filename=filename,
                **kwargs)

    elif format.lower() == "sig":
        if timezone is not None:
            raise NotImplementedError(timezone)

        trace = read_sig(
            filename=filename,
            **kwargs)
        stream = Stream([trace])

    elif format.lower() in ['tus', 'mus', 'tusmus']:
        if timezone is not None:
            raise NotImplementedError(timezone)

        stream = read_tus_mus(
            tus_file=filename,
            **kwargs)

    elif format.lower() in ["dzt"]:
        if timezone is not None:
            raise NotImplementedError(timezone)

        stream = read_dzt_as_stream(filename=filename, **kwargs)

    elif format.lower() == "npz":
        if timezone is not None:
            raise NotImplementedError(timezone)

        # reload the simple npz file written by readdat.write
        stream = Stream()
        with np.load(filename) as loader:
            starttimes = loader['starttimes']
            deltas = loader['delta']
            for n_trace, (starttime, delta) in enumerate(zip(starttimes, deltas)):
                header = {"starttime": starttime, "delta": delta}
                trace = Trace(header=header)
                trace.data = loader[f'trace_{n_trace:03d}']
                stream.append(trace)

    elif format.lower() == "seiscod":
        if timezone is not None:
            raise NotImplementedError(timezone)
                
        assert filename.endswith('.seiscodstream.npz')
        from seiscod import Stream as SeiscodStream
        stream = SeiscodStream().from_npz(filename, additional_keys="*")
        for trace in stream:
            while sum([_ == "." for _ in trace.seedid]) < 3:
                # for seedid format to "<ntw>.<sta>.<loc>.<chnl>"
                # for conversion to obspy
                trace.seedid += "."
        stream = stream.to_obspy()

        # bugfix
        for trace in stream:
            trace.stats._format = "SEISCOD"

    elif format.lower() in ["mat"]:
        stream = read_mat(filename=filename, timezone=timezone, **kwargs)

    elif format.lower() in ['csv']:
        # data array
        dat = np.genfromtxt(filename, delimiter=" ", dtype=float, comments="#")
        if dat.ndim != 2:
            dat = np.genfromtxt(filename, delimiter=",", dtype=float, comments="#")
            assert dat.ndim == 2            
        # number of samples
        npts = dat.shape[0]

        # number of traces
        ntraces = dat.shape[1] - 1
        assert ntraces > 0
    
        # time_array on first column        
        time_array = dat[:, 0]

        # one trace per column
        data_array = dat[:, 1:]

        # verify sampling
        dts = time_array[1:] - time_array[:-1]
        dt = dts[0]
        assert dt > 0., f"{dt=} must be > 0"
        assert np.all(np.abs(dts - dt) < 0.001 * dt), f"the time array is not regular"

        # pack all traces in obspy objects
        stream = Stream()
        for trace_number in range(ntraces):
            trace = Trace(
                data=data_array[:, trace_number],
                header={
                    "starttime": time_array[0],
                    "delta": dt,
                    "_format": "CSV",
                    "csv": {"trace_number": trace_number},
                    },
                )
            stream.append(trace)

    elif format.lower() == "arb":
        if timezone is not None:
            raise NotImplementedError(timezone)


        stream = read_arb(
            filename, **kwargs)

    else:
        raise ValueError(f'unknwon file format {format=}')

    return stream


if __name__ == "__main__":
    for filename in glob.glob('./filesamples/*.*'):
        print(filename, autodetect_file_format(filename))

