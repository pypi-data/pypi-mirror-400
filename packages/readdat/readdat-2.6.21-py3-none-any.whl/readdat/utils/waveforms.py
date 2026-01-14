from types import FunctionType
import numpy as np
import matplotlib.pyplot as plt
import obspy
from matplotlib.collections import LineCollection


def repr_stream(stream: obspy.core.stream.Stream) -> str:
    """
    Generate a string representation of a stream object
    Minimalist version of seispy.stream.Stream.__repr__
    """
    ans = f'# ##################### stream : {len(stream)} traces\n'

    if hasattr(stream, 'stats'):
        ans += f'# ==================== stream.stats\n'
        for key, val in stream.stats.items():
            if isinstance(val, obspy.core.AttribDict):
                for kkey, vval in val.items():
                    ans += f"    stream.stats['{key}']['{kkey}']={vval}\n"
            else:
                ans += f"  stream.stats['{key}']={val}\n"
    
    for ntrace, trace in enumerate(stream):
        ans += f'# ==================== stream[{ntrace}]\n'
        ans += f'  # ------------------ stream[{ntrace}].stats\n'

        for key, val in trace.stats.items():
            if isinstance(val, obspy.core.AttribDict):
                for kkey, vval in val.items():
                    ans += f"    stream[{ntrace}].stats['{key}']['{kkey}']={vval}\n"
            else:
                ans += f"  stream[{ntrace}].stats['{key}']={val}\n"
        ans += f'  # ------------------ stream[{ntrace}].data\n'
        ans += f"  stream[{ntrace}].data.dtype={stream[ntrace].data.dtype}\n"
        ans += f"  stream[{ntrace}].data.size={stream[ntrace].data.size}\n"
        ans += f"  stream[{ntrace}].data[:3]={stream[ntrace].data[:3]}\n"
    return ans


def print_stream(stream: obspy.core.stream.Stream):
    """Minimalist version of seispy.stream.Stream.__str__"""
    print(repr_stream(stream))


def show_stream(
    ax, stream: obspy.core.stream.Stream, 
    ydim=None,   # array of values or function : trace -> float
    gain=0.1, 
    starttime=None,
    swapxy: bool=False,
    set_lim: bool=True,
    **kwargs):

    assert len(stream)
    
    if ydim is None:
        ydim = np.arange(len(stream))   

    elif isinstance(ydim, (list, np.ndarray)):
        assert len(ydim) == len(stream), "one y value per trace please"

    elif isinstance(ydim, FunctionType):
        ydim = np.array([ydim(trace) for trace in stream])
    
    else:
        raise TypeError('ydim must be None, a list or array of floats or a function taking a trace as input')

    u = np.unique(ydim)
    interval = np.median(u[1:] - u[:-1])
    
    # find the std of all concatenated traces
    dev = np.std(np.concatenate([tr.data for tr in stream]))  #

    # auto adjust the amplitudes (preserve the relative amplitudes)
    gain1 = interval * (gain / dev) if dev != 0. else 1.0

    segments = []
    xmin, xmax = np.inf, -np.inf
    ymin, ymax = np.inf, -np.inf
    for trace_num, trace in enumerate(stream):
        # compute the time array (avoid linspace)
        time_array = np.arange(trace.stats.npts) * trace.stats.delta # seconds
        if starttime is None:
            time_array += trace.stats.starttime.timestamp
        else:
            time_array += starttime

        # the 1d data array for this trace is here
        data_array = (trace.data - trace.data.mean())

        # bug fix : if the ydim is a timestamp,
        # then the traces amplitudes might be altered by overflow => increase float size to 128
        data_array = data_array.astype('float128')

        x = time_array
        y = gain1 * data_array + ydim[trace_num]
        xmin = min([xmin, x.min()])
        xmax = max([xmax, x.max()])
        ymin = min([ymin, y.min()])
        ymax = max([ymax, y.max()])

        if swapxy:
            x, y = y, x

        segment = np.column_stack((x, y))
        segments.append(segment)

    if swapxy:
        xmin, xmax, ymin, ymax = ymin, ymax, xmin, xmax

    lc = LineCollection(segments, **kwargs)
    ax.add_collection(lc)

    if set_lim:
        ax.set_xlim((xmin, xmax))
        ax.set_ylim((ymin, ymax))

    return lc


def shade_stream(ax, stream, 
    ydim=None,
    starttime=None,
    powergain=0.6,
    swapxy: bool=False,
    **kwargs):

    assert len(stream)
    kwargs.setdefault('cmap', plt.get_cmap('seismic'))

    for trace in stream:
        # verify that the time array is the same for all traces (compare to first trace)
        if starttime is None:
            assert trace.stats.starttime == stream[0].stats.starttime
        assert trace.stats.delta == stream[0].stats.delta
        assert trace.stats.npts == stream[0].stats.npts

    # store the time array once for all traces
    time_array = +np.arange(trace.stats.npts) * trace.stats.delta # seconds
    if starttime is None:
        time_array += stream[0].stats.starttime.timestamp
    else:
        time_array += starttime

    if ydim is None:
        ydim = np.arange(len(stream))   

    elif isinstance(ydim, (list, np.ndarray)):
        assert len(ydim) == len(stream), "one y value per trace please"

    elif isinstance(ydim, FunctionType):
        ydim = np.array([ydim(trace) for trace in stream])
    
    else:
        raise TypeError('ydim must be None, '
            'a list or array of floats or a'
            ' function taking a trace as input')

    # all the data in one 2D matrix, 1 trace per row
    bscan = np.asarray([trace.data for trace in stream])

    # power gain to enhance the contrasts (only for display)
    bscan = np.sign(bscan) * np.abs(bscan) ** powergain

    i = np.argsort(ydim)
    x = time_array
    y = ydim[i]
    z = bscan[i, :]
    if swapxy:
        x, y = y, x
        z = z.T

    # show the bscan
    coll = ax.pcolormesh(
        x, y, z,
        vmin=-np.abs(bscan).max(),  # center the colorbar on 0
        vmax=+np.abs(bscan).max(),  # center the colorbar on 0
        shading="auto",
        **kwargs)

    return coll
