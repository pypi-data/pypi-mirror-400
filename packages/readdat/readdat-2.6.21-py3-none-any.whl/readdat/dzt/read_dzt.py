from readdat.dzt.dzt_file import read_dzt
from obspy.core import Trace, Stream, AttribDict, UTCDateTime


def read_dzt_as_stream(filename: str, **ignored) -> Stream:
    """
    :param filename: name of the dzt file to read
    :return stream: a stream object with the traces
    """

    header_dzt, data_dzt = read_dzt(filename=filename)

    stream = Stream()
    for nscan in data_dzt.nscan:
        trace_header = AttribDict(
            {"npts": header_dzt.nsamp,
             "sampling_rate": header_dzt.sps,
             "receiver_x": header_dzt.spm * nscan,
             "receiver_y": np.nan,
             "receiver_z": np.nan,
             "_format": "DZT",
             "dzt": AttribDict(header_dzt.__dict__),
            })

        trace = Trace(
            header=trace_header,
            data=data_dzt.data,
            )
        stream.append(trace)

    return stream
